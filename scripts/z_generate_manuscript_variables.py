#!/usr/bin/env python3
"""Generate DuckRabbit manuscript variables and resolved markdown when available."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from duckrabbit.io import atomic_write_text
from duckrabbit.manuscript_variables import generate_variables, save_variables
from _project import PROJECT_ROOT


def _fallback_hydrate(variables: dict[str, object]) -> Path:
    """Hydrate manuscript files when the sibling template extras are absent."""
    source_dir = PROJECT_ROOT / "manuscript"
    output_dir = PROJECT_ROOT / "output" / "manuscript"
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("*.md"):
        stale.unlink()
    for stale in output_dir.glob("*.bib"):
        stale.unlink()
    token_pattern = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
    replacements = {key: str(value) for key, value in variables.items()}
    excluded = {"AGENTS.md", "README.md", "SYNTAX.md"}
    for manuscript_file in sorted(source_dir.glob("*.md")):
        if manuscript_file.name in excluded:
            continue
        text = manuscript_file.read_text(encoding="utf-8")
        hydrated = token_pattern.sub(lambda match: replacements.get(match.group(1), match.group(0)), text)
        atomic_write_text(output_dir / manuscript_file.name, hydrated)
    for auxiliary in ("config.yaml", "preamble.md"):
        source = source_dir / auxiliary
        if source.is_file():
            shutil.copy2(source, output_dir / auxiliary)
    for bibliography in source_dir.glob("*.bib"):
        shutil.copy2(bibliography, output_dir / bibliography.name)
    return output_dir


def main() -> int:
    variables = generate_variables()
    path = save_variables(variables, PROJECT_ROOT / "output" / "data" / "manuscript_variables.json")
    try:
        from infrastructure.rendering.manuscript_injection import write_resolved_manuscript_tree
    except ImportError:
        _fallback_hydrate(variables)
        print(path)
        return 0 if path.is_file() else 1
    write_resolved_manuscript_tree(PROJECT_ROOT, {key: str(value) for key, value in variables.items()})
    print(path)
    return 0 if path.is_file() else 1


if __name__ == "__main__":
    raise SystemExit(main())
