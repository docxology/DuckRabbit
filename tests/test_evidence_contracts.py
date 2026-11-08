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


@pytest.mark.parametrize("mutation", ["role", "unrelated", "missing_edge"])
def test_source_roles_and_taxonomy_edges_are_exact(mutation: str) -> None:
    sources, entries = load_evidence_matrix()
    base = entries["visual.duck_rabbit"]
    if mutation == "role":
        altered = replace(base, primary_sources=base.review_sources, review_sources=base.primary_sources)
    elif mutation == "unrelated":
        altered = replace(base, primary_sources=("mcgurk1976speech",))
    else:
        altered = replace(base, review_sources=())
    with pytest.raises(ParameterValidationError):
        validate_evidence_matrix(sources, {**entries, base.illusion_id: altered})


def test_unattached_historical_sources_remain_permitted() -> None:
    sources, entries = load_evidence_matrix()
    used = {key for record in entries.values() for key in record.primary_sources + record.review_sources + record.theory_sources}
    assert set(sources) - used
    validate_evidence_matrix(sources, entries)


def test_direct_evidence_constructors_detach_mutable_inputs() -> None:
    from duckrabbit.evidence import EvidenceLineage, EvidenceRole

    keys = ["source"]
    edge = EvidenceLineage(EvidenceRole.PRIMARY_DEMONSTRATION, "A bounded statement", keys)
    authors = ["George Berkeley"]
    source = SourceRecord("source", "source", "A title", "primary", "https://example.org", None, "A bounded claim", authors=authors)
    limitations = ["No observer evidence"]
    record = EvidenceRecord("example", EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY, ImplementationStatus.IMPLEMENTED, keys, [], [], "Engineering basis", limitations, "A bounded claim")
    keys.append("later")
    authors.clear()
    limitations.clear()
    assert edge.source_keys == ("source",)
    assert record.primary_sources == ("source",)
    assert record.evidence_limitations == ("No observer evidence",)
    assert source.authors == ("George Berkeley",)
    with pytest.raises(ParameterValidationError):
        replace(record, implementation_status="implemented")
    for field in ("primary_sources", "review_sources", "theory_sources", "evidence_limitations"):
        with pytest.raises(ParameterValidationError):
            replace(record, **{field: "not-a-sequence"})
    with pytest.raises(ParameterValidationError):
        replace(edge, source_keys="source")
    with pytest.raises(ParameterValidationError):
        replace(source, authors="George Berkeley")


@pytest.mark.parametrize("field,value", [("title", "What you see is not what you hear"), ("author", "Berkeley, Nobody"), ("year", "1710")])
def test_bibliography_identity_rejects_changed_fields(tmp_path: Path, field: str, value: str) -> None:
    from duckrabbit.evidence import validate_bibliography_links

    source = SourceRecord("berkeley", "berkeley", "An Essay Towards a New Theory of Vision", "primary", "https://example.org/vision", None, "Historical source", authors=("George Berkeley",), year=1709)
    fields = {"title": source.title, "author": "Berkeley, George", "year": "1709", "url": source.url}
    bibliography = tmp_path / "references.bib"
    bibliography.write_text("@book{berkeley,\n" + "".join(f"  {name} = {{{text}}},\n" for name, text in fields.items()) + "}\n", encoding="utf-8")
    validate_bibliography_links({source.key: source}, bibliography)
    fields[field] = value
    bibliography.write_text("@book{berkeley,\n" + "".join(f"  {name} = {{{text}}},\n" for name, text in fields.items()) + "}\n", encoding="utf-8")
    with pytest.raises(ParameterValidationError):
        validate_bibliography_links({source.key: source}, bibliography)


def test_bibliography_normalizes_tex_and_preserves_identity(tmp_path: Path) -> None:
    from duckrabbit.evidence import validate_bibliography_links

    sources, _ = load_evidence_matrix()
    source = sources["howe2005muller"]
    bibliography = tmp_path / "references.bib"
    bibliography.write_text('@article{howe2005muller,\n  title = {The {M}{\\"u}ller-{L}yer illusion explained by the statistics of image-source relationships},\n  doi = {' + source.doi + '},\n  url = {' + source.url + '}\n}\n', encoding="utf-8")
    validate_bibliography_links({source.key: source}, bibliography)
    bibliography.write_text(bibliography.read_text(encoding="utf-8").replace("illusion", r"\unknown{illusion}"), encoding="utf-8")
    with pytest.raises(ParameterValidationError):
        validate_bibliography_links({source.key: source}, bibliography)


def test_claim_lineage_is_immutable_and_checkout_locations_resolve(tmp_path: Path) -> None:
    from duckrabbit.claims import ClaimBasis, ClaimRecord, default_claim_registry, validate_claim_registry

    lineage = ["code"]
    claim = ClaimRecord("bounded", "A bounded claim", ClaimBasis.DERIVED_FROM_CODE, ClaimLevel.PHYSICAL_METRIC, lineage, "No observer evidence", "docs/manuscript/00_intro.md")
    lineage.clear()
    assert claim.source_or_artifact_lineage == ("code",)
    manuscript = tmp_path / "docs" / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "00_intro.md").write_text("# Introduction", encoding="utf-8")
    assert validate_claim_registry([claim], project_root=tmp_path) == (claim,)
    for location in ("manuscript/00_intro.md", "docs/manuscript/missing.md", "docs/manuscript/../outside.md", str(manuscript / "00_intro.md")):
        with pytest.raises(ValueError):
            validate_claim_registry([replace(claim, manuscript_location=location)], project_root=tmp_path)
    assert all(record.manuscript_location.startswith("docs/manuscript/") for record in default_claim_registry())


@pytest.mark.parametrize("body", [
    '<!-- <a href="#ref-source">cite</a><div id="ref-source"><a href="https://example.org/paper">source</a></div> -->',
    '<p>href="#ref-source" https://example.org/paper</p>',
    '<a href="#ref-source">cite</a><a href="https://example.org/paper">source</a>',
    '<a href="#ref-source">cite</a><div id="ref-source"></div><a href="https://example.org/paper">source</a>',
    '<a href="#ref-source">cite</a><div id="ref-source"></div><div id="ref-other"><a href="https://example.org/paper">source</a></div>',
    '<a href="#ref-source">cite</a><div id="ref-source"><a href="https://example.org/paper">source</a></div><div id="ref-source"></div>',
])
def test_html_links_reject_nonlinks_missing_or_wrong_destinations(tmp_path: Path, body: str) -> None:
    from duckrabbit.evidence import validate_rendered_bibliography_links, validate_rendered_citation_links

    source = SourceRecord("source", "source", "A title", "primary", "https://example.org/paper", None, "A claim")
    html = tmp_path / "index.html"
    html.write_text(body, encoding="utf-8")
    bibliography = tmp_path / "references.bib"
    bibliography.write_text("@article{source,\n  url={https://example.org/paper}\n}\n", encoding="utf-8")
    with pytest.raises(ParameterValidationError):
        validate_rendered_citation_links(html, {source.key: source})
    with pytest.raises(ParameterValidationError):
        validate_rendered_bibliography_links(html, bibliography)


def test_html_links_parse_real_anchors_and_entity_escaped_urls(tmp_path: Path) -> None:
    from duckrabbit.evidence import validate_rendered_citation_links

    source = SourceRecord("source", "source", "A title", "primary", "https://example.org/paper?a=1&b=2", None, "A claim")
    html = tmp_path / "index.html"
    html.write_text("<a href='#ref-source'>cite</a><section id='ref-source'><p><a href='https://example.org/paper?a=1&amp;b=2'>source</a></p></section>", encoding="utf-8")
    validate_rendered_citation_links(html, {source.key: source})
