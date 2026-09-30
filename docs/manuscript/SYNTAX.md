# DuckRabbit manuscript syntax

- Use Pandoc citations: `[@gregory1997visual]`.
- Use section labels: `# Methodology {#sec:methodology}`.
- Use generated values as `{{TOKEN}}` and define them in
  `src/duckrabbit/manuscript_variables.py`.
- Reference generated figures with `[@fig:label]` and paths under
  `../output/figures/`.
- Do not hard-code changing catalog counts or raw LaTeX citation/reference
  commands.

