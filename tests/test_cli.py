"""CLI tests using real registry and filesystem behavior."""

from __future__ import annotations

import json

from duckrabbit.cli import main
from duckrabbit.taxonomy import taxonomy_entries


def test_list_and_validate_commands(capsys, tmp_path):
    assert main(["list", "--implemented-only"]) == 0
    listed = capsys.readouterr().out
    assert "visual.duck_rabbit" in listed
    assert "audiovisual.mcgurk" not in listed

    config = tmp_path / "params.json"
    config.write_text(json.dumps({"duck_weight": 0.8}), encoding="utf-8")
    assert main(["validate", "visual.duck_rabbit", "--config", str(config)]) == 0
    validated = capsys.readouterr().out
    assert '"valid": true' in validated


def test_generate_command_writes_artifact_and_manifest(tmp_path, capsys):
    assert main(["generate", "visual.duck_rabbit", "--output-dir", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert '"canonical_digest"' in output
    assert (tmp_path / "visual_duck_rabbit.png").exists()
    assert (tmp_path / "visual_duck_rabbit.png.json").exists()


def test_cli_inspect_and_verify_commands(tmp_path, capsys):
    assert main(["generate", "visual.duck_rabbit", "--output-dir", str(tmp_path)]) == 0
    capsys.readouterr()
    assert main(["inspect", str(tmp_path / "visual_duck_rabbit.png")]) == 0
    inspected = json.loads(capsys.readouterr().out)
    assert inspected["kind"] == "image"
    assert main(["verify", str(tmp_path / "visual_duck_rabbit.png.json")]) == 0
    verified = json.loads(capsys.readouterr().out)
    assert verified["status"] == "verified"


def test_manuscript_variables_follow_live_registry():
    from duckrabbit.manuscript_variables import generate_variables

    variables = generate_variables()
    assert variables["IMPLEMENTED_GENERATORS"] == len(__import__("duckrabbit").default_registry.list())
    assert variables["CATALOG_ENTRIES"] == len(taxonomy_entries())
    assert "visual.duck_rabbit" in variables["IMPLEMENTED_IDS"]
    assert variables["SYNTHETIC_MODEL_ID"] == "duckrabbit.synthetic.feature_observer"
    assert "human_data=false" in variables["SYNTHETIC_PSYCHOPHYSICS_STATUS"]
    assert "Claim level:" in variables["FIGURE_CAPTION_SYNTHETIC_PSYCHOPHYSICS"]
    assert "Source data:" in variables["FIGURE_CAPTION_SYNTHETIC_PSYCHOPHYSICS"]


def test_cli_synthetic_psychophysics_writes_model_only_diagnostic(tmp_path, capsys):
    path = tmp_path / "diagnostic.json"
    assert main(["synthetic-psychophysics", "--output", str(path)]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["claim_level"] == "synthetic_model_output"
    assert status["human_data"] is False
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["model"]["training_data"] == "none"
    assert payload["summary"]["epistemic_status"] == "model_output_not_human_data"


def test_validate_command_reports_unknown_parameter_fields(tmp_path, capsys):
    config = tmp_path / "typo.json"
    config.write_text(json.dumps({"duck_weigth": 0.8}), encoding="utf-8")
    assert main(["validate", "visual.duck_rabbit", "--config", str(config)]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "failed"
    assert "unknown parameter field" in report["errors"][0]


def test_list_json_status_and_describe_commands(capsys):
    assert main(["list", "--status", "planned", "--json"]) == 0
    planned = json.loads(capsys.readouterr().out)
    assert planned == []
    assert main(["describe", "visual.duck_rabbit"]) == 0
    described = json.loads(capsys.readouterr().out)
    assert described["parameter_type"] == "DuckRabbitParams"
    assert described["taxonomy"]["evidence_references"]
    assert described["parameter_schema"]["schema_version"] == "duckrabbit/parameters/v1"


def test_cli_reports_bad_parameter_files(tmp_path, capsys):
    missing = tmp_path / "missing.json"
    assert main(["validate", "visual.duck_rabbit", "--config", str(missing)]) == 1
    assert "cannot read parameter file" in json.loads(capsys.readouterr().out)["errors"][0]
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")
    assert main(["validate", "visual.duck_rabbit", "--config", str(invalid)]) == 1
    assert "not valid JSON" in json.loads(capsys.readouterr().out)["errors"][0]


def test_cli_capabilities_are_typed_and_structured(capsys):
    assert main(["capabilities"]) == 0
    capabilities = json.loads(capsys.readouterr().out)
    assert {record["format"] for record in capabilities} == {"png", "gif", "wav", "npz", "mp4"}
    assert all({"operation", "backend", "available", "dependency", "detail"} <= set(record) for record in capabilities)


def test_cli_verify_returns_structured_failure_for_malformed_manifest(tmp_path, capsys):
    missing = tmp_path / "missing.json"
    assert main(["verify", str(missing)]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "failed"
    assert report["errors"]
