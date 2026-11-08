"""Release identity, claim lineage, caption, and strict-audit oracles."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib

import pytest
import yaml

import duckrabbit
from duckrabbit.audit import run_audit
from duckrabbit.claims import ClaimBasis, ClaimRecord, default_claim_registry, validate_claim_registry
from duckrabbit.evidence import EvidenceLineage, EvidenceRole, SourceRecord, SourceVerificationStatus
from duckrabbit.metadata import MetadataAuditReport, PublicationMetadata, validate_project_metadata
from duckrabbit.taxonomy import ClaimLevel
from duckrabbit.version import __version__


ROOT = Path(__file__).resolve().parents[1]


def test_metadata_identity_is_cross_file_consistent_and_serializable() -> None:
    report = validate_project_metadata(ROOT)
    assert report.status == "passed", json.dumps(report.to_dict(), indent=2)
    assert report.metadata.author == "Daniel Ari Friedman"
    assert report.metadata.orcid == "0000-0001-6232-9096"
    assert report.metadata.version == __version__
    assert report.to_dict()["schema_version"] == "duckrabbit/metadata-audit/v1"
    assert MetadataAuditReport("passed", PublicationMetadata("a", "b", "c", "d", "e", "", "forthcoming"), (), ()).to_dict()["errors"] == []
    with pytest.raises(ValueError, match="status"):
        MetadataAuditReport("bad", report.metadata, (), ())


def test_supported_python_floor_and_lock_metadata_are_consistent() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    locked_project = next(package for package in lock["package"] if package["name"] == project["name"])
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    assert project["requires-python"] == lock["requires-python"] == ">=3.11"
    assert "3.11" in workflow["jobs"]["test"]["strategy"]["matrix"]["python-version"]
    assert locked_project["version"] == project["version"] == __version__
    assert not any(dependency.startswith(("tomli", "typing-extensions")) for dependency in project["dependencies"])
    assert not any(dependency["name"] in {"tomli", "typing-extensions"} for dependency in locked_project["metadata"]["requires-dist"])


def test_typed_claim_registry_and_evidence_lineage_are_fail_closed() -> None:
    claims = default_claim_registry()
    assert len(claims) >= len(duckrabbit.taxonomy_entries())
    assert all(claim.limitation and claim.source_or_artifact_lineage for claim in claims)
    assert validate_claim_registry(claims) == claims
    with pytest.raises(ValueError, match="limitation"):
        ClaimRecord("bad", "A fact", ClaimBasis.DERIVED_FROM_CODE, ClaimLevel.PHYSICAL_METRIC, ("code",), "", "manuscript/x.md")
    with pytest.raises(ValueError, match="id"):
        ClaimRecord("", "A fact", ClaimBasis.DERIVED_FROM_CODE, ClaimLevel.PHYSICAL_METRIC, ("code",), "limit", "manuscript/x.md")
    with pytest.raises(ValueError, match="typed enums"):
        ClaimRecord("bad-type", "A fact", "code", ClaimLevel.PHYSICAL_METRIC, ("code",), "limit", "manuscript/x.md")
    with pytest.raises(ValueError, match="lineage"):
        ClaimRecord("bad-lineage", "A fact", ClaimBasis.DERIVED_FROM_CODE, ClaimLevel.PHYSICAL_METRIC, (), "limit", "manuscript/x.md")
    with pytest.raises(ValueError, match="overclaim"):
        ClaimRecord("bad-claim", "This causes observers to perceive a result", ClaimBasis.DERIVED_FROM_CODE, ClaimLevel.PHYSICAL_METRIC, ("code",), "limit", "manuscript/x.md")
    assert claims[0].to_dict()["claim_id"] == "catalog:count"
    with pytest.raises(ValueError, match="duplicate"):
        validate_claim_registry([claims[0], claims[0]])
    lineage = EvidenceLineage(EvidenceRole.LIMITATION, "display conditions are external")
    assert lineage.to_dict() if hasattr(lineage, "to_dict") else lineage.role is EvidenceRole.LIMITATION
    source = SourceRecord("x", "x", "A source", "review", "https://example.org/x", None, "a claim", SourceVerificationStatus.SNAPSHOT_VALIDATED)
    assert source.role is EvidenceRole.REVIEW_OR_SYNTHESIS
    historic = SourceRecord("historic", "historic", "A pre-1800 source", "primary", "https://example.org/historic", None, "a historical claim", year=1700)
    assert historic.year == 1700
    with pytest.raises(Exception, match="verification status"):
        SourceRecord("x", "x", "A source", "review", "https://example.org/x", None, "a claim", "reachable")
    for field, value, message in (("verified_on", 3, "ISO date"), ("verified_on", "not-a-date", "ISO date"), ("resolver", "", "resolver"), ("authors", [3], "authors"), ("year", 0, "year")):
        kwargs = {field: value}
        with pytest.raises(Exception, match=message):
            SourceRecord("bad", "bad", "A source", "review", "https://example.org/x", None, "a claim", **kwargs)


def test_release_audit_requires_and_accepts_publication_bundle(tmp_path: Path, publication_bundle) -> None:
    missing = run_audit(project_root=ROOT, output_root=tmp_path / "missing", release=True)
    assert missing.status == "failed"
    assert any(issue.code == "figure_registry.not_generated" and issue.severity == "error" for issue in missing.issues)
    ready = run_audit(project_root=ROOT, output_root=publication_bundle, release=True)
    assert ready.status == "passed", json.dumps(ready.to_dict(), indent=2)
    assert "publication_bundle" in ready.checks
