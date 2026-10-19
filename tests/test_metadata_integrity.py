"""Metadata shape and DOI role drift must fail closed."""

import json
from pathlib import Path
import shutil
import re

import pytest

from duckrabbit.metadata import validate_project_metadata


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def metadata_root(tmp_path: Path) -> Path:
    for name in ("pyproject.toml", "CITATION.cff", "codemeta.json", ".zenodo.json", "docs/manuscript/config.yaml"):
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    return tmp_path


@pytest.mark.parametrize(
    ("name", "field", "value"),
    [(".zenodo.json", "creators", []), (".zenodo.json", "creators", [1]),
     ("codemeta.json", "author", []), ("codemeta.json", "author", [None]),
     (".zenodo.json", "doi", "10.5281/zenodo.99999999"),
     ("codemeta.json", "@id", "https://doi.org/10.5281/zenodo.99999999"),
     ("codemeta.json", "identifier", "https://doi.org/10.5281/zenodo.99999999")],
)
def test_malformed_metadata_and_doi_role_drift_fail(metadata_root: Path, name: str, field: str, value: object) -> None:
    path = metadata_root / name
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload[field] = value
    path.write_text(json.dumps(payload), encoding="utf-8")
    report = validate_project_metadata(metadata_root)
    assert report.status == "failed"
    assert report.errors


def test_unknown_doi_status_and_citation_identifier_drift_fail(metadata_root: Path) -> None:
    config = metadata_root / "docs/manuscript/config.yaml"
    original = config.read_text(encoding="utf-8")
    config.write_text(original.replace('doi_status: "published"', 'doi_status: "nonsense"'), encoding="utf-8")
    assert any("doi_status" in error for error in validate_project_metadata(metadata_root).errors)
    config.write_text(original, encoding="utf-8")
    citation = metadata_root / "CITATION.cff"
    citation.write_text(citation.read_text(encoding="utf-8").replace("value: 10.5281/zenodo.21419693", "value: 10.5281/zenodo.99999999"), encoding="utf-8")
    assert any("DOI identifiers" in error for error in validate_project_metadata(metadata_root).errors)


def test_empty_pyproject_authors_return_a_failed_report(metadata_root: Path) -> None:
    project = metadata_root / "pyproject.toml"
    project.write_text(project.read_text(encoding="utf-8").replace('authors = [{name = "Daniel Ari Friedman"}]', 'authors = []'), encoding="utf-8")
    assert validate_project_metadata(metadata_root).status == "failed"


def test_consistent_forthcoming_metadata_without_identifiers_is_allowed(metadata_root: Path) -> None:
    config = metadata_root / "docs/manuscript/config.yaml"
    config.write_text(config.read_text(encoding="utf-8").replace('doi: "10.5281/zenodo.21419693"', 'doi: ""').replace('doi_status: "published"', 'doi_status: "forthcoming"'), encoding="utf-8")
    citation = metadata_root / "CITATION.cff"
    text = citation.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^doi:.*\n", "", text)
    text = re.sub(r"(?ms)^identifiers:\n.*?(?=^abstract:)", "", text)
    citation.write_text(text, encoding="utf-8")
    for name, keys in ((".zenodo.json", ("doi",)), ("codemeta.json", ("@id", "identifier"))):
        path = metadata_root / name
        payload = json.loads(path.read_text(encoding="utf-8"))
        for key in keys:
            payload.pop(key)
        path.write_text(json.dumps(payload), encoding="utf-8")
    report = validate_project_metadata(metadata_root)
    assert report.status == "passed", report.errors
