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
| `test_schema_serialization.py` | Recursive JSON validity, schema value-object constraints, and streaming canonical hashes |
| `test_import_boundaries.py`, `test_performance.py` | Lazy public exports, real profiling workloads, source/environment/result binding, and fail-closed comparisons |
| `test_media_and_render.py`, `test_v03_contracts.py` | Real codec round trips, inspection, manifests, and tamper detection |
| `test_evidence_contracts.py`, `test_v04_scholarly.py` | Strict evidence JSON, source tiers, claim levels, and publication lineage |
| `test_metrics_statistics.py` | Objective units, luminance semantics, synthetic response families, and future-study power scenarios |
| `test_stimulus_integrity.py`, `test_observer_integrity.py` | Stimulus geometry, effective audio controls, observer provenance, immutability, and statistical edge cases |
| `test_media_integrity.py`, `test_publication_integrity.py` | Decoded-media tamper controls, safe output publication, and fail-closed publication audits |
| `test_publication_v05.py`, `test_project_audit.py` | Figure/caption/formalism contracts and the independent verifier |
| `test_publication_visualizations.py` | Actual frame-hold/timestamp geometry, retained spectral peaks, channel conventions, and quantized delivery facts |
| `test_cli.py`, `test_fixtures.py` | User-facing commands and input-dependent fixture boundaries |
| `test_catalog_contracts.py`, `test_release_contracts.py` | Live registry snapshots, release identity, claim lineage, and strict publication audits |
| `test_packaging_contracts.py`, `test_metadata_integrity.py` | Installed resource portability, metadata shape validation, and concept/version DOI roles |
| `test_scholarship_audit.py` | Scholarship audit network transport, DOI classification, and offline snapshot assembly |
| `test_synthetic_psychophysics.py` | Model-output-only synthetic psychophysics layers and their typed boundaries |
| `test_io.py`, `test_manuscript_hydration.py` | Atomic file writes and fallback manuscript hydration when template extras are absent |

When the parent monorepo may be switching branches, run this suite from the
isolated worktree documented in `../AGENTS.md`; a source tree that changes
during collection is not a valid test result.
