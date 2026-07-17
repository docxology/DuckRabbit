#!/usr/bin/env python3
"""Thin wrapper for deterministic publication figures, tables, and registries."""

from __future__ import annotations

import argparse
from pathlib import Path

from duckrabbit.publication import generate_publication_outputs
from _project import PROJECT_ROOT


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate DuckRabbit publication outputs")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "output")
    parser.add_argument("--clean", action="store_true", help="remove stale generated files in figures/data")
    args = parser.parse_args(argv)
    print(generate_publication_outputs(args.output_dir, clean=args.clean))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
