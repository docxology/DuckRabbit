"""Drift guards between checked-in experiment configs and live registries.

These tests keep the prose-layer experiment/configuration files
(``experiment_plan.yaml``, ``domain_profile.yaml``, ``data/claim_ledger.yaml``,
``data/observer_analysis_plan.json``) pinned to the package surfaces that
actually generate the publication outputs, and pin the Monte Carlo power
estimator to the closed-form two-proportion result.
"""

from __future__ import annotations

import json
import math
import statistics
import tomllib
from pathlib import Path

import pytest
import yaml

from duckrabbit.evidence import load_evidence_matrix
from duckrabbit.formalism import formalism_registry
from duckrabbit.generators import build_default_registry
from duckrabbit.observer_analysis import (
    ParameterValidationError,
    _wilson,
    default_study_design,
    simulate_power,
    summarize_binary_responses,
)
from duckrabbit.publication import publication_caption_specs, publication_table_payloads
from duckrabbit.publication_specs import PUBLICATION_FIGURE_LABELS
from duckrabbit.taxonomy import taxonomy_entries


ROOT = Path(__file__).resolve().parents[1]


def _plan() -> dict[str, object]:
    return yaml.safe_load((ROOT / "experiment_plan.yaml").read_text(encoding="utf-8"))


def test_experiment_plan_figures_and_tables_match_code_labels() -> None:
    plan = _plan()
    assert plan["expected_figures"] == list(PUBLICATION_FIGURE_LABELS)
    table_labels = {payload["label"] for payload in publication_table_payloads().values()}
    assert set(plan["expected_tables"]) == table_labels


def test_experiment_plan_conditions_are_internally_consistent() -> None:
    plan = _plan()
    condition_names = {condition["name"] for condition in plan["conditions"]}
    assert set(plan["baselines"]) <= condition_names
    assert set(plan["ablations"]) <= condition_names
    metric_names = {plan["metrics"]["primary"]["name"], *(m["name"] for m in plan["metrics"]["secondary"])}
    assert all(isinstance(name, str) and name for name in metric_names)


def test_domain_profile_artifact_expectations_exist() -> None:
    profile = yaml.safe_load((ROOT / "domain_profile.yaml").read_text(encoding="utf-8"))
    for expectation in profile["artifact_expectations"]:
        assert (ROOT / expectation).is_file(), expectation


def test_domain_profile_required_packages_are_declared() -> None:
    profile = yaml.safe_load((ROOT / "domain_profile.yaml").read_text(encoding="utf-8"))
    dependencies = set(tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["dependencies"])
    for package in profile["required_packages"]:
        assert any(dep.split(">=")[0].split("==")[0] == package for dep in dependencies), package


def test_claim_ledger_counts_match_live_registries() -> None:
    ledger = yaml.safe_load((ROOT / "data" / "claim_ledger.yaml").read_text(encoding="utf-8"))
    values = {claim["claim_id"]: claim["value"] for claim in ledger["claims"] if claim["kind"] == "number"}
    sources, evidence = load_evidence_matrix()
    assert values["implemented-generator-count"] == len(build_default_registry().list())
    assert values["catalog-entry-count"] == len(taxonomy_entries())
    assert values["evidence-record-count"] == len(evidence)
    assert values["scholarly-source-count"] == len(sources)
    assert values["publication-figure-count"] == len(PUBLICATION_FIGURE_LABELS)
    assert values["publication-table-count"] == len(publication_table_payloads())
    assert values["caption-spec-count"] == len(publication_caption_specs())
    assert values["formalism-definition-count"] == len(formalism_registry())


def test_observer_analysis_plan_matches_default_study_design() -> None:
    plan = json.loads((ROOT / "data" / "observer_analysis_plan.json").read_text(encoding="utf-8"))
    assert plan == default_study_design().to_dict()


def test_simulate_power_matches_two_proportion_closed_form() -> None:
    # n=24 per arm, baseline 0.5, effect 0.2: SE_H1 = sqrt((0.25+0.21)/24),
    # power = Phi(effect/SE - z_{0.975}) ~= 0.3032. The pre-fix estimator
    # divided the pooled variance by 2n and returned ~0.53 for this point.
    estimate = simulate_power(24, 0.2, repetitions=600, seed=7)
    se = math.sqrt((0.5 * 0.5 + 0.7 * 0.3) / 24)
    expected = statistics.NormalDist().cdf(0.2 / se - statistics.NormalDist().inv_cdf(0.975))
    assert estimate.repetitions == 600
    assert estimate.power == pytest.approx(expected, abs=0.05)


def test_simulate_power_null_effect_calibrates_to_alpha() -> None:
    # Under H0 the two-proportion z statistic is standard normal, so the
    # nominal 5% test must reject about 5% of the time (the pre-fix SE made
    # this ~16.6%).
    estimate = simulate_power(24, 0.0, repetitions=1000, seed=11)
    assert estimate.power == pytest.approx(0.05, abs=0.03)


def test_wilson_interval_matches_closed_form_and_rejects_invalid_input() -> None:
    low, high = _wilson(7, 24)
    assert low == pytest.approx(0.1491, abs=1e-3)
    assert high == pytest.approx(0.4917, abs=1e-3)
    with pytest.raises(ParameterValidationError):
        _wilson(0, 0)
    with pytest.raises(ParameterValidationError):
        _wilson(25, 24)


def test_binary_summary_intervals_are_wilson_intervals() -> None:
    conditions = default_study_design().conditions
    responses = [
        (conditions[0].condition_id, conditions[0].response_labels[0], f"observer-{index}")
        for index in range(18)
    ]
    responses.extend(
        (conditions[0].condition_id, conditions[0].response_labels[0], f"extra-{index}")
        for index in range(6)
    )
    responses.extend(
        (conditions[0].condition_id, conditions[0].response_labels[-1], f"other-{index}")
        for index in range(6)
    )
    summaries = summarize_binary_responses(conditions, responses)
    top = summaries[0]
    assert top.count == 24 and top.total == 30
    low, high = _wilson(24, 30)
    assert (top.interval_low, top.interval_high) == pytest.approx((low, high))
