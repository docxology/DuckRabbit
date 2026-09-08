"""Typed, observer-independent metrics for generated stimuli."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

import numpy as np

from .artifacts import AudioBuffer, AudiovisualTimeline, CanonicalArtifact, ImageFrame, VideoSequence
from .taxonomy import ClaimLevel


MetricValue = float | int | tuple[float, ...]


@dataclass(frozen=True)
class MetricRecord:
    """One measured physical property with units and provenance."""

    name: str
    value: MetricValue
    unit: str
    source: str = "canonical_artifact"
    claim_level: ClaimLevel = ClaimLevel.PHYSICAL_METRIC
    tolerance: float | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.unit or not self.source:
            raise ValueError("metric name, unit, and source are required")
        if not isinstance(self.claim_level, ClaimLevel) or self.claim_level not in {ClaimLevel.PHYSICAL_METRIC, ClaimLevel.ENCODED_MEDIA}:
            raise ValueError("metric claim_level must be physical_metric or encoded_media")
        values = self.value if isinstance(self.value, tuple) else (self.value,)
        if not values or not all(type(item) in (int, float) and isfinite(float(item)) for item in values):
            raise ValueError(f"metric {self.name} contains a non-finite or invalid value")
        if self.tolerance is not None and (not isfinite(self.tolerance) or self.tolerance < 0):
            raise ValueError(f"metric {self.name} tolerance must be finite and non-negative")

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": list(self.value) if isinstance(self.value, tuple) else self.value,
            "unit": self.unit,
            "source": self.source,
            "claim_level": self.claim_level.value,
            "tolerance": self.tolerance,
        }


@dataclass(frozen=True)
class MetricSuite:
    """Immutable collection of physical stimulus metrics."""

    artifact_type: str
    records: tuple[MetricRecord, ...]
    computation_version: str = "duckrabbit/metrics/v2"

    def __post_init__(self) -> None:
        if self.artifact_type not in {"image", "audio", "video", "audiovisual"} or not self.records:
            raise ValueError("metric suite requires an artifact type and records")
        if not all(isinstance(record, MetricRecord) for record in self.records):
            raise ValueError("metric suite records must be MetricRecord objects")
        if len({record.name for record in self.records}) != len(self.records):
            raise ValueError("metric names must be unique")
        if not self.computation_version:
            raise ValueError("metric computation version is required")

    @property
    def values(self) -> Mapping[str, MetricValue]:
        """Compatibility view used by the v0.3 API."""
        return {record.name: record.value for record in self.records}

    def record(self, name: str) -> MetricRecord:
        for record in self.records:
            if record.name == name:
                return record
        raise KeyError(name)

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "computation_version": self.computation_version,
            "values": dict(sorted(self.values.items())),
            "records": [record.to_dict() for record in self.records],
        }


StimulusMetrics = MetricSuite


def _suite(artifact_type: str, values: Mapping[str, MetricValue], units: Mapping[str, str]) -> MetricSuite:
    missing_units = sorted(set(values) - set(units))
    if missing_units:
        raise ValueError(f"metrics missing units: {missing_units}")
    records = tuple(MetricRecord(name, value, units[name]) for name, value in values.items())
    return MetricSuite(artifact_type, records)


def _relative_luminance(pixels: np.ndarray) -> np.ndarray:
    """Return Rec. 709 relative luminance for grayscale or RGB pixels."""
    if pixels.ndim == 2:
        return pixels
    if pixels.ndim == 3 and pixels.shape[-1] == 3:
        return 0.2126 * pixels[..., 0] + 0.7152 * pixels[..., 1] + 0.0722 * pixels[..., 2]
    raise ValueError("image pixels must be grayscale or RGB")


def measure_artifact(artifact: CanonicalArtifact) -> MetricSuite:
    """Measure stable luminance, signal, temporal, and timing properties."""
    if isinstance(artifact, ImageFrame):
        values = artifact.pixels
        luminance = _relative_luminance(values)
        luminance_low = float(np.min(luminance))
        luminance_high = float(np.max(luminance))
        return _suite(
            "image",
            {
                "width": artifact.width,
                "height": artifact.height,
                "channels": artifact.channels,
                "mean_luminance": float(np.mean(luminance)),
                "std_luminance": float(np.std(luminance)),
                "unique_values": int(np.unique(values).size),
                "min_luminance": luminance_low,
                "max_luminance": luminance_high,
                "effective_dynamic_range": luminance_high - luminance_low,
            },
            {
                "width": "pixels",
                "height": "pixels",
                "channels": "channels",
                "mean_luminance": "normalized_luminance",
                "std_luminance": "normalized_luminance",
                "unique_values": "levels",
                "min_luminance": "normalized_luminance",
                "max_luminance": "normalized_luminance",
                "effective_dynamic_range": "normalized_luminance",
            },
        )
    if isinstance(artifact, AudioBuffer):
        samples = artifact.samples
        # Aggregate channels by mean magnitude so stereo metrics do not
        # silently report only the left channel.
        spectrum = np.mean(np.abs(np.fft.rfft(samples, axis=0)), axis=1)
        frequencies = np.fft.rfftfreq(samples.shape[0], 1.0 / artifact.sample_rate.value)
        denominator = max(float(np.sum(spectrum)), 1e-12)
        spectral_centroid = float(np.sum(frequencies * spectrum) / denominator)
        dominant_frequency = float(frequencies[int(np.argmax(spectrum))]) if spectrum.size else 0.0
        spectral_variance = float(np.sum(((frequencies - spectral_centroid) ** 2) * spectrum) / denominator)
        spectral_bandwidth = float(np.sqrt(max(spectral_variance, 0.0)))
        peak = artifact.peak
        return _suite(
            "audio",
            {
                "samples": artifact.sample_count,
                "channels": artifact.channels,
                "sample_rate": artifact.sample_rate.value,
                "duration_seconds": artifact.duration_seconds,
                "peak": artifact.peak,
                "rms": artifact.rms,
                "spectral_centroid_hz": spectral_centroid,
                "dominant_frequency_hz": dominant_frequency,
                "spectral_bandwidth_hz": spectral_bandwidth,
                "crest_factor": peak / max(artifact.rms, 1e-12),
            },
            {
                "samples": "samples",
                "channels": "channels",
                "sample_rate": "Hz",
                "duration_seconds": "seconds",
                "peak": "normalized_amplitude",
                "rms": "normalized_amplitude",
                "spectral_centroid_hz": "Hz",
                "dominant_frequency_hz": "Hz",
                "spectral_bandwidth_hz": "Hz",
                "crest_factor": "ratio",
            },
        )
    if isinstance(artifact, VideoSequence):
        return _suite(
            "video",
            {
                "width": artifact.width,
                "height": artifact.height,
                "frames": artifact.frame_count,
                "frame_rate": artifact.frame_rate.value,
                "duration_seconds": artifact.duration_seconds,
                "mean_temporal_delta": artifact.mean_temporal_delta,
                "temporal_deltas": artifact.temporal_deltas,
            },
            {
                "width": "pixels",
                "height": "pixels",
                "frames": "frames",
                "frame_rate": "frames/second",
                "duration_seconds": "seconds",
                "mean_temporal_delta": "normalized_pixel_difference",
                "temporal_deltas": "normalized_pixel_difference",
            },
        )
    if isinstance(artifact, AudiovisualTimeline):
        child = measure_artifact(artifact.video)
        return _suite(
            "audiovisual",
            {
                "duration_seconds": artifact.duration_seconds,
                "presentation_duration_seconds": artifact.presentation_duration_seconds,
                "sync_offset_ms": artifact.sync_offset.value,
                "spatial_offset": artifact.spatial_offset.value,
                "video_mean_temporal_delta": float(child.values["mean_temporal_delta"]),
                "audio_rms": artifact.audio.rms,
            },
            {
                "duration_seconds": "seconds",
                "presentation_duration_seconds": "seconds",
                "sync_offset_ms": "milliseconds",
                "spatial_offset": "normalized_spatial_offset",
                "video_mean_temporal_delta": "normalized_pixel_difference",
                "audio_rms": "normalized_amplitude",
            },
        )
    raise TypeError(f"unsupported artifact type: {type(artifact).__name__}")


__all__ = ["MetricRecord", "MetricSuite", "StimulusMetrics", "measure_artifact"]
