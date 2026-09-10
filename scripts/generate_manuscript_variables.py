#!/usr/bin/env python3
"""Generate DuckRabbit manuscript variables and resolved markdown when available."""

from __future__ import annotations

from duckrabbit.manuscript_variables import generate_variables, save_variables
from _project import PROJECT_ROOT


def main() -> int:
    variables = generate_variables()
    path = save_variables(variables, PROJECT_ROOT / "output" / "data" / "manuscript_variables.json")
    # Integration glue only: the sibling template engine is an optional,
    # out-of-package dependency (the layer contract forbids importing it from
    # src/duckrabbit), so the selection lives in this entry point and reports
    # which hydrator produced output/manuscript.
    try:
        from infrastructure.rendering.manuscript_injection import write_resolved_manuscript_tree
    except ImportError:
        from duckrabbit.manuscript_variables import hydrate_manuscript_files

        hydrate_manuscript_files(variables, PROJECT_ROOT)
        print(f"{path}\nhydrator: package fallback")
        return 0
    write_resolved_manuscript_tree(PROJECT_ROOT, {key: str(value) for key, value in variables.items()})
    print(f"{path}\nhydrator: sibling template")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
