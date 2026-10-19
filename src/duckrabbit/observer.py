"""Typed observer-study records kept separate from deterministic generation."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
import math
import random
from types import MappingProxyType

from .parameters import DurationSeconds, Seed
from .serialization import jsonable


def _freeze_overrides(value: object) -> object:
    """Copy nested override containers into immutable snapshots."""
    return _freeze_normalized_overrides(jsonable(value))


def _freeze_normalized_overrides(value: object) -> object:
    """Freeze a tree already normalized to JSON primitives."""
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_normalized_overrides(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_normalized_overrides(item) for item in value)
    return value


def _thaw_overrides(value: object) -> object:
    """Return fresh serialization containers for a frozen override snapshot."""
    if isinstance(value, Mapping):
        return {key: _thaw_overrides(item) for key, item in value.items()}
    if isinstance(value, (tuple, frozenset)):
        return [_thaw_overrides(item) for item in value]
    return value


def _deterministic_rng(seed: int | Seed) -> random.Random:
    """Return a local, reproducible RNG; this is never a security primitive."""
    return random.Random(int(Seed(seed)))  # nosec B311 -- study randomization is deterministic, not cryptographic


@dataclass(frozen=True)
class TrialSpec:
    """A preregistered stimulus trial with no personally identifying data."""

    trial_id: str
    illusion_id: str
    condition: str
    seed: Seed
    expected_response_labels: tuple[str, ...]
    parameter_overrides: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.trial_id or not self.illusion_id or not self.condition:
            raise ValueError("trial identity and condition are required")
        if not isinstance(self.seed, Seed):
            object.__setattr__(self, "seed", Seed(self.seed))
        if not self.expected_response_labels or not all(isinstance(item, str) and item for item in self.expected_response_labels):
            raise ValueError("trial response labels must be non-empty strings")
        if not isinstance(self.parameter_overrides, Mapping) or not all(isinstance(key, str) and key for key in self.parameter_overrides):
            raise ValueError("trial parameter_overrides must be a string-keyed mapping")
        object.__setattr__(self, "parameter_overrides", _freeze_overrides(self.parameter_overrides))
        object.__setattr__(self, "expected_response_labels", tuple(self.expected_response_labels))

    def to_dict(self) -> dict[str, object]:
        """Serialize trial identity and declared condition parameters."""
        return {
            "trial_id": self.trial_id,
            "illusion_id": self.illusion_id,
            "condition": self.condition,
            "seed": int(self.seed),
            "expected_response_labels": list(self.expected_response_labels),
            "parameter_overrides": _thaw_overrides(self.parameter_overrides),
        }


@dataclass(frozen=True)
class ObserverResponse:
    """One response record keyed only by a pseudonymous observer identifier."""

    trial_id: str
    observer_key: str
    response: str
    reaction_time: DurationSeconds

    def __post_init__(self) -> None:
        if not self.trial_id or not self.observer_key or not self.response:
            raise ValueError("observer response identity and response are required")
        if not isinstance(self.reaction_time, DurationSeconds):
            object.__setattr__(self, "reaction_time", DurationSeconds(self.reaction_time))


@dataclass(frozen=True)
class ObserverAggregate:
    """Aggregate response statistics without retaining raw identifying data."""

    illusion_id: str
    condition: str
    response_counts: tuple[tuple[str, int], ...]
    mean_reaction_time: float
    sample_count: int

    def __post_init__(self) -> None:
        if not self.illusion_id or not self.condition:
            raise ValueError("aggregate identity is required")
        if type(self.sample_count) is not int or self.sample_count < 1:
            raise ValueError("aggregate sample_count must be positive")
        if not math.isfinite(self.mean_reaction_time) or self.mean_reaction_time <= 0:
            raise ValueError("aggregate mean_reaction_time must be finite and positive")
        if not self.response_counts or any(type(count) is not int or count < 0 for _, count in self.response_counts):
            raise ValueError("aggregate response counts are invalid")
        labels = [label for label, _ in self.response_counts]
        if not all(isinstance(label, str) and label for label in labels) or len(set(labels)) != len(labels):
            raise ValueError("aggregate response labels must be non-empty and unique")
        if sum(count for _, count in self.response_counts) != self.sample_count:
            raise ValueError("aggregate response counts must sum to sample_count")
        object.__setattr__(self, "response_counts", tuple(tuple(item) for item in self.response_counts))


def randomized_trials(trials: Iterable[TrialSpec], seed: int | Seed) -> tuple[TrialSpec, ...]:
    """Return a reproducible randomized trial order using a local RNG."""
    ordered = list(trials)
    rng = _deterministic_rng(seed)
    rng.shuffle(ordered)
    return tuple(ordered)


def aggregate_responses(trials: Iterable[TrialSpec], responses: Iterable[ObserverResponse]) -> tuple[ObserverAggregate, ...]:
    """Aggregate responses by illusion and condition with explicit missing-data checks."""
    trial_map: dict[str, TrialSpec] = {}
    for trial in trials:
        if trial.trial_id in trial_map:
            raise ValueError(f"duplicate trial_id {trial.trial_id}")
        trial_map[trial.trial_id] = trial
    groups: dict[tuple[str, str], list[ObserverResponse]] = {}
    seen: set[tuple[str, str]] = set()
    for response in responses:
        identity = (response.trial_id, response.observer_key)
        if identity in seen:
            raise ValueError(f"duplicate response for trial and observer {identity}")
        seen.add(identity)
        trial = trial_map.get(response.trial_id)
        if trial is None:
            raise ValueError(f"response references unknown trial {response.trial_id}")
        if response.response not in trial.expected_response_labels:
            raise ValueError(f"response label {response.response!r} is not allowed for trial {response.trial_id}")
        groups.setdefault((trial.illusion_id, trial.condition), []).append(response)
    result = []
    for (illusion_id, condition), group in sorted(groups.items()):
        counts: dict[str, int] = {}
        for response in group:
            counts[response.response] = counts.get(response.response, 0) + 1
        result.append(
            ObserverAggregate(
                illusion_id,
                condition,
                tuple(sorted(counts.items())),
                sum(response.reaction_time.value for response in group) / len(group),
                len(group),
            )
        )
    return tuple(result)
