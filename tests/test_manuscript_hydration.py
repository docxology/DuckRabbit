"""Contracts for fallback manuscript hydration when template extras are absent."""

from __future__ import annotations

import json
import re
from pathlib import Path
import pytest

from duckrabbit.manuscript_variables import generate_variables, hydrate_manuscript_files, save_variables


ROOT = Path(__file__).resolve().parents[1]


def test_hydrate_manuscript_files_substitutes_copies_and_cleans(tmp_path: Path):
    source_dir = tmp_path / "docs" / "manuscript"
    source_dir.mkdir(parents=True)
    (source_dir / "chapter.md").write_text("Version {{PACKAGE_VERSION}}.\n", encoding="utf-8")
    (source_dir / "AGENTS.md").write_text("agent guidance stays out of output\n", encoding="utf-8")
    (source_dir / "config.yaml").write_text("cover_height_fraction: 0.58\n", encoding="utf-8")
    (source_dir / "references.bib").write_text("@misc{key2020, title = {A}}\n", encoding="utf-8")
    output_dir = tmp_path / "output" / "manuscript"
    output_dir.mkdir(parents=True)
    (output_dir / "stale.md").write_text("stale\n", encoding="utf-8")
    (output_dir / "stale.bib").write_text("stale\n", encoding="utf-8")
    (output_dir / "README.md").write_text("retained output guide\n", encoding="utf-8")
    (output_dir / "AGENTS.md").write_text("retained output instructions\n", encoding="utf-8")

    result = hydrate_manuscript_files({"PACKAGE_VERSION": "candidate"}, tmp_path)

    assert result == output_dir
    assert (output_dir / "chapter.md").read_text(encoding="utf-8") == "Version candidate.\n"
    assert (output_dir / "AGENTS.md").read_text(encoding="utf-8") == "retained output instructions\n"
    assert (output_dir / "README.md").read_text(encoding="utf-8") == "retained output guide\n"
    assert (output_dir / "config.yaml").read_text(encoding="utf-8") == "cover_height_fraction: 0.58\n"
    assert (output_dir / "references.bib").is_file()
    assert not (output_dir / "stale.md").exists()
    assert not (output_dir / "stale.bib").exists()


def test_hydrate_manuscript_files_falls_back_to_legacy_manuscript_dir(tmp_path: Path):
    legacy = tmp_path / "manuscript"
    legacy.mkdir()
    (legacy / "only.md").write_text("count {{CATALOG_ENTRIES}}\n", encoding="utf-8")

    result = hydrate_manuscript_files({"CATALOG_ENTRIES": 7}, tmp_path)

    assert (result / "only.md").read_text(encoding="utf-8") == "count 7\n"


def test_save_variables_writes_sorted_json_with_trailing_newline(tmp_path: Path):
    variables = generate_variables()
    path = save_variables(variables, tmp_path / "nested" / "manuscript_variables.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload == variables
    text = path.read_text(encoding="utf-8")
    assert text.endswith("}\n")
    serialized_keys = [line.strip().removesuffix('": {').lstrip('"') for line in text.splitlines() if line.strip().startswith('"')]
    assert serialized_keys == sorted(serialized_keys)


def test_every_manuscript_template_token_is_a_generated_variable():
    variables = generate_variables()
    token_pattern = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
    # The hydrator excludes these documentation files; SYNTAX.md documents
    # the token syntax itself, so its literal {{TOKEN}} is not a real use.
    excluded = {"AGENTS.md", "README.md", "SYNTAX.md"}
    used = {
        match
        for manuscript_file in (ROOT / "docs" / "manuscript").glob("*.md")
        if manuscript_file.name not in excluded
        for match in token_pattern.findall(manuscript_file.read_text(encoding="utf-8"))
    }
    missing = used - set(variables)
    assert not missing, f"manuscript tokens without a generated variable: {sorted(missing)}"


def test_unresolved_delivery_token_fails_before_overwriting_existing_manuscript(tmp_path: Path):
    source = tmp_path / "docs" / "manuscript"
    source.mkdir(parents=True)
    (source / "chapter.md").write_text("Count {{UNKNOWN_TOKEN}}\n")
    destination = tmp_path / "output" / "manuscript"
    destination.mkdir(parents=True)
    (destination / "chapter.md").write_text("preserved previous output\n")
    with pytest.raises(ValueError, match="unresolved manuscript"):
        hydrate_manuscript_files({}, tmp_path)
    assert (destination / "chapter.md").read_text() == "preserved previous output\n"
