"""Integrity oracles for observer records, trial identities, and simulations."""

from dataclasses import dataclass, replace
import json
import math
from pathlib import Path
import statistics
from types import MappingProxyType

import numpy as np
import pytest

import duckrabbit
from duckrabbit.errors import ParameterValidationError
from duckrabbit.observer import ObserverAggregate, ObserverResponse, TrialSpec, aggregate_responses
from duckrabbit.observer_analysis import (
    ConditionSpec,
    ParticipantId,
    PowerEstimate,
    ResponseKind,
    ResponseSummary,
    StimulusReference,
    TrialDisposition,
    TrialRecord,
    build_trial_sequence,
    default_study_design,
    simulate_binary_responses,
    simulate_continuous_responses,
    simulate_event_counts,
    simulate_power,
    simulate_power_curve,
    simulate_reaction_times,
)
from duckrabbit.parameters import replace_from_mapping


def _trial_record(kind: ResponseKind, value: object, **kwargs: object) -> TrialRecord:
    return TrialRecord(
        "study:observer:condition:0", ParticipantId("observer"), "condition", 0,
        StimulusReference("visual.duck_rabbit", "a" * 64), kind, value, **kwargs,
    )


def test_every_default_condition_resolves_and_generates() -> None:
    design = default_study_design()
    for condition, serialized in zip(design.conditions, design.to_dict()["conditions"]):
        parameters = replace_from_mapping(
            duckrabbit.default_parameters(condition.illusion_id), serialized["parameter_overrides"],
        )
        artifact = duckrabbit.generate(condition.illusion_id, parameters, seed=0)
        assert artifact is not None
    temporal = next(condition for condition in design.conditions if condition.condition_id == "temporal_sync")
    assert temporal.parameter_overrides == {"config": {"sync_offset": 0.0}}


@pytest.mark.parametrize("rate", [0.0, 0.05, 2.0, 1_000.0, 10_000.0])
def test_poisson_distribution_and_seed_repeatability(rate: float) -> None:
    design = replace(default_study_design(), trials_per_condition=1_000)
    design = replace(design, conditions=(design.conditions[0],))
    rates = {design.conditions[0].condition_id: rate}
    first = simulate_event_counts(design, ("observer",), rates, seed=83)
    assert first == simulate_event_counts(design, ("observer",), rates, seed=83)
    values = [record.value for record in first]
    assert all(type(value) is int and value >= 0 for value in values)
    assert statistics.mean(values) == pytest.approx(rate, abs=max(0.01, 6 * math.sqrt(rate / len(values))))
    if rate:
        assert statistics.variance(values) == pytest.approx(rate, rel=0.3)
        assert first != simulate_event_counts(design, ("observer",), rates, seed=84)
    else:
        assert set(values) == {0}


@pytest.mark.parametrize("kind", [kind for kind in ResponseKind if kind is not ResponseKind.FORCED_CHOICE])
@pytest.mark.parametrize("value", ["not a count", float("nan"), float("inf"), -float("inf"), True])
def test_numeric_trial_responses_require_finite_numbers(kind: ResponseKind, value: object) -> None:
    with pytest.raises(ParameterValidationError):
        _trial_record(kind, value)


@pytest.mark.parametrize("value", [-3, 1.25])
def test_event_counts_reject_negative_and_fractional_values(value: object) -> None:
    with pytest.raises(ParameterValidationError, match="non-negative integer"):
        _trial_record(ResponseKind.EVENT_COUNT, value)


@pytest.mark.parametrize("value", [0, 3, 3.0])
def test_event_counts_accept_nonnegative_integral_values(value: object) -> None:
    assert _trial_record(ResponseKind.EVENT_COUNT, value).response_value == value


@pytest.mark.parametrize("value", ["", " ", 2, 0.4])
def test_forced_choice_requires_nonempty_labels(value: object) -> None:
    with pytest.raises(ParameterValidationError, match="non-empty label"):
        _trial_record(ResponseKind.FORCED_CHOICE, value)


@pytest.mark.parametrize("value", [0, -1])
def test_reaction_time_response_requires_positive_value(value: object) -> None:
    with pytest.raises(ParameterValidationError, match="positive"):
        _trial_record(ResponseKind.REACTION_TIME, value)


@pytest.mark.parametrize("value", [True, "0.4", float("nan"), float("inf"), 0, -0.1])
def test_reaction_time_metadata_requires_finite_positive_number(value: object) -> None:
    with pytest.raises(ParameterValidationError):
        _trial_record(ResponseKind.FORCED_CHOICE, "duck", reaction_time_seconds=value)


def test_valid_trial_families_and_explicit_missingness() -> None:
    for kind, value in (
        (ResponseKind.FORCED_CHOICE, "duck"), (ResponseKind.CONTINUOUS_MAGNITUDE, -1.2),
        (ResponseKind.LOCALIZATION, -0.5), (ResponseKind.REACTION_TIME, 0.4),
        (ResponseKind.REVERSAL, 0.2),
    ):
        assert _trial_record(kind, value).response_value == value
    assert _trial_record(
        ResponseKind.EVENT_COUNT, None, disposition=TrialDisposition.MISSING, missing_reason="not recorded",
    ).response_value is None


@pytest.mark.parametrize("digest", [None, "", "BAD", "A" * 64, "g" * 64, 123])
def test_manifest_digest_is_mandatory_valid_sha256(digest: object) -> None:
    with pytest.raises(ParameterValidationError, match="manifest_sha256"):
        StimulusReference("visual.duck_rabbit", digest)
    assert StimulusReference("visual.duck_rabbit", "a" * 64).encoded_sha256 is None


def test_nested_overrides_are_snapshots_and_serialization_is_detached() -> None:
    overrides = {"config": {"sync_offset": 0.0}, "items": [{"values": [1, 2]}]}
    condition = ConditionSpec("nested", "visual.duck_rabbit", overrides, ("duck",))
    trial = TrialSpec("trial", "visual.duck_rabbit", "nested", 0, ("duck",), overrides)
    overrides["config"]["sync_offset"] = 20
    overrides["items"][0]["values"].append(3)
    for record in (condition, trial):
        assert record.parameter_overrides["config"]["sync_offset"] == 0.0
        assert record.parameter_overrides["items"][0]["values"] == (1, 2)
        with pytest.raises(TypeError):
            record.parameter_overrides["config"]["sync_offset"] = 30
        with pytest.raises(TypeError):
            record.parameter_overrides["items"][0]["values"][0] = 30
    design = replace(default_study_design(), conditions=(condition,))
    for payload in (trial.to_dict(), design.to_dict()["conditions"][0]):
        json.dumps(payload)
        payload["parameter_overrides"]["config"]["sync_offset"] = 40
        payload["parameter_overrides"]["items"][0]["values"].append(4)
    assert trial.to_dict()["parameter_overrides"]["items"][0]["values"] == [1, 2]
    assert design.to_dict()["conditions"][0]["parameter_overrides"]["config"]["sync_offset"] == 0.0
    sequence = build_trial_sequence(design, ("observer",))
    assert sequence[0].parameter_overrides == condition.parameter_overrides


def test_aggregation_rejects_duplicate_trials_and_responses() -> None:
    trial = TrialSpec("trial", "visual.duck_rabbit", "default", 0, ("duck", "rabbit"))
    response = ObserverResponse("trial", "observer", "duck", 0.4)
    with pytest.raises(ValueError, match="duplicate trial_id"):
        aggregate_responses((trial, replace(trial, condition="different")), ())
    with pytest.raises(ValueError, match="duplicate response"):
        aggregate_responses((trial,), (response, replace(response, response="rabbit")))
    result = aggregate_responses((trial,), (response, replace(response, observer_key="another")))
    assert result[0].sample_count == 2
    assert result[0].response_counts == (("duck", 2),)


def test_trial_sequences_reject_duplicate_observer_keys() -> None:
    with pytest.raises(ParameterValidationError, match="unique"):
        build_trial_sequence(default_study_design(), ("observer", "observer"))


def test_all_simulators_retain_observer_keys_with_colons_in_study_identity() -> None:
    design = replace(default_study_design(), study_id="study:v1", trials_per_condition=2)
    observers = ("observer-a", "observer:b")
    values = {condition.condition_id: 0.5 for condition in design.conditions}
    binary = simulate_binary_responses(design, observers, values)
    assert {record[2] for record in binary} == set(observers)
    for simulator in (simulate_continuous_responses, simulate_event_counts, simulate_reaction_times):
        observations = simulator(design, observers, values)
        assert {record.observer_key for record in observations} == set(observers)
        for record in observations:
            assert record.trial_id.startswith(f"study:v1:{record.observer_key}:")


@pytest.mark.parametrize("effect", [-0.99, -0.50001, 0.50001, 0.99])
def test_power_rejects_impossible_probability_differences(effect: float) -> None:
    with pytest.raises(ParameterValidationError, match="effect"):
        simulate_power(20, effect, repetitions=10)


@pytest.mark.parametrize("effect", [-0.5, 0.0, 0.5])
def test_power_accepts_and_reports_supported_effects(effect: float) -> None:
    point = simulate_power(20, effect, repetitions=10)
    assert point.effect == effect
    assert point == simulate_power(20, effect, repetitions=10)


@pytest.mark.parametrize("mean", [float("nan"), float("inf"), -float("inf"), 0.0])
def test_aggregate_mean_reaction_time_is_finite_positive(mean: float) -> None:
    with pytest.raises(ValueError, match="mean_reaction_time"):
        ObserverAggregate("visual.duck_rabbit", "default", (("duck", 1),), mean, 1)


@pytest.mark.parametrize("counts", [(("duck", 2),), (("duck", 0),), (("duck", 1), ("duck", 0)), (("", 1),)])
def test_aggregate_counts_match_sample_total_and_have_unique_labels(counts: tuple) -> None:
    with pytest.raises(ValueError):
        ObserverAggregate("visual.duck_rabbit", "default", counts, 0.4, 1)


def test_override_arrays_are_snapshots_and_nonfinite_values_are_rejected() -> None:
    values = np.array([2, 3])
    trial = TrialSpec("trial", "audio.missing_fundamental", "default", 0, ("one",), {"harmonics": values})
    values[0] = 99
    assert trial.parameter_overrides["harmonics"] == (2, 3)
    assert trial.to_dict()["parameter_overrides"] == {"harmonics": [2, 3]}
    with pytest.raises(ParameterValidationError, match="finite"):
        ConditionSpec("condition", "visual.duck_rabbit", {"duck_weight": float("nan")}, ("duck",))


def test_composite_trial_id_collisions_are_rejected() -> None:
    design = replace(default_study_design(), conditions=(
        ConditionSpec("b:c", "visual.duck_rabbit", {}, ("duck",)),
        ConditionSpec("c", "visual.duck_rabbit", {}, ("duck",)),
    ), trials_per_condition=1)
    with pytest.raises(ParameterValidationError, match="trial IDs must be unique"):
        build_trial_sequence(design, ("a", "a:b"))


def test_override_normalization_freezes_supported_nested_values() -> None:
    @dataclass
    class Configuration:
        values: list[int]

    array = np.array([[0.25, 0.75]], dtype=np.float32)
    configuration = Configuration([1, 2])
    nested = {"array": array, "configuration": configuration, "empty": [], "mapping": {}}
    overrides = MappingProxyType({
        "nested": MappingProxyType(nested), "path": Path("stimulus.png"),
        "kind": ResponseKind.EVENT_COUNT, "scalar": np.int64(3),
    })
    records = (
        ConditionSpec("condition", "visual.duck_rabbit", overrides, ("duck",)),
        TrialSpec("trial", "visual.duck_rabbit", "condition", 0, ("duck",), overrides),
    )
    array[0, 0] = 1
    configuration.values.append(3)
    nested["empty"].append(4)
    expected = {
        "nested": {"array": [[0.25, 0.75]], "configuration": {"values": [1, 2]}, "empty": [], "mapping": {}},
        "path": "stimulus.png", "kind": "event_count", "scalar": 3,
    }

    def serialize(record: ConditionSpec | TrialSpec) -> dict[str, object]:
        if isinstance(record, ConditionSpec):
            return replace(default_study_design(), conditions=(record,)).to_dict()["conditions"][0]
        return record.to_dict()

    for record in records:
        assert serialize(record)["parameter_overrides"] == expected
        with pytest.raises(TypeError):
            record.parameter_overrides["nested"]["mapping"]["new"] = 1
        with pytest.raises(TypeError):
            record.parameter_overrides["nested"]["array"][0][0] = 1
        with pytest.raises(TypeError):
            record.parameter_overrides["nested"]["configuration"]["values"][0] = 1
        serialized = serialize(record)["parameter_overrides"]
        serialized["nested"]["array"][0].append(2)
        assert serialize(record)["parameter_overrides"] == expected


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf")])
def test_override_readonly_mappings_and_arrays_still_validate(invalid: float) -> None:
    overrides = MappingProxyType({"nested": MappingProxyType({"array": np.array([invalid])})})
    with pytest.raises(ParameterValidationError, match="finite"):
        TrialSpec("trial", "visual.duck_rabbit", "condition", 0, ("duck",), overrides)
    with pytest.raises(ParameterValidationError, match="finite"):
        ConditionSpec("condition", "visual.duck_rabbit", overrides, ("duck",))


def test_override_nested_mapping_key_collisions_still_validate() -> None:
    overrides = {"nested": MappingProxyType({1: "first", "1": "second"})}
    with pytest.raises(ParameterValidationError, match="duplicate JSON mapping key"):
        TrialSpec("trial", "visual.duck_rabbit", "condition", 0, ("duck",), overrides)
    with pytest.raises(ParameterValidationError, match="duplicate JSON mapping key"):
        ConditionSpec("condition", "visual.duck_rabbit", overrides, ("duck",))


@pytest.mark.parametrize("invalid", [True, False, None, "0.5", complex(0.5), float("nan"), float("inf"), -float("inf"), 10 ** 400])
def test_probability_and_effect_apis_reject_invalid_numeric_values(invalid: object) -> None:
    design = replace(default_study_design(), trials_per_condition=1)
    probabilities = {condition.condition_id: invalid for condition in design.conditions}
    with pytest.raises(ParameterValidationError, match="probability"):
        simulate_binary_responses(design, ("observer:a",), probabilities)
    with pytest.raises(ParameterValidationError, match="effect"):
        simulate_power(2, invalid, repetitions=1)
    with pytest.raises(ParameterValidationError, match="effect"):
        simulate_power_curve(2, (0.0, invalid), repetitions=1)
    with pytest.raises(ParameterValidationError, match="alpha"):
        simulate_power(2, 0.0, repetitions=1, alpha=invalid)
    with pytest.raises(ParameterValidationError, match="effect/power"):
        PowerEstimate(invalid, 0.5, 1)
    with pytest.raises(ParameterValidationError, match="effect/power"):
        PowerEstimate(0.0, invalid, 1)
    for name in ("proportion", "interval_low", "interval_high"):
        values = dict(proportion=0.5, interval_low=0.0, interval_high=1.0)
        values[name] = invalid
        with pytest.raises(ParameterValidationError, match="interval"):
            ResponseSummary("condition", "duck", 1, 2, **values)


@pytest.mark.parametrize("probability", [0.0, 1.0])
def test_binary_probability_endpoints_preserve_colon_observer_identity(probability: float) -> None:
    design = replace(default_study_design(), study_id="study:v1", trials_per_condition=2)
    observers = ("observer:a", "observer:b")
    probabilities = {condition.condition_id: probability for condition in design.conditions}
    records = simulate_binary_responses(design, observers, probabilities)
    labels = {condition.condition_id: condition.response_labels[0 if probability else -1] for condition in design.conditions}
    assert all(label == labels[condition] for condition, label, observer in records)
    assert {observer for condition, label, observer in records} == set(observers)
    assert records == simulate_binary_responses(design, observers, probabilities)


def test_power_curve_preserves_effect_seed_offsets() -> None:
    effects = (-0.5, -0.1, 0.0, 0.1, 0.5)
    assert simulate_power_curve(32, effects, repetitions=20, seed=17) == tuple(
        simulate_power(32, effect, repetitions=20, seed=17 + index)
        for index, effect in enumerate(effects)
    )
