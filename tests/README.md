# DuckRabbit tests

The suite covers typed parameter boundaries, canonical artifacts, registry and
taxonomy consistency, deterministic generators, real media encoders, manifests,
CLI behavior, and optional ffmpeg failures. Run it with:

```bash
uv run pytest tests/ --cov=src/duckrabbit --cov-report=term-missing --cov-fail-under=90
```

The modules are intentionally organized by contract surface:

| Module | Responsibility |
| --- | --- |
| `test_parameters.py`, `test_generators.py` | Typed domains, deterministic canonical media, registry promotion gates |
| `test_media_and_render.py`, `test_v03_contracts.py` | Real codec round trips, inspection, manifests, and tamper detection |
| `test_evidence_contracts.py`, `test_v04_scholarly.py` | Strict evidence JSON, source tiers, claim levels, and publication lineage |
| `test_metrics_statistics.py` | Objective units, luminance semantics, synthetic response families, and future-study power scenarios |
| `test_publication_v05.py`, `test_project_audit.py` | Figure/caption/formalism contracts and the independent verifier |
| `test_cli.py`, `test_fixtures.py` | User-facing commands and input-dependent fixture boundaries |

When the parent monorepo may be switching branches, run this suite from the
isolated worktree documented in `../AGENTS.md`; a source tree that changes
during collection is not a valid test result.
