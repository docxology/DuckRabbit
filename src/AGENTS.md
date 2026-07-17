# `src/` guidance

`src/duckrabbit/` is the installable, deterministic core. Keep media
construction independent of the template engine and optional codecs.

## Boundaries

- `parameters.py` owns immutable scalar value objects and validated generator
  configuration.
- `artifacts.py` owns canonical in-memory media and invariant checks.
- `taxonomy.py` records orthogonal classification facets and evidence status.
- `registry.py` owns typed discovery and dispatch.
- `generators.py` contains the representative illusion implementations.
- `media.py` contains lazy Pillow, WAV, GIF, and optional ffmpeg adapters.
- `render.py` owns serialization-facing orchestration and manifest digests.
- `cli.py` is the command-line boundary; `scripts/` only delegates to it.

## Invariants

Canonical arrays are finite, deterministic, and normalized: images are float32
in `[0, 1]`, audio is float32 in `[-1, 1]`, and video/audio-visual timelines
have positive dimensions, rates, frame counts, and consistent durations.

Generators must reject malformed typed parameters before allocating media. Do
not import `infrastructure` from the package core. Do not claim an observer
perceived an illusion merely because a stimulus was generated.

## Development

Run from the project root:

```bash
uv run pytest tests/ --cov=src/duckrabbit --cov-fail-under=90
uv run python -m duckrabbit list
uv run python -m duckrabbit generate visual.duck_rabbit --format png
```

Use real arrays, files, and optional backends in tests. Do not add mocks.
