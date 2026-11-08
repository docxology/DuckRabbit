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

The source-owned variable generator writes resolved Markdown, configuration and
bibliography under `output/manuscript/`; `--output-dir` selects an isolated bundle.
It rejects unresolved delivery tokens before replacing earlier output. It does
not typeset a PDF or validate rendered page layout. Strict release auditing
compares the delivered bytes and variables with current source. See
[`../publication.md`](../publication.md) and [`../performance.md`](../performance.md).

## Optional typesetting integration

A sibling template installation may render the hydrated manuscript to PDF,
HTML, and slides. Use that installation's documented project registration and
render/validation commands; an old `ongoing/Art/DuckRabbit` alias is not a
portable prerequisite. Inspect the resulting pages and citation links before
claiming a successful typeset build.

## Revision identity

Version 0.5.0 is already published under concept DOI `10.5281/zenodo.21419693`
and version DOI `10.5281/zenodo.21419694`. Version 0.6.0 metadata is forthcoming;
it does not revise that archive or certify its PDF as current-source rendering.
