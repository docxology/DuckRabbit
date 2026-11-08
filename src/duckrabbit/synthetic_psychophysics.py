"""Deterministic synthetic-psychophysics diagnostics.

This module is deliberately not a human-observer model.  It implements a
small, inspectable feature observer whose preprocessing, weights, temperature,
seed, and lack of training data are serialized with every prediction.  The
outputs are useful for testing orchestration, stimulus sensitivity, and
analysis plumbing; they are never evidence about human perception.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
import hashlib
import json
import math
from numbers import Real
from types import MappingProxyType

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
        if isinstance(self.temperature, bool) or not isinstance(self.temperature, Real) or not math.isfinite(float(self.temperature)) or self.temperature <= 0:
            raise ParameterValidationError("synthetic model temperature must be positive and finite")
        if type(self.seed) is not int or self.seed < 0:
            raise ParameterValidationError("synthetic model seed must be a non-negative integer")
        for name in ("training_data", "calibration", "human_validation"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ParameterValidationError(f"synthetic model {name} is required")
        if self.claim_level is not ClaimLevel.SYNTHETIC_MODEL_OUTPUT:
            raise ParameterValidationError("synthetic model outputs require synthetic_model_output claim level")
        object.__setattr__(self, "feature_weights", MappingProxyType({name: float(weight) for name, weight in self.feature_weights.items()}))
        object.__setattr__(self, "temperature", float(self.temperature))

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
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
            "human_data": False,
            "computation_version": "duckrabbit.synthetic.feature_observer/v1",
            "feature_extraction": "duckrabbit.synthetic_psychophysics.extract_features/v1",
            "probability_rule": "clipped_logistic_score_difference_over_temperature",
            "logit_clip": [-60.0, 60.0],
            "tie_choice": "comparison",
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        payload["model_spec_digest"] = hashlib.sha256(encoded).hexdigest()
        return payload


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
        if any(not isinstance(value, str) or not value.strip() for value in (self.trial_id, self.condition_id, self.model_id)):
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
        if not self.feature_schema or any(not isinstance(name, str) or name not in _FEATURES for name in self.feature_schema) or len(set(self.feature_schema)) != len(self.feature_schema):
            raise ParameterValidationError("synthetic prediction feature schema is invalid")
        if type(self.seed) is not int or self.seed < 0:
            raise ParameterValidationError("synthetic prediction seed must be non-negative")
        if self.claim_level is not ClaimLevel.SYNTHETIC_MODEL_OUTPUT or self.human_data is not False:
            raise ParameterValidationError("synthetic predictions cannot be human observer claims")
        if self.choice != ("comparison" if self.probability_comparison >= 0.5 else "reference"):
            raise ParameterValidationError("synthetic prediction choice disagrees with probability")
        if self.reference_digest == self.comparison_digest and self.score_reference != self.score_comparison:
            raise ParameterValidationError("synthetic prediction identical digests require identical scores")
        if self.score_reference == self.score_comparison and self.probability_comparison != 0.5:
            raise ParameterValidationError("synthetic prediction equal scores require probability 0.5")
        object.__setattr__(self, "feature_schema", tuple(self.feature_schema))

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
        if not isinstance(self.prediction, SyntheticPrediction):
            raise ParameterValidationError("synthetic curve point requires SyntheticPrediction")

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
    reference_features: Mapping[str, float],
    reference_digest: str,
    comparison_features: Mapping[str, float],
    comparison_digest: str,
    *,
    trial_id: str,
    condition_id: str,
    seed: int,
) -> SyntheticPrediction:
    """Score precomputed features and digests without regenerating stimuli."""
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
        comparison_digest,
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
        extract_features(comparison),
        canonical_digest(comparison),
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
    if not isinstance(model, SyntheticModelSpec):
        raise ParameterValidationError("sensitivity_curve requires SyntheticModelSpec")
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
                extract_features(artifact),
                canonical_digest(artifact),
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


def _variant_specs(model: SyntheticModelSpec) -> tuple[tuple[str, str | None, float | None, SyntheticModelSpec], ...]:
    """Declared one-at-a-time analyst choices, not fitted uncertainty intervals."""
    variants: list[tuple[str, str | None, float | None, SyntheticModelSpec]] = [
        ("feature_ablation", name, None, replace(
            model, model_id=f"{model.model_id}:without:{name}",
            feature_weights={key: 0.0 if key == name else value for key, value in model.feature_weights.items()},
        ))
        for name in sorted(model.feature_weights)
    ]
    variants.append(("null_weights", None, None, replace(
        model, model_id=f"{model.model_id}:null", feature_weights=dict.fromkeys(model.feature_weights, 0.0),
    )))
    variants.extend(
        ("temperature", None, factor, replace(
            model, model_id=f"{model.model_id}:temperature:{factor:g}", temperature=model.temperature * factor,
        ))
        for factor in (0.5, 1.0, 2.0)
    )
    return tuple(variants)


@dataclass(frozen=True)
class _DiagnosticVariant:
    model: SyntheticModelSpec
    kind: str
    points: tuple[SyntheticCurvePoint, ...]
    ablated_feature: str | None = None
    temperature_factor: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "points", tuple(self.points))

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "ablated_feature": self.ablated_feature,
            "temperature_factor": self.temperature_factor,
            "model": self.model.to_dict(),
            "points": [point.to_dict() for point in self.points],
            "summary": summarize_curve(self.points),
        }


def _validate_curve(model: SyntheticModelSpec, reference_digest: str, points: Sequence[SyntheticCurvePoint]) -> None:
    """Check relationships that do not require regenerating canonical artifacts."""
    if not isinstance(points, Sequence) or not points or any(not isinstance(point, SyntheticCurvePoint) for point in points):
        raise ParameterValidationError("synthetic diagnostic requires curve points")
    first = points[0].prediction
    seen_trials: set[str] = set()
    scores_by_digest = {reference_digest: first.score_reference}
    for point in points:
        prediction = point.prediction
        if prediction.model_id != model.model_id or prediction.seed != model.seed:
            raise ParameterValidationError("synthetic diagnostic model identity or seed disagrees with prediction")
        if prediction.reference_digest != reference_digest:
            raise ParameterValidationError("synthetic diagnostic reference digest disagrees with prediction")
        if prediction.feature_schema != first.feature_schema or not set(prediction.feature_schema) <= set(model.feature_weights):
            raise ParameterValidationError("synthetic diagnostic feature schema disagrees with model or curve")
        if prediction.trial_id in seen_trials or prediction.condition_id != first.condition_id:
            raise ParameterValidationError("synthetic diagnostic trial or condition identity is inconsistent")
        seen_trials.add(prediction.trial_id)
        delta = (prediction.score_comparison - prediction.score_reference) / model.temperature
        expected = 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, delta))))
        if prediction.probability_comparison != expected or prediction.score_reference != first.score_reference:
            raise ParameterValidationError("synthetic diagnostic scores or probability disagree with model")
        previous = scores_by_digest.setdefault(prediction.comparison_digest, prediction.score_comparison)
        if previous != prediction.score_comparison:
            raise ParameterValidationError("synthetic diagnostic scores disagree for identical digests")


def _freeze_features(features: Mapping[str, float], schema: tuple[str, ...]) -> Mapping[str, float]:
    if not isinstance(features, Mapping) or tuple(features) != schema:
        raise ParameterValidationError("synthetic diagnostic extracted feature schema is inconsistent")
    values = {name: _finite(value, name) for name, value in features.items()}
    if any(not 0.0 <= value <= 1.0 for value in values.values()):
        raise ParameterValidationError("synthetic diagnostic extracted features must be in [0, 1]")
    return MappingProxyType(values)


@dataclass(frozen=True)
class SyntheticDiagnostic:
    """Model-only curve, controls and declared model-sensitivity configurations.

    Optional provenance and variants retain the original five-argument API.
    Extracted features permit internal score checks, not independent certification
    of canonical pixels: that still requires the digest-bound source artifacts.
    """

    model: SyntheticModelSpec
    reference_label: str
    reference_digest: str
    points: tuple[SyntheticCurvePoint, ...]
    summary: Mapping[str, object]
    variants: tuple[_DiagnosticVariant, ...] = ()
    zero_difference_control: SyntheticPrediction | None = None
    reference_features: Mapping[str, float] = field(default_factory=dict)
    comparison_features: tuple[Mapping[str, float], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.model, SyntheticModelSpec):
            raise ParameterValidationError("synthetic diagnostic requires SyntheticModelSpec")
        if not isinstance(self.reference_label, str) or not self.reference_label.strip():
            raise ParameterValidationError("synthetic diagnostic reference label is required")
        if not isinstance(self.reference_digest, str) or len(self.reference_digest) != 64 or any(char not in "0123456789abcdef" for char in self.reference_digest):
            raise ParameterValidationError("synthetic diagnostic reference digest must be lowercase SHA-256")
        _validate_curve(self.model, self.reference_digest, self.points)
        expected_summary = summarize_curve(self.points)
        if not isinstance(self.summary, Mapping) or any(
            type(self.summary.get(name)) is not type(value) or self.summary[name] != value
            for name, value in expected_summary.items()
        ):
            raise ParameterValidationError("synthetic diagnostic summary disagrees with curve or epistemic boundary")
        object.__setattr__(self, "points", tuple(self.points))
        object.__setattr__(self, "summary", MappingProxyType(dict(self.summary)))
        if not isinstance(self.variants, Sequence):
            raise ParameterValidationError("synthetic diagnostic variants must be a sequence")
        if not isinstance(self.reference_features, Mapping) or not isinstance(self.comparison_features, Sequence):
            raise ParameterValidationError("synthetic diagnostic extracted features have invalid containers")
        object.__setattr__(self, "variants", tuple(self.variants))
        schema = self.points[0].prediction.feature_schema
        if self.reference_features or self.comparison_features:
            reference_features = _freeze_features(self.reference_features, schema)
            if len(self.comparison_features) != len(self.points):
                raise ParameterValidationError("synthetic diagnostic extracted features do not match point count")
            comparison_features = tuple(_freeze_features(features, schema) for features in self.comparison_features)
            object.__setattr__(self, "reference_features", reference_features)
            object.__setattr__(self, "comparison_features", comparison_features)
            features_by_digest = {self.reference_digest: reference_features}
            for point, features in zip(self.points, comparison_features, strict=True):
                previous = features_by_digest.setdefault(point.prediction.comparison_digest, features)
                if previous != features:
                    raise ParameterValidationError("synthetic diagnostic extracted features disagree for identical digests")
            self._validate_feature_scores(self.model, self.points)
        else:
            object.__setattr__(self, "reference_features", MappingProxyType({}))
            object.__setattr__(self, "comparison_features", ())
        if self.zero_difference_control is not None:
            control = self.zero_difference_control
            _validate_curve(self.model, self.reference_digest, (SyntheticCurvePoint("zero_difference", 0.0, control),))
            if (control.comparison_digest != self.reference_digest or control.probability_comparison != 0.5
                    or control.feature_schema != schema or control.score_reference != self.points[0].prediction.score_reference):
                raise ParameterValidationError("synthetic diagnostic zero-difference control is inconsistent")
        if self.variants:
            if not self.reference_features or self.zero_difference_control is None:
                raise ParameterValidationError("synthetic diagnostic variants require extracted features and zero-difference control")
            expected_variants = _variant_specs(self.model)
            if len(self.variants) != len(expected_variants):
                raise ParameterValidationError("synthetic diagnostic variant configurations are incomplete")
            for variant, (kind, feature, factor, model) in zip(self.variants, expected_variants, strict=True):
                if not isinstance(variant, _DiagnosticVariant) or (variant.kind, variant.ablated_feature, variant.temperature_factor, variant.model) != (kind, feature, factor, model):
                    raise ParameterValidationError("synthetic diagnostic variant specification is inconsistent")
                _validate_curve(model, self.reference_digest, variant.points)
                if len(variant.points) != len(self.points):
                    raise ParameterValidationError("synthetic diagnostic variant point count is inconsistent")
                for baseline, varied in zip(self.points, variant.points, strict=True):
                    if (varied.x_label, varied.x_value, varied.prediction.trial_id, varied.prediction.condition_id,
                            varied.prediction.comparison_digest) != (baseline.x_label, baseline.x_value,
                            baseline.prediction.trial_id, baseline.prediction.condition_id, baseline.prediction.comparison_digest):
                        raise ParameterValidationError("synthetic diagnostic variant stimulus identity is inconsistent")
                self._validate_feature_scores(model, variant.points)

    def _validate_feature_scores(self, model: SyntheticModelSpec, points: Sequence[SyntheticCurvePoint]) -> None:
        for point, features in zip(points, self.comparison_features, strict=True):
            prediction = point.prediction
            expected = _predict_from_features(
                model, self.reference_features, self.reference_digest, features, prediction.comparison_digest,
                trial_id=prediction.trial_id, condition_id=prediction.condition_id, seed=model.seed,
            )
            if prediction != expected:
                raise ParameterValidationError("synthetic diagnostic prediction disagrees with extracted features")

    def to_dict(self) -> dict[str, object]:
        configurations = ((self.model.model_id, self.points),) + tuple((variant.model.model_id, variant.points) for variant in self.variants)
        bounds = []
        for index, point in enumerate(self.points):
            probabilities = [points[index].prediction.probability_comparison for _, points in configurations]
            bounds.append({
                "x_label": point.x_label, "x_value": point.x_value,
                "probability_min": min(probabilities), "probability_max": max(probabilities),
                "probability_spread": max(probabilities) - min(probabilities),
            })
        return {
            "model": self.model.to_dict(),
            "reference": {"label": self.reference_label, "canonical_digest": self.reference_digest},
            "points": [point.to_dict() for point in self.points],
            "summary": dict(self.summary),
            "variants": [variant.to_dict() for variant in self.variants],
            "zero_difference_control": None if self.zero_difference_control is None else self.zero_difference_control.to_dict(),
            "extracted_features": {
                "reference": dict(self.reference_features),
                "comparisons": [dict(features) for features in self.comparison_features],
            },
            "uncertainty": {
                "kind": "model_sensitivity", "human_data": False,
                "configuration_ids": [model_id for model_id, _ in configurations],
                "configuration_count": len(configurations), "points": bounds,
                "temperature_factors": [variant.temperature_factor for variant in self.variants if variant.kind == "temperature"],
                "interpretation": "Min/max spread over declared analyst-chosen configurations, not confidence intervals or empirical uncertainty.",
                "empirical_uncertainty": "not_estimated_no_observer_data",
            },
        }


def default_duck_rabbit_diagnostic() -> SyntheticDiagnostic:
    """Build controls and sensitivity using one feature extraction per stimulus.

    Every weight is ablated in turn (zeroed, never removed), including weights
    inactive for this image schema. The null model zeros all weights. The
    temperature multipliers 0.5/1/2 are declared analyst choices, not a fit.
    """
    from .generators import DuckRabbitParams, default_parameters, default_registry

    base = default_parameters("visual.duck_rabbit")
    if not isinstance(base, DuckRabbitParams):
        raise ParameterValidationError("duck-rabbit defaults have the wrong parameter type")
    reference_weight = 0.5
    reference = default_registry.generate(
        "visual.duck_rabbit", replace(base, duck_weight=type(base.duck_weight)(reference_weight))
    )
    reference_digest = canonical_digest(reference)
    reference_features = extract_features(reference)
    comparisons = []
    for weight in (0.0, 0.25, 0.5, 0.75, 1.0):
        if weight == reference_weight:
            digest, features = reference_digest, reference_features
        else:
            artifact = default_registry.generate("visual.duck_rabbit", replace(base, duck_weight=type(base.duck_weight)(weight)))
            digest, features = canonical_digest(artifact), extract_features(artifact)
        comparisons.append((f"{weight:.2f}", weight, digest, features))

    def curve(model: SyntheticModelSpec) -> tuple[SyntheticCurvePoint, ...]:
        return tuple(
            SyntheticCurvePoint(label, weight, _predict_from_features(
                model, reference_features, reference_digest, features, digest,
                trial_id=f"duck_weight:{index}", condition_id="duck_weight", seed=model.seed,
            ))
            for index, (label, weight, digest, features) in enumerate(comparisons)
        )

    model = default_synthetic_model()
    points = curve(model)
    variants = tuple(
        _DiagnosticVariant(spec, kind, curve(spec), feature, factor)
        for kind, feature, factor, spec in _variant_specs(model)
    )
    control = _predict_from_features(
        model, reference_features, reference_digest, reference_features, reference_digest,
        trial_id="zero_difference_control", condition_id="zero_difference_control", seed=model.seed,
    )
    return SyntheticDiagnostic(
        model, "duck_weight=0.50", reference_digest, points, summarize_curve(points), variants, control,
        reference_features, tuple(features for _, _, _, features in comparisons),
    )


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
