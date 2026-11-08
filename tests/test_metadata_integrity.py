"""Metadata shape and published/forthcoming DOI roles must fail closed."""

import json
from pathlib import Path
import re
import shutil

import pytest
import yaml

from duckrabbit.metadata import validate_project_metadata


ROOT = Path(__file__).resolve().parents[1]
# Owned, already-published v0.5.0 identities exercise the published schema only;
# these fixtures do not assert that the checkout's next version has been minted.
PUBLISHED_CONCEPT_DOI = "10.5281/zenodo.21419693"
PUBLISHED_VERSION_DOI = "10.5281/zenodo.21419694"
PUBLISHED_VERSION_RECORD = "https://zenodo.org/records/21419694"


def _write_yaml(path: Path, payload: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _metadata_tree(root: Path, status: str) -> Path:
    for name in ("pyproject.toml", "CITATION.cff", "codemeta.json", ".zenodo.json", "docs/manuscript/config.yaml"):
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    published = status == "published"
    config_path = root / "docs/manuscript/config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["publication"]["doi"] = PUBLISHED_CONCEPT_DOI if published else ""
    config["publication"]["doi_status"] = status
    for key in ("version_doi", "version_record"):
        config["publication"].pop(key, None)
    if published:
        config["publication"]["version_doi"] = PUBLISHED_VERSION_DOI
        config["publication"]["version_record"] = PUBLISHED_VERSION_RECORD
    _write_yaml(config_path, config)
    citation_path = root / "CITATION.cff"
    citation = yaml.safe_load(citation_path.read_text(encoding="utf-8"))
    for key in ("doi", "identifiers"):
        citation.pop(key, None)
    if published:
        citation["doi"] = PUBLISHED_VERSION_DOI
        citation["identifiers"] = [
            {"type": "doi", "value": PUBLISHED_CONCEPT_DOI},
            {"type": "doi", "value": PUBLISHED_VERSION_DOI},
        ]
    _write_yaml(citation_path, citation)
    for name, fields in (
        (".zenodo.json", {"doi": PUBLISHED_CONCEPT_DOI}),
        ("codemeta.json", {"@id": f"https://doi.org/{PUBLISHED_CONCEPT_DOI}", "identifier": f"https://doi.org/{PUBLISHED_VERSION_DOI}"}),
    ):
        path = root / name
        payload = json.loads(path.read_text(encoding="utf-8"))
        for key, value in fields.items():
            payload.pop(key, None)
            if published:
                payload[key] = value
        path.write_text(json.dumps(payload), encoding="utf-8")
    return root


@pytest.fixture(params=["published", "forthcoming"])
def metadata_root(tmp_path: Path, request: pytest.FixtureRequest) -> Path:
    return _metadata_tree(tmp_path, request.param)


@pytest.fixture
def published_root(tmp_path: Path) -> Path:
    return _metadata_tree(tmp_path, "published")


@pytest.fixture
def forthcoming_root(tmp_path: Path) -> Path:
    return _metadata_tree(tmp_path, "forthcoming")


def test_owned_published_and_forthcoming_fixtures_are_consistent(metadata_root: Path) -> None:
    report = validate_project_metadata(metadata_root)
    assert report.status == "passed", report.errors
    assert report.files == ("pyproject.toml", "CITATION.cff", "codemeta.json", ".zenodo.json", "docs/manuscript/config.yaml")


@pytest.mark.parametrize(
    ("name", "field", "value"),
    [(".zenodo.json", "creators", []), (".zenodo.json", "creators", [1]),
     ("codemeta.json", "author", []), ("codemeta.json", "author", [None]),
     (".zenodo.json", "doi", PUBLISHED_VERSION_DOI),
     ("codemeta.json", "@id", f"https://doi.org/{PUBLISHED_VERSION_DOI}"),
     ("codemeta.json", "identifier", f"https://doi.org/{PUBLISHED_CONCEPT_DOI}")],
)
def test_malformed_metadata_and_doi_role_drift_fail(metadata_root: Path, name: str, field: str, value: object) -> None:
    path = metadata_root / name
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload[field] = value
    path.write_text(json.dumps(payload), encoding="utf-8")
    report = validate_project_metadata(metadata_root)
    assert report.status == "failed"
    assert report.errors


@pytest.mark.parametrize("value", ["independently-stale", "", None])
def test_software_version_cannot_drift_independently(metadata_root: Path, value: object) -> None:
    path = metadata_root / "codemeta.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["softwareVersion"] = value
    path.write_text(json.dumps(payload), encoding="utf-8")
    report = validate_project_metadata(metadata_root)
    assert report.status == "failed"
    assert any("codemeta softwareVersion" in error for error in report.errors)


def test_software_version_is_required(metadata_root: Path) -> None:
    path = metadata_root / "codemeta.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    del payload["softwareVersion"]
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert any("codemeta softwareVersion" in error for error in validate_project_metadata(metadata_root).errors)


@pytest.mark.parametrize(
    ("section", "field", "value", "expected"),
    [("authors", "name", "Other Author", "config author"),
     ("authors", "orcid", "0000-0000-0000-0000", "ORCID"),
     ("paper", "version", "independently-stale", "version"),
     ("paper", "title", "Other title", "title"),
     ("metadata", "license", "GPL", "license"),
     ("publication", "doi", "10.5281/zenodo.XXXX", "placeholder"),
     ("publication", "doi_status", "nonsense", "doi_status")],
)
def test_metadata_audit_catches_each_identity_field(metadata_root: Path, section: str, field: str, value: str, expected: str) -> None:
    path = metadata_root / "docs/manuscript/config.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    record = payload[section][0] if section == "authors" else payload[section]
    record[field] = value
    _write_yaml(path, payload)
    report = validate_project_metadata(metadata_root)
    assert report.status == "failed"
    assert any(expected in error for error in report.errors)


def test_published_doi_requires_published_status(published_root: Path) -> None:
    path = published_root / "docs/manuscript/config.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["publication"]["doi_status"] = "forthcoming"
    _write_yaml(path, payload)
    assert any("doi_status must be published" in error for error in validate_project_metadata(published_root).errors)


def test_empty_doi_requires_forthcoming_status(forthcoming_root: Path) -> None:
    path = forthcoming_root / "docs/manuscript/config.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["publication"]["doi_status"] = "published"
    _write_yaml(path, payload)
    assert any("doi_status must be forthcoming" in error for error in validate_project_metadata(forthcoming_root).errors)


def test_citation_identifier_drift_fails(metadata_root: Path) -> None:
    path = metadata_root / "CITATION.cff"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["identifiers"] = [{"type": "doi", "value": PUBLISHED_CONCEPT_DOI}]
    _write_yaml(path, payload)
    assert any("DOI identifiers" in error for error in validate_project_metadata(metadata_root).errors)


@pytest.mark.parametrize("duplicate", [PUBLISHED_CONCEPT_DOI, PUBLISHED_VERSION_DOI])
def test_duplicate_doi_identifiers_fail_even_when_the_set_matches(published_root: Path, duplicate: str) -> None:
    path = published_root / "CITATION.cff"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["identifiers"].append({"type": "doi", "value": duplicate})
    _write_yaml(path, payload)
    report = validate_project_metadata(published_root)
    assert report.status == "failed"
    assert any("duplicates" in error for error in report.errors)


def test_published_concept_and_version_doi_must_be_distinct(published_root: Path) -> None:
    citation = published_root / "CITATION.cff"
    payload = yaml.safe_load(citation.read_text(encoding="utf-8"))
    payload["doi"] = PUBLISHED_CONCEPT_DOI
    payload["identifiers"][1]["value"] = PUBLISHED_CONCEPT_DOI
    _write_yaml(citation, payload)
    codemeta = published_root / "codemeta.json"
    payload = json.loads(codemeta.read_text(encoding="utf-8"))
    payload["identifier"] = f"https://doi.org/{PUBLISHED_CONCEPT_DOI}"
    codemeta.write_text(json.dumps(payload), encoding="utf-8")
    config = published_root / "docs/manuscript/config.yaml"
    payload = yaml.safe_load(config.read_text(encoding="utf-8"))
    payload["publication"]["version_doi"] = PUBLISHED_CONCEPT_DOI
    payload["publication"]["version_record"] = "https://zenodo.org/records/21419693"
    _write_yaml(config, payload)
    report = validate_project_metadata(published_root)
    assert report.status == "failed"
    assert any("must be distinct" in error for error in report.errors)


@pytest.mark.parametrize(
    ("field", "value"),
    [("version_doi", PUBLISHED_CONCEPT_DOI),
     ("version_record", "https://zenodo.org/records/21419693")],
)
def test_manuscript_version_identity_must_match_if_present(metadata_root: Path, field: str, value: str) -> None:
    path = metadata_root / "docs/manuscript/config.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["publication"][field] = value
    _write_yaml(path, payload)
    report = validate_project_metadata(metadata_root)
    assert report.status == "failed"
    assert any(field in error for error in report.errors)


@pytest.mark.parametrize("field", ["version_doi", "version_record"])
def test_published_manuscript_version_fields_cannot_be_empty_if_present(published_root: Path, field: str) -> None:
    path = published_root / "docs/manuscript/config.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["publication"][field] = ""
    _write_yaml(path, payload)
    report = validate_project_metadata(published_root)
    assert report.status == "failed"
    assert any(field in error for error in report.errors)


def test_manuscript_version_identity_is_optional(published_root: Path) -> None:
    path = published_root / "docs/manuscript/config.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    for field in ("version_doi", "version_record"):
        del payload["publication"][field]
    _write_yaml(path, payload)
    report = validate_project_metadata(published_root)
    assert report.status == "passed", report.errors


def test_forthcoming_manuscript_version_fields_may_be_empty(forthcoming_root: Path) -> None:
    path = forthcoming_root / "docs/manuscript/config.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["publication"].update(version_doi="", version_record="")
    _write_yaml(path, payload)
    report = validate_project_metadata(forthcoming_root)
    assert report.status == "passed", report.errors


def test_published_version_doi_must_be_well_formed(published_root: Path) -> None:
    citation = published_root / "CITATION.cff"
    payload = yaml.safe_load(citation.read_text(encoding="utf-8"))
    payload["doi"] = "not-a-doi"
    _write_yaml(citation, payload)
    assert any("well-formed Zenodo DOI" in error for error in validate_project_metadata(published_root).errors)


def test_empty_pyproject_authors_return_a_failed_report(metadata_root: Path) -> None:
    project = metadata_root / "pyproject.toml"
    project.write_text(re.sub(r"(?m)^authors = .*", "authors = []", project.read_text(encoding="utf-8")), encoding="utf-8")
    assert validate_project_metadata(metadata_root).status == "failed"


@pytest.mark.parametrize("value", ["[]", "not JSON"])
def test_malformed_codemeta_returns_a_failed_report(metadata_root: Path, value: str) -> None:
    (metadata_root / "codemeta.json").write_text(value, encoding="utf-8")
    assert validate_project_metadata(metadata_root).status == "failed"
