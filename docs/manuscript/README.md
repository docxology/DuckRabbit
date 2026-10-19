# DuckRabbit manuscript

The manuscript documents the typed parameter, canonical artifact, registry,
taxonomy, and media-adapter contracts. Numeric catalog values are injected by
`scripts/generate_manuscript_variables.py` from the live package registry.

## Public-checkout workflow

Run from the DuckRabbit repository root; no private workspace alias is needed:

```bash
uv sync --locked --extra dev
uv run python -m duckrabbit publish --output-dir output --clean
uv run python scripts/generate_manuscript_variables.py
uv run python scripts/validate_scholarship.py
uv run python -m duckrabbit audit --output-root output --release
```

The variable generator reports which hydrator it used. The package fallback
writes resolved Markdown and bibliography under `output/manuscript/`; it does
not typeset a PDF or validate rendered page layout. Do not edit those generated
files. See [`../publication.md`](../publication.md) for the release gates and
[`../performance.md`](../performance.md) for separately instrumented workloads.

## Optional typesetting integration

A sibling template installation may render the hydrated manuscript to PDF,
HTML, and slides. Use that installation's documented project registration and
render/validation commands; an old `ongoing/Art/DuckRabbit` alias is not a
portable prerequisite. Inspect the resulting pages and citation links before
claiming a successful typeset build.

## Revision identity

Version 0.5.0 is already published with the identifiers in `CITATION.cff`.
Current development corrections are unreleased and do not revise that archive
or certify the checked-in historical PDF as a rendering of the current source.
