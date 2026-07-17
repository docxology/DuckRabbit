"""Metric units, luminance semantics, and synthetic observer summaries."""

from __future__ import annotations

import numpy as np
import pytest

import duckrabbit
from duckrabbit.artifacts import AudioBuffer, ImageFrame
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
