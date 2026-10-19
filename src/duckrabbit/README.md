# duckrabbit/

Python package `duckrabbit` — the project's business logic (src-layout).

Contents: __init__.py, __main__.py, artifacts.py, audit.py, canonical.py, claims.py, cli.py, cover.py, errors.py, evidence.py, fixtures.py, formalism.py, generators.py, inspection.py, io.py, manifest.py, manuscript_variables.py, media.py, metadata.py, metrics.py, observer.py, observer_analysis.py, parameters.py, publication.py, publication_specs.py, py.typed, registry.py, render.py, schema.py, serialization.py, synthetic_psychophysics.py, taxonomy.py, urls.py, version.py

These are tracked sources of the public package. `__init__.py` exposes the
stable API while loading optional analysis/publication surfaces on demand.
`performance.py` provides reproducible profiling workloads; `_resources/`
contains the runtime scholarly snapshots bundled in wheels. See
`../../docs/architecture.md` and `../../docs/performance.md`.
