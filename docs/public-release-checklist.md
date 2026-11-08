# Public-release checklist

DuckRabbit is maintained in this public repository, with optional manuscript
rendering through a sibling template checkout. This checklist defines the handoff from a verified release
candidate to a public repository or archival deposit.

**v0.5.0 status: released.** Public repository:
[docxology/DuckRabbit](https://github.com/docxology/DuckRabbit). Concept DOI:
[10.5281/zenodo.21419693](https://doi.org/10.5281/zenodo.21419693). Version
DOI: [10.5281/zenodo.21419694](https://doi.org/10.5281/zenodo.21419694). The
steps below remain the checklist for the *next* release.

**Current candidate: 0.6.0, DOI forthcoming.** No new archive identity is assigned.
Preserve every v0.5.0 tag, release asset, DOI and historical review artifact.
The [current audit receipt](audit-2026-11-08.md) distinguishes the tagged/GitHub,
retained root and Zenodo PDF identities. A new release must bind its exact source,
assets and deposit separately; historical release prose is not byte verification.

## Required source state

- The public source contains the package, tests, manuscript, bibliography,
  evidence matrix, `CITATION.cff`, CodeMeta, Zenodo metadata, license, and
  changelog.
- Author identity is Daniel Ari Friedman, Active Inference Institute, ORCID
  `0000-0001-6232-9096`.
- The public software repository is
  `https://github.com/docxology/DuckRabbit`.
- Version, title, license, and DOI status agree across all metadata files.
- A new version awaiting its first deposit uses empty DOI fields and
  `forthcoming` status consistently across sidecars. Once real identifiers are
  minted, `doi_status` becomes `published`. Unreleased fixes do not rewrite
  the archived v0.5.0 identifiers or mint a release automatically.
- No participant data, private fixtures, credentials or temporary runtime/profile
  state are included. Curated source-bound review artifacts remain explicitly
  distinct from a published version and its immutable historical deliveries.

## Required verification

Run from the project root:

```bash
OUT=dist/release-candidate  # choose a fresh, wholly owned destination
uv run ruff check src scripts tests
uv run pytest tests/ --cov=src/duckrabbit --cov-fail-under=90
uv run python scripts/generate_publication_outputs.py --output-dir "$OUT"
uv run python scripts/generate_manuscript_variables.py --output-dir "$OUT"
uv run python scripts/validate_scholarship.py
uv run python scripts/audit_scholarship.py --output "$OUT/reports/scholarship_audit.json"
uv run python -m duckrabbit synthetic-psychophysics --output "$OUT/data/synthetic_psychophysics_cli.json"
uv run python -m duckrabbit audit --output-root "$OUT" --release
```

Also run `uv lock --check`, locked development sync, `uv build`, and an
independent wheel install/CLI smoke outside the checkout import path on the
Python 3.11 floor. A missing compatible locked wheel or unsuccessful sync is
an explicit gap, never a successful clean-environment claim. There is no native
type-checker gate; do not invent one. Record source/runtime hashes, exact
commands, outcomes, dependency advisories and rendered-input provenance.
Use a new owned output directory for `--clean`; it recursively deletes generated
figures/data, not merely stale registry members.

The network audit is required at release time. HTTP reachability is not source
identity: unresolved DOI-less records, blocked services and mismatches remain
failures. Machine-readable reports preserve successful peers and every failure.
The native network command covers the 36 evidence-source records. Review every
additional manuscript citation too; the dated audit records the separate
11-reference check, its retained primary metadata and its unresolved failures.
Exact ordered identity includes corporate authors, not only person-name fields.

For a new typeset manuscript release, render and validate through a declared
read-only renderer snapshot/overlay with all outputs and caches repository-local.
Do not run sibling-root recipes or overwrite frozen historical outputs. Review
every PDF page, HTML, and slides visually; confirm citation destinations and
resolver links. Compilation, same-code replay, and link presence alone do not
establish scientific validity, fresh network identity, or accessibility.

## External publication sequence

1. Publish or mirror the exact release source to the intended public repository.
2. Create the immutable version tag and archive the source plus generated
   publication bundle.
3. Mint the DOI from the public record.
4. Update the DOI atomically in all release metadata and rerun the metadata,
   scholarship, render, and release gates.

Use ordinary fast-forward publication, satisfy branch protections/required CI,
tag the validated main commit, and verify remote main/tag/release asset bytes.
Inherited GitVault leases and mapped-identity/plan/confirmation policy still
apply; disabled GitHub write classes are blockers, not permission to use raw
API alternatives. Never label a local build, branch push or draft PR released.

Passing local gates establishes readiness of the next candidate, not a new
public deposit or a newly minted DOI. Version 0.5.0 is already publicly released
with the identifiers above. Development changes must not be represented as
part of that immutable archive; a new release requires the external sequence.
