#!/usr/bin/env python3
"""Thin project entry point for generating the representative catalog."""

from __future__ import annotations

import sys
from duckrabbit.cli import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
