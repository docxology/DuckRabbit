"""Independent negative controls for publication, evidence, and claim integrity."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from duckrabbit.audit import run_audit
from duckrabbit.claims import ClaimBasis, ClaimRecord, default_claim_registry
from duckrabbit.evidence import SourceRecord, SourceVerificationStatus
from duckrabbit.publication import (
    generate_publication_outputs,
    publication_table_payloads,
    validate_figure_registry,
    validate_publication_report,
    validate_publication_tables,
    validate_publication_visual_qa,
)
from duckrabbit.scholarship import compare_doi_metadata
from duckrabbit.taxonomy import ClaimLevel


ROOT = Path(__file__).resolve().parents[1]


def test_clean_publication_preserves_guides_and_separate_pipeline_outputs(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    protected = {"AGENTS.md": "# Local guidance\n", "README.md": "# Data\n", "manuscript_variables.json": '{"source": "hydrator"}\n'}
    for filename, content in protected.items():
        (data / filename).write_text(content, encoding="utf-8")
    stale = data / "removed_figure.json"
    stale.write_text("{}", encoding="utf-8")
    generate_publication_outputs(tmp_path, clean=True)
    assert not stale.exists()
    for filename, content in protected.items():
        assert (data / filename).read_text(encoding="utf-8") == content


@pytest.fixture
def mutable_bundle(tmp_path: Path, publication_bundle: Path) -> Path:
    destination = tmp_path / "output"
    shutil.copytree(publication_bundle, destination)
    return destination


def _read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_generated_publication_has_independent_integrity_surfaces(publication_bundle: Path) -> None:
    validate_publication_tables(publication_bundle)
    validate_publication_visual_qa(publication_bundle)
    validate_publication_report(publication_bundle)
    assert run_audit(project_root=ROOT, output_root=publication_bundle, release=True).status == "passed"


@pytest.mark.parametrize("corruption", ["invalid_json", "changed_json", "fabricated_markdown", "missing_json"])
def test_release_rejects_each_table_corruption(mutable_bundle: Path, corruption: str) -> None:
    path = mutable_bundle / "data" / "catalog_table.json"
    if corruption == "invalid_json":
        path.write_text("NOT JSON", encoding="utf-8")
    elif corruption == "changed_json":
        payload = _read(path)
        payload["records"][0]["id"] = "fabricated.catalog.entry"
        _write(path, payload)
    elif corruption == "fabricated_markdown":
        path.with_suffix(".md").write_text("# Fabricated catalog\n", encoding="utf-8")
    else:
        path.unlink()
    report = run_audit(project_root=ROOT, output_root=mutable_bundle, release=True)
    assert report.status == "failed"
    assert "publication_bundle.failed" in {issue.code for issue in report.errors}
    assert not {"visual_qa.failed", "publication_report.failed"} & {issue.code for issue in report.errors}


@pytest.mark.parametrize("report_name", ["visual_qa", "publication_report"])
@pytest.mark.parametrize("corruption", ["missing", "invalid_json", "changed"])
def test_release_requires_each_independent_report(mutable_bundle: Path, report_name: str, corruption: str) -> None:
    path = mutable_bundle / "reports" / f"{report_name}.json"
    if corruption == "missing":
        path.unlink()
    elif corruption == "invalid_json":
        path.write_text("NOT JSON", encoding="utf-8")
    else:
        payload = _read(path)
        if report_name == "visual_qa":
            payload["figures"][0]["thumbnail_sha256"] = "0" * 64
        else:
            payload["sha256"] = "0" * 64
        _write(path, payload)
    report = run_audit(project_root=ROOT, output_root=mutable_bundle, release=True)
    assert report.status == "failed"
    assert {issue.code for issue in report.errors} == {f"{report_name}.failed"}


@pytest.mark.parametrize("field,value", [
    ("figure_count", 14), ("table_count", 9), ("cover", {}),
    ("table_files", ["output/data/fabricated.md"]),
    ("registry", "output/data/not_the_registry.json"),
])
def test_publication_report_fields_are_not_trusted(mutable_bundle: Path, field: str, value: object) -> None:
    path = mutable_bundle / "reports" / "publication_report.json"
    payload = _read(path)
    payload[field] = value
    _write(path, payload)
    with pytest.raises(ValueError, match="publication report"):
        validate_publication_report(mutable_bundle)


@pytest.mark.parametrize("field,value", [
    ("schema_version", "invented"), ("figure_count", 14), ("scales", ["thumbnail"]),
    ("figures", []),
])
def test_independent_visual_qa_contract_is_code_owned(mutable_bundle: Path, field: str, value: object) -> None:
    path = mutable_bundle / "reports" / "visual_qa.json"
    payload = _read(path)
    payload[field] = value
    _write(path, payload)
    with pytest.raises(ValueError, match="independent visual QA"):
        validate_publication_visual_qa(mutable_bundle)


def test_registry_thumbnail_digest_is_independently_inspected(publication_bundle: Path) -> None:
    payload = _read(publication_bundle / "figures" / "figure_registry.json")
    payload["figures"][0]["visual_qa"]["thumbnail_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="visual QA disagrees"):
        validate_figure_registry(payload, output_dir=publication_bundle)


@pytest.mark.parametrize("field", ["evidence_references", "limitations", "generator", "generated_by"])
def test_registry_rejects_plausible_but_invented_provenance(publication_bundle: Path, field: str) -> None:
    payload = _read(publication_bundle / "figures" / "figure_registry.json")
    first = payload["figures"][0]
    if field == "evidence_references":
        first[field] = ["observer:preregistered_estimands"]
    elif field == "limitations":
        first[field] = ["Arbitrary limitations unrelated to this figure."]
    else:
        first[field] = "invented.valid.looking.producer"
    with pytest.raises(ValueError, match="lineage|limitations|producer"):
        validate_figure_registry(payload, output_dir=publication_bundle)


@pytest.mark.parametrize("field", ["generator", "parameters", "seed", "parameter_seed"])
def test_refreshed_sidecar_hash_cannot_hide_forged_provenance(mutable_bundle: Path, field: str) -> None:
    registry_path = mutable_bundle / "figures" / "figure_registry.json"
    registry = _read(registry_path)
    record = registry["figures"][0]
    path = mutable_bundle / "data" / "architecture.json"
    sidecar = _read(path)
    if field == "generator":
        sidecar[field] = "duckrabbit.publication._observer"
    elif field == "parameters":
        sidecar[field]["figure_stem"] = "observer_protocol"
    elif field == "seed":
        sidecar[field] = False
    else:
        sidecar["parameters"]["seed"] = False
    _write(path, sidecar)
    record["source_data_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    _write(registry_path, registry)
    with pytest.raises(ValueError, match="source-data producer|source-data provenance"):
        validate_figure_registry(registry_path, output_dir=mutable_bundle)


@pytest.mark.parametrize("corruption", ["evidence", "bibliography", "legacy_bibliography"])
def test_checkout_audit_uses_selected_evidence_and_bibliography(tmp_path: Path, corruption: str) -> None:
    checkout = tmp_path / "checkout"
    for directory in ("src", "docs", "tests", "data", "experiments"):
        shutil.copytree(ROOT / directory, checkout / directory)
    for filename in ("pyproject.toml", "CITATION.cff", "codemeta.json", ".zenodo.json"):
        shutil.copyfile(ROOT / filename, checkout / filename)
    manuscript = checkout / "docs" / "manuscript"
    if corruption == "legacy_bibliography":
        manuscript.rename(checkout / "manuscript")
        manuscript = checkout / "manuscript"
    baseline = run_audit(project_root=checkout, output_root=tmp_path / "absent")
    assert "evidence.failed" not in {issue.code for issue in baseline.errors}
    if corruption == "evidence":
        (checkout / "data" / "evidence_matrix.json").write_text("NOT JSON", encoding="utf-8")
    else:
        (manuscript / "references.bib").write_text("NOT A BIBLIOGRAPHY", encoding="utf-8")
    report = run_audit(project_root=checkout, output_root=tmp_path / "absent")
    assert report.status == "failed"
    assert "evidence.failed" in {issue.code for issue in report.errors}


def _source() -> SourceRecord:
    return SourceRecord("source", "source1997", "Visual capture of gravity", "primary", "https://example.org/paper", "10.1234/paper", "A source-supported claim", year=1997)


@pytest.mark.parametrize("print_date,online_date", [
    ({"date-parts": [[1997]]}, None),
    ({"date-parts": [[1998, 1, 1]]}, {"date-parts": [[1997, 12, 31]]}),
    (None, {"date-parts": [[1997, 5]]}),
])
def test_doi_year_accepts_real_print_or_online_dates(print_date: object, online_date: object) -> None:
    source = _source()
    metadata = {"DOI": source.doi, "title": [source.title], "published-print": print_date, "published-online": online_date}
    assert compare_doi_metadata(source, metadata) is SourceVerificationStatus.DOI_METADATA_MATCH


@pytest.mark.parametrize("published", [
    "1997-05-01", {"unrelated": 1997}, {"date-parts": [[1998]], "note": "1997"},
    {"date-parts": "1997"}, {"date-parts": [1997]}, {"date-parts": [["1997"]]},
    {"date-parts": [[1997, 13, 1]]}, {"date-parts": [[1997, 2, 31]]},
    {"date-parts": [[1997, True]]}, {"date-parts": [[1997.0]]},
])
def test_doi_year_cannot_match_unrelated_or_malformed_properties(published: object) -> None:
    source = _source()
    metadata = {"DOI": source.doi, "title": [source.title], "published-print": published}
    assert compare_doi_metadata(source, metadata) is SourceVerificationStatus.METADATA_MISMATCH


@pytest.mark.parametrize("text", [
    "Observers perceive a rabbit.", "Observers see a rabbit.", "Participants perceived a rabbit.",
    "The stimulus is perceived as a rabbit.", "The signal will sound continuous.",
])
def test_code_claim_rejects_caption_overclaim_language(text: str) -> None:
    record = default_claim_registry()[0]
    with pytest.raises(ValueError, match="overclaim"):
        replace(record, text=text)


@pytest.mark.parametrize("basis,level", [
    (ClaimBasis.DERIVED_FROM_CODE, ClaimLevel.VALIDATED_OBSERVER_EFFECT),
    (ClaimBasis.DERIVED_FROM_CANONICAL_ARTIFACT, ClaimLevel.OBSERVER_HYPOTHESIS),
    (ClaimBasis.DERIVED_FROM_DECODED_MEDIA, ClaimLevel.SOURCE_SUPPORTED),
    (ClaimBasis.SYNTHETIC_MODEL_OUTPUT, ClaimLevel.VALIDATED_OBSERVER_EFFECT),
    (ClaimBasis.FUTURE_OBSERVER_HYPOTHESIS, ClaimLevel.VALIDATED_OBSERVER_EFFECT),
    (ClaimBasis.PUBLICATION_ILLUSTRATION, ClaimLevel.CANONICAL_STIMULUS),
])
def test_claim_basis_cannot_be_relabelled_as_stronger_evidence(basis: ClaimBasis, level: ClaimLevel) -> None:
    with pytest.raises(ValueError, match="incompatible"):
        ClaimRecord("bad", "A bounded claim", basis, level, ("artifact",), "Not observer evidence", "manuscript/x.md")


def test_claim_registry_preserves_bounded_scope_and_future_hypotheses() -> None:
    assert default_claim_registry()
    ClaimRecord("future", "Observers perceive a rabbit.", ClaimBasis.FUTURE_OBSERVER_HYPOTHESIS, ClaimLevel.OBSERVER_HYPOTHESIS, ("protocol",), "Unvalidated future hypothesis", "manuscript/x.md")
    assert len(publication_table_payloads()) == 10
