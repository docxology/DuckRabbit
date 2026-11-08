"""Exact-test calibration and descriptive observer-study boundaries."""

from dataclasses import replace
import json
import math

import pytest

from duckrabbit.errors import ParameterValidationError
from duckrabbit.observer_analysis import (
    AnalysisModel,
    ResponseKind,
    SyntheticObservation,
    _fisher_exact_two_sided,
    default_model_specs,
    default_study_design,
    simulate_binary_responses,
    simulate_power,
    summarize_binary_responses,
    summarize_numeric_responses,
)


def test_default_plan_is_illustrative_and_identifies_binary_contrasts() -> None:
    design = default_study_design()
    by_id = {condition.condition_id: condition for condition in design.conditions}
    assert len(by_id) == 6
    assert {name: by_id[name].parameter_overrides["config"]["sync_offset"] for name in ("temporal_early", "temporal_sync", "temporal_late")} == {
        "temporal_early": -120.0, "temporal_sync": 0.0, "temporal_late": 120.0,
    }
    for estimand in design.estimands:
        assert estimand.response_kind is by_id[estimand.reference_condition].response_kind is ResponseKind.FORCED_CHOICE
        assert estimand.model is AnalysisModel.LOGISTIC_MIXED
    serialized = design.to_dict()
    assert serialized["observer_data_status"] == "none_bundled"
    assert serialized["design_status"] == "illustrative_not_preregistration_ready"
    assert len(serialized["external_requirements"]) == 3
    assert "not positional counterbalancing" in serialized["randomization"]


def test_estimand_reference_response_and_model_compatibility() -> None:
    design = default_study_design()
    with pytest.raises(ParameterValidationError, match="reference condition does not exist"):
        replace(design, estimands=(replace(design.estimands[0], reference_condition="absent"),))
    for kind in ResponseKind:
        if kind is not ResponseKind.FORCED_CHOICE:
            with pytest.raises(ParameterValidationError, match="incompatible"):
                replace(design.estimands[0], response_kind=kind)
    reference = next(condition for condition in design.conditions if condition.condition_id == "sifi_one_beep")
    with pytest.raises(ParameterValidationError, match="does not match"):
        replace(design, conditions=tuple(replace(condition, response_kind=ResponseKind.EVENT_COUNT) if condition is reference else condition for condition in design.conditions))
    for labels in (("one",), ("one", "two", "three")):
        with pytest.raises(ParameterValidationError, match="exactly two"):
            replace(design, conditions=tuple(replace(condition, response_labels=labels) if condition is reference else condition for condition in design.conditions))
    with pytest.raises(ParameterValidationError, match="distinct"):
        replace(reference, response_labels=("one", "one"))


def test_design_and_model_sequences_are_immutable_snapshots() -> None:
    design = default_study_design()
    conditions, estimands = list(design.conditions), list(design.estimands)
    inclusion, exclusion = ["complete"], ["technical failure"]
    snapshot = replace(design, conditions=conditions, estimands=estimands, inclusion_rules=inclusion, exclusion_rules=exclusion)
    conditions.clear()
    estimands.clear()
    inclusion.append("changed")
    exclusion.clear()
    assert snapshot.conditions == design.conditions
    assert snapshot.estimands == design.estimands
    assert snapshot.inclusion_rules == ("complete",)
    assert snapshot.exclusion_rules == ("technical failure",)
    effects = ["participant", "item"]
    spec = replace(default_model_specs()[0], random_effects=effects)
    effects.clear()
    assert spec.random_effects == ("participant", "item")
    assert default_model_specs()[2].formula.startswith("reaction_time ~")
    assert default_model_specs()[2].family == "lognormal"
    assert default_model_specs()[2].link == "log"


def test_binary_summary_includes_zero_count_labels_and_repeated_measure_boundary() -> None:
    condition = default_study_design().conditions[0]
    summaries = summarize_binary_responses((condition,), [(condition.condition_id, "duck", "same-observer")] * 8)
    assert [(row.label, row.count, row.total, row.observer_count) for row in summaries] == [("duck", 8, 8, 1), ("rabbit", 0, 8, 1)]
    assert summaries[1].proportion == 0
    assert 0 < summaries[1].interval_high < 1
    assert all("independent-trial Wilson" in row.to_dict()["interval_method"] for row in summaries)
    assert all("participant or item effects" in row.to_dict()["inference_boundary"] for row in summaries)
    assert summarize_binary_responses((condition,), ()) == ()
    for labels in (("duck",), ("duck", "rabbit", "other")):
        with pytest.raises(ParameterValidationError, match="exactly two"):
            summarize_binary_responses((replace(condition, response_labels=labels),), ())
        with pytest.raises(ParameterValidationError, match="exactly two"):
            simulate_binary_responses(replace(default_study_design(), conditions=default_study_design().conditions + (replace(condition, condition_id="invalid", response_labels=labels),)), ("observer",), {})


def test_binary_summary_counts_distinct_observers_per_condition() -> None:
    condition = default_study_design().conditions[0]
    rows = summarize_binary_responses((condition,), [(condition.condition_id, "duck", "a"), (condition.condition_id, "duck", "a"), (condition.condition_id, "rabbit", "b")])
    assert all(row.observer_count == 2 and row.total == 3 for row in rows)


def test_single_numeric_record_has_unavailable_variance_and_interval() -> None:
    record = SyntheticObservation("trial", "observer", "condition", ResponseKind.CONTINUOUS_MAGNITUDE, 0.75)
    summary, = summarize_numeric_responses((record,))
    assert summary.mean == 0.75
    assert summary.observer_count == summary.sample_count == 1
    assert summary.standard_deviation is summary.interval_low is summary.interval_high is None
    assert summary.to_dict()["interval_method"] == "unavailable_n_less_than_two"
    assert json.loads(json.dumps(summary.to_dict()))["interval_low"] is None
    with pytest.raises(ParameterValidationError, match="unavailable"):
        replace(summary, standard_deviation=0.0, interval_low=0.75, interval_high=0.75)
    pair, = summarize_numeric_responses((record, replace(record, trial_id="trial2", value=1.25)))
    assert pair.standard_deviation == pytest.approx(math.sqrt(0.125))
    assert pair.observer_count == 1 and pair.sample_count == 2
    assert pair.interval_low < pair.mean < pair.interval_high
    assert "participant/item-aware" in pair.to_dict()["inference_boundary"]


@pytest.mark.parametrize(("table", "expected"), [
    ((1, 9, 11, 3), 0.0027594561852200836),
    ((0, 2, 2, 0), 1 / 3),
    ((1, 1, 1, 1), 1.0),
    ((0, 0, 0, 0), 1.0),
    ((0, 5, 5, 0), 1 / 126),
])
def test_fisher_exact_known_tables_and_symmetries(table: tuple[int, ...], expected: float) -> None:
    a, b, c, d = table
    assert _fisher_exact_two_sided(a, b, c, d) == pytest.approx(expected)
    assert _fisher_exact_two_sided(c, d, a, b) == pytest.approx(expected)
    assert _fisher_exact_two_sided(b, a, d, c) == pytest.approx(expected)


def test_exact_n_two_null_rejection_probability_is_zero_not_wald_one_eighth() -> None:
    rejection_probability = sum(
        math.comb(2, reference) * math.comb(2, treatment) / 16
        for reference in range(3) for treatment in range(3)
        if _fisher_exact_two_sided(reference, 2 - reference, treatment, 2 - treatment) <= 0.05
    )
    assert rejection_probability == 0
    for effect in (-0.5, 0.0, 0.5):
        estimate = simulate_power(2, effect, repetitions=30, seed=7)
        assert estimate.power == estimate.detection_count == 0


def test_power_serializes_exact_test_assumptions_and_monte_carlo_uncertainty() -> None:
    estimate = simulate_power(12, 0.3, repetitions=80, seed=19, alpha=0.1)
    serialized = estimate.to_dict()
    assert serialized["sample_size_per_group"] == 12
    assert serialized["baseline"] == 0.5 and serialized["alternative"] == 0.8
    assert serialized["alpha"] == 0.1 and serialized["seed"] == 19
    assert "two-sided Fisher exact conditional" in serialized["test"]
    assert "no participant/item clustering or repeated-measures effects" in serialized["assumptions"]
    assert serialized["monte_carlo_interval_low"] <= estimate.power <= serialized["monte_carlo_interval_high"]
    assert "not uncertainty about an observed effect" in serialized["monte_carlo_interval_method"]
    assert estimate == simulate_power(12, 0.3, repetitions=80, seed=19, alpha=0.1)
    zero = simulate_power(2, 0.0, repetitions=1).to_dict()
    assert zero["monte_carlo_interval_high"] > 0
    with pytest.raises(ParameterValidationError, match="detection_count"):
        replace(estimate, power=1.0 if estimate.power != 1.0 else 0.0)
