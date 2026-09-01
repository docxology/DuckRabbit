"""Live registry count assertions and modular release-contract tests.

Replaces duplicated mutable catalog counts in prose with live registry
assertions plus one intentional versioned catalog snapshot (the
``expected`` map below, bumped only in a deliberate version release).
"""

from __future__ import annotations

from collections import Counter

import duckrabbit
from duckrabbit.audit import run_audit
from duckrabbit.taxonomy import taxonomy_entries

EXPECTED_CATALOG_SNAPSHOT_V0_5_0 = {
    "implemented": 17,
    "planned": 0,
    "input_required": 1,
}


def test_live_catalog_matches_versioned_snapshot() -> None:
    counts = Counter(entry.implementation_status.value for entry in taxonomy_entries())
    # Counter equality treats missing keys as zero, so this verifies the exact
    # snapshot (including the ``planned: 0`` entry) without requiring Counter
    # to emit zero-count keys, which ``dict(Counter)`` never does.
    assert counts == Counter(EXPECTED_CATALOG_SNAPSHOT_V0_5_0)


def test_every_registered_generator_has_a_live_taxonomy_entry() -> None:
    catalog_ids = {entry.illusion_id for entry in taxonomy_entries()}
    assert len(catalog_ids) == sum(EXPECTED_CATALOG_SNAPSHOT_V0_5_0.values())
    for spec in duckrabbit.default_registry.list():
        assert spec.illusion_id in catalog_ids


def test_strict_release_mode_fails_without_publication_bundle(tmp_path) -> None:
    report = run_audit(output_root=tmp_path / "missing", release=True)
    assert report.issues, "strict release audit must fail without publication outputs"


def test_strict_release_mode_accepts_generated_bundle(tmp_path) -> None:
    duckrabbit.generate_publication_outputs(tmp_path)
    report = run_audit(output_root=tmp_path, release=True)
    blocking = [issue for issue in report.issues if issue.severity == "error"]
    assert not blocking, [issue.message for issue in blocking]
