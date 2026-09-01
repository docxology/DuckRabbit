"""Cross-file publication metadata validation.

The project intentionally keeps metadata in the formats expected by the
Python package, citation managers, Zenodo, codemeta, and the manuscript
renderer.  This module is the small, dependency-free consistency oracle that
prevents those copies from silently drifting.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import tomllib

from .version import __version__
from .urls import ORCID_PREFIX


EXPECTED_AUTHOR = "Daniel Ari Friedman"
EXPECTED_ORCID = "0000-0001-6232-9096"
EXPECTED_VERSION = __version__
EXPECTED_TITLE = "DuckRabbit: Typed Multimodal Illusion Generator"
EXPECTED_LICENSE = "MIT"


@dataclass(frozen=True)
class PublicationMetadata:
    """Normalized identity fields collected from one project checkout."""

    author: str
    orcid: str
    version: str
    title: str
    license: str
    doi: str
    doi_status: str


@dataclass(frozen=True)
class MetadataAuditReport:
    """Machine-readable result of a cross-file metadata audit."""

    status: str
    metadata: PublicationMetadata
    files: tuple[str, ...]
    errors: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status not in {"passed", "failed"}:
            raise ValueError("metadata audit status must be passed or failed")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "duckrabbit/metadata-audit/v1",
            "status": self.status,
            "metadata": {
                "author": self.metadata.author,
                "orcid": self.metadata.orcid,
                "version": self.metadata.version,
                "title": self.metadata.title,
                "license": self.metadata.license,
                "doi": self.metadata.doi,
                "doi_status": self.metadata.doi_status,
            },
            "files": list(self.files),
            "errors": list(self.errors),
        }


def _json(root: Path, name: str) -> dict[str, object]:
    path = root / name
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{name} must contain an object")
    return value


def _yaml_scalar(text: str, key: str, *, allow_empty: bool = False) -> str:
    value_pattern = r"([^\"'\n#]*?)" if allow_empty else r"([^\"'\n#]+?)"
    match = re.search(rf"^\s*{re.escape(key)}:\s*[\"']?{value_pattern}[\"']?\s*$", text, re.MULTILINE)
    if not match:
        raise ValueError(f"manuscript/config.yaml is missing {key}")
    return match.group(1).strip()


def _yaml_author(text: str) -> tuple[str, str]:
    match = re.search(
        r"^\s*- name:\s*[\"']?([^\"'\n]+?)[\"']?\s*$.*?^\s+orcid:\s*[\"']?([^\"'\n]+?)[\"']?\s*$",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise ValueError("manuscript/config.yaml must declare author name and ORCID")
    return match.group(1).strip(), match.group(2).strip()


def _cff(text: str) -> dict[str, str]:
    def scalar(key: str) -> str:
        match = re.search(rf"^\s*{re.escape(key)}:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", text, re.MULTILINE)
        if not match:
            raise ValueError(f"CITATION.cff is missing {key}")
        return match.group(1).strip()

    family = re.search(r"^\s*-\s*family-names:\s*([^\n]+)$", text, re.MULTILINE)
    given = re.search(r"^\s+given-names:\s*([^\n]+)$", text, re.MULTILINE)
    orcid = re.search(r"^\s+orcid:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", text, re.MULTILINE)
    if not family or not given or not orcid:
        raise ValueError("CITATION.cff must declare family, given, and ORCID")
    return {
        "title": scalar("title"),
        "version": scalar("version"),
        "license": scalar("license"),
        "author": f"{given.group(1).strip()} {family.group(1).strip()}",
            "orcid": orcid.group(1).strip().removeprefix(ORCID_PREFIX),
    }


def _normalized_author(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def default_manuscript_dir(project_root: Path | None = None) -> Path:
    """Canonical manuscript directory with legacy fallback.

    The manuscript lives at ``docs/manuscript/``; the legacy top-level
    ``manuscript/`` path is still accepted for checkouts that have not been
    relocated. docs-first matches the resolver convention used across the
    sibling template ecosystem. ``project_root`` defaults to this package's
    own repository; audits over a copied tree must pass the copy's root so the
    copied tree's own manuscript directory is audited, not this repo's.
    """
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[2]
    relocated = root / "docs" / "manuscript"
    if relocated.is_dir():
        return relocated
    return root / "manuscript"


def validate_project_metadata(project_root: Path | None = None) -> MetadataAuditReport:
    """Validate identity, version, license, and DOI status across sidecars."""
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[2]
    errors: list[str] = []
    files = ("pyproject.toml", "CITATION.cff", "codemeta.json", ".zenodo.json")
    try:
        pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        config_text = (default_manuscript_dir(root) / "config.yaml").read_text(encoding="utf-8")
        cff = _cff((root / "CITATION.cff").read_text(encoding="utf-8"))
        codemeta = _json(root, "codemeta.json")
        zenodo = _json(root, ".zenodo.json")
        config_author, config_orcid = _yaml_author(config_text)
        config = {
            "title": _yaml_scalar(config_text, "title"),
            "version": _yaml_scalar(config_text, "version"),
            "doi": _yaml_scalar(config_text, "doi", allow_empty=True),
            "doi_status": _yaml_scalar(config_text, "doi_status"),
            "license": _yaml_scalar(config_text, "license"),
            "author": config_author,
            "orcid": config_orcid,
        }
        project = pyproject.get("project", {})
        project_author = project.get("authors", [{}])[0] if isinstance(project.get("authors", [{}]), list) else {}
        codemeta_author = codemeta.get("author", [{}])[0] if isinstance(codemeta.get("author", [{}]), list) else {}
        zenodo_author = zenodo.get("creators", [{}])[0] if isinstance(zenodo.get("creators", [{}]), list) else {}
        normalized = PublicationMetadata(
            author=EXPECTED_AUTHOR,
            orcid=EXPECTED_ORCID,
            version=str(project.get("version", "")),
            title=str(project.get("name", "")),
            license=str(project.get("license", "")),
            doi=str(config["doi"]),
            doi_status=str(config["doi_status"]),
        )
        comparisons = {
            "config author": config_author,
            "CITATION author": cff["author"],
            "codemeta author": f"{codemeta_author.get('givenName', '')} {codemeta_author.get('familyName', '')}".strip(),
            "Zenodo author": (
                " ".join(reversed([part.strip() for part in str(zenodo_author.get("name", "")).split(",", 1)]))
                if "," in str(zenodo_author.get("name", ""))
                else str(zenodo_author.get("name", ""))
            ),
            "pyproject author": str(project_author.get("name", "")),
        }
        for source, value in comparisons.items():
            if _normalized_author(value) != EXPECTED_AUTHOR:
                errors.append(f"{source} disagrees with {EXPECTED_AUTHOR!r}: {value!r}")
        orcids = {
            "config": config_orcid,
            "CITATION": cff["orcid"],
            "codemeta": str(codemeta_author.get("@id", "")).removeprefix(ORCID_PREFIX),
            "Zenodo": str(zenodo_author.get("orcid", "")),
        }
        for source, value in orcids.items():
            if value != EXPECTED_ORCID:
                errors.append(f"{source} ORCID disagrees with {EXPECTED_ORCID}: {value!r}")
        versions = {"pyproject": str(project.get("version", "")), "config": config["version"], "CITATION": cff["version"], "codemeta": str(codemeta.get("version", "")), "Zenodo": str(zenodo.get("version", ""))}
        for source, value in versions.items():
            if value != EXPECTED_VERSION:
                errors.append(f"{source} version disagrees with {EXPECTED_VERSION}: {value!r}")
        titles = {"config": config["title"], "CITATION": cff["title"], "codemeta": str(codemeta.get("name", "")), "Zenodo": str(zenodo.get("title", ""))}
        for source, value in titles.items():
            if value != EXPECTED_TITLE:
                errors.append(f"{source} title disagrees with expected title: {value!r}")
        licenses = {"config": config["license"], "CITATION": cff["license"], "codemeta": "MIT" if str(codemeta.get("license", "")).endswith("/MIT.html") else str(codemeta.get("license", "")), "Zenodo": str(zenodo.get("license", "")), "pyproject": str(project.get("license", ""))}
        for source, value in licenses.items():
            if value != EXPECTED_LICENSE:
                errors.append(f"{source} license disagrees with {EXPECTED_LICENSE}: {value!r}")
        if config["doi"] == "":
            if config["doi_status"] != "forthcoming":
                errors.append("publication doi_status must be forthcoming while DOI is empty")
        else:
            if not re.fullmatch(r"10\.5281/zenodo\.\d+", config["doi"]):
                errors.append(f"publication DOI does not look like a real Zenodo DOI: {config['doi']!r}")
            if config["doi_status"] == "forthcoming":
                errors.append("publication doi_status must not be forthcoming once a DOI is set")
        if "XXXX" in config["doi"] or "placeholder" in config["doi"].lower():
            errors.append("fake DOI placeholder detected")
    except (OSError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        errors.append(str(exc))
        normalized = PublicationMetadata("", "", "", "", "", "", "")
    return MetadataAuditReport("failed" if errors else "passed", normalized, files, tuple(errors))


__all__ = ["EXPECTED_AUTHOR", "EXPECTED_ORCID", "EXPECTED_VERSION", "EXPECTED_TITLE", "EXPECTED_LICENSE", "MetadataAuditReport", "PublicationMetadata", "validate_project_metadata"]
