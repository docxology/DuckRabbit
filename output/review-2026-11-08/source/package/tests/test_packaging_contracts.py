"""Distribution resources must work without a source-checkout layout."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from duckrabbit.generators import default_registry


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("source", ["data/evidence_matrix.json", "docs/manuscript/references.bib"])
def test_bundled_evidence_is_identical_to_checkout_sources(source: str) -> None:
    original = ROOT / source
    bundled = ROOT / "src" / "duckrabbit" / "_resources" / original.name
    assert bundled.read_bytes() == original.read_bytes()


def test_runtime_evidence_and_claims_work_outside_a_checkout(tmp_path: Path) -> None:
    package_root = tmp_path / "site-packages"
    shutil.copytree(ROOT / "src" / "duckrabbit", package_root / "duckrabbit", ignore=shutil.ignore_patterns("__pycache__"))
    environment = dict(os.environ, PYTHONPATH=str(package_root))
    result = subprocess.run(
        [sys.executable, "-c", """
import json
from pathlib import Path
import duckrabbit
sources, entries = duckrabbit.load_evidence_matrix()
claims = duckrabbit.default_claim_registry()
artifact = duckrabbit.generate('visual.duck_rabbit')
print(json.dumps({'package': str(Path(duckrabbit.__file__).resolve()),
                  'sources': len(sources), 'entries': len(entries),
                  'claims': bool(claims), 'width': artifact.width}))
"""],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert Path(payload["package"]).is_relative_to(package_root)
    assert payload["entries"] > len(default_registry.list())
    assert payload["sources"] > 0 and payload["claims"] and payload["width"] > 0
