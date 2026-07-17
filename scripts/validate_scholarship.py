#!/usr/bin/env python3
"""Validate the checked-in DuckRabbit evidence matrix without network writes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from duckrabbit.evidence import load_evidence_matrix, validate_bibliography_integrity, validate_rendered_bibliography_links, validate_rendered_citation_links


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=None, help="evidence matrix JSON path")
    parser.add_argument("--html", type=Path, default=None, help="rendered combined HTML to check for citation and resolver links")
    args = parser.parse_args()
    sources, entries = load_evidence_matrix(args.path)
    bibliography = validate_bibliography_integrity()
    if args.html is not None:
        validate_rendered_citation_links(args.html, sources)
        validate_rendered_bibliography_links(args.html)
    print(json.dumps({"source_count": len(sources), "entry_count": len(entries), "bibliography_entry_count": bibliography["entry_count"], "status": "valid"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
