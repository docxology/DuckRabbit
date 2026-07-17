# DuckRabbit scripts

```bash
uv run python scripts/generate_illusions.py list --implemented-only
uv run python scripts/generate_illusions.py generate visual.duck_rabbit --output-dir output/media
uv run python scripts/generate_publication_outputs.py
uv run python scripts/validate_scholarship.py
```

The script is a compatibility wrapper around `duckrabbit.cli`; the installable
console command and `python -m duckrabbit` are the primary interfaces.

`generate_publication_outputs.py` is the thin orchestration entry point for the
importable publication workflow in `duckrabbit.publication`.
`validate_scholarship.py` checks the source-tiered evidence matrix and its
catalog/status consistency without modifying or downloading source material.
