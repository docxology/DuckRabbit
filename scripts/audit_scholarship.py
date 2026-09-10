#!/usr/bin/env python3
"""Explicit network audit of the checked-in scholarship URL snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from duckrabbit.errors import DuckRabbitError
from duckrabbit.io import atomic_write_text
from duckrabbit.scholarship import run_scholarship_audit

from _project import PROJECT_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "output" / "reports" / "scholarship_audit.json")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    try:
        payload = run_scholarship_audit(timeout=args.timeout)
    except DuckRabbitError as exc:
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__, "errors": [str(exc)]}, sort_keys=True), file=sys.stderr)
        return 1
    atomic_write_text(args.output, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("entry_count", "source_count", "verified_count", "audited_on")}, sort_keys=True))
    return 0 if payload["verified_count"] == payload["source_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
