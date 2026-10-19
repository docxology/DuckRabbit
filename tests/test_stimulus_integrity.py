"""Computed geometry, signal, and provenance oracles for stimulus integrity."""

from dataclasses import replace
from itertools import combinations
import json
import math

import numpy as np
import pytest

from duckrabbit.artifacts import _validate_artifact_summary
from duckrabbit.errors import ParameterValidationError
from duckrabbit.formalism import formalism_registry, validate_formalism_registry
from duckrabbit.generators import (
    EbbinghausParams,
    KanizsaParams,
    MullerLyerParams,
    OctaveIllusionParams,
    PoggendorffParams,
    SoundInducedFlashParams,
    TemporalVentriloquismParams,
    _ebbinghaus_geometry,
    _make_beeps,
    generate_ebbinghaus,
    generate_kanizsa_triangle,
    generate_muller_lyer,
    generate_octave_illusion,
    generate_poggendorff,
    generate_sound_induced_flash,
    generate_temporal_ventriloquism,
)
from duckrabbit.metrics import MetricRecord, measure_artifact
from duckrabbit.parameters import (
    AngleDegrees,
    AudioConfig,
    AudiovisualConfig,
    DurationSeconds,
    Envelope,
    FrameRate,
    FrequencyHz,
    ImageConfig,
    Normalized,
    PhaseRadians,
    SampleRate,
    VideoConfig,
)
from duckrabbit.render import artifact_summary
from duckrabbit.synthetic_psychophysics import SyntheticModelSpec, extract_features


def _grid(config):
    return np.meshgrid(np.linspace(0.0, 1.0, config.width), np.linspace(0.0, 1.0, config.height))


@pytest.mark.parametrize("count,left,right,target", [(8, 0.045, 0.15, 0.08), (4, 0.12, 0.03, 0.06), (16, 0.02, 0.09, 0.1), (6, 0.1, 0.1, 0.04)])
def test_ebbinghaus_full_equal_targets_and_disjoint_fields(count, left, right, target):
    parameters = EbbinghausParams(
        config=ImageConfig(width=801, height=801),
        context_count=count,
        left_context_radius=Normalized(left),
        right_context_radius=Normalized(right),
        center_radius=Normalized(target),
    )
    circles = _ebbinghaus_geometry(parameters)
    for center_x, center_y, radius in circles:
        assert radius > 0.0
        assert center_x - radius >= 0.05 - 1e-12
        assert center_x + radius <= 0.95 + 1e-12
        assert center_y - radius >= 0.05 - 1e-12
        assert center_y + radius <= 0.95 + 1e-12
    for first, second in combinations(circles, 2):
        assert math.hypot(first[0] - second[0], first[1] - second[1]) > first[2] + second[2]
    assert circles[0][2] == circles[1][2]
    assert circles[2][2] / circles[0][2] == pytest.approx(left / target)
    assert circles[2 + count][2] / circles[0][2] == pytest.approx(right / target)
    pixels = generate_ebbinghaus(parameters).pixels
    horizontal, vertical = _grid(parameters.config)
    masks = [(horizontal - center_x) ** 2 + (vertical - center_y) ** 2 <= radius**2 for center_x, center_y, radius in circles]
    np.testing.assert_array_equal(masks[0], masks[1][:, ::-1])
    for index, mask in enumerate(masks):
        assert mask.any()
        expected = round((0.65 if index < 2 else 0.15) * 255) / 255
        np.testing.assert_allclose(pixels[mask], expected, atol=1e-7)
    np.testing.assert_array_equal(pixels, generate_ebbinghaus(parameters, seed=19).pixels)


@pytest.mark.parametrize("angle", [0.0, 15.0, 28.0, 55.0])
@pytest.mark.parametrize("occluder", [0.08, 0.18, 0.4])
def test_poggendorff_segments_share_actual_line_and_occlusion(angle, occluder):
    parameters = PoggendorffParams(config=ImageConfig(width=601, height=601), line_angle=AngleDegrees(angle), occluder_fraction=Normalized(occluder))
    pixels = generate_poggendorff(parameters).pixels
    horizontal, vertical = _grid(parameters.config)
    expected_y = 0.52 + math.tan(math.radians(angle)) * (horizontal - 0.5)
    hidden = np.abs(horizontal - 0.5) <= occluder / 2.0 - 1e-12
    assert np.all(pixels[hidden] == 1.0)
    for side in (-1, 1):
        selected = (pixels == 0.0) & (side * (horizontal - 0.5) > occluder / 2.0) & (horizontal > 0.10) & (horizontal < 0.90)
        assert selected.any()
        perpendicular = np.abs(vertical[selected] - expected_y[selected]) * math.cos(math.radians(angle))
        assert np.max(perpendicular) <= 0.008 + 1e-12
        columns = np.where((side * (horizontal[0] - 0.5) > occluder / 2.0 + 0.005) & (horizontal[0] > 0.10) & (horizontal[0] < 0.90))[0]
        for column in columns:
            row = round(expected_y[0, column] * (parameters.config.height - 1))
            if 0 <= row < parameters.config.height:
                assert pixels[row, column] == 0.0


@pytest.mark.parametrize("fraction", [0.15, 0.30, 0.45])
def test_kanizsa_wedges_point_inward_with_exact_edge_boundaries(fraction):
    parameters = KanizsaParams(config=ImageConfig(width=1001, height=1001), gap_fraction=Normalized(fraction))
    pixels = generate_kanizsa_triangle(parameters).pixels
    centers = np.array(((0.5, 0.20), (0.25, 0.72), (0.75, 0.72)))
    for index, center in enumerate(centers):
        edges = np.delete(centers, index, axis=0) - center
        directions = edges / np.linalg.norm(edges, axis=1)[:, None]
        bisector = directions.sum(axis=0)
        orientation = math.atan2(bisector[1], bisector[0])
        half_angle = math.acos(float(directions[0] @ directions[1])) / 2 * fraction / 0.30
        for offset, expected in ((0.0, 1.0), (math.pi, 0.0), (half_angle - 0.05, 1.0), (half_angle + 0.05, 0.0), (-half_angle + 0.05, 1.0), (-half_angle - 0.05, 0.0)):
            probe = center + 0.075 * np.array((math.cos(orientation + offset), math.sin(orientation + offset)))
            assert pixels[round(probe[1] * 1000), round(probe[0] * 1000)] == expected


@pytest.mark.parametrize("tip_inward", [True, False])
def test_muller_lyer_opposes_wings_preserving_equal_shafts(tip_inward):
    parameters = MullerLyerParams(config=ImageConfig(width=801, height=801), tip_inward=tip_inward)
    pixels = generate_muller_lyer(parameters).pixels
    for index, center_y in enumerate((0.375, 0.625)):
        row = round(center_y * 800)
        assert np.all(pixels[row, 208:593] == 1.0)
        for endpoint, side in ((0.26, 1), (0.74, -1)):
            direction = side if tip_inward == (index == 0) else -side
            for candidate, expected in ((direction, 1.0), (-direction, 0.0)):
                probe_x = endpoint + candidate * 0.08 * math.cos(math.pi / 6)
                probe_y = center_y + 0.08 * math.sin(math.pi / 6)
                assert pixels[round(probe_y * 800), round(probe_x * 800)] == expected
    swapped = generate_muller_lyer(replace(parameters, tip_inward=not tip_inward)).pixels
    np.testing.assert_array_equal(pixels, swapped[::-1])


def _av_config(**audio_controls):
    return AudiovisualConfig(
        audio=AudioConfig(duration=DurationSeconds(0.25), **audio_controls),
        video=VideoConfig(width=16, height=16, frame_rate=FrameRate(4.0), frame_count=1),
    )


def test_single_frame_video_and_av_metrics_and_features():
    timeline = generate_sound_induced_flash(SoundInducedFlashParams(config=_av_config()))
    video_metrics = measure_artifact(timeline.video)
    assert video_metrics.values["temporal_deltas"] == ()
    assert video_metrics.record("temporal_deltas").to_dict()["value"] == []
    assert video_metrics.values["mean_temporal_delta"] == 0.0
    assert measure_artifact(timeline).values["video_mean_temporal_delta"] == 0.0
    for artifact in (timeline.video, timeline):
        features = extract_features(artifact)
        assert features["temporal_delta"] == 0.0
        assert all(math.isfinite(value) for value in features.values())


@pytest.mark.parametrize("name,value,unit", [("other", (), "units"), ("temporal_deltas", (), "wrong"), ("temporal_deltas", (float("nan"),), "normalized_pixel_difference"), ("other", float("inf"), "units"), ("other", True, "units")])
def test_metrics_still_reject_invalid_observations(name, value, unit):
    with pytest.raises(ValueError):
        MetricRecord(name, value, unit)


@pytest.mark.parametrize("frequency", [500.0, 880.0])
def test_beep_carrier_must_be_strictly_below_nyquist(frequency):
    with pytest.raises(ParameterValidationError, match="Nyquist"):
        _make_beeps(AudioConfig(sample_rate=SampleRate(1000)), 1, frequency=frequency)


def test_fixed_beep_rejects_low_rate_in_public_generator():
    with pytest.raises(ParameterValidationError, match="Nyquist"):
        generate_sound_induced_flash(SoundInducedFlashParams(config=_av_config(sample_rate=SampleRate(1000))))


@pytest.mark.parametrize("low", [250.0, 300.0])
def test_octave_carriers_must_be_strictly_below_nyquist(low):
    with pytest.raises(ParameterValidationError, match="Nyquist"):
        OctaveIllusionParams(config=AudioConfig(sample_rate=SampleRate(1000), channels=2), low_frequency=FrequencyHz(low), high_frequency=FrequencyHz(2 * low))


def test_octave_valid_carriers_have_requested_spectral_peaks():
    parameters = OctaveIllusionParams(config=AudioConfig(sample_rate=SampleRate(1000), channels=2, duration=DurationSeconds(1.0), envelope=Envelope.RECTANGULAR), cycles=1, low_frequency=FrequencyHz(200.0), high_frequency=FrequencyHz(400.0))
    samples = generate_octave_illusion(parameters).samples
    for start, stop, expected in ((0, 500, (400.0, 200.0)), (500, 1000, (200.0, 400.0))):
        spectrum = np.abs(np.fft.rfft(samples[start:stop], axis=0))
        frequencies = np.fft.rfftfreq(stop - start, 0.001)
        np.testing.assert_array_equal(frequencies[np.argmax(spectrum, axis=0)], expected)


@pytest.mark.parametrize("phase", [0.0, 0.7])
@pytest.mark.parametrize("envelope", list(Envelope))
def test_temporal_ventriloquism_honors_phase_and_envelope(phase, envelope):
    config = _av_config(phase=PhaseRadians(phase), envelope=envelope)
    parameters = TemporalVentriloquismParams(config=config)
    timeline = generate_temporal_ventriloquism(parameters)
    time = np.arange(2000) / 8000
    duration = 0.25
    window = np.maximum(0.0, 1.0 - np.abs(time - duration / 2) / 0.01)
    envelopes = {
        Envelope.RECTANGULAR: np.ones_like(time),
        Envelope.LINEAR: np.minimum(time / duration, (duration - time) / duration),
        Envelope.SINE_SQUARED: np.sin(np.pi * time / duration) ** 2,
    }
    expected = np.sin(2 * np.pi * 1200 * time + phase) * window * envelopes[envelope] * 0.5
    np.testing.assert_allclose(timeline.audio.samples[:, 0], expected, atol=2e-8)
    assert np.count_nonzero(expected) > 100


def test_formalism_requires_exact_declared_equation_label(tmp_path):
    definition = formalism_registry()[0]
    for relative in definition.implementation:
        path = tmp_path / "src" / "duckrabbit" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    for relative in definition.tests:
        path = tmp_path / "tests" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    manuscript = tmp_path / "docs" / "manuscript" / "method.md"
    manuscript.parent.mkdir(parents=True)
    manuscript.write_text("$$ q = 1 $$ {#eq:typed_request}\n", encoding="utf-8")
    assert validate_formalism_registry((definition,), project_root=tmp_path) == (definition,)
    with pytest.raises(ValueError, match="absent"):
        validate_formalism_registry((replace(definition, label="eq:typed_reques"),), project_root=tmp_path)
    manuscript.write_text("See @eq:typed_request and eq:typed_request.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="absent"):
        validate_formalism_registry((definition,), project_root=tmp_path)


def test_numpy_synthetic_parameters_are_json_serializable_python_floats():
    model = SyntheticModelSpec("numpy-model", "1", {"temporal_delta": np.float32(0.7)}, temperature=np.float32(0.25))
    assert type(model.feature_weights["temporal_delta"]) is float
    assert type(model.temperature) is float
    payload = json.loads(json.dumps(model.to_dict(), allow_nan=False))
    assert payload["temperature"] == 0.25
    assert payload["feature_weights"]["temporal_delta"] == pytest.approx(0.7)


@pytest.mark.parametrize("child,replacement", [("audio", "video"), ("video", "audio")])
def test_audiovisual_summary_enforces_exact_child_discriminants(child, replacement):
    timeline = generate_sound_induced_flash(SoundInducedFlashParams(config=_av_config()))
    summary = artifact_summary(timeline)
    _validate_artifact_summary(summary)
    summary[child] = summary[replacement]
    summary["nbytes"] = summary["audio"]["nbytes"] + summary["video"]["nbytes"]
    with pytest.raises(ParameterValidationError, match=f"{child} must have type"):
        _validate_artifact_summary(summary)
