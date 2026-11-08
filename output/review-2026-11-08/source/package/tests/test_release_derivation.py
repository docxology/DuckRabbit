"""Real release-consumer counterexamples, including coordinated hash changes."""
from pathlib import Path
import hashlib
import json
import shutil

import numpy as np
from PIL import Image, ImageDraw
import pytest

from duckrabbit.artifacts import AudioBuffer, AudiovisualTimeline, ImageFrame, VideoSequence
from duckrabbit.audit import run_audit
from duckrabbit.metrics import measure_artifact
from duckrabbit.parameters import FrameRate, FrequencyHz, SampleRate
from duckrabbit.publication import _draw_audiovisual_traces, _parameter_domains, validate_publication_derivation

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("color", [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0.5, 0.5, 0.5)])
def test_rgb_video_and_image_readouts_share_the_declared_proxy(color):
    frame = ImageFrame(np.broadcast_to(np.array(color, dtype=np.float32), (2, 3, 3)), mode="RGB")
    timeline = AudiovisualTimeline(AudioBuffer(np.zeros((1000, 1)), SampleRate(1000)), VideoSequence((frame,), FrameRate(1)))
    image = Image.new("RGB", (101, 101))
    traces = _draw_audiovisual_traces(ImageDraw.Draw(image), timeline, (0, 0, 100, 50), (0, 51, 100, 100))
    np.testing.assert_allclose(traces["video"]["values"], measure_artifact(frame).record("mean_luminance").value)


def test_frequency_figure_does_not_invent_finite_validation_bounds(tmp_path):
    for value in (0.01, 50000):
        assert FrequencyHz(value).value == value
    _, payload = _parameter_domains(tmp_path / "domains.png")
    domain = next(row for row in payload["domains"] if row["type"] == "FrequencyHz")
    assert domain["minimum"] == 0 and domain["minimum_inclusive"] is False
    assert domain["maximum"] is None and domain["finite"] is True
    with pytest.raises(ValueError):
        FrequencyHz(0)


@pytest.mark.parametrize("corruption", ["empty_data", "false_metric", "different_raster"])
def test_release_rejects_coordinated_scientific_data_and_hash_changes(tmp_path, publication_bundle, corruption):
    output = tmp_path / "output"
    shutil.copytree(publication_bundle, output)
    registry_path = output / "figures" / "figure_registry.json"
    registry = json.loads(registry_path.read_text())
    record = next(record for record in registry["figures"] if record["label"] == "fig:metrics_dashboard")
    sidecar = output / "data" / "metrics_dashboard.json"
    payload = json.loads(sidecar.read_text())
    if corruption == "empty_data":
        payload["data"] = {}
    elif corruption == "false_metric":
        payload["data"]["cards"][0]["metrics"]["values"]["mean_luminance"] = 0.123456
    else:
        target = output / "figures" / "metrics_dashboard.png"
        with Image.open(target) as image:
            changed = image.copy()
        changed.putpixel((100, 100), (255, 0, 255))
        changed.save(target)
        record["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    sidecar.write_text(json.dumps(payload))
    record["source_data_sha256"] = hashlib.sha256(sidecar.read_bytes()).hexdigest()
    registry_path.write_text(json.dumps(registry))
    report_path = output / "reports" / "publication_report.json"
    report = json.loads(report_path.read_text())
    report["sha256"] = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    report_path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="live derivation"):
        validate_publication_derivation(output)
    outcome = run_audit(output_root=output, release=True)
    assert "publication_derivation.failed" in {issue.code for issue in outcome.errors}


@pytest.mark.parametrize("corruption", ["missing_chapter", "stale_prose", "unknown_token", "stale_variables", "stale_bibliography"])
def test_release_checks_actual_hydrated_delivery(tmp_path, publication_bundle, corruption):
    output = tmp_path / "output"
    shutil.copytree(publication_bundle, output)
    chapter = output / "manuscript" / "00_abstract.md"
    if corruption == "missing_chapter":
        chapter.unlink()
    elif corruption in {"stale_prose", "unknown_token"}:
        chapter.write_text("stale prose" if corruption == "stale_prose" else "{{UNKNOWN_TOKEN}}")
    elif corruption == "stale_variables":
        (output / "data" / "manuscript_variables.json").write_text("{}")
    else:
        (output / "manuscript" / "references.bib").write_text("@misc{invented}")
    outcome = run_audit(output_root=output, release=True)
    assert "manuscript_delivery.failed" in {issue.code for issue in outcome.errors}


def test_execution_audit_refuses_a_foreign_source_tree(tmp_path):
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    outcome = run_audit(project_root=foreign)
    assert outcome.status == "failed" and outcome.generated_artifacts == 0
    assert {issue.code for issue in outcome.errors} == {"executing_source.mismatch"}
