"""Pytest configuration for the DuckRabbit package."""

from __future__ import annotations

import pytest

from duckrabbit.publication import generate_publication_outputs


@pytest.fixture(scope="session")
def publication_bundle(tmp_path_factory):
    """One deterministic publication bundle shared by read-only consumers."""
    root = tmp_path_factory.mktemp("publication_bundle")
    generate_publication_outputs(root)
    return root
