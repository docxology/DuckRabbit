"""Pytest configuration for the DuckRabbit package."""

from __future__ import annotations

import pytest

from duckrabbit.publication import generate_publication_outputs
from pathlib import Path
from duckrabbit.manuscript_variables import generate_variables, hydrate_manuscript_files, save_variables


@pytest.fixture(scope="session")
def publication_bundle(tmp_path_factory):
    """One deterministic publication bundle shared by read-only consumers."""
    root = tmp_path_factory.mktemp("publication_bundle")
    generate_publication_outputs(root)
    variables = generate_variables()
    save_variables(variables, root / "data" / "manuscript_variables.json")
    hydrate_manuscript_files(variables, Path(__file__).resolve().parents[1], output_dir=root / "manuscript")
    return root
