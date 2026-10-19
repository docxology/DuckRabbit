# Manuscript Status

- **Project:** DuckRabbit
- **Manuscript title:** DuckRabbit: Typed Multimodal Illusion Generator
- **Location:** `docs/manuscript/` (canonical; fallback `manuscript/` resolved by `src/duckrabbit/manuscript_variables.py::hydrate_manuscript_files`)
- **Type:** Active publication-target manuscript (11 section files)
- **Status file purpose:** Tracks publication-readiness of the manuscript content in this directory.
- **Revision boundary:** v0.5.0 is published; current correctness, visualization,
  and performance changes are unreleased development work. Archived DOI/PDF
  artifacts are not rewritten by source-only validation.
- **Standalone validation:** Generate publication outputs, hydrate Markdown,
  validate offline scholarship, and run the strict release audit using
  [`README.md`](README.md). Typeset PDF/HTML/slides require optional tooling and
  visual inspection; a package test pass does not certify their build.
