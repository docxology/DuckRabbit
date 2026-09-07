"""Contracts for fallback manuscript hydration when template extras are absent."""

from __future__ import annotations

from pathlib import Path

from duckrabbit.manuscript_variables import hydrate_manuscript_files


def test_hydrate_manuscript_files_substitutes_copies_and_cleans(tmp_path: Path):
    source_dir = tmp_path / "docs" / "manuscript"
    source_dir.mkdir(parents=True)
    (source_dir / "chapter.md").write_text("Version {{PACKAGE_VERSION}} keeps {{UNKNOWN_TOKEN}}.\n", encoding="utf-8")
    (source_dir / "AGENTS.md").write_text("agent guidance stays out of output\n", encoding="utf-8")
    (source_dir / "config.yaml").write_text("cover_height_fraction: 0.58\n", encoding="utf-8")
    (source_dir / "references.bib").write_text("@misc{key2020, title = {A}}\n", encoding="utf-8")
    output_dir = tmp_path / "output" / "manuscript"
    output_dir.mkdir(parents=True)
    (output_dir / "stale.md").write_text("stale\n", encoding="utf-8")
    (output_dir / "stale.bib").write_text("stale\n", encoding="utf-8")

    result = hydrate_manuscript_files({"PACKAGE_VERSION": "0.5.0"}, tmp_path)

    assert result == output_dir
    assert (output_dir / "chapter.md").read_text(encoding="utf-8") == "Version 0.5.0 keeps {{UNKNOWN_TOKEN}}.\n"
    assert not (output_dir / "AGENTS.md").exists()
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
