# DuckRabbit manuscript

The manuscript documents the typed parameter, canonical artifact, registry,
taxonomy, and media-adapter contracts. Numeric catalog values are injected by
`scripts/generate_manuscript_variables.py` from the live package registry.

Render and validate from the sibling template checkout root:
`uv run python scripts/pipeline/stage_03_render.py --project ongoing/Art/DuckRabbit`
then `uv run python scripts/pipeline/stage_04_validate.py`. The qualified
name used by this checkout is `ongoing/Art/DuckRabbit`, resolved through
the template's `projects/ongoing/Art` alias.
