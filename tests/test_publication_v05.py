"""Publication cover, caption, formalism, and atlas contract tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from duckrabbit.cover import DEFAULT_COVER_SOURCE, install_cover, validate_cover_manifest
from duckrabbit.formalism import FormalDefinition, formalism_registry, validate_formalism_registry
from duckrabbit.publication import generate_publication_outputs, publication_caption_specs, publication_table_payloads, validate_figure_registry
from duckrabbit.publication_specs import CaptionSpec, caption_variable_name
from duckrabbit.taxonomy import CognitiveProcess, ClaimLevel, ImplementationStatus, Mechanism, Modality, taxonomy_entries


EXPECTED_PUBLICATION_TABLES_V0_5_0 = frozenset({
    "caption_audit_table",
    "catalog_table",
    "claim_ledger_table",
    "encoding_profiles_table",
    "evidence_source_audit_table",
    "formalism_traceability_table",
    "metrics_table",
    "observer_estimands_table",
    "parameter_domains_table",
    "verification_failure_modes_table",
})


def test_caption_contract_is_complete_and_rejects_overclaims():
    assert Mechanism.AMBIGUITY.value in {entry.mechanisms[0].value for entry in taxonomy_entries()}
    assert CognitiveProcess.PERCEPTUAL_ORGANIZATION.value in {entry.cognitive_processes[0].value for entry in taxonomy_entries()}
    specs = publication_caption_specs()
    assert len(specs) == len({spec.label for spec in specs})
    assert all("source data" in spec.caption.lower() for spec in specs)
    assert all("claim level:" in spec.rendered_caption.lower() for spec in specs)
    assert all("controls:" in spec.rendered_caption.lower() for spec in specs)
    assert all("objective facts:" in spec.rendered_caption.lower() for spec in specs)
    assert all("boundary:" in spec.rendered_caption.lower() for spec in specs)
    assert all(spec.boundary_statement.strip() for spec in specs)
    assert all(spec.limitations and spec.accessibility_notes for spec in specs)
    assert any(spec.claim_level is ClaimLevel.OBSERVER_HYPOTHESIS for spec in specs)
    assert caption_variable_name("duck_rabbit", "caption") == "FIGURE_CAPTION_DUCK_RABBIT"
    with pytest.raises(ValueError, match="overclaim"):
        CaptionSpec("fig:bad", "bad", "bad", "This causes every observer to perceive a result; source data output/data/bad.json.", "source data", ClaimLevel.PHYSICAL_METRIC, "output/data/bad.json", ("x",), ("limit",), ("note",))
    with pytest.raises(ValueError, match="overclaim"):
        CaptionSpec("fig:bad", "bad", "bad", "The construction guarantees observers will see the target; source data output/data/bad.json.", "source data", ClaimLevel.PHYSICAL_METRIC, "output/data/bad.json", ("x",), ("limit",), ("note",))
    with pytest.raises(ValueError, match="limitations"):
        CaptionSpec("fig:bad", "bad", "bad", "A fact; source data output/data/bad.json.", "A fact", ClaimLevel.PHYSICAL_METRIC, "output/data/bad.json", ("x",), (), ("note",))


def test_visual_panel_caption_and_source_data_cover_live_visual_registry():
    visual_entries = tuple(
        entry
        for entry in taxonomy_entries()
        if Modality.VISUAL in entry.modalities
        and entry.implementation_status is ImplementationStatus.IMPLEMENTED
    )
    spec = next(spec for spec in publication_caption_specs() if spec.label == "fig:visual_panel")
    assert len(visual_entries) >= 1
    assert all(entry.name in spec.caption for entry in visual_entries)
    assert "exhaustive" in spec.boundary_statement
    assert any(term in spec.boundary_statement.lower() for term in ("observer", "viewer", "perceive"))

    output_dir = Path(__file__).parents[1] / "output"
    if (output_dir / "data" / "visual_panel.json").is_file():
        payload = json.loads((output_dir / "data" / "visual_panel.json").read_text(encoding="utf-8"))
        assert {record["illusion_id"] for record in payload["data"]["stimuli"]} == {entry.illusion_id for entry in visual_entries}


def test_catalog_is_referenced_by_standalone_appendix():
    appendix = Path(__file__).parents[1] / "docs" / "manuscript" / "09_appendix_catalog.md"
    results = Path(__file__).parents[1] / "docs" / "manuscript" / "03_results.md"
    appendix_text = appendix.read_text(encoding="utf-8")
    results_text = results.read_text(encoding="utf-8")
    assert "{#tbl:catalog}" in appendix_text
    assert "[@sec:appendix_catalog] and in [@tbl:catalog]" in results_text
    assert "{{CATALOG_TABLE_ROWS}}" not in results_text


def test_formalism_registry_is_traceable_and_typed():
    records = formalism_registry()
    assert {record.label for record in records} == {"eq:typed_request", "eq:canonical_generation", "eq:canonical_digest", "eq:encoding_verification", "eq:clock_definition", "eq:objective_statistics", "eq:temporal_spectral_metrics", "eq:observer_estimand", "eq:synthetic_observer"}
    assert all(record.tests and record.figures and record.claim_level for record in records)
    assert any(record.claim_level is ClaimLevel.OBSERVER_HYPOTHESIS for record in records)
    assert validate_formalism_registry() == records
    bad = FormalDefinition("eq:typed_request", "q = (i, θ, s, e)", ("q",), ("missing.py",), ("test_generators.py",), ("fig:architecture",), ClaimLevel.CANONICAL_STIMULUS)
    with pytest.raises(ValueError, match="implementation path"):
        validate_formalism_registry((bad,))


def test_publication_tables_expand_with_audit_lineage():
    payloads = publication_table_payloads()
    assert set(payloads) == EXPECTED_PUBLICATION_TABLES_V0_5_0
    assert all(payload["records"] for payload in payloads.values())
    assert all(payload["label"].startswith("tbl:") for payload in payloads.values())
    assert len(payloads["catalog_table"]["headers"]) == 5
    assert len(payloads["caption_audit_table"]["headers"]) == 4
    assert len(payloads["evidence_source_audit_table"]["headers"]) == 5
    evidence_rows = payloads["evidence_source_audit_table"]["records"]
    assert any(row["key"].startswith("entry:") and "limitation" in row["supported_claim"].lower() for row in evidence_rows)
    assert "DOI: recorded" in payloads["evidence_source_audit_table"]["body"]
    assert "brugger 1999 duckrabbit" in payloads["catalog_table"]["body"]
    assert any(row["doi"] == "10.1016/S1364-6613(97)01060-7" for row in evidence_rows)
    claim_rows = payloads["claim_ledger_table"]["records"]
    assert any(row["claim_id"] == "evidence:audiovisual.mcgurk" for row in claim_rows)
    assert any("engineering=" in row["lineage"] and "limitation=" in row["lineage"] for row in claim_rows if row["claim_id"].startswith("evidence:"))


def test_cover_manifest_variants_are_nonempty_and_hashed(tmp_path: Path):
    manifest = install_cover(tmp_path, DEFAULT_COVER_SOURCE)
    assert manifest["claim_level"] == "publication_illustration"
    assert manifest["previewed"] is True
    source = DEFAULT_COVER_SOURCE
    assert manifest["source_asset_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert manifest["source_asset_dimensions_px"] == {"width": 1122, "height": 1402}
    assert validate_cover_manifest(tmp_path / "reports" / "cover_visualization.json", output_dir=tmp_path)["claim_level"] == "publication_illustration"
    assert validate_cover_manifest(tmp_path / "reports" / "cover_visualization.json")["claim_level"] == "publication_illustration"
    for variant in manifest["variants"].values():
        path = tmp_path / variant["path"].replace("output/", "")
        assert path.stat().st_size > 0
        assert hashlib.sha256(path.read_bytes()).hexdigest() == variant["sha256"]
    report = json.loads((tmp_path / "reports" / "cover_visualization.json").read_text(encoding="utf-8"))
    assert report["source_kind"] == "editorial_charcoal_image_generation_v2"
    assert report["source_scope"] == "project_asset"

    bad = dict(manifest)
    bad["source_asset_sha256"] = "bad"
    with pytest.raises(ValueError, match="source_asset_sha256"):
        validate_cover_manifest(bad, output_dir=tmp_path)


def test_cover_manifest_rejects_provenance_and_variant_corruption(tmp_path: Path):
    manifest = install_cover(tmp_path, DEFAULT_COVER_SOURCE)

    def invalid(mutator, message: str) -> None:
        payload = json.loads(json.dumps(manifest))
        mutator(payload)
        with pytest.raises(ValueError, match=message):
            validate_cover_manifest(payload, output_dir=tmp_path)

    invalid(lambda payload: payload.update({"schema_version": "bad"}), "schema version")
    invalid(lambda payload: payload.update({"claim_level": "physical_metric"}), "claim level")
    invalid(lambda payload: payload.update({"caption": ""}), "provenance field caption")
    invalid(lambda payload: payload.update({"prompt_sha256": "bad"}), "prompt_sha256")
    invalid(lambda payload: payload.update({"dimensions_px": {"width": 1, "height": 1}}), "4:5")
    invalid(lambda payload: payload.update({"variants": {}}), "variants")
    invalid(lambda payload: payload["variants"].update({"png": {}}), "variant png is malformed")
    invalid(lambda payload: payload["variants"]["png"].update({"sha256": "bad"}), "variant png has an invalid hash")
    invalid(lambda payload: payload["variants"]["png"].update({"path": "output/figures/../cover.png"}), "variant png is missing or escapes")

    png = tmp_path / "figures" / "cover_visualization.png"
    png.write_bytes(png.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="variant png hash is stale"):
        validate_cover_manifest(manifest, output_dir=tmp_path)

    with pytest.raises(FileNotFoundError, match="source is unavailable"):
        install_cover(tmp_path / "missing", tmp_path / "no-cover.png")
    with pytest.raises(ValueError, match="cannot read cover manifest"):
        validate_cover_manifest(tmp_path / "no-cover.json", output_dir=tmp_path)
    invalid_dimensions = json.loads(json.dumps(manifest))
    invalid_dimensions["dimensions_px"] = {"width": 0, "height": 1}
    with pytest.raises(ValueError, match="positive integers"):
        validate_cover_manifest(invalid_dimensions, output_dir=tmp_path)
    invalid_source_dimensions = json.loads(json.dumps(manifest))
    invalid_source_dimensions["source_asset_dimensions_px"]["width"] += 1
    with pytest.raises(ValueError, match="source_asset_dimensions"):
        validate_cover_manifest(invalid_source_dimensions, output_dir=tmp_path)
    invalid_variant_path = json.loads(json.dumps(manifest))
    invalid_variant_path["variants"]["png"]["path"] = "cover.png"
    with pytest.raises(ValueError, match="output/figures"):
        validate_cover_manifest(invalid_variant_path, output_dir=tmp_path)


def test_figure_registry_is_an_independent_hash_and_caption_oracle(tmp_path: Path):
    generate_publication_outputs(tmp_path)
    registry_path = tmp_path / "figures" / "figure_registry.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    assert validate_figure_registry(registry_path, output_dir=tmp_path)["figure_count"] == len(publication_caption_specs())

    payload["figures"][0]["source_data_sha256"] = "0" * 64
    bad_hash = tmp_path / "bad-hash.json"
    bad_hash.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="source-data hash is stale"):
        validate_figure_registry(bad_hash, output_dir=tmp_path)

    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload["figures"][0]["caption"] = "This guarantees a perceptual result; source data output/data/architecture.json."
    bad_caption = tmp_path / "bad-caption.json"
    bad_caption.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="caption contract"):
        validate_figure_registry(bad_caption, output_dir=tmp_path)

    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    source_path = tmp_path / "data" / "architecture.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["figure_label"] = "fig:wrong"
    source_path.write_text(json.dumps(source), encoding="utf-8")
    payload["figures"][0]["source_data_sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    bad_source = tmp_path / "bad-source.json"
    bad_source.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="source-data identity"):
        validate_figure_registry(bad_source, output_dir=tmp_path)


def test_figure_registry_rejects_structural_and_lineage_corruption(tmp_path: Path, publication_bundle: Path):
    registry_path = publication_bundle / "figures" / "figure_registry.json"
    original = json.loads(registry_path.read_text(encoding="utf-8"))
    assert validate_figure_registry(registry_path, output_dir=publication_bundle)["figure_count"] == len(publication_caption_specs())

    def invalid(mutator, message: str, name: str) -> None:
        payload = json.loads(json.dumps(original))
        mutator(payload)
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            validate_figure_registry(path, output_dir=publication_bundle)

    invalid(lambda payload: payload.update({"schema_version": "bad"}), "schema version", "bad-schema")
    invalid(lambda payload: payload.update({"figures": {}}), "figures must be a list", "bad-figures")
    invalid(lambda payload: payload.update({"figure_count": 14}), "count must", "bad-count")
    invalid(lambda payload: payload["figures"][0].pop("caption"), "missing", "missing-caption")
    invalid(lambda payload: payload["figures"][1].update({"label": payload["figures"][0]["label"]}), "duplicate or unknown", "duplicate-label")
    invalid(lambda payload: payload["figures"][0].update({"path": "output/figures/other.png"}), "paths do not match", "bad-path")
    invalid(lambda payload: payload["figures"][0].update({"claim_level": "observer_effect"}), "claim level", "bad-claim")
    invalid(lambda payload: payload["figures"][0].update({"evidence_references": ["unknown"]}), "evidence references", "bad-reference")
    invalid(lambda payload: payload["figures"][0].update({"limitations": []}), "limitations", "bad-limitations")
    invalid(lambda payload: payload["figures"][0].update({"accessibility": {}}), "accessibility", "bad-accessibility")
    invalid(lambda payload: payload["figures"][0].update({"sha256": "bad"}), "hashes", "bad-figure-hash")
    invalid(lambda payload: payload["figures"][0].update({"seed": True}), "seed", "bad-seed")
    invalid(lambda payload: payload["figures"][0].update({"parameters": []}), "parameters", "bad-parameters")
    invalid(lambda payload: payload["figures"].__setitem__(0, "bad"), "records must be objects", "bad-record")

    with pytest.raises(ValueError, match="must be an object"):
        validate_figure_registry([], output_dir=tmp_path)

    bad_registry_json = tmp_path / "not-json.json"
    bad_registry_json.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError, match="cannot read figure registry"):
        validate_figure_registry(bad_registry_json, output_dir=tmp_path)

    # The tamper probes below mutate real files, so they need a disposable bundle.
    generate_publication_outputs(tmp_path)
    mutable_registry = tmp_path / "figures" / "figure_registry.json"
    source_path = tmp_path / "data" / "architecture.json"
    source_path.write_bytes(source_path.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="source-data hash is stale"):
        validate_figure_registry(mutable_registry, output_dir=tmp_path)

    figure_path = tmp_path / "figures" / "architecture.png"
    original_figure_bytes = figure_path.read_bytes()
    figure_path.write_bytes(original_figure_bytes + b"tampered")
    with pytest.raises(ValueError, match="figure hash is stale"):
        validate_figure_registry(mutable_registry, output_dir=tmp_path)

    figure_path.write_bytes(original_figure_bytes)
    source_path.unlink()
    with pytest.raises(ValueError, match="missing output"):
        validate_figure_registry(mutable_registry, output_dir=tmp_path)
