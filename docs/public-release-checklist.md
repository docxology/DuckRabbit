# Public-release checklist

DuckRabbit is maintained in a private sidecar and rendered through the sibling
template checkout. This checklist defines the handoff from a verified release
candidate to a public repository or archival deposit.

**v0.5.0 status: released.** Public repository:
[docxology/DuckRabbit](https://github.com/docxology/DuckRabbit). Concept DOI:
[10.5281/zenodo.21419693](https://doi.org/10.5281/zenodo.21419693). Version
DOI: [10.5281/zenodo.21419694](https://doi.org/10.5281/zenodo.21419694). The
steps below remain the checklist for the *next* release.

## Required source state

- The public source contains the package, tests, manuscript, bibliography,
  evidence matrix, `CITATION.cff`, CodeMeta, Zenodo metadata, license, and
  changelog.
- Author identity is Daniel Ari Friedman, Active Inference Institute, ORCID
  `0000-0001-6232-9096`.
- The public software repository is
  `https://github.com/docxology/DuckRabbit`.
- Version, title, license, and DOI status agree across all metadata files.
- Between releases the DOI is empty and marked `forthcoming` until the next
  real public identifier is minted; once minted, `doi_status` becomes
  `published` and the DOI is real (never a placeholder).
- No participant data, private fixtures, credentials, or generated review
  state are included.

## Required verification

Run from the project root:

```bash
uv run ruff check src scripts tests
uv run pytest tests/ --cov=src/duckrabbit --cov-fail-under=90
uv run python scripts/generate_publication_outputs.py --clean
uv run python scripts/generate_manuscript_variables.py
uv run python scripts/validate_scholarship.py
uv run python scripts/audit_scholarship.py --output output/reports/scholarship_audit.json
uv run python -m duckrabbit synthetic-psychophysics
uv run python -m duckrabbit audit --output-root output --release
```

The `audit_scholarship.py` step is a network audit and is required at
release time only.

Then render and validate through the sibling template checkout. Review the PDF,
HTML, and slides visually; confirm that every in-text citation reaches its
reference entry and that every DOI or archival URL is resolver-linked.

## External publication sequence

1. Publish or mirror the exact release source to the intended public repository.
2. Create the immutable version tag and archive the source plus generated
   publication bundle.
3. Mint the DOI from the public record.
4. Update the DOI atomically in all release metadata and rerun the metadata,
   scholarship, render, and release gates.

The package is public-release ready when the local gates pass. It is not
publicly released, and it does not have a DOI, until the external handoff is
complete.
