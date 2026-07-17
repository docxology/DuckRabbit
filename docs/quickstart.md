# DuckRabbit quickstart

```bash
uv sync --extra dev
uv run python -m duckrabbit list
uv run python -m duckrabbit list --json
uv run python -m duckrabbit describe visual.duck_rabbit
uv run python -m duckrabbit validate visual.duck_rabbit
uv run python -m duckrabbit generate visual.apparent_motion --output-dir output/media
uv run python -m duckrabbit inspect output/media/visual_apparent_motion.gif
uv run python -m duckrabbit verify output/media/visual_apparent_motion.gif.json
uv run python -m duckrabbit capabilities
uv run python scripts/generate_publication_outputs.py
uv run python scripts/z_generate_manuscript_variables.py
uv run pytest tests/ --cov=src/duckrabbit --cov-fail-under=90
```

For JSON overrides:

```json
{"duck_weight": 0.8, "config": {"width": 320, "height": 240, "quantization_levels": 8}}
```

```bash
uv run python -m duckrabbit validate visual.duck_rabbit --config params.json
```

Encoded output can be selected explicitly from `png`, `wav`, `gif`, `mp4`, and
`npz`. WAV output supports typed 8-, 16-, 24-, and 32-bit PCM profiles through
the Python API. The generated v2 sidecar includes the parameter schema,
canonical little-endian digest, objective metrics, decoded media facts, backend
profile, verification status, and encoded SHA-256 digest. `read_manifest()` can
upconvert older v1 sidecars as explicitly unverified records.
Media writes create parent directories atomically; `OutputSpec.overwrite`
controls whether an existing path may be replaced.

All user-facing validation and codec failures are emitted as structured JSON
with `status`, `error_type`, and `errors`. The capability command is a read-only
probe of the current environment; it does not create files or infer observer
effects.

The generated publication report is at `output/reports/publication_report.json`.
The figure registry is at `output/figures/figure_registry.json`, and each
figure has a corresponding source-data file under `output/data/`.
The same directory contains generated catalog/evidence, parameter-domain,
encoding-profile, metric-definition, observer-estimand, and verification
failure-mode tables in Markdown and JSON forms.
