"""Consumer-visible counterexamples from the final defensive review."""
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import pytest
import yaml

from duckrabbit.artifacts import ImageFrame, VideoSequence
from duckrabbit.audit import run_audit
from duckrabbit.errors import DuckRabbitError
from duckrabbit.inspection import inspect_media, verify_manifest
from duckrabbit.manifest import validate_manifest_payload
from duckrabbit.media import read_npz, write_npz
from duckrabbit.metadata import validate_project_metadata
from duckrabbit.parameters import DurationSeconds, FrameRate
from duckrabbit.render import artifact_summary, generate_artifact

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("corruption", ["projection", "record", "both", "unit", "boolean", "definition", "duplicate"])
def test_npz_metrics_are_replayed_not_merely_self_described(tmp_path, corruption):
    _, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path, format_name="npz")
    path = Path(payload["manifest"])
    document = json.loads(path.read_text())
    metrics = document["metrics"]
    record = next(row for row in metrics["records"] if row["name"] == "mean_luminance")
    if corruption in {"projection", "both"}:
        metrics["values"]["mean_luminance"] = 999
    if corruption in {"record", "both"}:
        record["value"] = 999
    if corruption == "unit":
        record["unit"] = "candela"
    if corruption == "boolean":
        record = next(row for row in metrics["records"] if row["name"] == "channels")
        record["value"] = metrics["values"]["channels"] = True
    if corruption == "definition":
        record["provenance"]["window"] = "unrelated_window"
        record["window_sha256"] = hashlib.sha256(json.dumps("unrelated_window").encode()).hexdigest()
    if corruption == "duplicate":
        metrics["records"].append(dict(record))
    path.write_text(json.dumps(document))
    report = verify_manifest(path)
    assert report["status"] == "failed"
    assert "canonical_digest" in report["checks"]
    assert "canonical_metrics" not in report["checks"]


@pytest.mark.parametrize("state", ["absent", "null", "reordered", "old_version", "old_runtime"])
def test_npz_metric_verification_scope_is_explicit(tmp_path, state):
    _, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path, format_name="npz")
    path = Path(payload["manifest"])
    document = json.loads(path.read_text())
    if state == "absent":
        document.pop("metrics")
    elif state == "null":
        document["metrics"] = None
    elif state == "reordered":
        document["metrics"]["records"].reverse()
    elif state == "old_version":
        document["metrics"]["computation_version"] = "historical_computation"
    else:
        document["metrics"]["records"][0]["provenance"]["numpy_version"] = "historical_runtime"
    path.write_text(json.dumps(document))
    report = verify_manifest(path)
    assert "canonical_digest" in report["checks"]
    assert report["status"] == ("unverified" if state.startswith("old_") else "verified")
    assert ("canonical_metrics" in report["checks"]) is (state == "reordered")
    assert report["errors"] == []


@pytest.mark.parametrize("layouts", [("C", "C"), ("F", "F"), ("F", "C")])
def test_temporal_facts_survive_exact_npz_layout_normalization(tmp_path, layouts):
    pixels = np.zeros((8, 8), dtype=np.float32)
    pixels[0, 1] = 1
    pixels[0, 0] = pixels[1, 0] = pixels[2, 0] = np.float32(2**-24)
    frames = tuple(ImageFrame(np.array(values, order=layout)) for values, layout in zip((np.zeros_like(pixels), pixels), layouts))
    video = VideoSequence(frames, FrameRate(60))
    decoded = read_npz(write_npz(video, tmp_path / "layout.npz"))
    assert video.temporal_deltas == (float(np.float32((1 + 3 * 2**-24) / 64)),)
    assert artifact_summary(video) == artifact_summary(decoded)
    for frame, values in zip(frames, (np.zeros_like(pixels), pixels)):
        np.testing.assert_array_equal(frame.pixels, values)


@pytest.mark.parametrize("kind", ["audio", "video"])
def test_unrepresentable_npz_clock_is_a_domain_error(tmp_path, kind):
    path = tmp_path / "clock.npz"
    key = "sample_rate" if kind == "audio" else "frame_rate"
    metadata = {"kind": kind, key: 10**400, "mode": "L"}
    arrays = {"samples": np.zeros((4, 1), dtype=np.float32)} if kind == "audio" else {"frames": np.zeros((2, 4, 4), dtype=np.float32)}
    np.savez(path, metadata_json=np.asarray(json.dumps(metadata)), **arrays)
    for consumer in (inspect_media, read_npz):
        with pytest.raises(DuckRabbitError):
            consumer(path)


def test_unrepresentable_manifest_and_typed_numbers_are_domain_errors(tmp_path):
    _, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path)
    document = json.loads(Path(payload["manifest"]).read_text())
    document["artifact"]["min_value"] = 10**400
    with pytest.raises(DuckRabbitError):
        validate_manifest_payload(document)
    with pytest.raises(DuckRabbitError):
        DurationSeconds(10**400)


@pytest.mark.parametrize("surface", ["pyproject.toml", "CITATION.cff", "codemeta.json", ".zenodo.json", "docs/manuscript/config.yaml"])
def test_attribution_cannot_gain_an_author_on_only_one_surface(tmp_path, surface):
    for name in ("pyproject.toml", "CITATION.cff", "codemeta.json", ".zenodo.json", "docs/manuscript/config.yaml"):
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    path = tmp_path / surface
    if surface.endswith(".json"):
        document = json.loads(path.read_text())
        document["creators" if surface == ".zenodo.json" else "author"].append({"name": "Other, Person"})
        path.write_text(json.dumps(document))
    elif surface.endswith(".toml"):
        path.write_text(path.read_text().replace('authors = [{name = "Daniel Ari Friedman"}]', 'authors = [{name = "Daniel Ari Friedman"}, {name = "Other Person"}]'))
    else:
        document = yaml.safe_load(path.read_text())
        document["authors"].append({"name": "Other Person", "family-names": "Person", "given-names": "Other"})
        path.write_text(yaml.safe_dump(document, sort_keys=False))
    assert validate_project_metadata(tmp_path).status == "failed"


@pytest.mark.parametrize("field,value", [("human_data", 0), ("seed", False)])
def test_release_rejects_equal_valued_json_type_substitution(tmp_path, publication_bundle, field, value):
    output = tmp_path / "output"
    shutil.copytree(publication_bundle, output)
    sidecar = output / "data/synthetic_psychophysics.json"
    document = json.loads(sidecar.read_text())
    document["data"]["points"][0]["prediction"][field] = value
    sidecar.write_text(json.dumps(document))
    registry_path = output / "figures/figure_registry.json"
    registry = json.loads(registry_path.read_text())
    next(row for row in registry["figures"] if row["label"] == "fig:synthetic_psychophysics")["source_data_sha256"] = hashlib.sha256(sidecar.read_bytes()).hexdigest()
    registry_path.write_text(json.dumps(registry))
    report_path = output / "reports/publication_report.json"
    report = json.loads(report_path.read_text())
    report["sha256"] = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    report_path.write_text(json.dumps(report))
    result = run_audit(output_root=output, release=True)
    assert "publication_derivation.failed" in {issue.code for issue in result.errors}


@pytest.mark.parametrize("identity", ["visual.duck_rabbit", "audio.missing_fundamental", "visual.apparent_motion", "audiovisual.sound_induced_flash"])
@pytest.mark.parametrize("dtype", ["<f8", ">f4"])
def test_exact_npz_cannot_hide_storage_dtype_changes(tmp_path, capsys, identity, dtype):
    from duckrabbit.cli import main

    _, payload = generate_artifact(identity, output_dir=tmp_path, format_name="npz")
    sidecar = Path(payload["manifest"])
    document = json.loads(sidecar.read_text())
    path = sidecar.parent / document["encoding"]["path"]
    with np.load(path, allow_pickle=False) as archive:
        arrays = {name: archive[name] for name in archive.files}
    for name in arrays.keys() - {"metadata_json"}:
        arrays[name] = arrays[name].astype(dtype)
    np.savez(path, **arrays)
    document["encoding"]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    document["encoding"]["size_bytes"] = path.stat().st_size
    sidecar.write_text(json.dumps(document))
    for consumer, target in ((read_npz, path), (inspect_media, path), (verify_manifest, sidecar)):
        with pytest.raises(DuckRabbitError):
            consumer(target)
    assert main(["verify", str(sidecar)]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "failed" and report["command"] == "verify"
    assert report["error_type"] == "MediaInspectionError"


@pytest.mark.parametrize("case", ["duration", "frame_count"])
def test_malformed_legacy_numbers_remain_structured_domain_failures(tmp_path, capsys, case):
    from duckrabbit.cli import main
    from duckrabbit.manifest import read_manifest

    identity = "audio.missing_fundamental" if case == "duration" else "visual.apparent_motion"
    _, payload = generate_artifact(identity, output_dir=tmp_path, format_name="npz")
    sidecar = Path(payload["manifest"])
    document = json.loads(sidecar.read_text())
    document["schema_version"] = "duckrabbit/artifact/v1"
    if case == "duration":
        document["duration_seconds"] = 10**400
    else:
        document["artifact"]["frames"] = 10**400
    sidecar.write_text(json.dumps(document))
    for consumer in (read_manifest, verify_manifest):
        with pytest.raises(DuckRabbitError):
            consumer(sidecar)
    assert main(["verify", str(sidecar)]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "failed" and report["error_type"] == "ManifestValidationError"


@pytest.mark.parametrize("key,value", [("PLANNED_COUNT", False), ("INPUT_REQUIRED_COUNT", True), ("PLANNED_COUNT", 0.0), ("PLANNED_COUNT", "deep_json_marker")])
def test_release_variables_preserve_numeric_types_and_bounded_failure(tmp_path, publication_bundle, key, value):
    output = tmp_path / "output"
    shutil.copytree(publication_bundle, output)
    path = output / "data/manuscript_variables.json"
    variables = json.loads(path.read_text())
    variables[key] = value
    text = json.dumps(variables)
    if value == "deep_json_marker":
        text = text.replace('"deep_json_marker"', "[" * 1500 + "0" + "]" * 1500)
    path.write_text(text)
    result = run_audit(output_root=output, release=True)
    assert "manuscript_delivery.failed" in {issue.code for issue in result.errors}
