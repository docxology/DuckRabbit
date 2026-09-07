# AGENTS: `scripts/` — Thin Orchestrator Scripts

Technical specification for the DuckRabbit project's scripts.

## Script Inventory

| Script | Pattern | Input | Output |
| --- | --- | --- | --- |
| `generate_illusions.py` | Thin Orchestrator | `duckrabbit.cli` | generated media under the requested output directory |
| `generate_publication_outputs.py` | Thin Orchestrator | `duckrabbit.publication.generate_publication_outputs` | `output/figures/`, `output/data/` |
| `validate_scholarship.py` | Thin Orchestrator | `duckrabbit.evidence` loaders and validators | JSON summary on stdout |
| `audit_scholarship.py` | Thin Orchestrator | `duckrabbit.scholarship.run_scholarship_audit` | `output/reports/scholarship_audit.json` |
| `z_generate_manuscript_variables.py` | Thin Orchestrator | `duckrabbit.manuscript_variables` | `output/data/manuscript_variables.json`, hydrated `output/manuscript/*` |
| `_project.py` | Shared bootstrap | — | `PROJECT_ROOT` constant |

## Design Contract

- Scripts are orchestration only: path bootstrap (`_project.py`), argparse,
  and delegated calls into `src/duckrabbit/` entrypoints.
- Business, transport, data, plot, and analysis logic lives in `src/duckrabbit/`
  and must be importable and covered by tests in `tests/`.
- HTTP transport with scheme hardening (`duckrabbit.scholarship`), Crossref DOI
  metadata comparison, title-identity matching, and manuscript hydration are
  package code; do not re-inline them in a script.
- Keep commands deterministic and reproducible; do not write generated
  artifacts outside the requested output directory.
