"""Contracts for the network scholarship audit transport and classification."""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request

import pytest

import duckrabbit.scholarship as scholarship
from duckrabbit.evidence import SourceRecord, SourceVerificationStatus
from duckrabbit.scholarship import audit_source, classify_http, compare_doi_metadata, run_scholarship_audit, title_matches


class _FakeResponse:
    """Minimal URL response standing in for the network transport boundary."""

    def __init__(self, payload: bytes, status: int = 200):
        self._payload = payload
        self.status = status

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


def _source(doi: str | None = "10.1234/abc", **overrides) -> SourceRecord:
    fields: dict[str, object] = {
        "key": "test_source",
        "citation_key": "testsource2020",
        "title": "Visual Capture of Gravity",
        "source_type": "primary",
        "url": "https://example.org/paper",
        "doi": doi,
        "supports": "claim",
        "year": 1997,
    }
    fields.update(overrides)
    return SourceRecord(**fields)


def test_title_matches_identity_without_punctuation_parity():
    assert title_matches("Visual Capture of Gravity!", "Visual Capture of Gravity")
    # Crossref short title: a substantial observed subset is still identity.
    assert title_matches(
        "Perception of Illusory Motion in Static Patterns and Related Phenomena",
        "Perception of Illusory Motion in Static Patterns",
    )
    assert not title_matches("Motion Perception", "Illusory Bereft")
    assert not title_matches("", "Visual Capture")
    assert not title_matches("Visual Capture", "")


def test_classify_http_maps_transport_outcomes_to_epistemic_status():
    assert classify_http(401, None) is SourceVerificationStatus.ACCESS_CONTROLLED
    assert classify_http(403, None) is SourceVerificationStatus.ACCESS_CONTROLLED
    assert classify_http(405, None) is SourceVerificationStatus.ACCESS_CONTROLLED
    assert classify_http(None, "timed out") is SourceVerificationStatus.UNAVAILABLE
    assert classify_http(500, None) is SourceVerificationStatus.UNAVAILABLE
    assert classify_http(200, None) is SourceVerificationStatus.URL_REACHABLE_UNRESOLVED


def test_compare_doi_metadata_requires_doi_title_and_year_identity():
    metadata = {
        "DOI": "https://doi.org/10.1234/ABC",
        "title": ["Visual Capture of Gravity!"],
        "published-print": "1997-05-01",
    }
    assert compare_doi_metadata(_source(), metadata) is SourceVerificationStatus.DOI_METADATA_MATCH
    assert compare_doi_metadata(_source(), {**metadata, "DOI": "10.9999/other"}) is SourceVerificationStatus.METADATA_MISMATCH
    assert compare_doi_metadata(_source(doi=None), metadata) is SourceVerificationStatus.METADATA_MISMATCH
    assert compare_doi_metadata(_source(), {**metadata, "title": ["Unrelated Keywords Entirely"]}) is SourceVerificationStatus.METADATA_MISMATCH
    assert compare_doi_metadata(_source(), {**metadata, "published-print": "2001-01-01"}) is SourceVerificationStatus.METADATA_MISMATCH


def test_open_http_rejects_non_http_schemes_before_io():
    with pytest.raises(ValueError, match="non-http"):
        scholarship._open_http(Request("file:///etc/passwd"), timeout=1.0)


def test_audit_source_doi_path_compares_crossref_metadata(monkeypatch):
    seen: list[tuple[str, str, float]] = []

    def fake_urlopen(request: Request, timeout: float):
        seen.append((request.full_url, request.get_method(), timeout))
        payload = {
            "message": {
                "DOI": "10.1234/abc",
                "title": ["Visual Capture of Gravity"],
                "published-print": "1997-05-01",
            }
        }
        return _FakeResponse(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr(scholarship, "urlopen", fake_urlopen)
    result = audit_source(_source(), timeout=2.5)
    assert result["verified"] is True
    assert result["verification_status"] == "doi_metadata_match"
    assert result["doi_http_status"] == 200
    assert result["metadata"]["DOI"] == "10.1234/abc"
    assert seen == [("https://api.crossref.org/works/10.1234%2Fabc", "GET", 2.5)]


def test_audit_source_doi_less_reachability(monkeypatch):
    monkeypatch.setattr(scholarship, "urlopen", lambda request, timeout: _FakeResponse(b"", status=200))
    result = audit_source(_source(doi=None), timeout=1.0)
    assert result["verified"] is True
    assert result["verification_status"] == "doi_less_archival"
    assert result["http_status"] == 200
    monkeypatch.setattr(scholarship, "urlopen", lambda request, timeout: _FakeResponse(b"", status=500))
    unavailable = audit_source(_source(doi=None), timeout=1.0)
    assert unavailable["verified"] is False
    assert unavailable["verification_status"] == "unavailable"


def test_audit_source_transport_failure_is_never_verified(monkeypatch):
    def refusing(request: Request, timeout: float):
        raise URLError("no route to host")

    monkeypatch.setattr(scholarship, "urlopen", refusing)
    result = audit_source(_source(doi=None), timeout=1.0)
    assert result["verified"] is False
    assert result["verification_status"] == "unavailable"
    assert result["http_status"] is None
    assert "no route to host" in result["error"]


def test_run_scholarship_audit_assembles_payload_from_offline_snapshot(monkeypatch):
    def offline(request: Request, timeout: float):
        raise URLError("offline")

    monkeypatch.setattr(scholarship, "urlopen", offline)
    payload = run_scholarship_audit(timeout=0.05, audited_on="2026-09-06")
    assert payload["schema_version"] == "duckrabbit/scholarship-audit/v1"
    assert payload["audited_on"] == "2026-09-06"
    assert payload["entry_count"] == len(payload["entry_audit"])
    assert payload["source_count"] == len(payload["results"])
    assert payload["verified_count"] == sum(1 for row in payload["results"] if row["verified"])
    assert sum(payload["verification_status_counts"].values()) == payload["source_count"]
    assert sum(payload["source_role_counts"].values()) == sum(len(row["source_keys"]) for row in payload["entry_audit"])
    assert payload["evidence_gap_entries"] == [row["illusion_id"] for row in payload["entry_audit"] if row["evidence_gap"]]
    assert all(row["verification_status"] == "unavailable" for row in payload["results"])
