"""Strict v2 provenance, inspection, and verification contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .artifacts import ArtifactSummary, CanonicalArtifact, EncodedArtifact, _validate_artifact_summary
from .errors import ManifestValidationError
from .io import atomic_write_text
from .parameters import BackendKind, MediaFormat, Seed
from .schema import ParameterSchema
from .serialization import jsonable
from .taxonomy import ClaimLevel, EvidenceStatus, ImplementationStatus, Modality, TaxonomyEntry


class VerificationStatus(str, Enum):
    """Result of deterministic artifact and encoded-media checks."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    FAILED = "failed"


@dataclass(frozen=True)
class DecodedInspection:
    """Typed facts obtained by decoding an encoded artifact."""

    format: MediaFormat
    backend: BackendKind
    kind: str
    facts: Mapping[str, object]

    def __post_init__(self) -> None:
        if not isinstance(self.format, MediaFormat):
            raise ManifestValidationError("decoded inspection format must be MediaFormat")
        if not isinstance(self.backend, BackendKind):
            raise ManifestValidationError("decoded inspection backend must be BackendKind")
        if not self.kind or not isinstance(self.kind, str):
            raise ManifestValidationError("decoded inspection kind is required")
        if not isinstance(self.facts, Mapping) or not all(isinstance(key, str) for key in self.facts):
            raise ManifestValidationError("decoded inspection facts must be a string-keyed mapping")
        object.__setattr__(self, "facts", _freeze(self.facts))

    def to_dict(self) -> dict[str, object]:
        return {
            "format": self.format.value,
            "backend": self.backend.value,
            "kind": self.kind,
            "facts": jsonable(self.facts),
        }


@dataclass(frozen=True)
class CanonicalRecord:
    """Hash and storage facts for the canonical in-memory stimulus."""

    schema_version: str
    algorithm: str
    digest: str
    byte_order: str
    dtype: str
    byte_count: int

    def __post_init__(self) -> None:
        if self.schema_version != "duckrabbit/canonical/v1":
            raise ManifestValidationError("unsupported canonical schema version")
        if self.algorithm != "sha256" or self.byte_order != "little" or self.dtype != "<f4":
            raise ManifestValidationError("canonical record must use little-endian float32 SHA-256")
        if len(self.digest) != 64 or any(character not in "0123456789abcdef" for character in self.digest):
            raise ManifestValidationError("canonical digest must be lowercase SHA-256 hex")
        if type(self.byte_count) is not int or self.byte_count <= 0:
            raise ManifestValidationError("canonical byte_count must be a positive integer")


@dataclass(frozen=True)
class VerificationReport:
    """Machine-readable checks performed during generation or inspection."""

    status: VerificationStatus
    checks: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.status, VerificationStatus):
            raise ManifestValidationError("verification status must be VerificationStatus")
        if not all(isinstance(item, str) and item for item in (*self.checks, *self.errors)):
            raise ManifestValidationError("verification checks and errors must be non-empty strings")
        if self.status is VerificationStatus.FAILED and not self.errors:
            raise ManifestValidationError("failed verification requires at least one error")


@dataclass(frozen=True)
class Manifest:
    """Typed v2 provenance manifest for one generated canonical stimulus."""

    package_version: str
    generator_version: str
    illusion_id: str
    implementation_status: ImplementationStatus
    evidence_status: EvidenceStatus
    claim_level: ClaimLevel
    modality: tuple[Modality, ...]
    taxonomy: TaxonomyEntry
    parameter_schema: ParameterSchema
    parameters: Mapping[str, object]
    seed: Seed
    artifact: ArtifactSummary
    canonical: CanonicalRecord
    verification: VerificationReport
    metrics: Mapping[str, object] | None = None
    encoding: EncodedArtifact | None = None
    decoded_inspection: DecodedInspection | None = None
    schema_version: str = "duckrabbit/artifact/v2"
    legacy_manifest: str | None = None

    def __post_init__(self) -> None:
        if self.schema_version != "duckrabbit/artifact/v2":
            raise ManifestValidationError("unsupported manifest schema version")
        for name, value in (("package_version", self.package_version), ("generator_version", self.generator_version), ("illusion_id", self.illusion_id)):
            if not isinstance(value, str) or not value:
                raise ManifestValidationError(f"manifest {name} is required")
        if not isinstance(self.implementation_status, ImplementationStatus):
            raise ManifestValidationError("manifest implementation_status must be ImplementationStatus")
        if not isinstance(self.evidence_status, EvidenceStatus):
            raise ManifestValidationError("manifest evidence_status must be EvidenceStatus")
        if not isinstance(self.claim_level, ClaimLevel):
            raise ManifestValidationError("manifest claim_level must be ClaimLevel")
        if not isinstance(self.modality, tuple) or not self.modality or not all(isinstance(item, Modality) for item in self.modality):
            raise ManifestValidationError("manifest modality must be a non-empty tuple of Modality")
        if not isinstance(self.taxonomy, TaxonomyEntry):
            raise ManifestValidationError("manifest taxonomy must be TaxonomyEntry")
        if self.taxonomy.illusion_id != self.illusion_id or self.taxonomy.modalities != self.modality:
            raise ManifestValidationError("manifest taxonomy disagrees with identity or modality")
        if self.taxonomy.implementation_status is not self.implementation_status or self.taxonomy.evidence_status is not self.evidence_status:
            raise ManifestValidationError("manifest taxonomy disagrees with status metadata")
        if not isinstance(self.parameter_schema, ParameterSchema) or self.parameter_schema.parameter_type == "":
            raise ManifestValidationError("manifest parameter_schema is invalid")
        if not isinstance(self.parameters, Mapping) or not all(isinstance(key, str) for key in self.parameters):
            raise ManifestValidationError("manifest parameters must be a string-keyed mapping")
        try:
            self.parameter_schema.validate_payload(self.parameters)
        except ValueError as exc:
            raise ManifestValidationError(f"manifest parameters are invalid: {exc}") from exc
        if not isinstance(self.seed, Seed):
            try:
                object.__setattr__(self, "seed", Seed(self.seed))
            except (TypeError, ValueError) as exc:
                raise ManifestValidationError("manifest seed must be a signed 64-bit integer") from exc
        try:
            _validate_artifact_summary(self.artifact)
        except ValueError as exc:
            raise ManifestValidationError(f"manifest artifact summary is invalid: {exc}") from exc
        if not isinstance(self.canonical, CanonicalRecord):
            raise ManifestValidationError("manifest canonical record is invalid")
        if not isinstance(self.verification, VerificationReport):
            raise ManifestValidationError("manifest verification report is invalid")
        if self.metrics is not None and not isinstance(self.metrics, Mapping):
            raise ManifestValidationError("manifest metrics must be a mapping or null")
        if self.encoding is not None and not isinstance(self.encoding, EncodedArtifact):
            raise ManifestValidationError("manifest encoding must be EncodedArtifact")
        if self.decoded_inspection is not None and not isinstance(self.decoded_inspection, DecodedInspection):
            raise ManifestValidationError("decoded inspection must be DecodedInspection or null")
        if self.legacy_manifest is not None and not isinstance(self.legacy_manifest, str):
            raise ManifestValidationError("legacy_manifest must be a string or null")
        object.__setattr__(self, "parameters", _freeze(self.parameters))
        if self.metrics is not None:
            object.__setattr__(self, "metrics", _freeze(self.metrics))

    def to_dict(self) -> dict[str, object]:
        """Serialize the manifest to stable JSON-compatible primitives."""
        result = jsonable(self)
        if not isinstance(result, dict):  # pragma: no cover - dataclass invariant
            raise ManifestValidationError("manifest did not serialize to an object")
        return result

    def write(self, path: Path) -> Path:
        """Write a canonical, sorted manifest JSON document."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return atomic_write_text(path, json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n")


@dataclass(frozen=True)
class RenderResult:
    """Typed result of canonical generation and optional encoding."""

    artifact: CanonicalArtifact
    manifest: Manifest
    output_path: Path | None = None
    manifest_path: Path | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.manifest, Manifest):
            raise ManifestValidationError("render result manifest must be Manifest")
        if self.output_path is not None and not isinstance(self.output_path, Path):
            raise ManifestValidationError("render result output_path must be Path or null")
        if self.manifest_path is not None and not isinstance(self.manifest_path, Path):
            raise ManifestValidationError("render result manifest_path must be Path or null")

    def to_dict(self) -> dict[str, object]:
        payload = self.manifest.to_dict()
        payload["output"] = str(self.output_path) if self.output_path else None
        payload["manifest"] = str(self.manifest_path) if self.manifest_path else None
        return payload


def _freeze(value: object) -> object:
    """Recursively freeze JSON-like mappings and sequences at the API boundary."""
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def upconvert_v1_manifest(payload: Mapping[str, object]) -> dict[str, object]:
    """Convert a v1 JSON manifest into an explicitly unverified v2 payload."""
    if payload.get("schema_version") != "duckrabbit/artifact/v1":
        raise ManifestValidationError("upconversion requires a duckrabbit/artifact/v1 manifest")
    encoded = payload.get("encoding")
    canonical_digest = payload.get("canonical_digest")
    artifact = payload.get("artifact")
    taxonomy = payload.get("taxonomy")
    if not isinstance(artifact, Mapping) or "nbytes" not in artifact:
        raise ManifestValidationError(
            "upconversion requires the v1 manifest's artifact summary to declare nbytes"
        )
    result = dict(payload)
    result.update(
        {
            "schema_version": "duckrabbit/artifact/v2",
            "legacy_manifest": "duckrabbit/artifact/v1",
            "claim_level": ClaimLevel.CANONICAL_STIMULUS.value,
            "canonical": {
                "schema_version": "duckrabbit/canonical/v1",
                "algorithm": "sha256",
                "digest": canonical_digest,
                "byte_order": "little",
                "dtype": "<f4",
                "byte_count": int(artifact["nbytes"]),
            },
            "verification": {
                "status": VerificationStatus.UNVERIFIED.value,
                "checks": [],
                "errors": ["manifest was upconverted from v1; encoded media was not re-inspected"],
            },
            "encoding": encoded,
            "decoded_inspection": None,
            "package_version": "unknown",
            "generator_version": "unknown",
            "evidence_status": (
                taxonomy.get("evidence_status", "literature_backed_engineering_entry")
                if isinstance(taxonomy, Mapping)
                else "literature_backed_engineering_entry"
            ),
        }
    )
    return result


def read_manifest(path: Path) -> dict[str, object]:
    """Read v1 or v2 JSON and return a version-normalized payload."""
    path = Path(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestValidationError(f"cannot read manifest {path}: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise ManifestValidationError("manifest JSON must contain an object")
    if payload.get("schema_version") == "duckrabbit/artifact/v1":
        return upconvert_v1_manifest(payload)
    if payload.get("schema_version") != "duckrabbit/artifact/v2":
        raise ManifestValidationError("unsupported manifest schema version")
    return dict(payload)


def verify_file_hash(path: Path, expected_sha256: str) -> bool:
    """Verify an encoded file hash for the inspection command."""
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return digest == expected_sha256
