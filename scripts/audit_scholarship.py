#!/usr/bin/env python3
"""Explicit network audit of the checked-in scholarship URL snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from duckrabbit.io import atomic_write_text
from duckrabbit.scholarship import run_scholarship_audit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output/reports/scholarship_audit.json"))
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    payload = run_scholarship_audit(timeout=args.timeout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(args.output, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("entry_count", "source_count", "verified_count", "audited_on")}, sort_keys=True))
    return 0 if payload["verified_count"] == payload["source_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
