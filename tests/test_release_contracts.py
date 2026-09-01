"""Release identity, claim lineage, caption, and strict-audit oracles."""

from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

import duckrabbit
from duckrabbit.audit import run_audit
from duckrabbit.claims import ClaimBasis, ClaimRecord, default_claim_registry, validate_claim_registry
from duckrabbit.evidence import EvidenceLineage, EvidenceRole, SourceRecord, SourceVerificationStatus
from duckrabbit.metadata import MetadataAuditReport, PublicationMetadata, validate_project_metadata
from duckrabbit.taxonomy import ClaimLevel
from duckrabbit.publication import generate_publication_outputs


ROOT = Path(__file__).resolve().parents[1]


def test_metadata_identity_is_cross_file_consistent_and_serializable() -> None:
    report = validate_project_metadata(ROOT)
    assert report.status == "passed", json.dumps(report.to_dict(), indent=2)
    assert report.metadata.author == "Daniel Ari Friedman"
    assert report.metadata.orcid == "0000-0001-6232-9096"
    assert report.metadata.version == "0.5.0"
    assert report.metadata.doi == "10.5281/zenodo.21419693"
    assert report.metadata.doi_status == "published"
    assert report.to_dict()["schema_version"] == "duckrabbit/metadata-audit/v1"
    assert MetadataAuditReport("passed", PublicationMetadata("a", "b", "c", "d", "e", "", "forthcoming"), (), ()).to_dict()["errors"] == []
    with pytest.raises(ValueError, match="status"):
        MetadataAuditReport("bad", report.metadata, (), ())


def test_metadata_audit_fails_on_drift_without_network(tmp_path: Path) -> None:
    for name in ("pyproject.toml", "docs/manuscript/config.yaml", "CITATION.cff", "codemeta.json", ".zenodo.json"):
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, destination)
    config = tmp_path / "docs" / "manuscript" / "config.yaml"
    # A real DOI is set (checked-in release state) — reverting doi_status to
    # "forthcoming" while the DOI stays populated must be caught as drift.
    config.write_text(config.read_text(encoding="utf-8").replace("doi_status: \"published\"", "doi_status: \"forthcoming\""), encoding="utf-8")
    report = validate_project_metadata(tmp_path)
    assert report.status == "failed"
    assert any("doi_status" in error for error in report.errors)


def test_metadata_audit_fails_when_doi_empty_but_status_not_forthcoming(tmp_path: Path) -> None:
    for name in ("pyproject.toml", "docs/manuscript/config.yaml", "CITATION.cff", "codemeta.json", ".zenodo.json"):
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, destination)
    config = tmp_path / "docs" / "manuscript" / "config.yaml"
    text = config.read_text(encoding="utf-8")
    text = text.replace('doi: "10.5281/zenodo.21419693"', 'doi: ""')
    config.write_text(text, encoding="utf-8")
    report = validate_project_metadata(tmp_path)
    assert report.status == "failed"
    assert any("doi_status must be forthcoming" in error for error in report.errors)


def test_metadata_audit_catches_each_identity_field(tmp_path: Path) -> None:
    for name in ("pyproject.toml", "docs/manuscript/config.yaml", "CITATION.cff", "codemeta.json", ".zenodo.json"):
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, destination)

    def check_config(old: str, new: str, expected: str) -> None:
        path = tmp_path / "docs" / "manuscript" / "config.yaml"
        original = (ROOT / "docs" / "manuscript" / "config.yaml").read_text(encoding="utf-8")
        path.write_text(original.replace(old, new), encoding="utf-8")
        result = validate_project_metadata(tmp_path)
        assert result.status == "failed" and any(expected in error for error in result.errors)

    check_config('name: "Daniel Ari Friedman"', 'name: "Other Author"', "config author")
    check_config('orcid: "0000-0001-6232-9096"', 'orcid: "0000-0000-0000-0000"', "ORCID")
    check_config('version: "0.5.0"', 'version: "0.4.0"', "version")
    check_config('title: "DuckRabbit: Typed Multimodal Illusion Generator"', 'title: "Other title"', "title")
    check_config('license: "MIT"', 'license: "GPL"', "license")
    check_config('doi: "10.5281/zenodo.21419693"', 'doi: "10.5281/zenodo.XXXX"', "placeholder")
    check_config('doi_status: "published"', 'doi_status: "forthcoming"', "doi_status")

    (tmp_path / "codemeta.json").write_text("[]", encoding="utf-8")
    malformed = validate_project_metadata(tmp_path)
    assert malformed.status == "failed"


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


def test_release_audit_requires_and_accepts_publication_bundle(tmp_path: Path) -> None:
    missing = run_audit(project_root=ROOT, output_root=tmp_path / "missing", release=True)
    assert missing.status == "failed"
    assert any(issue.code == "figure_registry.not_generated" and issue.severity == "error" for issue in missing.issues)
    generate_publication_outputs(tmp_path / "ready")
    ready = run_audit(project_root=ROOT, output_root=tmp_path / "ready", release=True)
    assert ready.status == "passed", json.dumps(ready.to_dict(), indent=2)
    assert "publication_bundle" in ready.checks
