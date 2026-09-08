"""Deterministic synthetic-psychophysics diagnostics.

This module is deliberately not a human-observer model.  It implements a
small, inspectable feature observer whose preprocessing, weights, temperature,
seed, and lack of training data are serialized with every prediction.  The
outputs are useful for testing orchestration, stimulus sensitivity, and
analysis plumbing; they are never evidence about human perception.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np

from .artifacts import AudioBuffer, AudiovisualTimeline, CanonicalArtifact, ImageFrame, VideoSequence
from .canonical import canonical_digest
from .errors import ParameterValidationError
from .metrics import measure_artifact
from .taxonomy import ClaimLevel


_FEATURES = {
    "mean_luminance",
    "std_luminance",
    "edge_energy",
    "dynamic_range",
    "quantization_fraction",
    "rms",
    "peak",
    "spectral_centroid_fraction",
    "spectral_bandwidth_fraction",
    "crest_factor_fraction",
    "temporal_delta",
    "frame_rate_fraction",
    "sync_offset_fraction",
    "spatial_offset_fraction",
}


def _finite(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(float(value)):
        raise ParameterValidationError(f"synthetic feature {name} must be finite")
    return float(value)


def _clip(value: float) -> float:
    return min(1.0, max(0.0, value))


@dataclass(frozen=True)
class SyntheticModelSpec:
    """Fully specified, non-human feature observer."""

    model_id: str
    version: str
    feature_weights: Mapping[str, float]
    temperature: float = 0.05
    seed: int = 0
    training_data: str = "none"
    calibration: str = "analytic logistic calibration; no human or pretrained-model fit"
    human_validation: str = "not performed"
    claim_level: ClaimLevel = ClaimLevel.SYNTHETIC_MODEL_OUTPUT

    def __post_init__(self) -> None:
        if not isinstance(self.model_id, str) or not self.model_id.strip() or not isinstance(self.version, str) or not self.version.strip():
            raise ParameterValidationError("synthetic model identity is required")
        if not isinstance(self.feature_weights, Mapping) or not self.feature_weights:
            raise ParameterValidationError("synthetic model feature_weights are required")
        if any(not isinstance(name, str) or not name for name in self.feature_weights):
            raise ParameterValidationError("synthetic model feature names must be strings")
        if any(name not in _FEATURES for name in self.feature_weights):
            raise ParameterValidationError("synthetic model contains an unknown feature")
        try:
            for weight in self.feature_weights.values():
                _finite(weight, "weight")
        except (TypeError, ValueError, ParameterValidationError) as exc:
            raise ParameterValidationError("synthetic model weights must be finite") from exc
        if not isinstance(self.temperature, Real) or not math.isfinite(float(self.temperature)) or self.temperature <= 0:
            raise ParameterValidationError("synthetic model temperature must be positive and finite")
        if type(self.seed) is not int or self.seed < 0:
            raise ParameterValidationError("synthetic model seed must be a non-negative integer")
        for name in ("training_data", "calibration", "human_validation"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ParameterValidationError(f"synthetic model {name} is required")
        if self.claim_level is not ClaimLevel.SYNTHETIC_MODEL_OUTPUT:
            raise ParameterValidationError("synthetic model outputs require synthetic_model_output claim level")
        object.__setattr__(self, "feature_weights", MappingProxyType(dict(self.feature_weights)))

    def to_dict(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "version": self.version,
            "feature_weights": dict(sorted(self.feature_weights.items())),
            "temperature": self.temperature,
            "seed": self.seed,
            "training_data": self.training_data,
            "calibration": self.calibration,
            "human_validation": self.human_validation,
            "claim_level": self.claim_level.value,
            "epistemic_status": "model_output_not_human_data",
        }


@dataclass(frozen=True)
class SyntheticPrediction:
    """One deterministic pairwise model prediction."""

    trial_id: str
    condition_id: str
    reference_digest: str
    comparison_digest: str
    score_reference: float
    score_comparison: float
    probability_comparison: float
    choice: str
    model_id: str
    feature_schema: tuple[str, ...]
    seed: int
    claim_level: ClaimLevel = ClaimLevel.SYNTHETIC_MODEL_OUTPUT
    human_data: bool = False

    def __post_init__(self) -> None:
        if not self.trial_id or not self.condition_id or not self.model_id:
            raise ParameterValidationError("synthetic prediction identity is required")
        for name in ("reference_digest", "comparison_digest"):
            value = getattr(self, name)
            if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise ParameterValidationError(f"synthetic prediction {name} must be lowercase SHA-256")
        for name in ("score_reference", "score_comparison", "probability_comparison"):
            _finite(getattr(self, name), name)
        if not 0 <= self.probability_comparison <= 1:
            raise ParameterValidationError("synthetic prediction probability must be in [0, 1]")
        if self.choice not in {"reference", "comparison"}:
            raise ParameterValidationError("synthetic prediction choice must be reference or comparison")
        if not self.feature_schema or not all(name in _FEATURES for name in self.feature_schema):
            raise ParameterValidationError("synthetic prediction feature schema is invalid")
        if type(self.seed) is not int or self.seed < 0:
            raise ParameterValidationError("synthetic prediction seed must be non-negative")
        if self.claim_level is not ClaimLevel.SYNTHETIC_MODEL_OUTPUT or self.human_data is not False:
            raise ParameterValidationError("synthetic predictions cannot be human observer claims")

    def to_dict(self) -> dict[str, object]:
        return {
            "trial_id": self.trial_id,
            "condition_id": self.condition_id,
            "reference_digest": self.reference_digest,
            "comparison_digest": self.comparison_digest,
            "score_reference": self.score_reference,
            "score_comparison": self.score_comparison,
            "score_delta": self.score_comparison - self.score_reference,
            "probability_comparison": self.probability_comparison,
            "choice": self.choice,
            "model_id": self.model_id,
            "feature_schema": list(self.feature_schema),
            "seed": self.seed,
            "claim_level": self.claim_level.value,
            "human_data": self.human_data,
        }


@dataclass(frozen=True)
class SyntheticCurvePoint:
    """One x-position in a synthetic model sensitivity curve."""

    x_label: str
    x_value: float
    prediction: SyntheticPrediction

    def __post_init__(self) -> None:
        if not isinstance(self.x_label, str) or not self.x_label.strip() or not isinstance(self.x_value, Real) or not math.isfinite(float(self.x_value)):
            raise ParameterValidationError("synthetic curve point x value is invalid")

    def to_dict(self) -> dict[str, object]:
        return {"x_label": self.x_label, "x_value": self.x_value, "prediction": self.prediction.to_dict()}


def default_synthetic_model() -> SyntheticModelSpec:
    """Return the transparent feature observer used by publication figures."""
    return SyntheticModelSpec(
        model_id="duckrabbit.synthetic.feature_observer",
        version="1.0",
        feature_weights={
            "mean_luminance": 0.10,
            "std_luminance": 0.25,
            "edge_energy": 0.30,
            "dynamic_range": 0.20,
            "quantization_fraction": 0.15,
            "rms": 0.25,
            "peak": 0.15,
            "spectral_centroid_fraction": 0.25,
            "spectral_bandwidth_fraction": 0.20,
            "crest_factor_fraction": 0.15,
            "temporal_delta": 0.40,
            "frame_rate_fraction": 0.15,
            "sync_offset_fraction": 0.25,
            "spatial_offset_fraction": 0.20,
        },
    )


def extract_features(artifact: CanonicalArtifact) -> dict[str, float]:
    """Extract bounded, observer-independent features from a canonical artifact."""
    metrics = measure_artifact(artifact).values
    features: dict[str, float] = {}
    if isinstance(artifact, ImageFrame):
        pixels = artifact.pixels
        gradients = []
        if pixels.shape[0] > 1:
            gradients.append(np.abs(np.diff(pixels, axis=0)).mean())
        if pixels.shape[1] > 1:
            gradients.append(np.abs(np.diff(pixels, axis=1)).mean())
        features.update(
            mean_luminance=_clip(_finite(metrics["mean_luminance"], "mean_luminance")),
            std_luminance=_clip(_finite(metrics["std_luminance"], "std_luminance")),
            edge_energy=_clip(float(np.mean(gradients)) if gradients else 0.0),
            dynamic_range=_clip(_finite(metrics["effective_dynamic_range"], "dynamic_range")),
            quantization_fraction=_clip(float(metrics["unique_values"]) / 256.0),
        )
    elif isinstance(artifact, AudioBuffer):
        features.update(
            rms=_clip(_finite(metrics["rms"], "rms")),
            peak=_clip(_finite(metrics["peak"], "peak")),
            spectral_centroid_fraction=_clip(float(metrics["spectral_centroid_hz"]) / max(float(metrics["sample_rate"]) / 2.0, 1.0)),
            spectral_bandwidth_fraction=_clip(float(metrics["spectral_bandwidth_hz"]) / max(float(metrics["sample_rate"]) / 2.0, 1.0)),
            crest_factor_fraction=_clip(float(metrics["crest_factor"]) / 20.0),
        )
    elif isinstance(artifact, VideoSequence):
        features.update(
            temporal_delta=_clip(_finite(metrics["mean_temporal_delta"], "temporal_delta")),
            frame_rate_fraction=_clip(float(metrics["frame_rate"]) / 240.0),
        )
    elif isinstance(artifact, AudiovisualTimeline):
        features.update(
            sync_offset_fraction=_clip(abs(float(metrics["sync_offset_ms"])) / 10000.0),
            spatial_offset_fraction=_clip(abs(float(metrics["spatial_offset"]))),
            temporal_delta=_clip(float(metrics["video_mean_temporal_delta"])),
            rms=_clip(float(metrics["audio_rms"])),
        )
    else:
        raise TypeError(f"unsupported synthetic artifact type: {type(artifact).__name__}")
    return dict(sorted(features.items()))


def _score(model: SyntheticModelSpec, features: Mapping[str, float]) -> float:
    unknown = set(features) - set(model.feature_weights)
    if unknown:
        raise ParameterValidationError(f"synthetic model does not declare features: {sorted(unknown)}")
    return sum(float(model.feature_weights[name]) * _finite(features[name], name) for name in features)


def _predict_from_features(
    model: SyntheticModelSpec,
    reference_features: tuple[str, ...],
    reference_digest: str,
    comparison: CanonicalArtifact,
    *,
    trial_id: str,
    condition_id: str,
    seed: int,
) -> SyntheticPrediction:
    """Score one comparison against precomputed reference state."""
    comparison_features = extract_features(comparison)
    if set(reference_features) != set(comparison_features):
        raise ParameterValidationError("synthetic pair must have the same feature schema")
    score_reference = _score(model, reference_features)
    score_comparison = _score(model, comparison_features)
    delta = (score_comparison - score_reference) / model.temperature
    probability = 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, delta))))
    return SyntheticPrediction(
        trial_id,
        condition_id,
        reference_digest,
        canonical_digest(comparison),
        score_reference,
        score_comparison,
        probability,
        "comparison" if probability >= 0.5 else "reference",
        model.model_id,
        tuple(reference_features),
        seed,
    )


def predict_pair(
    model: SyntheticModelSpec,
    reference: CanonicalArtifact,
    comparison: CanonicalArtifact,
    *,
    trial_id: str,
    condition_id: str,
    seed: int | None = None,
) -> SyntheticPrediction:
    """Compare two artifacts with an explicit deterministic logistic rule."""
    if not isinstance(model, SyntheticModelSpec):
        raise ParameterValidationError("predict_pair requires SyntheticModelSpec")
    return _predict_from_features(
        model,
        extract_features(reference),
        canonical_digest(reference),
        comparison,
        trial_id=trial_id,
        condition_id=condition_id,
        seed=model.seed if seed is None else seed,
    )


def sensitivity_curve(
    model: SyntheticModelSpec,
    reference: CanonicalArtifact,
    comparisons: Sequence[tuple[str, float, CanonicalArtifact]],
    *,
    condition_id: str = "synthetic_sweep",
) -> tuple[SyntheticCurvePoint, ...]:
    """Generate a deterministic model-output curve over named stimuli."""
    if not comparisons:
        raise ParameterValidationError("synthetic sensitivity curve requires comparisons")
    reference_features = extract_features(reference)
    reference_digest = canonical_digest(reference)
    return tuple(
        SyntheticCurvePoint(
            label,
            x_value,
            _predict_from_features(
                model,
                reference_features,
                reference_digest,
                artifact,
                trial_id=f"{condition_id}:{index}",
                condition_id=condition_id,
                seed=model.seed,
            ),
        )
        for index, (label, x_value, artifact) in enumerate(comparisons)
    )


def summarize_curve(points: Sequence[SyntheticCurvePoint]) -> dict[str, object]:
    """Return a bounded summary with no human-data or effect-size interpretation."""
    if not points:
        raise ParameterValidationError("synthetic curve summary requires points")
    probabilities = [point.prediction.probability_comparison for point in points]
    return {
        "model_id": points[0].prediction.model_id,
        "point_count": len(points),
        "probability_min": min(probabilities),
        "probability_max": max(probabilities),
        "probability_mean": sum(probabilities) / len(probabilities),
        "claim_level": ClaimLevel.SYNTHETIC_MODEL_OUTPUT.value,
        "human_data": False,
        "epistemic_status": "model_output_not_human_data",
        "evaluation_boundary": "A deterministic feature observer is a diagnostic; it is not a pretrained vision model and not a human psychophysics result.",
    }


@dataclass(frozen=True)
class SyntheticDiagnostic:
    """Typed end-to-end output for the default model-only demonstration."""

    model: SyntheticModelSpec
    reference_label: str
    reference_digest: str
    points: tuple[SyntheticCurvePoint, ...]
    summary: Mapping[str, object]

    def __post_init__(self) -> None:
        if not isinstance(self.reference_label, str) or not self.reference_label.strip():
            raise ParameterValidationError("synthetic diagnostic reference label is required")
        if not isinstance(self.reference_digest, str) or len(self.reference_digest) != 64 or any(char not in "0123456789abcdef" for char in self.reference_digest):
            raise ParameterValidationError("synthetic diagnostic reference digest must be lowercase SHA-256")
        if not self.points:
            raise ParameterValidationError("synthetic diagnostic requires curve points")
        if not isinstance(self.summary, Mapping) or self.summary.get("claim_level") != ClaimLevel.SYNTHETIC_MODEL_OUTPUT.value or self.summary.get("human_data") is not False:
            raise ParameterValidationError("synthetic diagnostic summary must preserve its epistemic boundary")
        object.__setattr__(self, "points", tuple(self.points))
        object.__setattr__(self, "summary", MappingProxyType(dict(self.summary)))

    def to_dict(self) -> dict[str, object]:
        return {
            "model": self.model.to_dict(),
            "reference": {"label": self.reference_label, "canonical_digest": self.reference_digest},
            "points": [point.to_dict() for point in self.points],
            "summary": dict(self.summary),
        }


def default_duck_rabbit_diagnostic() -> SyntheticDiagnostic:
    """Build the publication/CLI diagnostic without importing generators at module load."""
    from dataclasses import replace

    from .generators import DuckRabbitParams, default_parameters, default_registry

    base = default_parameters("visual.duck_rabbit")
    if not isinstance(base, DuckRabbitParams):
        raise ParameterValidationError("duck-rabbit defaults have the wrong parameter type")
    reference_weight = 0.5
    reference = default_registry.generate(
        "visual.duck_rabbit", replace(base, duck_weight=type(base.duck_weight)(reference_weight))
    )
    comparisons = tuple(
        (
            f"{weight:.2f}",
            weight,
            default_registry.generate("visual.duck_rabbit", replace(base, duck_weight=type(base.duck_weight)(weight))),
        )
        for weight in (0.0, 0.25, 0.5, 0.75, 1.0)
    )
    model = default_synthetic_model()
    points = sensitivity_curve(model, reference, comparisons, condition_id="duck_weight")
    return SyntheticDiagnostic(model, "duck_weight=0.50", canonical_digest(reference), points, summarize_curve(points))


__all__ = [
    "SyntheticCurvePoint",
    "SyntheticDiagnostic",
    "SyntheticModelSpec",
    "SyntheticPrediction",
    "default_synthetic_model",
    "default_duck_rabbit_diagnostic",
    "extract_features",
    "predict_pair",
    "sensitivity_curve",
    "summarize_curve",
]
