"""Independent verifier for the package, evidence graph, and publication boundary."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

from .canonical import canonical_digest
from .errors import DuckRabbitError
from .evidence import load_evidence_matrix
from .formalism import validate_formalism_registry
from .generators import default_parameters, default_registry
from .metrics import measure_artifact
from .publication import validate_figure_registry
from .cover import validate_cover_manifest
from .metadata import validate_project_metadata
from .publication import publication_table_payloads, publication_caption_specs
from .schema import parameter_schema
from .taxonomy import ImplementationStatus, validate_taxonomy_catalog


@dataclass(frozen=True)
class AuditIssue:
    """One verifier finding with a stable machine-readable surface."""

    code: str
    severity: str
    surface: str
    message: str

    def __post_init__(self) -> None:
        if not self.code or self.severity not in {"error", "warning"} or not self.surface or not self.message:
            raise ValueError("audit issue requires code, severity, surface, and message")

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "severity": self.severity, "surface": self.surface, "message": self.message}


@dataclass(frozen=True)
class AuditReport:
    """Immutable result of an end-to-end DuckRabbit consistency audit."""

    schema_version: str
    status: str
    checks: tuple[str, ...]
    issues: tuple[AuditIssue, ...]
    generated_artifacts: int

    def __post_init__(self) -> None:
        if self.schema_version != "duckrabbit/audit/v1" or self.status not in {"passed", "failed"}:
            raise ValueError("unsupported audit report contract")
        if type(self.generated_artifacts) is not int or self.generated_artifacts < 0:
            raise ValueError("generated_artifacts must be a non-negative integer")

    @property
    def errors(self) -> tuple[AuditIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "error")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "checks": list(self.checks),
            "issue_count": len(self.issues),
            "error_count": len(self.errors),
            "warning_count": len(self.issues) - len(self.errors),
            "generated_artifacts": self.generated_artifacts,
            "issues": [issue.to_dict() for issue in self.issues],
        }


_T = TypeVar("_T")


def _check(issues: list[AuditIssue], checks: list[str], name: str, action: Callable[[], _T]) -> _T | None:
    checks.append(name)
    try:
        return action()
    except (DuckRabbitError, OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        issues.append(AuditIssue(f"{name}.failed", "error", name, str(exc)))
        return None


def run_audit(*, project_root: Path | None = None, output_root: Path | None = None, release: bool = False) -> AuditReport:
    """Run deterministic package, evidence, generator, and output checks.

    Development audits keep the historical warning for absent publication
    outputs.  ``release=True`` promotes that warning, metadata drift, and
    incomplete publication bundles to hard failures.
    """
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[2]
    output = Path(output_root) if output_root is not None else root / "output"
    issues: list[AuditIssue] = []
    checks: list[str] = []
    _check(issues, checks, "taxonomy", validate_taxonomy_catalog)
    metadata = _check(issues, checks, "metadata", lambda: validate_project_metadata(root))
    if metadata is not None and metadata.status == "failed":
        for error in metadata.errors:
            issues.append(AuditIssue("metadata.inconsistent", "error", "metadata", error))
    evidence = _check(issues, checks, "evidence", load_evidence_matrix)
    if evidence is not None:
        sources, records = evidence
        if len(sources) < len(records):
            issues.append(AuditIssue("evidence.coverage", "error", "evidence", "evidence source count is unexpectedly below record count"))
    _check(issues, checks, "formalism", lambda: validate_formalism_registry(project_root=root))
    generated = 0
    def generators_check() -> None:
        nonlocal generated
        implemented = {entry.illusion_id for entry in validate_taxonomy_catalog() if entry.implementation_status is ImplementationStatus.IMPLEMENTED}
        registered = {spec.illusion_id for spec in default_registry.list()}
        if registered != implemented:
            raise ValueError(f"registry/catalog mismatch: registered={sorted(registered)}, implemented={sorted(implemented)}")
        for spec in default_registry.list():
            parameters = default_parameters(spec.illusion_id)
            parameter_schema(parameters)
            artifact = default_registry.generate(spec.illusion_id, parameters, seed=0)
            digest = canonical_digest(artifact)
            # canonical_digest is content-addressed sha256; the audit asserts
            # digest well-formedness (shape + lowercase hex) rather than
            # re-hashing the same serialization against itself.
            if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
                raise ValueError(f"canonical digest failed for {spec.illusion_id}")
            measure_artifact(artifact)
            generated += 1
    _check(issues, checks, "generators", generators_check)
    registry_path = output / "figures" / "figure_registry.json"
    if registry_path.is_file():
        _check(issues, checks, "figure_registry", lambda: validate_figure_registry(registry_path, output_dir=output))
    else:
        checks.append("figure_registry")
        severity = "error" if release else "warning"
        issues.append(AuditIssue("figure_registry.not_generated", severity, "publication", f"figure registry not present at {registry_path}; run publish before release"))
    cover_manifest = output / "reports" / "cover_visualization.json"
    if cover_manifest.is_file():
        _check(issues, checks, "cover", lambda: validate_cover_manifest(cover_manifest, output_dir=output))
    else:
        checks.append("cover")
        if release:
            issues.append(AuditIssue("cover.not_generated", "error", "publication", f"cover manifest not present at {cover_manifest}"))
    if release:
        def publication_bundle_check() -> None:
            expected_tables = publication_table_payloads()
            for stem in expected_tables:
                for suffix in (".md", ".json"):
                    path = output / "data" / f"{stem}{suffix}"
                    if not path.is_file() or not path.read_bytes():
                        raise ValueError(f"publication table output missing or empty: {path}")
            if len(publication_caption_specs()) != 15 or len(expected_tables) != 10:
                raise ValueError("publication figure/table counts drift from the v0.5 release contract")
        _check(issues, checks, "publication_bundle", publication_bundle_check)
    status = "failed" if any(issue.severity == "error" for issue in issues) else "passed"
    return AuditReport("duckrabbit/audit/v1", status, tuple(checks), tuple(issues), generated)


__all__ = ["AuditIssue", "AuditReport", "run_audit"]
