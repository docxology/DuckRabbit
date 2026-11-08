# DuckRabbit manuscript source and render boundaries

This directory is the canonical modular manuscript for **0.6.0 (unreleased;
DOI forthcoming)**. It describes deterministic stimulus construction and
verification, not empirical observer findings. Numeric values, table rows,
figure captions, and alt text are hydrated from the live package registry by
`scripts/generate_manuscript_variables.py`; they are not hand-maintained prose.
The current source contract is 16 scientific figures and 10 tables. The 36
evidence-source records are a narrower set than the 47-entry bibliography.

## Module map and reading order

Stable filenames determine order; descriptive headings can change without
changing explicit section, equation, figure, or table identifiers.

| Module | Contribution |
|---|---|
| [`00_abstract.md`](00_abstract.md) | Bounded software contribution and nonhuman-data statement |
| [`01_introduction.md`](01_introduction.md) | Construction/observation distinction, engineering hypotheses, historical context |
| [`02_methodology.md`](02_methodology.md) | Typed requests, clocks, canonical digests, verification, metrics, model equation |
| [`03_results.md`](03_results.md) | Graphical abstract, computed stimulus atlas, physical metrics, data-free estimands, synthetic diagnostic |
| [`04_experimental_setup.md`](04_experimental_setup.md) | Runtime dependencies and software-validation protocol; no participant experiment |
| [`05_reproducibility.md`](05_reproducibility.md) | Regeneration, retained provenance, versioned identity, performance and data availability |
| [`06_scope_and_related_work.md`](06_scope_and_related_work.md) | Source-supported family claims, engineering fidelity, calibration and observer limitations |
| [`07_publication_audit.md`](07_publication_audit.md) | Claim levels, figure lineage, formalism and generated audit tables |
| [`08_discussion_and_conclusion.md`](08_discussion_and_conclusion.md) | Methods contribution, unreleased identity and future observer-evidence boundary |
| [`09_appendix_catalog.md`](09_appendix_catalog.md) | Complete generated catalog/source-tier matrix (`tbl:catalog`) |
| [`99_references.md`](99_references.md) | Conventional references heading; entries live in `references.bib` |

`config.yaml` supplies identity and render configuration; `preamble.md` supplies
TeX support, not a scientific section. `README.md`, `SYNTAX.md`,
`MANUSCRIPT_STATUS.md`, and `AGENTS.md` are contributor guides excluded from
hydration. See [`SYNTAX.md`](SYNTAX.md) for the label/token contract.

## Generate and audit a fresh, wholly owned bundle

The [publication procedure](../publication.md#generate-and-audit-a-native-bundle)
owns the single native generation, hydration, synthetic-output and strict-audit
recipe. Run it from the public checkout in a new repository-local output root;
never overwrite a dated review snapshot. The hydrator resolves live variables
and writes numbered Markdown, bibliography, configuration and preamble.

Same-code checks do not typeset pages, establish live bibliographic identity,
authenticate historical cover-generation claims, or validate human perception.
See [performance](../performance.md) for separately bound timing evidence.

## Native PDF, HTML and slides are a separate renderer stage

Optional native/template tooling consumes the hydrated manuscript. Use its
documented registration and render interface; there is no portable package
command here that certifies all three formats. Keep canonical hydrated sources
separate from declared renderer overlays. Adapt layout, link routing, math and
table presentation through reproducible source-owned adapters and loss-checked
post-processing—not hand edits to generated TeX/HTML or scientific records.

Acceptance requires actual PDF/HTML/slides rendering plus inspection of
headings, every figure, table placement, citation/reference links and math.
Source hydration, package tests and a strict audit are distinct evidence and do
not imply that this renderer stage succeeded. This source refresh claims no
new rendering or publication-readiness result.

## Revision identity and immutable prior observations

Version 0.5.0 is published under concept DOI `10.5281/zenodo.21419693` and version
DOI `10.5281/zenodo.21419694`. The current version is 0.6.0, unreleased, with
empty DOI and `doi_status: forthcoming`; it does not revise that archive.
`output/review-2026-11-08/` is a frozen prior 15-figure snapshot, not evidence
for the new 16-figure source. A separate `output/visual-review-2026-11-08/`
is the designated integration-review destination; its own fresh receipts define
acceptance rather than this guide or the older snapshot.
