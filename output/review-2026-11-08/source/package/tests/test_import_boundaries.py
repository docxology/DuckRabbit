"""The public facade keeps optional analysis and publication imports lazy."""

import importlib
import json
from pathlib import Path
import subprocess
import sys
import typing

import pytest

import duckrabbit


def test_import_and_ordinary_generation_do_not_load_publication_stack(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-c", """
import json
import sys
import duckrabbit
artifact = duckrabbit.generate('visual.duck_rabbit')
assert artifact.width > 0
print(json.dumps(sorted(sys.modules)))
"""],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    )
    modules = json.loads(result.stdout)
    for name in ("duckrabbit.audit", "duckrabbit.publication", "duckrabbit.scholarship", "duckrabbit.observer_analysis", "PIL"):
        assert name not in modules


def test_every_lazy_export_has_the_original_owning_module_identity() -> None:
    for name, module_name in duckrabbit._LAZY_EXPORTS.items():
        original = getattr(importlib.import_module(f"duckrabbit.{module_name}"), name)
        assert getattr(duckrabbit, name) is original
        assert duckrabbit.__dict__[name] is original
        assert name in dir(duckrabbit)
    assert set(duckrabbit.__all__).issubset(dir(duckrabbit))


def test_unknown_public_attributes_fail_and_generate_annotations_still_resolve() -> None:
    with pytest.raises(AttributeError, match="no attribute 'not_an_export'"):
        getattr(duckrabbit, "not_an_export")
    hints = typing.get_type_hints(duckrabbit.generate)
    assert hints["seed"] is int
    assert hints["return"] == duckrabbit.CanonicalArtifact


def test_star_import_preserves_the_documented_public_surface() -> None:
    namespace = {}
    exec("from duckrabbit import *", namespace)
    assert {name for name in namespace if name != "__builtins__"} == set(duckrabbit.__all__)
    assert namespace["generate"] is duckrabbit.generate
    assert namespace["load_evidence_matrix"]()[0]


def test_catalog_cli_does_not_load_auditing_or_publication_modules(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-c", """
import contextlib
import io
import json
import sys
from duckrabbit.cli import main
from duckrabbit.generators import default_registry
with contextlib.redirect_stdout(io.StringIO()) as captured:
    assert main(['list', '--implemented-only', '--json']) == 0
assert len(json.loads(captured.getvalue())) == len(default_registry.list())
print(json.dumps(sorted(sys.modules)))
"""],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    )
    modules = json.loads(result.stdout)
    for name in ("duckrabbit.audit", "duckrabbit.publication", "duckrabbit.synthetic_psychophysics", "PIL"):
        assert name not in modules
