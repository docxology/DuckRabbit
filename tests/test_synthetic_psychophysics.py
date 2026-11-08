"""No-mock tests for the model-output-only synthetic psychophysics layer."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import fields, replace

import numpy as np
import pytest

import duckrabbit
from duckrabbit.artifacts import ImageFrame
from duckrabbit.canonical import canonical_digest
from duckrabbit.errors import ParameterValidationError
from duckrabbit.synthetic_psychophysics import (
    SyntheticCurvePoint,
    SyntheticDiagnostic,
    SyntheticModelSpec,
    SyntheticPrediction,
    default_duck_rabbit_diagnostic,
    default_synthetic_model,
    extract_features,
    predict_pair,
    sensitivity_curve,
    summarize_curve,
)
from duckrabbit.taxonomy import ClaimLevel


def test_default_diagnostic_is_typed_deterministic_and_explicitly_nonhuman() -> None:
    first = default_duck_rabbit_diagnostic()
    second = default_duck_rabbit_diagnostic()
    assert isinstance(first, SyntheticDiagnostic)
    assert first == second
    assert first.model.to_dict()["epistemic_status"] == "model_output_not_human_data"
    assert first.summary["human_data"] is False
    assert first.summary["claim_level"] == ClaimLevel.SYNTHETIC_MODEL_OUTPUT.value
    assert first.reference_label == "duck_weight=0.50"
    assert len(first.points) == 5
    assert [point.x_value for point in first.points] == [0.0, 0.25, 0.5, 0.75, 1.0]
    payload = first.to_dict()
    assert json.loads(json.dumps(payload))["model"]["training_data"] == "none"


def test_feature_extraction_and_pair_prediction_are_reproducible_for_modalities() -> None:
    model = default_synthetic_model()
    pairs = (
        ("visual.duck_rabbit", "visual.simultaneous_contrast"),
        ("audio.shepard_tone", "audio.missing_fundamental"),
        ("visual.apparent_motion", "visual.apparent_motion"),
        ("audiovisual.sound_induced_flash", "audiovisual.temporal_ventriloquism"),
    )
    for index, (reference_id, comparison_id) in enumerate(pairs):
        reference = duckrabbit.generate(reference_id)
        comparison = duckrabbit.generate(comparison_id)
        reference_features = extract_features(reference)
        comparison_features = extract_features(comparison)
        assert reference_features and comparison_features
        assert all(0.0 <= value <= 1.0 for value in reference_features.values())
        prediction_a = predict_pair(model, reference, comparison, trial_id=f"trial-{index}", condition_id="condition", seed=8)
        prediction_b = predict_pair(model, reference, comparison, trial_id=f"trial-{index}", condition_id="condition", seed=8)
        assert prediction_a == prediction_b
        assert prediction_a.reference_digest == canonical_digest(reference)
        assert prediction_a.comparison_digest == canonical_digest(comparison)
        assert 0.0 <= prediction_a.probability_comparison <= 1.0
        assert prediction_a.claim_level is ClaimLevel.SYNTHETIC_MODEL_OUTPUT
        assert prediction_a.human_data is False


def test_curve_summary_and_immutable_model_contract() -> None:
    model = default_synthetic_model()
    reference = duckrabbit.generate("visual.duck_rabbit")
    comparison = duckrabbit.generate("visual.duck_rabbit")
    points = sensitivity_curve(model, reference, (("same", 0.0, comparison),))
    assert isinstance(points[0], SyntheticCurvePoint)
    assert points[0].prediction.probability_comparison == pytest.approx(0.5)
    summary = summarize_curve(points)
    assert summary["probability_min"] == pytest.approx(0.5)
    with pytest.raises(TypeError):
        model.feature_weights["rms"] = 1.0  # type: ignore[index]
    with pytest.raises(ParameterValidationError, match="comparisons"):
        sensitivity_curve(model, reference, ())
    with pytest.raises(ParameterValidationError, match="points"):
        summarize_curve(())


def test_model_and_prediction_contracts_reject_malformed_values() -> None:
    base = dict(model_id="model", version="1", feature_weights={"rms": 1.0})
    with pytest.raises(ParameterValidationError, match="identity"):
        SyntheticModelSpec("", "1", {"rms": 1.0})
    with pytest.raises(ParameterValidationError, match="identity"):
        SyntheticModelSpec("model", "", {"rms": 1.0})
    with pytest.raises(ParameterValidationError, match="feature_weights"):
        SyntheticModelSpec("model", "1", {})
    with pytest.raises(ParameterValidationError, match="feature names"):
        SyntheticModelSpec("model", "1", {1: 1.0})  # type: ignore[dict-item]
    with pytest.raises(ParameterValidationError, match="unknown feature"):
        SyntheticModelSpec("model", "1", {"unknown": 1.0})
    with pytest.raises(ParameterValidationError, match="finite"):
        SyntheticModelSpec("model", "1", {"rms": float("nan")})
    with pytest.raises(ParameterValidationError, match="temperature"):
        SyntheticModelSpec("model", "1", {"rms": 1.0}, temperature=0.0)
    with pytest.raises(ParameterValidationError, match="seed"):
        SyntheticModelSpec("model", "1", {"rms": 1.0}, seed=-1)
    with pytest.raises(ParameterValidationError, match="training_data"):
        SyntheticModelSpec("model", "1", {"rms": 1.0}, training_data=" ")
    with pytest.raises(ParameterValidationError, match="calibration"):
        SyntheticModelSpec("model", "1", {"rms": 1.0}, calibration=" ")
    with pytest.raises(ParameterValidationError, match="human_validation"):
        SyntheticModelSpec("model", "1", {"rms": 1.0}, human_validation=" ")
    with pytest.raises(ParameterValidationError, match="claim level"):
        SyntheticModelSpec("model", "1", {"rms": 1.0}, claim_level=ClaimLevel.PHYSICAL_METRIC)
    assert base["model_id"] == "model"

    reference = duckrabbit.generate("audio.shepard_tone")
    prediction = predict_pair(default_synthetic_model(), reference, reference, trial_id="trial", condition_id="condition")
    prediction_data = {field.name: getattr(prediction, field.name) for field in fields(SyntheticPrediction)}
    for field in ("reference_digest", "comparison_digest"):
        invalid = dict(prediction_data, **{field: "bad"})
        with pytest.raises(ParameterValidationError, match=field):
            SyntheticPrediction(**invalid)
    with pytest.raises(ParameterValidationError, match="probability"):
        SyntheticPrediction(**{**prediction_data, "probability_comparison": 2.0})
    with pytest.raises(ParameterValidationError, match="choice"):
        SyntheticPrediction(**{**prediction_data, "choice": "uncertain"})
    with pytest.raises(ParameterValidationError, match="schema"):
        SyntheticPrediction(**{**prediction_data, "feature_schema": ("not_a_feature",)})
    with pytest.raises(ParameterValidationError, match="human"):
        SyntheticPrediction(**{**prediction_data, "human_data": True})


def test_prediction_rejects_incompatible_features_and_curve_points() -> None:
    image = duckrabbit.generate("visual.duck_rabbit")
    audio = duckrabbit.generate("audio.shepard_tone")
    with pytest.raises(ParameterValidationError, match="same feature schema"):
        predict_pair(default_synthetic_model(), image, audio, trial_id="trial", condition_id="condition")
    with pytest.raises(ParameterValidationError, match="x value"):
        SyntheticCurvePoint("", float("nan"), predict_pair(default_synthetic_model(), image, image, trial_id="t", condition_id="c"))


@pytest.mark.parametrize("model", [None, {}, "model", 1])
def test_sensitivity_curve_explicitly_rejects_invalid_model(model: object) -> None:
    image = duckrabbit.generate("visual.duck_rabbit")
    with pytest.raises(ParameterValidationError, match="requires SyntheticModelSpec"):
        sensitivity_curve(model, image, (("same", 0.0, image),))


@pytest.mark.parametrize("identity", ["visual.duck_rabbit", "audio.shepard_tone", "visual.apparent_motion", "audiovisual.sound_induced_flash"])
def test_sensitivity_curve_matches_complete_pair_predictions(identity: str) -> None:
    artifact = duckrabbit.generate(identity)
    model = default_synthetic_model()
    comparisons = tuple((str(index), float(index), artifact) for index in range(3))
    points = sensitivity_curve(model, artifact, comparisons, condition_id="condition:curve")
    expected = tuple(
        SyntheticCurvePoint(label, value, predict_pair(
            model, artifact, comparison, trial_id=f"condition:curve:{index}", condition_id="condition:curve",
        ))
        for index, (label, value, comparison) in enumerate(comparisons)
    )
    assert points == expected
    assert [point.to_dict() for point in points] == [point.to_dict() for point in expected]


@pytest.mark.parametrize("invalid", [True, False, None, "0.5", float("nan"), float("inf"), -float("inf")])
def test_prediction_rejects_invalid_numeric_probabilities(invalid: object) -> None:
    image = duckrabbit.generate("visual.duck_rabbit")
    prediction = predict_pair(default_synthetic_model(), image, image, trial_id="trial", condition_id="condition")
    with pytest.raises(ParameterValidationError, match="probability_comparison"):
        replace(prediction, probability_comparison=invalid)


@pytest.fixture(scope="module")
def complete_diagnostic() -> SyntheticDiagnostic:
    return default_duck_rabbit_diagnostic()


def test_default_controls_ablate_weights_not_feature_schema(complete_diagnostic: SyntheticDiagnostic) -> None:
    diagnostic = complete_diagnostic
    control = diagnostic.zero_difference_control
    assert control is not None
    assert control.reference_digest == control.comparison_digest == diagnostic.reference_digest
    assert control.score_reference == control.score_comparison
    assert control.probability_comparison == 0.5
    assert control.human_data is False
    assert diagnostic.points[2].prediction == replace(
        control, trial_id="duck_weight:2", condition_id="duck_weight",
    )
    ablations = [variant for variant in diagnostic.variants if variant.kind == "feature_ablation"]
    assert {variant.ablated_feature for variant in ablations} == set(diagnostic.model.feature_weights)
    for variant in ablations:
        feature = variant.ablated_feature
        assert feature is not None
        assert set(variant.model.feature_weights) == set(diagnostic.model.feature_weights)
        assert variant.model.feature_weights[feature] == 0.0
        assert all(
            weight == diagnostic.model.feature_weights[name]
            for name, weight in variant.model.feature_weights.items() if name != feature
        )
        for baseline, varied, features in zip(diagnostic.points, variant.points, diagnostic.comparison_features, strict=True):
            original, ablated = baseline.prediction, varied.prediction
            assert original.feature_schema == ablated.feature_schema
            contribution = diagnostic.model.feature_weights[feature] * (
                features.get(feature, 0.0) - diagnostic.reference_features.get(feature, 0.0)
            )
            original_delta = original.score_comparison - original.score_reference
            ablated_delta = ablated.score_comparison - ablated.score_reference
            assert original_delta - ablated_delta == pytest.approx(contribution, abs=1e-15)
            if feature not in original.feature_schema:
                assert ablated.probability_comparison == original.probability_comparison
    null, = (variant for variant in diagnostic.variants if variant.kind == "null_weights")
    assert set(null.model.feature_weights) == set(diagnostic.model.feature_weights)
    assert set(null.model.feature_weights.values()) == {0.0}
    assert all(point.prediction.score_reference == point.prediction.score_comparison == 0.0 for point in null.points)
    assert all(point.prediction.probability_comparison == 0.5 for point in null.points)


def test_temperature_variants_move_toward_half(complete_diagnostic: SyntheticDiagnostic) -> None:
    diagnostic = complete_diagnostic
    variants = [variant for variant in diagnostic.variants if variant.kind == "temperature"]
    assert [variant.temperature_factor for variant in variants] == [0.5, 1.0, 2.0]
    for variant in variants:
        assert variant.model.feature_weights == diagnostic.model.feature_weights
        assert variant.model.temperature == diagnostic.model.temperature * variant.temperature_factor
    for index, baseline in enumerate(diagnostic.points):
        predictions = [variant.points[index].prediction for variant in variants]
        distances = [abs(prediction.probability_comparison - 0.5) for prediction in predictions]
        assert distances[0] >= distances[1] >= distances[2]
        assert predictions[1].probability_comparison == baseline.prediction.probability_comparison
        assert all(prediction.score_reference == baseline.prediction.score_reference for prediction in predictions)
        assert all(prediction.score_comparison == baseline.prediction.score_comparison for prediction in predictions)


def test_serialized_sensitivity_bounds_and_complete_model_provenance(complete_diagnostic: SyntheticDiagnostic) -> None:
    payload = complete_diagnostic.to_dict()
    configurations = [payload] + payload["variants"]
    uncertainty = payload["uncertainty"]
    assert uncertainty["kind"] == "model_sensitivity"
    assert uncertainty["empirical_uncertainty"] == "not_estimated_no_observer_data"
    assert uncertainty["human_data"] is False
    assert uncertainty["temperature_factors"] == [0.5, 1.0, 2.0]
    assert uncertainty["configuration_count"] == len(configurations)
    assert uncertainty["configuration_ids"] == [configuration["model"]["model_id"] for configuration in configurations]
    assert len(set(uncertainty["configuration_ids"])) == len(configurations)
    for index, bounds in enumerate(uncertainty["points"]):
        probabilities = [configuration["points"][index]["prediction"]["probability_comparison"] for configuration in configurations]
        assert bounds["probability_min"] == min(probabilities)
        assert bounds["probability_max"] == max(probabilities)
        assert bounds["probability_spread"] == max(probabilities) - min(probabilities)
        assert bounds["x_value"] == payload["points"][index]["x_value"]
    for configuration in configurations:
        model = dict(configuration["model"])
        digest = model.pop("model_spec_digest")
        encoded = json.dumps(model, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        assert digest == hashlib.sha256(encoded).hexdigest()
        assert model["computation_version"]
        assert model["feature_extraction"]
        assert model["logit_clip"] == [-60.0, 60.0]
        assert model["training_data"] == "none"
        assert model["human_data"] is configuration["summary"]["human_data"] is False
        assert all(point["prediction"]["human_data"] is False for point in configuration["points"])
    assert payload["extracted_features"]["reference"] == dict(complete_diagnostic.reference_features)
    assert payload["extracted_features"]["comparisons"] == [dict(features) for features in complete_diagnostic.comparison_features]
    assert json.dumps(payload, sort_keys=True) == json.dumps(default_duck_rabbit_diagnostic().to_dict(), sort_keys=True)
    payload["extracted_features"]["reference"]["edge_energy"] = 99.0
    assert complete_diagnostic.reference_features["edge_energy"] != 99.0
    with pytest.raises(TypeError):
        complete_diagnostic.reference_features["edge_energy"] = 99.0  # type: ignore[index]
    with pytest.raises(TypeError):
        complete_diagnostic.comparison_features[0]["edge_energy"] = 99.0  # type: ignore[index]


def test_pair_swapping_identical_and_null_model_boundaries() -> None:
    reference = ImageFrame(np.full((4, 4), 0.2, dtype=np.float32))
    comparison = ImageFrame(np.full((4, 4), 0.8, dtype=np.float32))
    model = default_synthetic_model()

    def predict(spec: SyntheticModelSpec, first: ImageFrame, second: ImageFrame) -> SyntheticPrediction:
        return predict_pair(spec, first, second, trial_id="pair", condition_id="pair")

    forward = predict(model, reference, comparison)
    backward = predict(model, comparison, reference)
    assert forward.probability_comparison > 0.5
    assert backward.probability_comparison == pytest.approx(1.0 - forward.probability_comparison, abs=1e-15)
    assert backward.score_reference == forward.score_comparison
    assert backward.score_comparison == forward.score_reference
    assert predict(model, reference, reference).probability_comparison == 0.5
    null = replace(model, feature_weights=dict.fromkeys(model.feature_weights, 0.0))
    assert predict(null, reference, comparison).probability_comparison == 0.5
    cold = predict(replace(model, temperature=model.temperature * 0.5), reference, comparison)
    warm = predict(replace(model, temperature=model.temperature * 2.0), reference, comparison)
    assert cold.probability_comparison > forward.probability_comparison > warm.probability_comparison > 0.5
    clipped = predict(replace(model, temperature=1e-9), comparison, reference)
    assert clipped.probability_comparison == 1.0 / (1.0 + math.exp(60.0))
    assert clipped.probability_comparison > 0.0


@pytest.mark.parametrize("invalid", [True, False, None, "0.05", 0.0, -1.0, float("nan"), float("inf")])
def test_model_temperature_rejects_nonpositive_nonfinite_and_bool(invalid: object) -> None:
    with pytest.raises(ParameterValidationError, match="temperature"):
        replace(default_synthetic_model(), temperature=invalid)


def test_model_spec_digest_binds_full_specification() -> None:
    model = default_synthetic_model()
    digest = model.to_dict()["model_spec_digest"]
    changes = (
        {"temperature": model.temperature * 2.0}, {"seed": model.seed + 1},
        {"feature_weights": dict.fromkeys(model.feature_weights, 0.0)},
        {"calibration": "a different explicitly unvalidated analyst choice"},
    )
    assert all(replace(model, **change).to_dict()["model_spec_digest"] != digest for change in changes)
    assert replace(model, feature_weights=dict(reversed(tuple(model.feature_weights.items())))).to_dict()["model_spec_digest"] == digest


def test_original_five_argument_diagnostic_api_remains_available(complete_diagnostic: SyntheticDiagnostic) -> None:
    source = complete_diagnostic
    diagnostic = SyntheticDiagnostic(source.model, source.reference_label, source.reference_digest, source.points, source.summary)
    assert diagnostic.points == source.points
    assert diagnostic.to_dict()["variants"] == []
    assert diagnostic.to_dict()["uncertainty"]["configuration_count"] == 1
    with pytest.raises(ParameterValidationError):
        replace(diagnostic, summary={**diagnostic.summary, "probability_mean": 99.0})


def test_detached_five_argument_envelope_rejects_inconsistent_probability_and_temperature() -> None:
    reference = ImageFrame(np.full((4, 4), 0.2, dtype=np.float32))
    comparison = ImageFrame(np.full((4, 4), 0.8, dtype=np.float32))
    model = default_synthetic_model()
    points = sensitivity_curve(model, reference, (("different", 1.0, comparison),))
    digest = canonical_digest(reference)
    summary = summarize_curve(points)
    diagnostic = SyntheticDiagnostic(model, "reference", digest, points, summary)
    assert diagnostic.points[0].prediction.probability_comparison != 0.5
    with pytest.raises(ParameterValidationError):
        SyntheticDiagnostic(replace(model, temperature=model.temperature * 2.0), "reference", digest, points, summary)
    prediction = points[0].prediction
    forged_probability = 0.9 if prediction.probability_comparison != 0.9 else 0.8
    forged_points = (replace(points[0], prediction=replace(
        prediction, probability_comparison=forged_probability, choice="comparison",
    )),)
    with pytest.raises(ParameterValidationError):
        SyntheticDiagnostic(model, "reference", digest, forged_points, summarize_curve(forged_points))


def test_diagnostic_rejects_forged_prediction_metadata_and_scores(complete_diagnostic: SyntheticDiagnostic) -> None:
    diagnostic = complete_diagnostic
    first = diagnostic.points[0]
    prediction = first.prediction
    changed_probability = 0.9 if prediction.probability_comparison != 0.9 else 0.8
    changes = (
        {"model_id": "foreign-model"}, {"reference_digest": "f" * 64}, {"seed": prediction.seed + 1},
        {"feature_schema": tuple(reversed(prediction.feature_schema))},
        {"score_reference": prediction.score_reference + 0.1},
        {"probability_comparison": changed_probability, "choice": "comparison"},
        {"trial_id": diagnostic.points[1].prediction.trial_id}, {"condition_id": "foreign-condition"},
    )
    for change in changes:
        with pytest.raises(ParameterValidationError):
            changed = replace(first, prediction=replace(prediction, **change))
            replace(diagnostic, points=(changed,) + diagnostic.points[1:])
    with pytest.raises(ParameterValidationError):
        replace(diagnostic, model=replace(diagnostic.model, temperature=diagnostic.model.temperature * 2.0))
    with pytest.raises(ParameterValidationError):
        replace(diagnostic, summary={**diagnostic.summary, "probability_mean": 99.0})
    with pytest.raises(ParameterValidationError):
        replace(diagnostic, summary={**diagnostic.summary, "point_count": True})
    control = diagnostic.zero_difference_control
    assert control is not None
    with pytest.raises(ParameterValidationError):
        replace(control, probability_comparison=0.99)
    with pytest.raises(ParameterValidationError):
        replace(control, score_comparison=control.score_reference + 1.0)
    with pytest.raises(ParameterValidationError):
        replace(prediction, choice="reference" if prediction.choice == "comparison" else "comparison")
    with pytest.raises(ParameterValidationError):
        replace(prediction, feature_schema=prediction.feature_schema + prediction.feature_schema[:1])


def test_diagnostic_rejects_forged_feature_and_variant_envelopes(complete_diagnostic: SyntheticDiagnostic) -> None:
    diagnostic = complete_diagnostic
    changed_features = dict(diagnostic.reference_features)
    changed_features["edge_energy"] = 1.0 if changed_features["edge_energy"] != 1.0 else 0.0
    with pytest.raises(ParameterValidationError):
        replace(diagnostic, reference_features=changed_features)
    with pytest.raises(ParameterValidationError):
        replace(diagnostic, comparison_features=diagnostic.comparison_features[:-1])
    with pytest.raises(ParameterValidationError):
        replace(diagnostic, reference_features={}, comparison_features=())
    with pytest.raises(ParameterValidationError):
        replace(diagnostic, variants=diagnostic.variants[:-1])
    variant = diagnostic.variants[0]
    with pytest.raises(ParameterValidationError):
        changed = replace(variant, model=replace(variant.model, temperature=variant.model.temperature * 2.0))
        replace(diagnostic, variants=(changed,) + diagnostic.variants[1:])
    with pytest.raises(ParameterValidationError):
        changed = replace(variant, points=variant.points[:-1])
        replace(diagnostic, variants=(changed,) + diagnostic.variants[1:])
    with pytest.raises(ParameterValidationError):
        changed_point = replace(variant.points[0], x_value=-99.0)
        changed = replace(variant, points=(changed_point,) + variant.points[1:])
        replace(diagnostic, variants=(changed,) + diagnostic.variants[1:])
    with pytest.raises(ParameterValidationError):
        replace(diagnostic, zero_difference_control=None)
