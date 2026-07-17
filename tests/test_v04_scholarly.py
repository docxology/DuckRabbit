"""No-mock tests for evidence, metrics, observer analysis, and outputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import duckrabbit
from duckrabbit.errors import ParameterValidationError
from duckrabbit.evidence import (
    EvidenceRecord,
    SourceRecord,
    load_evidence_matrix,
    validate_bibliography_integrity,
    validate_bibliography_links,
    validate_citation_keys,
    validate_evidence_matrix,
    validate_rendered_bibliography_links,
    validate_rendered_citation_links,
)
from duckrabbit.metrics import MetricRecord, MetricSuite, measure_artifact
from duckrabbit.observer_analysis import (
    AggregateRecord,
    AnalysisModel,
    AnalysisModelSpec,
    ConditionSpec,
    Estimand,
    ParticipantId,
    ResponseKind,
    StudyDesign,
    StimulusReference,
    TrialDisposition,
    TrialRecord,
    build_trial_sequence,
    default_study_design,
    default_model_specs,
    simulate_binary_responses,
    simulate_power,
    summarize_binary_responses,
)
from duckrabbit.publication import generate_publication_outputs, publication_caption_specs, publication_table_payloads
from duckrabbit.taxonomy import ClaimLevel, PerceptualSignature, get_taxonomy, taxonomy_entries


def test_evidence_matrix_covers_live_catalog_and_sources_are_verified():
    sources, entries = load_evidence_matrix()
    validate_evidence_matrix(sources, entries)
    assert len(entries) == len(taxonomy_entries())
    assert len(sources) == len({record.citation_key for record in sources.values()})
    assert get_taxonomy("audiovisual.temporal_ventriloquism").signatures == (PerceptualSignature.TEMPORAL_BINDING,)
    assert all(record.url.startswith(("http://", "https://")) for record in sources.values())
    assert all(record.evidence_limitations for record in entries.values())
    assert entries["audiovisual.mcgurk"].missing_contract
    assert entries["visual.zollner"].missing_contract is None
    assert entries["audio.auditory_continuity"].missing_contract is None
    validate_citation_keys(sources)
    validate_bibliography_links(sources)
    bibliography = validate_bibliography_integrity()
    assert bibliography["entry_count"] == bibliography["cited_count"] == bibliography["linked_count"]
    with pytest.raises(ParameterValidationError, match="invalid URL"):
        SourceRecord("bad", "bad", "Bad", "review", "not-a-url", None, "claim")
    with pytest.raises(ParameterValidationError, match="requires limitations"):
        EvidenceRecord("visual.duck_rabbit", next(iter(entries.values())).evidence_status, next(iter(entries.values())).implementation_status, ("gregory1997visual",), (), (), "basis", (), "claim")
    with pytest.raises(ParameterValidationError, match="catalog mismatch"):
        validate_evidence_matrix(sources, {key: value for key, value in entries.items() if key != "visual.duck_rabbit"})


def test_evidence_matrix_metadata_and_source_tiers_are_strict(tmp_path: Path):
    payload = json.loads(Path("data/evidence_matrix.json").read_text(encoding="utf-8"))
    payload["schema_version"] = "wrong"
    path = tmp_path / "bad-evidence.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ParameterValidationError, match="schema version"):
        load_evidence_matrix(path)
    with pytest.raises(ParameterValidationError, match="source type"):
        SourceRecord("bad", "bad", "Bad", "blog", "https://example.com", None, "claim")
    with pytest.raises(ParameterValidationError, match="invalid DOI"):
        SourceRecord("bad", "bad", "Bad", "review", "https://example.com", "10.bad", "claim")
    with pytest.raises(ParameterValidationError, match="citation identifier"):
        SourceRecord("bad key", "bad", "Bad", "review", "https://example.com", None, "claim")
    with pytest.raises(ParameterValidationError, match="missing bibliography keys"):
        validate_citation_keys({"bad": SourceRecord("bad", "not_in_bib", "Bad", "review", "https://example.com", None, "claim")})


def test_rendered_citations_require_reference_and_resolver_links(tmp_path: Path):
    sources, _ = load_evidence_matrix()
    source = sources["gregory1997visual"]
    html = tmp_path / "index.html"
    html.write_text(
        f'<a href="#ref-{source.citation_key}">Gregory</a>'
        f'<a href="https://doi.org/{source.doi}">{source.doi}</a>',
        encoding="utf-8",
    )
    validate_rendered_citation_links(html, {source.key: source})
    html.write_text("<p>citation without reference</p>", encoding="utf-8")
    with pytest.raises(ParameterValidationError, match="citation anchors"):
        validate_rendered_citation_links(html, {source.key: source})


def test_bibliography_integrity_and_rendered_links_are_complete(tmp_path: Path):
    bibliography = tmp_path / "references.bib"
    bibliography.write_text(
        "@article{doi_entry,\n"
        "  title = {A DOI source},\n"
        "  doi = {10.1234/example},\n"
        "}\n\n"
        "@misc{url_entry,\n"
        "  title = {A URL source},\n"
        "  url = {https://example.org/source},\n"
        "}\n",
        encoding="utf-8",
    )
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    (manuscript / "00_intro.md").write_text("[@doi_entry; @url_entry]", encoding="utf-8")
    result = validate_bibliography_integrity(bibliography, manuscript)
    assert result == {"entry_count": 2, "cited_count": 2, "linked_count": 2}

    html = tmp_path / "index.html"
    html.write_text(
        '<a href="#ref-doi_entry">DOI</a><a href="https://doi.org/10.1234/example">resolver</a>'
        '<a href="#ref-url_entry">URL</a><a href="https://example.org/source">resolver</a>',
        encoding="utf-8",
    )
    validate_rendered_bibliography_links(html, bibliography)
    html.write_text('<a href="#ref-doi_entry">DOI</a>', encoding="utf-8")
    with pytest.raises(ParameterValidationError, match="bibliography anchors"):
        validate_rendered_bibliography_links(html, bibliography)
    html.write_text('<a href="#ref-doi_entry">DOI</a><a href="#ref-url_entry">URL</a>', encoding="utf-8")
    with pytest.raises(ParameterValidationError, match="resolver links"):
        validate_rendered_bibliography_links(html, bibliography)

    bad_manuscript = tmp_path / "bad-manuscript"
    bad_manuscript.mkdir()
    (bad_manuscript / "00_intro.md").write_text("[@missing]", encoding="utf-8")
    with pytest.raises(ParameterValidationError, match="missing bibliography entries"):
        validate_bibliography_integrity(bibliography, bad_manuscript)

    uncited_manuscript = tmp_path / "uncited-manuscript"
    uncited_manuscript.mkdir()
    (uncited_manuscript / "00_intro.md").write_text("[@doi_entry]", encoding="utf-8")
    with pytest.raises(ParameterValidationError, match="not cited"):
        validate_bibliography_integrity(bibliography, uncited_manuscript)

    unlinked_bibliography = tmp_path / "unlinked.bib"
    unlinked_bibliography.write_text("@misc{unlinked,\n  title = {No resolver},\n}\n", encoding="utf-8")
    unlinked_manuscript = tmp_path / "unlinked-manuscript"
    unlinked_manuscript.mkdir()
    (unlinked_manuscript / "00_intro.md").write_text("[@unlinked]", encoding="utf-8")
    with pytest.raises(ParameterValidationError, match="missing DOI and URL"):
        validate_bibliography_integrity(unlinked_bibliography, unlinked_manuscript)


def test_claim_levels_are_strict_and_metrics_have_units():
    assert ClaimLevel.PHYSICAL_METRIC.value == "physical_metric"
    with pytest.raises(ValueError, match="metric name"):
        MetricRecord("", 1.0, "unit")
    with pytest.raises(ValueError, match="non-finite"):
        MetricRecord("bad", float("nan"), "unit")
    with pytest.raises(ValueError, match="physical_metric"):
        MetricRecord("observer_claim", 1.0, "unit", claim_level=duckrabbit.ClaimLevel.OBSERVER_HYPOTHESIS)
    suite = measure_artifact(duckrabbit.generate("audio.shepard_tone"))
    assert isinstance(suite, MetricSuite)
    assert suite.record("rms").unit == "normalized_amplitude"
    assert suite.record("spectral_centroid_hz").claim_level is ClaimLevel.PHYSICAL_METRIC
    assert "records" in suite.to_dict()
    with pytest.raises(ValueError, match="unique"):
        MetricSuite("image", (MetricRecord("x", 1, "unit"), MetricRecord("x", 2, "unit")))


def test_observer_design_randomization_synthetic_responses_and_power(tmp_path: Path):
    design = default_study_design()
    trials_a = build_trial_sequence(design, ("observer-a", "observer-b"))
    trials_b = build_trial_sequence(design, ("observer-a", "observer-b"))
    assert trials_a == trials_b
    assert len(trials_a) == 64
    temporal_trial = next(trial for trial in trials_a if trial.condition == "temporal_sync")
    assert temporal_trial.parameter_overrides == {"sync_offset": 0.0}
    responses = simulate_binary_responses(
        design,
        ("observer-a", "observer-b"),
        {condition.condition_id: 0.7 for condition in design.conditions},
    )
    summaries = summarize_binary_responses(design.conditions, responses)
    assert summaries and all(0 <= summary.interval_low <= summary.proportion <= summary.interval_high <= 1 for summary in summaries)
    point = simulate_power(24, 0.2, repetitions=40, seed=4)
    assert 0 <= point.power <= 1 and point.assumed
    with pytest.raises(ParameterValidationError, match="probability"):
        simulate_binary_responses(design, ("observer-a",), {"duck_default": 1.5})
    with pytest.raises(ParameterValidationError, match="condition IDs"):
        StudyDesign(
            "bad",
            (ConditionSpec("same", "visual.duck_rabbit", {}, ("a",)), ConditionSpec("same", "visual.duck_rabbit", {}, ("a",))),
            1,
            1,
            0,
            (Estimand("e", ResponseKind.FORCED_CHOICE, AnalysisModel.LOGISTIC_MIXED, "a", "same"),),
        )
    path = tmp_path / "duckrabbit-v04-study-plan.json"
    duckrabbit.write_analysis_plan(design, path)
    plan = json.loads(path.read_text(encoding="utf-8"))
    assert plan["study_id"] == design.study_id
    assert len(plan["model_templates"]) == 5


def test_observer_provenance_trial_and_aggregate_contracts():
    stimulus = StimulusReference("visual.duck_rabbit", "a" * 64, "b" * 64)
    trial = TrialRecord("study:observer-a:0", ParticipantId("observer-a"), "duck_default", 0, stimulus, ResponseKind.FORCED_CHOICE, "duck", 0.42)
    assert trial.to_dict()["stimulus"]["manifest_sha256"] == "a" * 64
    aggregate = AggregateRecord("duck_choice", "duck_default", 0.7, "proportion", 0.5, 0.85, 24)
    assert aggregate.to_dict()["claim_level"] == "observer_hypothesis"
    assert len(default_model_specs()) == 5
    assert isinstance(default_model_specs()[0], AnalysisModelSpec)
    with pytest.raises(ParameterValidationError, match="pseudonymous"):
        ParticipantId("name with spaces")
    with pytest.raises(ParameterValidationError, match="SHA-256"):
        StimulusReference("visual.duck_rabbit", "bad")
    with pytest.raises(ParameterValidationError, match="illusion_id"):
        StimulusReference("bad", "a" * 64)
    with pytest.raises(ParameterValidationError, match="SHA-256"):
        StimulusReference("visual.duck_rabbit", "a" * 64, "BAD")
    with pytest.raises(ParameterValidationError, match="identity"):
        TrialRecord("", ParticipantId("observer-a"), "condition", 0, stimulus, ResponseKind.FORCED_CHOICE, "yes")
    with pytest.raises(ParameterValidationError, match="complete trial"):
        TrialRecord("bad", ParticipantId("observer-a"), "condition", 0, stimulus, ResponseKind.FORCED_CHOICE)
    with pytest.raises(ParameterValidationError, match="typed enums"):
        TrialRecord("bad-kind", ParticipantId("observer-a"), "condition", 0, stimulus, "forced_choice", "yes")
    with pytest.raises(ParameterValidationError, match="scalar"):
        TrialRecord("bad-value", ParticipantId("observer-a"), "condition", 0, stimulus, ResponseKind.FORCED_CHOICE, True)
    with pytest.raises(ParameterValidationError, match="reaction time"):
        TrialRecord("bad-rt", ParticipantId("observer-a"), "condition", 0, stimulus, ResponseKind.FORCED_CHOICE, "yes", float("nan"))
    with pytest.raises(ParameterValidationError, match="excluded trial"):
        TrialRecord("excluded", ParticipantId("observer-a"), "condition", 0, stimulus, ResponseKind.FORCED_CHOICE, "no", disposition=TrialDisposition.EXCLUDED)
    with pytest.raises(ParameterValidationError, match="missing reason"):
        TrialRecord("missing", ParticipantId("observer-a"), "condition", 0, stimulus, ResponseKind.FORCED_CHOICE, disposition=TrialDisposition.MISSING)
    with pytest.raises(ParameterValidationError, match="incomplete"):
        AnalysisModelSpec("bad", "formula", "family", "link", ("participant",))
    with pytest.raises(ParameterValidationError, match="random effects"):
        AnalysisModelSpec(AnalysisModel.LINEAR_MIXED, "formula", "family", "link", ())
    with pytest.raises(ParameterValidationError, match="aggregate estimate"):
        AggregateRecord("bad", "condition", float("nan"), "proportion", 0.4, 0.6, 2)
    with pytest.raises(ParameterValidationError, match="sample_count"):
        AggregateRecord("bad", "condition", 0.5, "proportion", 0.4, 0.6, 0)
    with pytest.raises(ParameterValidationError, match="claim level"):
        AggregateRecord("bad", "condition", 0.5, "proportion", 0.4, 0.6, 2, duckrabbit.ClaimLevel.PHYSICAL_METRIC)


def test_publication_outputs_are_complete_and_deterministic(tmp_path: Path):
    first = generate_publication_outputs(tmp_path / "one", clean=True)
    second = generate_publication_outputs(tmp_path / "two")
    assert first["figure_count"] == second["figure_count"] == len(publication_caption_specs())
    assert first["table_count"] == second["table_count"] == len(publication_table_payloads())
    first_registry = json.loads((tmp_path / "one" / "figures" / "figure_registry.json").read_text(encoding="utf-8"))
    second_registry = json.loads((tmp_path / "two" / "figures" / "figure_registry.json").read_text(encoding="utf-8"))
    first_records = {record["label"]: record for record in first_registry["figures"]}
    second_records = {record["label"]: record for record in second_registry["figures"]}
    assert first_records.keys() == second_records.keys()
    for label, record in first_records.items():
        path = tmp_path / "one" / record["path"].replace("output/", "")
        assert path.is_file(), label
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
        data_path = tmp_path / "one" / record["source_data"].replace("output/", "")
        assert data_path.is_file()
        source_payload = json.loads(data_path.read_text(encoding="utf-8"))
        assert source_payload["schema_version"] == "duckrabbit/figure-source/v1"
        assert source_payload["figure_label"] == label
        assert record["caption"] and record["alt_text"]
        second_path = tmp_path / "two" / second_records[label]["path"].replace("output/", "")
        second_data_path = tmp_path / "two" / second_records[label]["source_data"].replace("output/", "")
        assert path.read_bytes() == second_path.read_bytes()
        assert data_path.read_bytes() == second_data_path.read_bytes()
        assert record["sha256"] == second_records[label]["sha256"]
        assert record["source_data_sha256"] == second_records[label]["source_data_sha256"]
        assert record["visual_qa"] == second_records[label]["visual_qa"]
    assert (tmp_path / "one" / "data" / "catalog_table.md").is_file()
    assert "#tbl:catalog" in (tmp_path / "one" / "data" / "catalog_table.md").read_text(encoding="utf-8")
    assert (tmp_path / "one" / "figures" / "cover_visualization.webp").is_file()
    assert (tmp_path / "one" / "reports" / "cover_visualization.json").is_file()

    stale_figure = tmp_path / "one" / "figures" / "stale.png"
    stale_data = tmp_path / "one" / "data" / "stale.json"
    stale_figure.write_bytes(b"stale")
    stale_data.write_text("{}", encoding="utf-8")
    generate_publication_outputs(tmp_path / "one", clean=False)
    assert stale_figure.exists() and stale_data.exists()
    generate_publication_outputs(tmp_path / "one", clean=True)
    assert not stale_figure.exists() and not stale_data.exists()


def test_cli_publish_command_generates_registry(tmp_path: Path, capsys):
    from duckrabbit.cli import main

    assert main(["publish", "--output-dir", str(tmp_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["figure_count"] == len(publication_caption_specs())
    assert payload["table_count"] == len(publication_table_payloads())
    assert (tmp_path / "figures" / "figure_registry.json").is_file()
