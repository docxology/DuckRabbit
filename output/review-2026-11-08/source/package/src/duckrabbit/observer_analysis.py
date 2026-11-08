"""Illustrative observer schemas and deterministic synthetic-data utilities.

External task definitions, ethics approval, and presentation calibration are
required before preregistration or data collection. Synthetic responses test
the harness only; they are never empirical evidence.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import json
import math
import random
import re
import statistics
from numbers import Real
from pathlib import Path

from .errors import ParameterValidationError
from .io import atomic_write_text
from .observer import TrialSpec, _freeze_overrides, _thaw_overrides
from .parameters import Seed
from .taxonomy import ClaimLevel


def _is_finite_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, Real):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _deterministic_rng(seed: int | Seed) -> random.Random:
    """Return a local RNG for reproducible synthetic study utilities."""
    return random.Random(int(Seed(seed)))  # nosec B311 -- synthetic data are not security-sensitive


class ResponseKind(str, Enum):
    """Supported response families for a preregistered task."""

    FORCED_CHOICE = "forced_choice"
    CONTINUOUS_MAGNITUDE = "continuous_magnitude"
    LOCALIZATION = "localization"
    REACTION_TIME = "reaction_time"
    EVENT_COUNT = "event_count"
    REVERSAL = "reversal"


class AnalysisModel(str, Enum):
    """Analysis model template, not a fitted result."""

    LOGISTIC_MIXED = "logistic_mixed"
    LINEAR_MIXED = "linear_mixed"
    LOGNORMAL_MIXED = "lognormal_mixed"
    POISSON_OR_ORDINAL = "poisson_or_ordinal"
    TRANSITION_RATE = "transition_rate"


class TrialDisposition(str, Enum):
    """Preregistered disposition of one observer trial."""

    COMPLETE = "complete"
    EXCLUDED = "excluded"
    MISSING = "missing"


@dataclass(frozen=True)
class ParticipantId:
    """Pseudonymous participant key; no direct identifiers are accepted."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", self.value):
            raise ParameterValidationError("participant ID must be a short pseudonymous token")


@dataclass(frozen=True)
class StimulusReference:
    """Manifest and encoded-file identity attached to an observer trial."""

    illusion_id: str
    manifest_sha256: str
    encoded_sha256: str | None = None

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z]+\.[a-z0-9_]+", self.illusion_id):
            raise ParameterValidationError("stimulus reference illusion_id is invalid")
        for name, digest in (("manifest_sha256", self.manifest_sha256), ("encoded_sha256", self.encoded_sha256)):
            if name == "encoded_sha256" and digest is None:
                continue
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ParameterValidationError(f"stimulus reference {name} must be lowercase SHA-256 hex")


@dataclass(frozen=True)
class TrialRecord:
    """Study-ready trial identity, stimulus provenance, response, and missingness.

    This record is a schema for future human-observer studies. It is not
    a record of actual observer data. The randomization_seed links the
    trial to a specific stimulus presentation order.
    """

    trial_id: str
    participant: ParticipantId
    condition_id: str
    randomization_seed: Seed
    stimulus: StimulusReference
    response_kind: ResponseKind
    response_value: str | float | int | None = None
    reaction_time_seconds: float | None = None
    disposition: TrialDisposition = TrialDisposition.COMPLETE
    exclusion_reason: str | None = None
    missing_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.trial_id or not self.condition_id or not isinstance(self.participant, ParticipantId) or not isinstance(self.stimulus, StimulusReference):
            raise ParameterValidationError("trial identity and stimulus reference are required")
        if not isinstance(self.randomization_seed, Seed):
            object.__setattr__(self, "randomization_seed", Seed(self.randomization_seed))
        if not isinstance(self.response_kind, ResponseKind) or not isinstance(self.disposition, TrialDisposition):
            raise ParameterValidationError("trial response kind and disposition are typed enums")
        if isinstance(self.response_value, bool) or not isinstance(self.response_value, (str, int, float, type(None))):
            raise ParameterValidationError("trial response_value must be a scalar or null")
        if self.reaction_time_seconds is not None and (isinstance(self.reaction_time_seconds, bool) or not isinstance(self.reaction_time_seconds, (int, float)) or not math.isfinite(self.reaction_time_seconds) or self.reaction_time_seconds <= 0):
            raise ParameterValidationError("trial reaction time must be finite and positive")
        if self.disposition is TrialDisposition.COMPLETE and self.response_value is None:
            raise ParameterValidationError("complete trial requires a response value")
        if self.response_value is not None:
            if self.response_kind is ResponseKind.FORCED_CHOICE:
                if not isinstance(self.response_value, str) or not self.response_value.strip():
                    raise ParameterValidationError("forced-choice response must be a non-empty label")
            else:
                if not isinstance(self.response_value, (int, float)) or not math.isfinite(self.response_value):
                    raise ParameterValidationError("numeric response must be finite")
                if self.response_kind is ResponseKind.EVENT_COUNT and (self.response_value < 0 or int(self.response_value) != self.response_value):
                    raise ParameterValidationError("event count must be a non-negative integer")
                if self.response_kind is ResponseKind.REACTION_TIME and self.response_value <= 0:
                    raise ParameterValidationError("reaction-time response must be positive")
        if self.disposition is TrialDisposition.EXCLUDED and not self.exclusion_reason:
            raise ParameterValidationError("excluded trial requires an exclusion reason")
        if self.disposition is TrialDisposition.MISSING and not self.missing_reason:
            raise ParameterValidationError("missing trial requires a missing reason")

    def to_dict(self) -> dict[str, object]:
        return {
            "trial_id": self.trial_id,
            "participant": self.participant.value,
            "condition_id": self.condition_id,
            "randomization_seed": int(self.randomization_seed),
            "stimulus": {
                "illusion_id": self.stimulus.illusion_id,
                "manifest_sha256": self.stimulus.manifest_sha256,
                "encoded_sha256": self.stimulus.encoded_sha256,
            },
            "response_kind": self.response_kind.value,
            "response_value": self.response_value,
            "reaction_time_seconds": self.reaction_time_seconds,
            "disposition": self.disposition.value,
            "exclusion_reason": self.exclusion_reason,
            "missing_reason": self.missing_reason,
        }


@dataclass(frozen=True)
class AnalysisModelSpec:
    """Named analysis-model template with explicit formula and random effects."""

    model: AnalysisModel
    formula: str
    family: str
    link: str
    random_effects: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.model, AnalysisModel) or not self.formula or not self.family or not self.link:
            raise ParameterValidationError("analysis model specification is incomplete")
        if not self.random_effects or not all(self.random_effects):
            raise ParameterValidationError("analysis model random effects are required")
        if isinstance(self.random_effects, str) or not all(isinstance(effect, str) and effect for effect in self.random_effects):
            raise ParameterValidationError("analysis model random effects must be named strings")
        object.__setattr__(self, "random_effects", tuple(self.random_effects))

    def to_dict(self) -> dict[str, object]:
        return {"model": self.model.value, "formula": self.formula, "family": self.family, "link": self.link, "random_effects": list(self.random_effects)}


@dataclass(frozen=True)
class AggregateRecord:
    """Aggregate estimate with an explicit uncertainty interval."""

    estimand_name: str
    condition_id: str
    estimate: float
    unit: str
    interval_low: float
    interval_high: float
    sample_count: int
    claim_level: ClaimLevel = ClaimLevel.OBSERVER_HYPOTHESIS

    def __post_init__(self) -> None:
        if not self.estimand_name or not self.condition_id or not self.unit:
            raise ParameterValidationError("aggregate identity and unit are required")
        values = (self.estimate, self.interval_low, self.interval_high)
        if not all(math.isfinite(value) for value in values) or not self.interval_low <= self.estimate <= self.interval_high:
            raise ParameterValidationError("aggregate estimate and interval are invalid")
        if type(self.sample_count) is not int or self.sample_count < 1:
            raise ParameterValidationError("aggregate sample_count must be positive")
        if self.claim_level not in {ClaimLevel.OBSERVER_HYPOTHESIS, ClaimLevel.VALIDATED_OBSERVER_EFFECT}:
            raise ParameterValidationError("aggregate claim level must be observer-level")

    def to_dict(self) -> dict[str, object]:
        return {
            "estimand_name": self.estimand_name,
            "condition_id": self.condition_id,
            "estimate": self.estimate,
            "unit": self.unit,
            "interval_low": self.interval_low,
            "interval_high": self.interval_high,
            "sample_count": self.sample_count,
            "claim_level": self.claim_level.value,
        }


@dataclass(frozen=True)
class ConditionSpec:
    """One preregistered experimental condition."""

    condition_id: str
    illusion_id: str
    parameter_overrides: Mapping[str, object]
    response_labels: tuple[str, ...]
    response_kind: ResponseKind = ResponseKind.FORCED_CHOICE

    def __post_init__(self) -> None:
        if not self.condition_id or not self.illusion_id:
            raise ParameterValidationError("condition identity is required")
        if not isinstance(self.parameter_overrides, Mapping) or not all(isinstance(key, str) for key in self.parameter_overrides):
            raise ParameterValidationError("condition parameter_overrides must be a string-keyed mapping")
        if not self.response_labels or not all(isinstance(label, str) and label for label in self.response_labels):
            raise ParameterValidationError("condition response_labels must be non-empty strings")
        if isinstance(self.response_labels, str) or len(set(self.response_labels)) != len(self.response_labels):
            raise ParameterValidationError("condition response_labels must be distinct labels")
        if not isinstance(self.response_kind, ResponseKind):
            raise ParameterValidationError("condition response_kind must be ResponseKind")
        object.__setattr__(self, "parameter_overrides", _freeze_overrides(self.parameter_overrides))
        object.__setattr__(self, "response_labels", tuple(self.response_labels))


@dataclass(frozen=True)
class Estimand:
    """A preregistered quantity and contrast, independent of observed data."""

    name: str
    response_kind: ResponseKind
    model: AnalysisModel
    primary_contrast: str
    reference_condition: str
    uncertainty: str = "95% confidence interval"
    multiplicity: str = "Holm correction across confirmatory contrasts"

    def __post_init__(self) -> None:
        for name in ("name", "primary_contrast", "reference_condition", "uncertainty", "multiplicity"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ParameterValidationError(f"estimand {name} is required")
        if not isinstance(self.response_kind, ResponseKind) or not isinstance(self.model, AnalysisModel):
            raise ParameterValidationError("estimand response_kind and model are typed enums")
        compatible = {
            ResponseKind.FORCED_CHOICE: AnalysisModel.LOGISTIC_MIXED,
            ResponseKind.CONTINUOUS_MAGNITUDE: AnalysisModel.LINEAR_MIXED,
            ResponseKind.LOCALIZATION: AnalysisModel.LINEAR_MIXED,
            ResponseKind.REACTION_TIME: AnalysisModel.LOGNORMAL_MIXED,
            ResponseKind.EVENT_COUNT: AnalysisModel.POISSON_OR_ORDINAL,
            ResponseKind.REVERSAL: AnalysisModel.TRANSITION_RATE,
        }
        if self.model is not compatible[self.response_kind]:
            raise ParameterValidationError("estimand response kind and model are incompatible")


@dataclass(frozen=True)
class StudyDesign:
    """Illustrative condition, randomization, and analysis contract, not approval."""

    study_id: str
    conditions: tuple[ConditionSpec, ...]
    trials_per_condition: int
    observers: int
    randomization_seed: Seed
    estimands: tuple[Estimand, ...]
    inclusion_rules: tuple[str, ...] = ("complete primary response", "reaction time > 0",)
    exclusion_rules: tuple[str, ...] = ("prespecified technical failure",)

    def __post_init__(self) -> None:
        if not self.study_id or not self.conditions or not self.estimands:
            raise ParameterValidationError("study requires identity, conditions, and estimands")
        for name, kind in (("conditions", ConditionSpec), ("estimands", Estimand)):
            values = getattr(self, name)
            if not all(isinstance(value, kind) for value in values):
                raise ParameterValidationError(f"study {name} must contain typed records")
            object.__setattr__(self, name, tuple(values))
        for name in ("inclusion_rules", "exclusion_rules"):
            values = getattr(self, name)
            if isinstance(values, str) or not all(isinstance(value, str) and value for value in values):
                raise ParameterValidationError(f"study {name} must contain rule strings")
            object.__setattr__(self, name, tuple(values))
        if type(self.trials_per_condition) is not int or self.trials_per_condition < 1:
            raise ParameterValidationError("trials_per_condition must be positive")
        if type(self.observers) is not int or self.observers < 1:
            raise ParameterValidationError("observers must be positive")
        if not isinstance(self.randomization_seed, Seed):
            object.__setattr__(self, "randomization_seed", Seed(self.randomization_seed))
        if len({condition.condition_id for condition in self.conditions}) != len(self.conditions):
            raise ParameterValidationError("condition IDs must be unique")
        by_id = {condition.condition_id: condition for condition in self.conditions}
        for estimand in self.estimands:
            reference = by_id.get(estimand.reference_condition)
            if reference is None:
                raise ParameterValidationError("estimand reference condition does not exist")
            if reference.response_kind is not estimand.response_kind:
                raise ParameterValidationError("estimand response kind does not match its reference condition")
            if estimand.model is AnalysisModel.LOGISTIC_MIXED and len(reference.response_labels) != 2:
                raise ParameterValidationError("logistic estimand requires exactly two response labels")

    def to_dict(self) -> dict[str, object]:
        return {
            "study_id": self.study_id,
            "conditions": [
                {
                    "condition_id": condition.condition_id,
                    "illusion_id": condition.illusion_id,
                    "parameter_overrides": _thaw_overrides(condition.parameter_overrides),
                    "response_labels": list(condition.response_labels),
                    "response_kind": condition.response_kind.value,
                }
                for condition in self.conditions
            ],
            "trials_per_condition": self.trials_per_condition,
            "observers": self.observers,
            "randomization_seed": int(self.randomization_seed),
            "estimands": [
                {
                    "name": estimand.name,
                    "response_kind": estimand.response_kind.value,
                    "model": estimand.model.value,
                    "primary_contrast": estimand.primary_contrast,
                    "reference_condition": estimand.reference_condition,
                    "uncertainty": estimand.uncertainty,
                    "multiplicity": estimand.multiplicity,
                }
                for estimand in self.estimands
            ],
            "inclusion_rules": list(self.inclusion_rules),
            "exclusion_rules": list(self.exclusion_rules),
            "observer_data_status": "none_bundled",
            "design_status": "illustrative_not_preregistration_ready",
            "external_requirements": ["task and contrast specification", "ethics and consent approval", "display and playback calibration"],
            "randomization": "independent seeded shuffle per observer; not positional counterbalancing",
            "model_templates": [spec.to_dict() for spec in default_model_specs()],
        }


@dataclass(frozen=True)
class ResponseSummary:
    """Descriptive pooled-trial facts; Wilson assumes independent binary trials."""

    condition_id: str
    label: str
    count: int
    total: int
    proportion: float
    interval_low: float
    interval_high: float
    observer_count: int

    def __post_init__(self) -> None:
        if not self.condition_id or not self.label or type(self.count) is not int or type(self.total) is not int:
            raise ParameterValidationError("response summary identity and counts are invalid")
        if self.total < 1 or self.count < 0 or self.count > self.total:
            raise ParameterValidationError("response summary counts are invalid")
        if not all(_is_finite_number(value) for value in (self.interval_low, self.proportion, self.interval_high)) or not (0 <= self.interval_low <= self.proportion <= self.interval_high <= 1):
            raise ParameterValidationError("response summary interval is invalid")
        if type(self.observer_count) is not int or not 1 <= self.observer_count <= self.total:
            raise ParameterValidationError("response summary observer_count is invalid")
        if self.proportion != self.count / self.total:
            raise ParameterValidationError("response summary proportion must match counts")

    def to_dict(self) -> dict[str, object]:
        return {
            "condition_id": self.condition_id,
            "label": self.label,
            "count": self.count,
            "total": self.total,
            "proportion": self.proportion,
            "interval_low": self.interval_low,
            "interval_high": self.interval_high,
            "observer_count": self.observer_count,
            "interval_method": "descriptive 95% independent-trial Wilson",
            "inference_boundary": "Pooled repeated trials are not independent; this interval does not estimate participant or item effects. Use the prespecified hierarchical analysis for repeated measures.",
        }


@dataclass(frozen=True)
class PowerEstimate:
    """Monte Carlo detection fraction for an assumed independent-groups design."""

    effect: float
    power: float
    repetitions: int
    sample_size_per_group: int
    alpha: float
    baseline: float
    seed: Seed
    detection_count: int
    assumed: bool = True

    def __post_init__(self) -> None:
        if not _is_finite_number(self.effect) or not _is_finite_number(self.power) or not 0 <= self.power <= 1:
            raise ParameterValidationError("power point effect/power is invalid")
        if type(self.repetitions) is not int or self.repetitions < 1:
            raise ParameterValidationError("power repetitions must be positive")
        if type(self.sample_size_per_group) is not int or self.sample_size_per_group < 2:
            raise ParameterValidationError("power sample_size_per_group must be at least two")
        if not _is_finite_number(self.alpha) or not 0 < self.alpha < 1:
            raise ParameterValidationError("power alpha must be between zero and one")
        if not _is_finite_number(self.baseline) or not 0 <= self.baseline <= 1 or not 0 <= self.baseline + self.effect <= 1:
            raise ParameterValidationError("power baseline and effect imply invalid probabilities")
        if type(self.detection_count) is not int or not 0 <= self.detection_count <= self.repetitions or self.power != self.detection_count / self.repetitions:
            raise ParameterValidationError("power must match detection_count / repetitions")
        if self.assumed is not True:
            raise ParameterValidationError("power estimates must remain assumed")
        object.__setattr__(self, "seed", Seed(self.seed))

    def to_dict(self) -> dict[str, object]:
        low, high = _wilson(self.detection_count, self.repetitions)
        return {
            "effect": self.effect, "power": self.power, "repetitions": self.repetitions,
            "assumed": self.assumed, "sample_size_per_group": self.sample_size_per_group,
            "alpha": self.alpha, "baseline": self.baseline, "alternative": self.baseline + self.effect,
            "seed": int(self.seed), "detection_count": self.detection_count,
            "test": "two-sided Fisher exact conditional; probability-ordering; reject p <= alpha",
            "assumptions": ["two independent groups", "independent Bernoulli trials within groups", "fixed equal sample sizes", "no participant/item clustering or repeated-measures effects", "not power for the illustrative mixed-model study design"],
            "monte_carlo_interval_low": low, "monte_carlo_interval_high": high,
            "monte_carlo_interval_method": "95% Wilson interval for the simulated detection fraction; not uncertainty about an observed effect",
        }


# Compatibility alias retained for callers of the 0.4/0.5 public API.
PowerPoint = PowerEstimate


@dataclass(frozen=True)
class SyntheticObservation:
    """A deterministic synthetic response used only to test the study harness."""

    trial_id: str
    observer_key: str
    condition_id: str
    response_kind: ResponseKind
    value: str | float | int
    unit: str = "dimensionless"
    claim_level: ClaimLevel = ClaimLevel.OBSERVER_HYPOTHESIS
    synthetic_only: bool = True

    def __post_init__(self) -> None:
        if not self.trial_id or not self.observer_key or not self.condition_id or not self.unit:
            raise ParameterValidationError("synthetic observation identity and unit are required")
        if not isinstance(self.response_kind, ResponseKind) or self.claim_level is not ClaimLevel.OBSERVER_HYPOTHESIS:
            raise ParameterValidationError("synthetic observations must use observer_hypothesis claim level")
        if self.synthetic_only is not True:
            raise ParameterValidationError("synthetic observations must be marked synthetic_only")
        if self.response_kind is ResponseKind.FORCED_CHOICE:
            if not isinstance(self.value, str) or not self.value:
                raise ParameterValidationError("forced-choice synthetic value must be a non-empty string")
        elif self.response_kind is ResponseKind.EVENT_COUNT:
            if type(self.value) is not int or self.value < 0:
                raise ParameterValidationError("event-count synthetic value must be a non-negative integer")
        else:
            if isinstance(self.value, bool) or not isinstance(self.value, (int, float)) or not math.isfinite(float(self.value)):
                raise ParameterValidationError("numeric synthetic value must be finite")
            if self.response_kind is ResponseKind.REACTION_TIME and float(self.value) <= 0:
                raise ParameterValidationError("reaction-time synthetic value must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "trial_id": self.trial_id,
            "observer_key": self.observer_key,
            "condition_id": self.condition_id,
            "response_kind": self.response_kind.value,
            "value": self.value,
            "unit": self.unit,
            "claim_level": self.claim_level.value,
            "synthetic_only": self.synthetic_only,
        }


@dataclass(frozen=True)
class NumericSummary:
    """Descriptive summary of synthetic numeric observations, not a study result."""

    condition_id: str
    response_kind: ResponseKind
    unit: str
    sample_count: int
    mean: float
    standard_deviation: float | None
    interval_low: float | None
    interval_high: float | None
    observer_count: int
    claim_level: ClaimLevel = ClaimLevel.OBSERVER_HYPOTHESIS
    synthetic_only: bool = True

    def __post_init__(self) -> None:
        if not self.condition_id or not self.unit or not isinstance(self.response_kind, ResponseKind):
            raise ParameterValidationError("numeric summary identity, response kind, and unit are required")
        if type(self.sample_count) is not int or self.sample_count < 1:
            raise ParameterValidationError("numeric summary sample_count must be positive")
        if not _is_finite_number(self.mean):
            raise ParameterValidationError("numeric summary mean must be finite")
        if type(self.observer_count) is not int or not 1 <= self.observer_count <= self.sample_count:
            raise ParameterValidationError("numeric summary observer_count is invalid")
        uncertainty = (self.standard_deviation, self.interval_low, self.interval_high)
        if self.sample_count == 1:
            if any(value is not None for value in uncertainty):
                raise ParameterValidationError("single-observation variance and interval are unavailable")
        elif not all(_is_finite_number(value) for value in uncertainty) or self.standard_deviation < 0:
            raise ParameterValidationError("numeric summary uncertainty must be finite and non-negative where required")
        elif not self.interval_low <= self.mean <= self.interval_high:
            raise ParameterValidationError("numeric summary interval must contain the mean")
        if self.claim_level is not ClaimLevel.OBSERVER_HYPOTHESIS or self.synthetic_only is not True:
            raise ParameterValidationError("numeric summaries must remain synthetic observer hypotheses")

    def to_dict(self) -> dict[str, object]:
        return {
            "condition_id": self.condition_id,
            "response_kind": self.response_kind.value,
            "unit": self.unit,
            "sample_count": self.sample_count,
            "mean": self.mean,
            "standard_deviation": self.standard_deviation,
            "interval_low": self.interval_low,
            "interval_high": self.interval_high,
            "observer_count": self.observer_count,
            "interval_method": "unavailable_n_less_than_two" if self.sample_count == 1 else "descriptive 95% independent-trial normal approximation",
            "inference_boundary": "Synthetic pooled trials only; repeated measures require participant/item-aware inference. No participant effects are estimated.",
            "claim_level": self.claim_level.value,
            "synthetic_only": self.synthetic_only,
        }


def build_trial_sequence(design: StudyDesign, observer_keys: Sequence[str]) -> tuple[TrialSpec, ...]:
    """Build independently seeded shuffled orders, not positional counterbalancing."""
    if not observer_keys or not all(isinstance(key, str) and key for key in observer_keys):
        raise ParameterValidationError("observer_keys must be non-empty")
    if len(set(observer_keys)) != len(observer_keys):
        raise ParameterValidationError("observer_keys must be unique")
    trials: list[TrialSpec] = []
    for observer_index, observer_key in enumerate(observer_keys):
        local: list[TrialSpec] = []
        for condition_index, condition in enumerate(design.conditions):
            for repetition in range(design.trials_per_condition):
                local.append(
                    TrialSpec(
                        trial_id=f"{design.study_id}:{observer_key}:{condition.condition_id}:{repetition}",
                        illusion_id=condition.illusion_id,
                        condition=condition.condition_id,
                        # Mix condition into the seed so parallel conditions never
                        # share a stream and collisions need >1e4 trials/condition.
                        seed=Seed(
                            int(design.randomization_seed)
                            + observer_index * 1_000_003
                            + condition_index * 10_007
                            + repetition
                        ),
                        expected_response_labels=condition.response_labels,
                        parameter_overrides=condition.parameter_overrides,
                    )
                )
        rng = _deterministic_rng(int(design.randomization_seed) + observer_index)
        rng.shuffle(local)
        trials.extend(local)
    if len({trial.trial_id for trial in trials}) != len(trials):
        raise ParameterValidationError("composite trial IDs must be unique")
    return tuple(trials)


def _trial_observer_key(design: StudyDesign, trial: TrialSpec) -> str:
    """Recover the observer between known study and condition boundaries."""
    prefix_length = len(design.study_id) + 1
    suffix_length = len(trial.condition) + len(trial.trial_id.rsplit(":", 1)[-1]) + 2
    return trial.trial_id[prefix_length:-suffix_length]


def _wilson(count: int, total: int, alpha: float = 0.05) -> tuple[float, float]:
    if total <= 0 or not 0 <= count <= total:
        raise ParameterValidationError("Wilson interval requires total > 0 and 0 <= count <= total")
    if not _is_finite_number(alpha) or not 0 < alpha < 1:
        raise ParameterValidationError("Wilson interval confidence level must be between 0 and 1")
    z = statistics.NormalDist().inv_cdf(1 - alpha / 2)
    p = count / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return max(0.0, center - spread), min(1.0, center + spread)


def summarize_binary_responses(
    conditions: Sequence[ConditionSpec], responses: Sequence[tuple[str, str, str]]
) -> tuple[ResponseSummary, ...]:
    """Pool binary trial labels descriptively, retaining distinct observer counts.

    Intervals assume independent trials and must not be used as participant-level
    inference when an observer contributes repeated responses. Conditions with
    no responses have no estimable proportion and are omitted.
    """
    allowed = {}
    for condition in conditions:
        if condition.condition_id in allowed:
            raise ParameterValidationError("binary summary condition IDs must be unique")
        if condition.response_kind is not ResponseKind.FORCED_CHOICE or len(condition.response_labels) != 2:
            raise ParameterValidationError("binary summary requires exactly two forced-choice labels")
        allowed[condition.condition_id] = condition.response_labels
    groups: dict[tuple[str, str], int] = {}
    totals: dict[str, int] = {}
    observers: dict[str, set[str]] = {}
    for condition_id, label, observer_key in responses:
        if condition_id not in allowed or label not in allowed[condition_id] or not isinstance(observer_key, str) or not observer_key:
            raise ParameterValidationError("response does not match the study design")
        groups[(condition_id, label)] = groups.get((condition_id, label), 0) + 1
        totals[condition_id] = totals.get(condition_id, 0) + 1
        observers.setdefault(condition_id, set()).add(observer_key)
    result = []
    for condition_id in sorted(totals):
        total = totals[condition_id]
        for label in sorted(allowed[condition_id]):
            count = groups.get((condition_id, label), 0)
            low, high = _wilson(count, total)
            result.append(ResponseSummary(condition_id, label, count, total, count / total, low, high, len(observers[condition_id])))
    return tuple(result)


def simulate_binary_responses(
    design: StudyDesign, observer_keys: Sequence[str], probabilities: Mapping[str, float]
) -> tuple[tuple[str, str, str], ...]:
    """Generate explicitly synthetic binary responses for harness tests."""
    if any(condition.response_kind is not ResponseKind.FORCED_CHOICE or len(condition.response_labels) != 2 for condition in design.conditions):
        raise ParameterValidationError("binary simulation requires exactly two forced-choice labels")
    trials = build_trial_sequence(design, observer_keys)
    rng = _deterministic_rng(design.randomization_seed)
    records: list[tuple[str, str, str]] = []
    for trial in trials:
        probability = probabilities.get(trial.condition)
        if not _is_finite_number(probability) or not 0 <= probability <= 1:
            raise ParameterValidationError(f"missing or invalid synthetic probability for {trial.condition}")
        label = trial.expected_response_labels[0] if rng.random() < probability else trial.expected_response_labels[-1]
        records.append((trial.condition, label, _trial_observer_key(design, trial)))
    return tuple(records)


def _fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Conditional two-sided probability-ordering test for a 2x2 count table.

    Integer hypergeometric weights make probability ties exact, without SciPy
    or tolerance-dependent decisions. Row totals are fixed group sizes.
    """
    if any(type(value) is not int or value < 0 for value in (a, b, c, d)):
        raise ParameterValidationError("Fisher table must contain non-negative integer counts")
    first, second, successes = a + b, c + d, a + c
    low, high = max(0, successes - second), min(first, successes)
    observed = math.comb(first, a) * math.comb(second, c)
    weight = math.comb(first, low) * math.comb(second, successes - low)
    tail = 0
    for count in range(low, high + 1):
        if weight <= observed:
            tail += weight
        if count < high:
            weight = weight * (first - count) * (successes - count) // ((count + 1) * (second - successes + count + 1))
    return tail / math.comb(first + second, successes)


def simulate_power(
    sample_size: int,
    effect: float,
    *,
    repetitions: int = 200,
    seed: int | Seed = 0,
    alpha: float = 0.05,
) -> PowerEstimate:
    """Simulate an exact two-sided Fisher test in two independent groups.

    ``sample_size`` is n per group; baseline is 0.5 and ``effect`` is an
    assumed probability difference. This is not repeated-measures study power.
    """
    if type(sample_size) is not int or sample_size < 2 or type(repetitions) is not int or repetitions < 1:
        raise ParameterValidationError("sample_size and repetitions must be positive integers")
    if not _is_finite_number(effect) or not -0.5 <= effect <= 0.5 or not _is_finite_number(alpha) or not 0 < alpha < 1:
        raise ParameterValidationError("effect and alpha are invalid")
    baseline = 0.5
    alternative = baseline + effect
    rng = _deterministic_rng(seed)
    detected = 0
    p_values: dict[tuple[int, int], float] = {}  # local to this run, never persistent
    for _ in range(repetitions):
        reference = sum(rng.random() < baseline for _ in range(sample_size))
        treatment = sum(rng.random() < alternative for _ in range(sample_size))
        key = (min(reference, treatment), max(reference, treatment))
        p_value = p_values.get(key)
        if p_value is None:
            p_value = _fisher_exact_two_sided(reference, sample_size - reference, treatment, sample_size - treatment)
            p_values[key] = p_value
        if p_value <= alpha:
            detected += 1
    return PowerEstimate(effect, detected / repetitions, repetitions, sample_size, alpha, baseline, Seed(seed), detected)




def simulate_continuous_responses(
    design: StudyDesign,
    observer_keys: Sequence[str],
    means: Mapping[str, float],
    *,
    noise: float = 0.1,
    seed: int | Seed = 0,
    response_kind: ResponseKind = ResponseKind.CONTINUOUS_MAGNITUDE,
    unit: str = "arbitrary_units",
) -> tuple[SyntheticObservation, ...]:
    """Generate reproducible continuous or localization responses under assumptions."""
    if response_kind not in {ResponseKind.CONTINUOUS_MAGNITUDE, ResponseKind.LOCALIZATION}:
        raise ParameterValidationError("continuous simulation requires magnitude or localization response kind")
    if not math.isfinite(noise) or noise < 0 or not unit:
        raise ParameterValidationError("continuous simulation noise and unit are invalid")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)) for value in means.values()):
        raise ParameterValidationError("continuous means must be finite numbers")
    rng = _deterministic_rng(seed)
    result = []
    for trial in build_trial_sequence(design, observer_keys):
        if trial.condition not in means:
            raise ParameterValidationError(f"missing synthetic mean for {trial.condition}")
        value = float(means[trial.condition]) + rng.gauss(0.0, noise)
        result.append(SyntheticObservation(trial.trial_id, _trial_observer_key(design, trial), trial.condition, response_kind, value, unit))
    return tuple(result)


def _poisson(rng: random.Random, rate: float) -> int:
    """Sample an exact Poisson sum with subrates bounded against underflow."""
    if rate == 0.0:
        return 0
    parts = math.ceil(rate / 32.0)
    threshold = math.exp(-(rate / parts))
    total = 0
    for _ in range(parts):
        product = rng.random()
        while product > threshold:
            total += 1
            product *= rng.random()
    return total


def simulate_event_counts(
    design: StudyDesign,
    observer_keys: Sequence[str],
    rates: Mapping[str, float],
    *,
    seed: int | Seed = 0,
    unit: str = "events",
) -> tuple[SyntheticObservation, ...]:
    """Generate deterministic Poisson event-count responses under assumed rates."""
    if not unit or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)) or value < 0 for value in rates.values()):
        raise ParameterValidationError("event rates must be finite and non-negative")
    rng = _deterministic_rng(seed)
    result = []
    for trial in build_trial_sequence(design, observer_keys):
        if trial.condition not in rates:
            raise ParameterValidationError(f"missing synthetic rate for {trial.condition}")
        value = _poisson(rng, float(rates[trial.condition]))
        result.append(SyntheticObservation(trial.trial_id, _trial_observer_key(design, trial), trial.condition, ResponseKind.EVENT_COUNT, value, unit))
    return tuple(result)


def simulate_reaction_times(
    design: StudyDesign,
    observer_keys: Sequence[str],
    medians: Mapping[str, float],
    *,
    sigma: float = 0.25,
    seed: int | Seed = 0,
) -> tuple[SyntheticObservation, ...]:
    """Generate positive log-normal reaction times from assumed medians."""
    if not math.isfinite(sigma) or sigma < 0 or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)) or value <= 0 for value in medians.values()):
        raise ParameterValidationError("reaction-time medians and sigma are invalid")
    rng = _deterministic_rng(seed)
    result = []
    for trial in build_trial_sequence(design, observer_keys):
        if trial.condition not in medians:
            raise ParameterValidationError(f"missing synthetic reaction-time median for {trial.condition}")
        value = rng.lognormvariate(math.log(float(medians[trial.condition])), sigma)
        result.append(SyntheticObservation(trial.trial_id, _trial_observer_key(design, trial), trial.condition, ResponseKind.REACTION_TIME, value, "seconds"))
    return tuple(result)


def summarize_numeric_responses(observations: Sequence[SyntheticObservation]) -> tuple[NumericSummary, ...]:
    """Describe synthetic pooled trials; normal intervals need independent trials."""
    groups: dict[tuple[str, ResponseKind, str], list[float]] = {}
    observers: dict[tuple[str, ResponseKind, str], set[str]] = {}
    for observation in observations:
        if observation.claim_level is not ClaimLevel.OBSERVER_HYPOTHESIS or observation.response_kind is ResponseKind.FORCED_CHOICE:
            raise ParameterValidationError("numeric summary accepts only synthetic numeric observations")
        if not isinstance(observation.value, (int, float)) or isinstance(observation.value, bool):
            raise ParameterValidationError("numeric summary received a non-numeric value")
        groups.setdefault((observation.condition_id, observation.response_kind, observation.unit), []).append(float(observation.value))
        observers.setdefault((observation.condition_id, observation.response_kind, observation.unit), set()).add(observation.observer_key)
    result = []
    for (condition_id, response_kind, unit), values in sorted(groups.items(), key=lambda item: item[0]):
        mean = sum(values) / len(values)
        if len(values) == 1:
            standard_deviation = low = high = None
        else:
            standard_deviation = statistics.stdev(values)
            half_width = statistics.NormalDist().inv_cdf(0.975) * standard_deviation / math.sqrt(len(values))
            low, high = mean - half_width, mean + half_width
        result.append(NumericSummary(condition_id, response_kind, unit, len(values), mean, standard_deviation, low, high, len(observers[(condition_id, response_kind, unit)])))
    return tuple(result)


def simulate_power_curve(
    sample_size: int,
    effects: Sequence[float],
    *,
    repetitions: int = 200,
    seed: int | Seed = 0,
) -> tuple[PowerEstimate, ...]:
    """Return a deterministic curve of assumed-effect power points."""
    if not effects:
        raise ParameterValidationError("power curve requires at least one assumed effect")
    if not all(_is_finite_number(effect) for effect in effects):
        raise ParameterValidationError("power curve effects must be finite numbers")
    return tuple(simulate_power(sample_size, float(effect), repetitions=repetitions, seed=int(Seed(seed)) + index) for index, effect in enumerate(effects))


def write_analysis_plan(design: StudyDesign, path: Path) -> Path:
    """Write a stable, machine-readable study design without participant data."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return atomic_write_text(path, json.dumps(design.to_dict(), indent=2, sort_keys=True) + "\n")


def default_study_design() -> StudyDesign:
    """Return a data-free illustration requiring external study/ethics/calibration."""
    return StudyDesign(
        study_id="duckrabbit-v04-demo",
        conditions=(
            ConditionSpec("duck_default", "visual.duck_rabbit", {}, ("duck", "rabbit")),
            ConditionSpec("sifi_one_beep", "audiovisual.sound_induced_flash", {"beep_count": 1}, ("one", "two")),
            ConditionSpec("sifi_two_beep", "audiovisual.sound_induced_flash", {"beep_count": 2}, ("one", "two")),
            ConditionSpec("temporal_sync", "audiovisual.temporal_ventriloquism", {"config": {"sync_offset": 0.0}}, ("early", "late")),
            ConditionSpec("temporal_early", "audiovisual.temporal_ventriloquism", {"config": {"sync_offset": -120.0}}, ("early", "late")),
            ConditionSpec("temporal_late", "audiovisual.temporal_ventriloquism", {"config": {"sync_offset": 120.0}}, ("early", "late")),
        ),
        trials_per_condition=8,
        observers=24,
        randomization_seed=Seed(0),
        estimands=(
            Estimand(
                "sifi_flash_count_contrast",
                ResponseKind.FORCED_CHOICE,
                AnalysisModel.LOGISTIC_MIXED,
                "log odds of choosing 'two': sifi_two_beep minus sifi_one_beep",
                "sifi_one_beep",
            ),
            Estimand(
                "temporal_binding_offset_contrast",
                ResponseKind.FORCED_CHOICE,
                AnalysisModel.LOGISTIC_MIXED,
                "log odds of choosing 'late': temporal_early and temporal_late versus temporal_sync (categorical offsets -120/0/+120 ms)",
                "temporal_sync",
            ),
        ),
    )


def default_model_specs() -> tuple[AnalysisModelSpec, ...]:
    """Return illustrative model templates without fitted coefficients or approval."""
    return (
        AnalysisModelSpec(AnalysisModel.LOGISTIC_MIXED, "response ~ condition + (1|participant) + (1|item)", "binomial", "logit", ("participant", "item")),
        AnalysisModelSpec(AnalysisModel.LINEAR_MIXED, "magnitude ~ condition + (1|participant) + (1|item)", "Gaussian", "identity", ("participant", "item")),
        AnalysisModelSpec(AnalysisModel.LOGNORMAL_MIXED, "reaction_time ~ condition + (1|participant) + (1|item)", "lognormal", "log", ("participant", "item")),
        AnalysisModelSpec(AnalysisModel.POISSON_OR_ORDINAL, "count ~ condition + (1|participant) + (1|item)", "Poisson/negative-binomial/ordinal", "log or cumulative", ("participant", "item")),
        AnalysisModelSpec(AnalysisModel.TRANSITION_RATE, "reversal_transition ~ condition + (1|participant)", "survival or transition-rate", "hazard", ("participant",)),
    )


__all__ = [
    "AggregateRecord",
    "AnalysisModel",
    "AnalysisModelSpec",
    "ConditionSpec",
    "Estimand",
    "PowerEstimate",
    "PowerPoint",
    "SyntheticObservation",
    "NumericSummary",
    "ParticipantId",
    "ResponseKind",
    "ResponseSummary",
    "StudyDesign",
    "StimulusReference",
    "TrialDisposition",
    "TrialRecord",
    "build_trial_sequence",
    "default_study_design",
    "default_model_specs",
    "simulate_binary_responses",
    "simulate_power",
    "simulate_power_curve",
    "simulate_continuous_responses",
    "simulate_event_counts",
    "simulate_reaction_times",
    "summarize_numeric_responses",
    "summarize_binary_responses",
    "write_analysis_plan",
]
