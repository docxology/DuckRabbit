# DuckRabbit scripts

Thin orchestrator scripts for the DuckRabbit project. Testable logic lives in
`src/duckrabbit/`; scripts only bootstrap paths, parse arguments, and delegate
to package entrypoints.

## Inventory

| Script | Purpose | Delegates to | Command |
| --- | --- | --- | --- |
| `generate_illusions.py` | Catalog CLI entry point (list, generate, encode, verify) | `duckrabbit.cli` | `uv run python scripts/generate_illusions.py list --implemented-only` |
| `generate_publication_outputs.py` | Deterministic publication figures, tables, and registries | `duckrabbit.publication.generate_publication_outputs` | `uv run python scripts/generate_publication_outputs.py` |
| `validate_scholarship.py` | Offline validation of the evidence matrix and bibliography | `duckrabbit.evidence` loaders and validators | `uv run python scripts/validate_scholarship.py` |
| `audit_scholarship.py` | Explicit network audit: Crossref DOI metadata and URL reachability | `duckrabbit.scholarship.run_scholarship_audit` | `uv run python scripts/audit_scholarship.py --output output/reports/scholarship_audit.json` |
| `z_generate_manuscript_variables.py` | Manuscript variables JSON and resolved/hydrated markdown | `duckrabbit.manuscript_variables` (`generate_variables`, `save_variables`, `hydrate_manuscript_files`) | `uv run python scripts/z_generate_manuscript_variables.py` |
| `_project.py` | Shared `PROJECT_ROOT` path bootstrap (helper, not an entry point) | — | — |

`generate_illusions.py` is a compatibility wrapper around `duckrabbit.cli`; the
installable console command and `python -m duckrabbit` are the primary
interfaces.

## Outputs

- `output/reports/scholarship_audit.json` — dated network audit payload (`audit_scholarship.py`)
- `output/data/manuscript_variables.json` — live manuscript variables (`z_generate_manuscript_variables.py`)
- `output/manuscript/*.md` — hydrated manuscript files when the sibling template extras are absent (`z_generate_manuscript_variables.py`)
- `output/figures/`, `output/data/` — publication figures and registries (`generate_publication_outputs.py`)
