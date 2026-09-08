"""Focused negative controls for the checked-in scholarly evidence boundary."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from duckrabbit.errors import ParameterValidationError
from duckrabbit.evidence import EvidenceRecord, SourceRecord, evidence_for, load_evidence_matrix, validate_citation_keys, validate_evidence_matrix
from duckrabbit.taxonomy import ClaimLevel, EvidenceStatus, ImplementationStatus


ROOT = Path(__file__).resolve().parents[1]


def _matrix(tmp_path: Path) -> tuple[dict[str, object], Path]:
    payload = json.loads((ROOT / "data" / "evidence_matrix.json").read_text(encoding="utf-8"))
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload, path


@pytest.mark.parametrize(
    ("location", "value", "message"),
    (("source", None, "source key"), ("source_type", 3, "source_type"), ("entry_sources", "not-an-array", "primary_sources")),
)
def test_evidence_loader_rejects_malformed_json_types(tmp_path: Path, location: str, value: object, message: str) -> None:
    payload, path = _matrix(tmp_path)
    if location == "source":
        payload["sources"][0]["key"] = value  # type: ignore[index]
    elif location == "source_type":
        payload["sources"][0]["source_type"] = value  # type: ignore[index]
    else:
        payload["entries"][0]["primary_sources"] = value  # type: ignore[index]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ParameterValidationError, match=message):
        load_evidence_matrix(path)


def test_evidence_loader_rejects_non_string_claim_and_missing_contract(tmp_path: Path) -> None:
    payload, path = _matrix(tmp_path)
    payload["entries"][-1]["supported_claim"] = 12  # type: ignore[index]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ParameterValidationError, match="supported_claim"):
        load_evidence_matrix(path)

    payload, path = _matrix(tmp_path)
    payload["entries"][-1]["missing_contract"] = 42  # type: ignore[index]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ParameterValidationError, match="missing_contract"):
        load_evidence_matrix(path)


def test_evidence_relationships_and_io_fail_closed(tmp_path: Path) -> None:
    sources, entries = load_evidence_matrix()
    base = entries["visual.duck_rabbit"]
    with pytest.raises(ParameterValidationError, match="status disagrees"):
        validate_evidence_matrix(sources, {**entries, base.illusion_id: replace(base, implementation_status=ImplementationStatus.INPUT_REQUIRED, missing_contract="missing")})
    with pytest.raises(ParameterValidationError, match="evidence_status disagrees"):
        validate_evidence_matrix(sources, {**entries, base.illusion_id: replace(base, evidence_status=EvidenceStatus.LITERATURE_BACKED_PLANNED_ENTRY)})
    with pytest.raises(ParameterValidationError, match="lacks primary"):
        validate_evidence_matrix(sources, {**entries, base.illusion_id: replace(base, primary_sources=(), review_sources=(), theory_sources=("gregory1997visual",))})
    with pytest.raises(ParameterValidationError, match="not in the evidence matrix"):
        reduced_sources = dict(sources)
        reduced_sources.pop("gregory1997visual")
        validate_evidence_matrix(reduced_sources, entries)
    with pytest.raises(ParameterValidationError, match="claim level"):
        bad_claim = replace(base)
        object.__setattr__(bad_claim, "supported_claim_level", ClaimLevel.PHYSICAL_METRIC)
        validate_evidence_matrix(sources, {**entries, base.illusion_id: bad_claim})
    with pytest.raises(ParameterValidationError, match="cannot read bibliography"):
        validate_citation_keys(sources, tmp_path / "missing.bib")


@pytest.mark.parametrize(
    ("payload", "message"),
    (([], "JSON object"), ({"schema_version": "duckrabbit/evidence/v1", "verified_on": "not-a-date"}, "ISO date"), ({"schema_version": "duckrabbit/evidence/v1", "verified_on": "2026-01-01", "verification_policy": "x", "sources": [], "entries": []}, "catalog mismatch")),
)
def test_evidence_matrix_metadata_failures(tmp_path: Path, payload: object, message: str) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ParameterValidationError, match=message):
        load_evidence_matrix(path)


def test_evidence_value_objects_reject_every_malformed_contract() -> None:
    with pytest.raises(ParameterValidationError, match="source key"):
        SourceRecord("", "key", "title", "review", "https://example.com", None, "claim")
    valid = SourceRecord("valid", "valid", "title", "review", "https://example.com", None, "claim")
    with pytest.raises(ParameterValidationError, match="identity"):
        EvidenceRecord("x", "bad", ImplementationStatus.IMPLEMENTED, ("valid",), (), (), "basis", ("limit",), "claim")  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="requires at least one"):
        EvidenceRecord("x", EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY, ImplementationStatus.IMPLEMENTED, (), (), (), "basis", ("limit",), "claim")
    with pytest.raises(ParameterValidationError, match="duplicate"):
        EvidenceRecord("x", EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY, ImplementationStatus.IMPLEMENTED, ("valid", "valid"), (), (), "basis", ("limit",), "claim")
    with pytest.raises(ParameterValidationError, match="claim text"):
        EvidenceRecord("x", EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY, ImplementationStatus.IMPLEMENTED, ("valid",), (), (), "", ("limit",), "claim")
    with pytest.raises(ParameterValidationError, match="invalid claim level"):
        EvidenceRecord("x", EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY, ImplementationStatus.IMPLEMENTED, ("valid",), (), (), "basis", ("limit",), "claim", supported_claim_level="bad")  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="source_supported"):
        EvidenceRecord("x", EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY, ImplementationStatus.IMPLEMENTED, ("valid",), (), (), "basis", ("limit",), "claim", supported_claim_level=ClaimLevel.PHYSICAL_METRIC)
    with pytest.raises(ParameterValidationError, match="missing_contract"):
        EvidenceRecord("x", EvidenceStatus.LITERATURE_BACKED_INPUT_DEPENDENT_ENTRY, ImplementationStatus.INPUT_REQUIRED, ("valid",), (), (), "basis", ("limit",), "claim")
    with pytest.raises(ParameterValidationError, match="missing_contract must"):
        EvidenceRecord("x", EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY, ImplementationStatus.IMPLEMENTED, ("valid",), (), (), "basis", ("limit",), "claim", missing_contract=3)  # type: ignore[arg-type]
    assert valid.key == "valid"
    assert evidence_for("visual.duck_rabbit").illusion_id == "visual.duck_rabbit"
