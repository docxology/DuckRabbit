"""Typed, observer-independent metrics for generated stimuli."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from math import isfinite
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

import numpy as np

from .artifacts import AudioBuffer, AudiovisualTimeline, CanonicalArtifact, ImageFrame, VideoSequence
from .taxonomy import ClaimLevel


MetricValue = float | int | tuple[float, ...]

COMPUTATION_VERSION = "duckrabbit/metrics/v3"
_SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes() + b"\0" + Path(__file__).with_name("artifacts.py").read_bytes()).hexdigest()


def _definition_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class MetricRecord:
    """One measured physical property with units and provenance."""

    name: str
    value: MetricValue
    unit: str
    source: str = "canonical_artifact"
    claim_level: ClaimLevel = ClaimLevel.PHYSICAL_METRIC
    tolerance: float | None = None
    provenance: Mapping[str, str] = field(default_factory=lambda: {
        "color_space": "unspecified", "transfer_function": "unspecified",
        "window": "unspecified", "algorithm": "externally_supplied",
    })

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value.strip() for value in (self.name, self.unit, self.source)):
            raise ValueError("metric name, unit, and source are required")
        if not isinstance(self.claim_level, ClaimLevel) or self.claim_level not in {ClaimLevel.PHYSICAL_METRIC, ClaimLevel.ENCODED_MEDIA}:
            raise ValueError("metric claim_level must be physical_metric or encoded_media")
        values = self.value if isinstance(self.value, tuple) else (self.value,)
        empty_temporal_observations = not values and self.name == "temporal_deltas" and self.unit == "normalized_pixel_difference"
        if (not values and not empty_temporal_observations) or not all(type(item) in (int, float) and isfinite(float(item)) for item in values):
            raise ValueError(f"metric {self.name} contains a non-finite or invalid value")
        if self.tolerance is not None and (type(self.tolerance) not in (int, float) or not isfinite(self.tolerance) or self.tolerance < 0):
            raise ValueError(f"metric {self.name} tolerance must be finite and non-negative")
        required = {"color_space", "transfer_function", "window", "algorithm"}
        if not isinstance(self.provenance, Mapping) or not required <= self.provenance.keys() or any(
            not isinstance(key, str) or not isinstance(value, str) or not value.strip()
            for key, value in self.provenance.items()
        ):
            raise ValueError("metric provenance requires nonempty string definitions")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": list(self.value) if isinstance(self.value, tuple) else self.value,
            "unit": self.unit,
            "source": self.source,
            "claim_level": self.claim_level.value,
            "tolerance": self.tolerance,
            "provenance": dict(self.provenance),
            "computation_sha256": _definition_hash({"metric": self.name, "unit": self.unit, **self.provenance}),
            "window_sha256": _definition_hash(self.provenance["window"]),
        }


@dataclass(frozen=True)
class MetricSuite:
    """Immutable collection of physical stimulus metrics."""

    artifact_type: str
    records: tuple[MetricRecord, ...]
    computation_version: str = COMPUTATION_VERSION

    def __post_init__(self) -> None:
        if self.artifact_type not in {"image", "audio", "video", "audiovisual"} or not self.records:
            raise ValueError("metric suite requires an artifact type and records")
        if not all(isinstance(record, MetricRecord) for record in self.records):
            raise ValueError("metric suite records must be MetricRecord objects")
        if len({record.name for record in self.records}) != len(self.records):
            raise ValueError("metric names must be unique")
        if not isinstance(self.computation_version, str) or not self.computation_version.strip():
            raise ValueError("metric computation version is required")
        object.__setattr__(self, "records", tuple(self.records))

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


def _suite(artifact_type: str, values: Mapping[str, MetricValue], units: Mapping[str, str], *, scope: str) -> MetricSuite:
    missing_units = sorted(set(values) - set(units))
    if missing_units:
        raise ValueError(f"metrics missing units: {missing_units}")
    provenance = {
        "color_space": "uncalibrated_normalized_channel_values" if artifact_type in {"image", "video", "audiovisual"} else "not_applicable",
        "transfer_function": "none_applied; not_display_calibrated" if artifact_type in {"image", "video", "audiovisual"} else "not_applicable",
        "window": scope,
        "algorithm": COMPUTATION_VERSION,
        "source_sha256": _SOURCE_SHA256,
        "numpy_version": np.__version__,
        "implementation_sources": "metrics.py; artifacts.py",
        "temporal_reduction": "C_contiguous_float32_absolute_difference_mean" if artifact_type in {"video", "audiovisual"} else "not_applicable",
        "channel_rule": "Rec.709_coefficients_on_RGB_values; grayscale_identity" if artifact_type == "image" else "mean_channel_magnitude_rFFT; all_channel_RMS_peak" if artifact_type == "audio" else "video=all_channels_adjacent_frame_absolute_difference; audio=all_channel_RMS" if artifact_type == "audiovisual" else "all_channels_adjacent_frame_absolute_difference",
        "spectral_window": "rectangular; no_detrending; rFFT_including_DC_and_Nyquist_when_present" if artifact_type == "audio" else "not_applicable",
    }
    records = tuple(MetricRecord(name, value, units[name], provenance=provenance) for name, value in values.items())
    return MetricSuite(artifact_type, records)


def _relative_luminance(pixels: np.ndarray) -> np.ndarray:
    """Return a Rec. 709-weighted channel proxy, not calibrated luminance."""
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
            scope=f"full_image; shape={values.shape}; grayscale_identity_or_RGB_weighted_proxy",
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
        rms = artifact.rms
        return _suite(
            "audio",
            {
                "samples": artifact.sample_count,
                "channels": artifact.channels,
                "sample_rate": artifact.sample_rate.value,
                "duration_seconds": artifact.duration_seconds,
                "peak": peak,
                "rms": rms,
                "spectral_centroid_hz": spectral_centroid,
                "dominant_frequency_hz": dominant_frequency,
                "spectral_bandwidth_hz": spectral_bandwidth,
                "crest_factor": peak / max(rms, 1e-12),
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
            scope=f"full_audio; samples=[0,{artifact.sample_count}); channels={artifact.channels}; sample_rate_hz={artifact.sample_rate.value}",
        )
    if isinstance(artifact, VideoSequence):
        deltas = artifact.temporal_deltas
        return _suite(
            "video",
            {
                "width": artifact.width,
                "height": artifact.height,
                "frames": artifact.frame_count,
                "frame_rate": artifact.frame_rate.value,
                "duration_seconds": artifact.duration_seconds,
                "mean_temporal_delta": float(np.mean(deltas)) if deltas else 0.0,
                "temporal_deltas": deltas,
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
            scope=f"all_adjacent_frames; frames={artifact.frame_count}; frame_rate_hz={artifact.frame_rate.value}; shape={artifact.frames[0].pixels.shape}",
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
            scope=f"full_audiovisual; audio_samples={artifact.audio.sample_count}; sample_rate_hz={artifact.audio.sample_rate.value}; video_frames={artifact.video.frame_count}; frame_rate_hz={artifact.video.frame_rate.value}; audio_start_s={artifact.audio_start_seconds}; video_start_s={artifact.video_start_seconds}",
        )
    raise TypeError(f"unsupported artifact type: {type(artifact).__name__}")


__all__ = ["MetricRecord", "MetricSuite", "StimulusMetrics", "measure_artifact"]
