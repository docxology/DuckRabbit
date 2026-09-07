#!/usr/bin/env python3
"""Generate DuckRabbit manuscript variables and resolved markdown when available."""

from __future__ import annotations

from duckrabbit.manuscript_variables import generate_variables, hydrate_manuscript_files, save_variables
from _project import PROJECT_ROOT


def main() -> int:
    variables = generate_variables()
    path = save_variables(variables, PROJECT_ROOT / "output" / "data" / "manuscript_variables.json")
    try:
        from infrastructure.rendering.manuscript_injection import write_resolved_manuscript_tree
    except ImportError:
        hydrate_manuscript_files(variables, PROJECT_ROOT)
        print(path)
        return 0 if path.is_file() else 1
    write_resolved_manuscript_tree(PROJECT_ROOT, {key: str(value) for key, value in variables.items()})
    print(path)
    return 0 if path.is_file() else 1


if __name__ == "__main__":
    raise SystemExit(main())
