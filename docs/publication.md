# Generate a native publication bundle and isolate typesetting

**Version 0.6.0 is unreleased, with empty DOI fields and `doi_status: forthcoming`.**
Daniel Ari Friedman, Active Inference Institute,
[ORCID 0000-0001-6232-9096](https://orcid.org/0000-0001-6232-9096), is the author.
Version and identity must agree across package, manuscript configuration,
[CITATION.cff](../CITATION.cff), CodeMeta, and Zenodo metadata. The immutable
v0.5.0 [concept DOI](https://doi.org/10.5281/zenodo.21419693) and
[version DOI](https://doi.org/10.5281/zenodo.21419694) do not identify this candidate.

## Generate and audit a native bundle

This is the canonical native recipe. Run from the public checkout root, after
[locked installation](quickstart.md#install-and-discover-typed-requests). Choose
a **new, wholly owned repository-local** destination; do not reuse a historical
review tree. All commands below use the same output root:

```bash
OUT=output/local-publication-review
uv run python -m duckrabbit publish --output-dir "$OUT"
uv run python scripts/generate_manuscript_variables.py --output-dir "$OUT"
uv run python scripts/validate_scholarship.py
uv run python -m duckrabbit synthetic-psychophysics --output "$OUT/data/synthetic_psychophysics_cli.json"
uv run python -m duckrabbit audit --output-root "$OUT" --release
```

The thin `scripts/generate_publication_outputs.py --output-dir "$OUT"` wrapper
is equivalent to `duckrabbit publish`; do not run both as separate required
steps. The source-owned hydrator resolves manuscript variables and writes
Markdown, bibliography, configuration, and preamble; it does **not** typeset.

Publication writes known generated filenames. Hydration replaces its delivered
Markdown/bibliography set, even without `--clean`. Treat the whole selected
bundle as generated output. Omit `--clean`: it deletes PNG/WebP files under
figures and JSON/Markdown under data, including unrelated files of those types,
not just stale registry members. Never apply it to a shared or retained tree.

### Native output interfaces

| Relative to selected output root | Owning contract |
| --- | --- |
| `figures/figure_registry.json`, scientific PNGs | Stable labels, caption/alt text, controls, objective units, claim level, evidence lineage, raster/source-data digests. |
| `data/<figure-stem>.json` | Canonical construction and plotted display data; see [visualization](visualization.md). |
| `reports/readable_figure_panels.json`, `figures/*-detail-*.png` | Source-record readability variants with exact paths, hashes, dimensions and renderer provenance; not extra scientific figures. |
| `data/*_table.{md,json}` | Tables derived from taxonomy, evidence, metrics, observer designs, caption audit, and formalism registries. |
| `data/manuscript_variables.json`, `manuscript/` | Live variables and exact hydrated source delivery. |
| `reports/publication_report.json`, `reports/visual_qa.json` | Publication inventory and structural raster QA; not visual acceptance. |
| Cover assets and provenance registry | Separately typed editorial illustration and variant/source-byte verification. |

Registry `output/figures/...` and `output/data/...` references are logical
paths rebased to the selected bundle root by validators; they do not authorize
writes to the retained root output tree. Source authorities are
[`publication.py`](../src/duckrabbit/publication.py),
[`publication_specs.py`](../src/duckrabbit/publication_specs.py), and
[`manuscript_variables.py`](../src/duckrabbit/manuscript_variables.py).

## Separate offline replay, visual review, and live scholarship

The native `audit --release` fail-closed mode requires publication surfaces,
replays every registered scientific data/raster producer, verifies cover and
table contracts, and compares exact current-source hydrated delivery.
Readable detail variants and their dedicated report are generated and replayed
as part of the same native publication/audit sequence; there is no separate
manual panel-editing step.

The executing checkout must match any selected project root. This is trusted-code
consistency, not independent scientific replication, authenticated authorship,
a fresh network audit, or an authorization to publish. `visual_qa` checks
raster facts/hashes; [actual figure and page review](visualization.md#inspect-readability-at-delivery-scale)
is still required.

The explicit **live** scholarship gate is separate from the offline recipe:

```bash
OUT=output/local-publication-review
uv run python scripts/audit_scholarship.py --output "$OUT/reports/scholarship_audit.json"
```

A dated successful response, URL reachability, or a passing offline audit does
not establish fresh title/author/year identity. See
[scholarship scope and blockers](scholarship.md#separate-offline-lineage-from-live-identity).
Preserve unresolved, mismatched, blocked, or unavailable outcomes; do not lower
the gate to publish. Synthetic output remains a hand-specified nonhuman model
(`human_data=false`), and finite sensitivity ranges are not confidence intervals.

## Isolate optional typesetting

The package owns figures and hydrated manuscript inputs; an external renderer
may consume them to produce PDF, HTML, and slides. Rendering is optional for
native stimulus use, but a typeset release requires its own build and visual
acceptance. No private workspace alias or sibling-root write recipe is a
prerequisite.

Use an explicitly declared **read-only renderer snapshot**, not a moving
external checkout. Keep adaptations in a separate repository-local overlay and
all outputs, TeX/font/browser caches, and temporary state in repository-local
owned directories. Preserve canonical bundle inputs unchanged. Record renderer
source hashes, overlay transformations, actual commands, interpreter/native
binaries, font bytes, input/output hashes, and logs. Loss-check any wrapping or
slide transformations against full source payloads; do not shorten identifiers,
source locators, captions, tables, or references to conceal clipping.

There is no native DuckRabbit PDF/HTML/slides CLI. Use the declared renderer's
actual interface, not an invented package command or a copied historical
machine path. Inspect every output page/deck and citation destination;
compilation and static link presence alone cannot certify readability,
accessibility, print readiness, or a working browser presentation.

## Keep the refresh candidate separate from historical evidence

The [visual-review bundle](../output/visual-review-2026-11-08/) is the designated
current-source delivery. Its own source, native and visual-review receipts—not
this procedure alone—define acceptance.
The retained [earlier November bundle](../output/review-2026-11-08/) and
[November audit](audit-2026-11-08.md) describe prior inputs. The
[October render receipt](rendering-2026-10-19.md) is likewise historical, not
verification of this source or a portable command recipe.

Preserve distinct historical PDF byte identities and v0.5.0 artifacts rather
than silently replacing them. [Visualization](visualization.md#live-roster-and-historical-baseline)
explains the refreshed versus historical figure roster; the
[release checklist](public-release-checklist.md) owns compatibility/security,
external publication, and DOI sequencing. A new local bundle does not create
a tag, release, archive identity, or participant result.
