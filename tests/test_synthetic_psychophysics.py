"""No-mock tests for the model-output-only synthetic psychophysics layer."""

from __future__ import annotations

import json
from dataclasses import fields

import pytest

import duckrabbit
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
