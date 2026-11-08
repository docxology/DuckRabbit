"""Independent negative controls for publication, evidence, and claim integrity."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil

import pytest
from PIL import Image

from duckrabbit.audit import run_audit
from duckrabbit.claims import ClaimBasis, ClaimRecord, default_claim_registry
from duckrabbit.cover import install_cover, validate_cover_manifest
from duckrabbit.evidence import SourceRecord, SourceVerificationStatus, load_evidence_matrix
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
def test_file_only_validation_uses_selected_evidence_and_bibliography(tmp_path: Path, corruption: str) -> None:
    checkout = tmp_path / "checkout"
    for directory in ("src", "docs", "tests", "data", "experiments"):
        shutil.copytree(ROOT / directory, checkout / directory)
    for filename in ("pyproject.toml", "CITATION.cff", "codemeta.json", ".zenodo.json"):
        shutil.copyfile(ROOT / filename, checkout / filename)
    manuscript = checkout / "docs" / "manuscript"
    if corruption == "legacy_bibliography":
        manuscript.rename(checkout / "manuscript")
        manuscript = checkout / "manuscript"
    sources, records = load_evidence_matrix(checkout / "data" / "evidence_matrix.json", bibliography_path=manuscript / "references.bib", manuscript_dir=manuscript)
    assert "visual.duck_rabbit" in records and "gregory1997visual" in sources
    if corruption == "evidence":
        (checkout / "data" / "evidence_matrix.json").write_text("NOT JSON", encoding="utf-8")
    else:
        (manuscript / "references.bib").write_text("NOT A BIBLIOGRAPHY", encoding="utf-8")
    with pytest.raises(ValueError):
        load_evidence_matrix(checkout / "data" / "evidence_matrix.json", bibliography_path=manuscript / "references.bib", manuscript_dir=manuscript)


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


@pytest.fixture
def supplied_cover_bundle(tmp_path: Path) -> tuple[Path, Path, dict[str, object]]:
    source = tmp_path / "supplied.png"
    image = Image.linear_gradient("L").resize((400, 500)).convert("RGBA")
    image.putalpha(127)
    image.save(source)
    output = tmp_path / "delivery"
    return source, output, install_cover(output, source)


def test_supplied_cover_does_not_inherit_historical_generation_claims(supplied_cover_bundle) -> None:
    source, output, manifest = supplied_cover_bundle
    original = source.read_bytes()
    assert manifest["schema_version"] == "duckrabbit/cover/v2"
    assert manifest["source_kind"] == "supplied_editorial_image"
    assert manifest["source_scope"] == "external_input"
    assert manifest["source_asset_path"] == source.resolve().as_posix()
    assert manifest["source_asset_sha256"] == hashlib.sha256(original).hexdigest()
    assert manifest["source_asset_format"] == "PNG"
    assert manifest["generation_provenance"]["status"] == "not_recorded"
    assert manifest["generation_provenance"]["reported_claims"] is None
    assert not {"model", "prompt_sha256", "selected_candidate", "previewed"} & manifest.keys()
    with Image.open(source) as decoded, Image.open(output / "figures/cover_visualization.png") as png:
        rgb = decoded.convert("RGB")
        assert png.tobytes() == rgb.tobytes()
        rgb.thumbnail((320, 400), Image.Resampling.LANCZOS)
        with Image.open(output / "figures/cover_visualization-thumb.png") as thumbnail:
            assert thumbnail.size == (320, 400)
            assert thumbnail.tobytes() == rgb.tobytes()
    assert source.read_bytes() == original


@pytest.mark.parametrize("field,value", [
    ("source_asset_sha256", "0" * 64),
    ("source_kind", "supplied_editorial_image"),
    ("generation_provenance", {"status": "confirmed", "reported_claims": None}),
    ("previewed", False),
])
def test_historical_cover_rejects_forged_source_and_confirmation_claims(publication_bundle: Path, field: str, value: object) -> None:
    manifest = _read(publication_bundle / "reports/cover_visualization.json")
    manifest[field] = value
    with pytest.raises(ValueError, match="source_asset_sha256|source_kind|generation"):
        validate_cover_manifest(manifest, output_dir=publication_bundle)


@pytest.mark.parametrize("field,value", [
    ("prompt_sha256", "1" * 64), ("model", "authenticated-model"),
    ("selected_candidate", 999), ("selected_candidate", 4.0),
    ("previewed", False), ("previewed", 1),
])
def test_reported_cover_history_is_code_owned_but_not_authenticated(publication_bundle: Path, field: str, value: object) -> None:
    manifest = _read(publication_bundle / "reports/cover_visualization.json")
    assert manifest["generation_provenance"]["status"] == "reported_unverified"
    manifest["generation_provenance"]["reported_claims"][field] = value
    with pytest.raises(ValueError, match="generation_provenance"):
        validate_cover_manifest(manifest, output_dir=publication_bundle)


def test_supplied_cover_cannot_claim_historical_generation_provenance(supplied_cover_bundle, publication_bundle: Path) -> None:
    _, output, manifest = supplied_cover_bundle
    historical = _read(publication_bundle / "reports/cover_visualization.json")
    manifest["generation_provenance"] = historical["generation_provenance"]
    with pytest.raises(ValueError, match="generation_provenance"):
        validate_cover_manifest(manifest, output_dir=output)


@pytest.mark.parametrize("corruption", ["digest", "dimensions", "format", "source_bytes"])
def test_cover_source_facts_are_independently_checked(supplied_cover_bundle, corruption: str) -> None:
    source, output, manifest = supplied_cover_bundle
    if corruption == "digest":
        manifest["source_asset_sha256"] = "0" * 64
    elif corruption == "dimensions":
        manifest["dimensions_px"] = {"width": 404, "height": 505}
        manifest["source_asset_dimensions_px"] = {"width": 404, "height": 505}
    elif corruption == "format":
        manifest["source_asset_format"] = "JPEG"
    else:
        Image.new("RGB", (400, 500), "red").save(source)
    with pytest.raises(ValueError, match="source_asset"):
        validate_cover_manifest(manifest, output_dir=output)


@pytest.mark.parametrize("variant,corruption", [
    ("png", "format"), ("webp", "format"), ("thumbnail", "format"),
    ("png", "dimensions"), ("webp", "dimensions"), ("thumbnail", "dimensions"),
    ("png", "pixels"), ("webp", "pixels"), ("thumbnail", "pixels"),
])
def test_refreshed_cover_hash_cannot_hide_wrong_media_or_pixels(supplied_cover_bundle, variant: str, corruption: str) -> None:
    _, output, manifest = supplied_cover_bundle
    record = manifest["variants"][variant]
    path = output / record["path"].removeprefix("output/")
    size = tuple(record["dimensions_px"][key] for key in ("width", "height"))
    if corruption == "dimensions":
        size = (size[0] + 1, size[1])
    image = Image.new("RGB", size, "red")
    image.save(path, format="JPEG" if corruption == "format" else record["format"])
    record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match=f"variant {variant} (actual|pixels)"):
        validate_cover_manifest(manifest, output_dir=output)


@pytest.mark.parametrize("field,value", [
    ("path", "output/figures/cover_visualization.png"),
    ("format", "PNG"), ("role", "primary_image"),
    ("dimensions_px", {"width": 320, "height": 400}),
])
def test_cover_variant_roles_and_distinct_filenames_are_not_interchangeable(supplied_cover_bundle, field: str, value: object) -> None:
    _, output, manifest = supplied_cover_bundle
    manifest["variants"]["webp"][field] = value
    with pytest.raises(ValueError, match="variant webp"):
        validate_cover_manifest(manifest, output_dir=output)


def test_cover_missing_source_does_not_turn_history_into_verified_fact(supplied_cover_bundle) -> None:
    source, output, manifest = supplied_cover_bundle
    source.unlink()
    checked = validate_cover_manifest(manifest, output_dir=output)
    assert checked["generation_provenance"]["status"] == "not_recorded"
    assert "when the source is available" in checked["provenance_boundary"]
    record = manifest["variants"]["thumbnail"]
    path = output / record["path"].removeprefix("output/")
    Image.new("RGB", (320, 400), "red").save(path)
    record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="thumbnail pixels"):
        validate_cover_manifest(manifest, output_dir=output)


def test_cover_rejects_v1_without_compatibility_shim(supplied_cover_bundle) -> None:
    _, output, manifest = supplied_cover_bundle
    manifest["schema_version"] = "duckrabbit/cover/v1"
    with pytest.raises(ValueError, match="schema version"):
        validate_cover_manifest(manifest, output_dir=output)


@pytest.mark.parametrize("size", [(80, 100), (403, 500), (400, 503)])
def test_cover_thumbnail_rounding_and_no_upscaling(tmp_path: Path, size: tuple[int, int]) -> None:
    source = tmp_path / "source.png"
    image = Image.linear_gradient("L").resize(size).convert("RGB")
    image.save(source)
    manifest = install_cover(tmp_path / "out", source)
    image.thumbnail((320, 400), Image.Resampling.LANCZOS)
    assert manifest["variants"]["thumbnail"]["dimensions_px"] == {"width": image.width, "height": image.height}
    validate_cover_manifest(manifest, output_dir=tmp_path / "out")


def test_cover_installation_rejects_output_symlink_escape(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    Image.new("RGB", (80, 100), "blue").save(source)
    outside = tmp_path / "outside"
    outside.mkdir()
    output = tmp_path / "out"
    output.mkdir()
    (output / "figures").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes output"):
        install_cover(output, source)
    assert not tuple(outside.iterdir())


def test_cover_validation_rejects_real_variant_symlink_escape(supplied_cover_bundle) -> None:
    _, output, manifest = supplied_cover_bundle
    variant = output / "figures/cover_visualization.png"
    outside = output.parent / "outside.png"
    variant.rename(outside)
    variant.symlink_to(outside)
    with pytest.raises(ValueError, match="escapes output"):
        validate_cover_manifest(manifest, output_dir=output)


def test_cover_delivery_never_overwrites_supplied_source(tmp_path: Path) -> None:
    source = tmp_path / "figures/cover_visualization.png"
    source.parent.mkdir()
    Image.new("RGB", (80, 100), "blue").save(source)
    original = source.read_bytes()
    with pytest.raises(ValueError, match="overwrite its source"):
        install_cover(tmp_path, source)
    assert source.read_bytes() == original


@pytest.mark.parametrize("field", ["caption", "alt_text", "provenance_boundary"])
def test_cover_descriptions_cannot_claim_authenticated_generation(supplied_cover_bundle, field: str) -> None:
    _, output, manifest = supplied_cover_bundle
    manifest[field] = "The model, prompt, candidate, and preview quality are independently confirmed."
    with pytest.raises(ValueError, match="provenance|boundary"):
        validate_cover_manifest(manifest, output_dir=output)
