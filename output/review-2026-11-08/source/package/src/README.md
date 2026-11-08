# `src/duckrabbit/`

This package contains DuckRabbit's typed domain model, deterministic stimulus
generators, registry, taxonomy, and media/render boundaries.

- `parameters.py` — validated scalar and modality-specific configuration types
- `artifacts.py` — canonical in-memory image, audio, video, and timeline objects
- `taxonomy.py` — orthogonal cognitive and implementation metadata
- `registry.py` — generic typed generator protocol and discovery registry
- `generators.py` — representative v0.5 deterministic generators
- `media.py` — lazy PNG/GIF/WAV/NPZ/ffmpeg adapters
- `render.py` — artifact encoding, metrics, and v2 provenance manifests
- `schema.py`, `canonical.py` — parameter schemas and canonical byte hashing
- `inspection.py`, `observer.py` — decode verification and study records
- `cli.py` — package CLI implementation
- `evidence.py` — source-tiered evidence matrix and status validation
- `observer_analysis.py` — study schemas, synthetic data harness, and future power planning
- `synthetic_psychophysics.py` — transparent feature observer diagnostics, model contracts, and epistemic boundaries
- `publication.py` — deterministic figures, tables, and registries

No module in this directory imports the sibling template's `infrastructure`
package. File-system and codec boundaries are explicit and testable.
