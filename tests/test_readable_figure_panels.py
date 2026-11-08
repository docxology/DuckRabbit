"""Real source/raster counterexamples for the readable-delivery trust boundary."""
import hashlib
import json
import shutil

import numpy as np
from PIL import Image
import pytest

from duckrabbit.artifacts import AudioBuffer
from duckrabbit.canonical import canonical_digest
from duckrabbit.metrics import measure_artifact
from duckrabbit.parameters import SampleRate
from duckrabbit import publication as pub
from duckrabbit.publication_panels import (
    REPORT_PATH,
    _render_panel,
    _safe_path,
    generate_readable_figure_panels,
    validate_readable_figure_panels,
)


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def panel_bundle(tmp_path, publication_bundle):
    root = tmp_path / "output"
    shutil.copytree(publication_bundle, root)
    return root


def test_live_replay_accepts_source_bound_delivery(publication_bundle):
    report = validate_readable_figure_panels(publication_bundle)
    assert report == _read(publication_bundle / REPORT_PATH)
    # Every exact scientific identity has one separate, source-ordered variant.
    collections = {
        "catalog_matrix": ("entries", "illusion_id"),
        "audio_signals": ("signals", "illusion_id"),
        "scholarship_map": ("rows", "illusion_id"),
        "formalism_traceability": ("definitions", "label"),
    }
    for figure in report["figures"]:
        collection, key = collections[figure["stem"]]
        records = _read(publication_bundle / figure["source_data"].removeprefix("output/"))["data"][collection]
        assert [panel["record_ids"] for panel in figure["panels"]] == [[record[key]] for record in records]


def test_actual_ink_fits_complete_measured_blocks_at_delivery_boundary(publication_bundle):
    report = _read(publication_bundle / REPORT_PATH)
    for figure in report["figures"]:
        for panel in figure["panels"]:
            path = publication_bundle / panel["path"].removeprefix("output/")
            with Image.open(path) as image:
                assert image.size == (panel["width_px"], panel["height_px"])
                scale = min(807 / image.width, 605 / image.height)
                blocks = panel["display"]["text_blocks"]
                for block in blocks:
                    x, y, width, height = (block[key] for key in ("x", "y", "width", "height"))
                    assert 0 <= x < x + width <= image.width
                    assert 0 <= y < y + height <= image.height
                    assert pub._font(block["font_size"]).size * scale >= 16
                    # A genuinely rendered block, not a report-only claim.
                    ink = np.asarray(image.crop((x, y, x + width, y + height)))
                    assert np.any(np.any(ink != pub.CANVAS, axis=2))
                for index, left in enumerate(blocks):
                    for right in blocks[index + 1:]:
                        overlap_x = min(left["x"] + left["width"], right["x"] + right["width"]) - max(left["x"], right["x"])
                        overlap_y = min(left["y"] + left["height"], right["y"] + right["height"]) - max(left["y"], right["y"])
                        assert overlap_x <= 0 or overlap_y <= 0


def test_coordinated_source_content_deletion_is_not_certified(panel_bundle):
    path = panel_bundle / "data/scholarship_map.json"
    payload = _read(path)
    payload["data"]["rows"][0]["limitations"] = []
    _write(path, payload)
    # Real re-render refreshes panel pixels, metadata and every declared hash.
    # It must still fail against the trusted live scholarship source.
    generate_readable_figure_panels(panel_bundle)
    with pytest.raises(ValueError, match="source disagrees with live derivation"):
        validate_readable_figure_panels(panel_bundle)


def test_coordinated_pixel_and_report_hash_tamper_is_rejected(panel_bundle):
    report_path = panel_bundle / REPORT_PATH
    report = _read(report_path)
    panel = report["figures"][0]["panels"][0]
    path = panel_bundle / panel["path"].removeprefix("output/")
    with Image.open(path) as image:
        changed = image.copy()
    changed.paste(pub.CANVAS, (0, 0, changed.width, changed.height))
    changed.save(path, format="PNG")
    panel["sha256"] = _sha(path)
    _write(report_path, report)
    with pytest.raises(ValueError, match="exact source/raster replay"):
        validate_readable_figure_panels(panel_bundle)


@pytest.mark.parametrize("field", ["font_sha256", "renderer_sha256", "panel_producer_sha256"])
def test_stale_font_or_code_identity_fails_closed(panel_bundle, field):
    path = panel_bundle / REPORT_PATH
    report = _read(path)
    report["render_environment"][field] = "0" * 64
    _write(path, report)
    with pytest.raises(ValueError, match="provenance is stale"):
        validate_readable_figure_panels(panel_bundle)


def test_stale_source_identity_is_not_repaired_by_hash_update(panel_bundle):
    source_path = panel_bundle / "data/formalism_traceability.json"
    source = _read(source_path)
    source["figure_label"] = "fig:catalog_matrix"
    _write(source_path, source)
    report_path = panel_bundle / REPORT_PATH
    report = _read(report_path)
    figure = next(item for item in report["figures"] if item["stem"] == "formalism_traceability")
    figure["source_data_sha256"] = _sha(source_path)
    _write(report_path, report)
    with pytest.raises(ValueError, match="source identity"):
        validate_readable_figure_panels(panel_bundle)


@pytest.mark.parametrize("corruption", ["missing", "extra", "omitted_record", "traversal", "typed_index"])
def test_missing_extra_traversal_and_coercion_are_rejected(panel_bundle, corruption):
    report_path = panel_bundle / REPORT_PATH
    report = _read(report_path)
    panels = report["figures"][0]["panels"]
    path = panel_bundle / panels[0]["path"].removeprefix("output/")
    if corruption == "missing":
        path.unlink()
    elif corruption == "extra":
        shutil.copyfile(path, panel_bundle / "figures/unrelated-detail-01.png")
    elif corruption == "omitted_record":
        panels.pop()
        report["panel_count"] -= 1
    elif corruption == "traversal":
        panels[0]["path"] = "output/figures/../../outside.png"
    else:
        # In Python True == 1; strict typed report comparison must not agree.
        panels[0]["index"] = True
    _write(report_path, report)
    with pytest.raises(ValueError):
        validate_readable_figure_panels(panel_bundle)


def test_symlinked_panel_is_rejected_even_when_bytes_are_identical(panel_bundle):
    report = _read(panel_bundle / REPORT_PATH)
    path = panel_bundle / report["figures"][0]["panels"][0]["path"].removeprefix("output/")
    original = panel_bundle / "identical.png"
    path.rename(original)
    path.symlink_to(original)
    with pytest.raises(ValueError, match="symlink"):
        validate_readable_figure_panels(panel_bundle)


@pytest.mark.parametrize("relative", ["../outside.png", "/absolute.png", "figures/../outside.png", "figures//alias.png", "figures\\alias.png"])
def test_path_guard_rejects_aliases_before_access(tmp_path, relative):
    with pytest.raises(ValueError, match="path"):
        _safe_path(tmp_path, relative, existing=False)


def test_new_content_cannot_silently_shrink_or_truncate_at_display_boundary(tmp_path):
    record = {"label": "eq:complete", "equation": "full_content_" * 1000}
    path = tmp_path / "oversized.png"
    with pytest.raises(ValueError, match="text-fit boundary"):
        _render_panel("formalism_traceability", record, path)
    assert not path.exists()


def test_actual_audio_panel_preserves_skipped_impulse_and_separate_channel_extrema(tmp_path):
    samples = np.zeros((700, 2), dtype=np.float32)
    samples[1] = (1.0, -1.0)  # Former point decimation omitted index 1.
    samples[-1] = (-1.0, 1.0)
    artifact = AudioBuffer(samples, SampleRate(1000))
    record = {"illusion_id": "audio.real_boundary_probe",
              "canonical_digest": canonical_digest(artifact),
              "metrics": measure_artifact(artifact).to_dict(),
              "waveform": pub._audio_waveform(artifact),
              "spectrum": pub._audio_spectrum(artifact)}
    path = tmp_path / "impulses.png"
    panel = _render_panel("audio_signals", record, path)
    channel_labels = [block for block in panel["display"]["text_blocks"] if block["text"] in {"ch0", "ch1"}]
    with Image.open(path) as image:
        for lane, block in enumerate(channel_labels):
            top = block["y"] - 12
            pixels = np.asarray(image)
            # Inspect actual extrema ink, not just serialized numerical arrays.
            first_top = np.any(np.all(pixels[top:top + 30, 120:123] == pub.ACCENT, axis=2))
            first_bottom = np.any(np.all(pixels[top + 31:top + 61, 120:123] == pub.ACCENT, axis=2))
            assert bool(first_top) is (lane == 0)
            assert bool(first_bottom) is (lane == 1)
            last_top = np.any(np.all(pixels[top:top + 30, 574:577] == pub.ACCENT, axis=2))
            last_bottom = np.any(np.all(pixels[top + 31:top + 61, 574:577] == pub.ACCENT, axis=2))
            assert bool(last_top) is (lane == 1)
            assert bool(last_bottom) is (lane == 0)
