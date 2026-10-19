"""Metric units, luminance semantics, and synthetic observer summaries."""

from __future__ import annotations

import cProfile

import numpy as np
import pytest

import duckrabbit
from duckrabbit.artifacts import AudioBuffer, ImageFrame, VideoSequence
from duckrabbit.metrics import MetricRecord, MetricSuite, measure_artifact
from duckrabbit.observer_analysis import (
    ResponseKind,
    default_study_design,
    simulate_continuous_responses,
    simulate_event_counts,
    simulate_power_curve,
    simulate_reaction_times,
    summarize_numeric_responses,
)
from duckrabbit.parameters import FrameRate, SampleRate
from duckrabbit.render import artifact_summary


@pytest.mark.parametrize("consumer", [measure_artifact, artifact_summary])
def test_video_consumers_compute_adjacent_frame_changes_only_once(consumer) -> None:
    video = VideoSequence(tuple(ImageFrame(np.full((8, 9), value, dtype=np.float32)) for value in (0.0, 0.2, 0.5)), FrameRate(12.0))
    profiler = cProfile.Profile()
    result = profiler.runcall(consumer, video)
    calls = [entry.callcount for entry in profiler.getstats() if entry.code is VideoSequence.temporal_deltas.fget.__code__]
    assert calls == [1]
    values = result.values if isinstance(result, MetricSuite) else result
    assert values["temporal_deltas"] == pytest.approx((0.2, 0.3))
    assert values["mean_temporal_delta"] == pytest.approx(0.25)


def test_audio_metrics_reduce_peak_and_rms_once() -> None:
    artifact = AudioBuffer(np.array([[0.0], [0.5], [-0.25]], dtype=np.float32), SampleRate(8000))
    profiler = cProfile.Profile()
    metrics = profiler.runcall(measure_artifact, artifact)
    for property_name in ("peak", "rms"):
        getter = getattr(AudioBuffer, property_name).fget.__code__
        assert [entry.callcount for entry in profiler.getstats() if entry.code is getter] == [1]
        assert metrics.values[property_name] == getattr(artifact, property_name)


@pytest.mark.parametrize("layouts", [("C", "C", "C"), ("F", "F", "F"), ("F", "C", "F")])
def test_temporal_reduction_preserves_exact_values_and_input_buffers(layouts) -> None:
    rng = np.random.default_rng(23)
    frames = tuple(ImageFrame(np.array(rng.random((31, 37), dtype=np.float32), order=layout)) for layout in layouts)
    originals = tuple(frame.pixels.copy() for frame in frames)
    video = VideoSequence(frames, FrameRate(24.0))
    expected = tuple(float(np.mean(np.abs(current.pixels - previous.pixels))) for previous, current in zip(frames, frames[1:]))
    assert video.temporal_deltas == expected
    assert measure_artifact(video).values["temporal_deltas"] == expected
    assert artifact_summary(video)["mean_temporal_delta"] == float(np.mean(expected))
    for frame, original in zip(frames, originals):
        np.testing.assert_array_equal(frame.pixels, original)
        assert not frame.pixels.flags.writeable


def test_rgb_metrics_use_relative_luminance_and_new_audio_summaries() -> None:
    image = ImageFrame(np.array([[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]], dtype=np.float32), mode="RGB")
    metrics = measure_artifact(image)
    assert metrics.record("mean_luminance").value == pytest.approx((0.2126 + 0.7152) / 2)
    assert metrics.record("effective_dynamic_range").unit == "normalized_luminance"
    audio_metrics = measure_artifact(duckrabbit.generate("audio.shepard_tone"))
    assert audio_metrics.record("spectral_bandwidth_hz").value >= 0
    assert audio_metrics.record("crest_factor").unit == "ratio"


def test_stereo_spectral_metrics_aggregate_both_channels() -> None:
    sample_rate = 1_000
    time = np.arange(sample_rate, dtype=np.float32) / sample_rate
    stereo = AudioBuffer(
        np.column_stack((np.sin(2 * np.pi * 40 * time), np.sin(2 * np.pi * 160 * time))),
        duckrabbit.SampleRate(sample_rate),
    )
    left_only = AudioBuffer(stereo.samples[:, :1], duckrabbit.SampleRate(sample_rate))
    stereo_centroid = measure_artifact(stereo).record("spectral_centroid_hz").value
    left_centroid = measure_artifact(left_only).record("spectral_centroid_hz").value
    assert stereo_centroid != pytest.approx(left_centroid)


def test_spectral_centroid_uses_channel_mean_magnitudes_not_power() -> None:
    sample_rate = 1024
    time = np.arange(sample_rate, dtype=np.float64) / sample_rate
    samples = np.column_stack((0.2 * np.sin(2 * np.pi * 32 * time),
                               0.6 * np.sin(2 * np.pi * 128 * time))).astype(np.float32)
    audio = AudioBuffer(samples, SampleRate(sample_rate))
    frequencies = np.fft.rfftfreq(sample_rate, 1 / sample_rate)
    magnitude = np.mean(np.abs(np.fft.rfft(samples, axis=0)), axis=1)
    expected = float(np.sum(frequencies * magnitude) / np.sum(magnitude))
    power = np.mean(np.abs(np.fft.rfft(samples, axis=0)) ** 2, axis=1)
    power_centroid = float(np.sum(frequencies * power) / np.sum(power))
    assert measure_artifact(audio).values["spectral_centroid_hz"] == expected
    assert expected == pytest.approx(104, abs=1e-4)
    assert expected != pytest.approx(power_centroid)
    silence = AudioBuffer(np.zeros((sample_rate, 2), dtype=np.float32), SampleRate(sample_rate))
    assert measure_artifact(silence).values["spectral_centroid_hz"] == 0.0


def test_metric_suite_rejects_untyped_records_and_claims() -> None:
    with pytest.raises(ValueError, match="MetricRecord"):
        MetricSuite("image", ("bad",))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="physical_metric"):
        MetricRecord("observer", 1.0, "ratio", claim_level=duckrabbit.ClaimLevel.OBSERVER_HYPOTHESIS)
    with pytest.raises(ValueError, match="artifact type"):
        MetricSuite("not-an-artifact", (MetricRecord("x", 1, "unit"),))
    with pytest.raises(ValueError, match="artifact type"):
        MetricSuite("image", ())
    suite = MetricSuite("image", (MetricRecord("x", 1, "unit"),))
    with pytest.raises(KeyError):
        suite.record("missing")
    with pytest.raises(ValueError, match="computation version"):
        MetricSuite("image", (MetricRecord("x", 1, "unit"),), computation_version="")


def test_synthetic_numeric_observer_families_are_deterministic_and_bounded() -> None:
    design = default_study_design()
    observers = ("observer-a", "observer-b")
    means = {condition.condition_id: index / 10 for index, condition in enumerate(design.conditions)}
    continuous_a = simulate_continuous_responses(design, observers, means, seed=8)
    continuous_b = simulate_continuous_responses(design, observers, means, seed=8)
    assert continuous_a == continuous_b
    assert all(record.claim_level is duckrabbit.ClaimLevel.OBSERVER_HYPOTHESIS for record in continuous_a)
    counts = simulate_event_counts(design, observers, {condition.condition_id: 2.0 for condition in design.conditions}, seed=9)
    times = simulate_reaction_times(design, observers, {condition.condition_id: 0.4 for condition in design.conditions}, seed=10)
    summaries = summarize_numeric_responses(continuous_a + times)
    assert {summary.response_kind for summary in summaries} == {ResponseKind.CONTINUOUS_MAGNITUDE, ResponseKind.REACTION_TIME}
    assert all(summary.interval_low <= summary.mean <= summary.interval_high for summary in summaries)
    assert all(record.value >= 0 for record in counts)
    curve = simulate_power_curve(16, (-0.2, 0.0, 0.2), repetitions=30, seed=4)
    assert [point.effect for point in curve] == [-0.2, 0.0, 0.2]
    assert all(point.assumed and 0 <= point.power <= 1 for point in curve)
