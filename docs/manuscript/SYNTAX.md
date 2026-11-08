# DuckRabbit manuscript syntax and cross-reference contract

## Stable labels, descriptive titles

Use contribution-specific headings while preserving explicit identifiers:
`# Typed Requests, Canonical Identity, and Verification Rules {#sec:methodology}`.
Refer to labels (`[@sec:methodology]`), not hard-coded section numbers or title
text. Filenames remain stable for module ordering and renderer routing.
Keep every existing `sec:`, `eq:`, `fig:` and `tbl:` identifier unchanged.

## Citations and mathematical definitions

Use Pandoc citations such as `[@gregory1997visual]`; bibliography keys are owned
by `references.bib`. Use inline `$...$` and display `$$` math, retaining the
explicit `{#eq:...}` attribute after each labeled display. Preserve symbols,
units, sign conventions and equation-to-code links. Do not substitute raw
LaTeX citation/reference commands for Pandoc cross-references.

## Registry-owned figures, captions and tables

Use `{{TOKEN}}` values defined by `src/duckrabbit/manuscript_variables.py`;
the hydrator rejects unresolved tokens. Do not hard-code mutable catalog counts
or copy generated table rows into prose. Guides in this directory are excluded
from hydration; the numbered modules, preamble, bibliography and configuration
form the delivery sources.

Scientific figures use generated alt text and a separate generated caption:

```markdown
![{{FIGURE_ALT_GRAPHICAL_ABSTRACT}}](../../output/figures/graphical_abstract.png){#fig:graphical_abstract}

{{FIGURE_CAPTION_GRAPHICAL_ABSTRACT}}
```

Reference that figure with `[@fig:graphical_abstract]`. Its claim is deterministic
multimodal construction and verification, not observer findings. Retain the
existing `../../output/figures/` source path convention; isolated-bundle
resource resolution belongs to the renderer integration, not ad hoc source
path replacements. Preserve table headers, generated row tokens, and caption
attributes such as `{#tbl:catalog}`.

## Source-only rendering adaptations

Keep canonical hydrated Markdown distinct from declared renderer overlays.
Change layout or renderer support at source/overlay level and regenerate;
never patch generated TeX or frozen render snapshots. Inspect actual
PDF/HTML/slides for long headings, math, figure captions, table overflow and
working links. A parsed source or package audit alone is not page-level evidence.
