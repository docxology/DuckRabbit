# Manuscript guidance — DuckRabbit

Manuscript prose describes reproducible stimulus construction, not universal
observer percepts. Use `{{TOKEN}}` for values generated from the live registry;
the variable source is `src/duckrabbit/manuscript_variables.py` and the thin
entry point is `scripts/z_generate_manuscript_variables.py`.

Use Pandoc citations such as `[@gregory1997visual]`, keep bibliography keys in
`references.bib`, and use section labels rather than hard-coded numbering.
Generated media belongs under `output/figures/` or `output/media/`; never hand-
edit files under `output/`.

