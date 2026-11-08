#!/usr/bin/env python3
"""Generate source-owned DuckRabbit variables and resolved Markdown."""
from __future__ import annotations

import argparse
from pathlib import Path

from duckrabbit.manuscript_variables import generate_variables, hydrate_manuscript_files, save_variables
from _project import PROJECT_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "output")
    args = parser.parse_args()
    variables = generate_variables()
    path = save_variables(variables, args.output_dir / "data" / "manuscript_variables.json")
    hydrate_manuscript_files(variables, PROJECT_ROOT, output_dir=args.output_dir / "manuscript")
    print(f"{path}\nhydrator: DuckRabbit source-owned Markdown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
