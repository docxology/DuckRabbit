# AGENTS.md — DuckRabbit

DuckRabbit is a private sidecar project (currently under
`projects/ongoing/docxology/DuckRabbit` in the private monorepo). Read this file and
the relevant directory guidance before editing.

## Orientation ladder (cold start)

1. **What is this?** Read `README.md` (first 30 lines suffice).
2. **Current state:** `TODO.md` (backlog + release gate) and `CHANGELOG.md`
   (version history) are the canonical status surfaces. v0.5.0 is published
   (DOI `10.5281/zenodo.21419693`); verify with
   `grep -n version pyproject.toml CITATION.cff codemeta.json .zenodo.json`.
3. **What to do next:** `TODO.md` "Future research and optional improvements"
   and "Evidence gates" sections are the single authoritative pointer.
4. **Primary verification:** `uv run pytest tests/ --cov=src/duckrabbit
   --cov-fail-under=90` (from the project root; slow cold start on external
   drives — see "Performance note" below). Fast sanity check:
   `uv run python -m duckrabbit list`.

## Layer contract

| Surface | Rule |
| --- | --- |
| `src/duckrabbit/` | Typed domain logic and deterministic generators; no template-infrastructure imports |
| `src/duckrabbit/media.py` | Lazy optional media adapters and explicit capability errors |
| `src/duckrabbit/synthetic_psychophysics.py` | Serialized model-output diagnostics; never human observer evidence |
| `scripts/` | Thin command entry points only |
| `tests/` | Real computations and round trips; no `unittest.mock`, `MagicMock`, or `@patch` |
| `output/` | Disposable generated artifacts; never hand-edit |

The core boundary is deliberate: a generator must be runnable and testable
without the sibling template engine. The package may depend on NumPy and
Pillow; ffmpeg remains a system-level optional encoder.

## Invariants

- Public parameter objects are frozen dataclasses with explicit runtime
  validation.
- Canonical image pixels are float32 in `[0, 1]`; canonical audio samples are
  float32 in `[-1, 1]`.
- Repeating a request with the same typed parameters and seed produces the
  same canonical buffers and digest.
- Audio/video timelines must agree within one video frame and retain declared
  synchronization and spatial offsets.
- Every implemented generator has a taxonomy entry and a registry contract.
- Taxonomy status must not be upgraded to `implemented` without a generator,
  tests, and documented stimulus requirements.
- Synthetic psychophysics must serialize its model identity, feature schema,
  weights, temperature, seed, calibration statement, and `human_data=false`;
  it must never be described as a pretrained vision model or psychometric
  result without external validation.
- Manuscript numbers and generated artifacts must come from source/configuration
  and be regenerated through the template pipeline.
- Publication captions must include controls, objective units or explicit
  non-applicability, source-data path and registry digest, evidence lineage,
  `Limitations:`, and `Boundary:` clauses. The figure registry and its visual-QA
  sidecar are independent verification surfaces, not trusted renderer output.
- Evidence records distinguish checked-in `snapshot_validated` status from live
  DOI metadata matches, access control, mismatch, and unavailable outcomes;
  URL reachability alone is never scholarly verification.
- Cross-file identity is release-critical: Daniel Ari Friedman, ORCID
  `0000-0001-6232-9096`, and version `0.5.0` must agree across package,
  manuscript, citation, codemeta, and Zenodo metadata. The DOI must be either
  empty with `doi_status: forthcoming` (no release minted yet) or a real,
  well-formed Zenodo DOI with `doi_status: published` (never a placeholder) —
  `src/duckrabbit/metadata.py` enforces this pairing. v0.5.0 is published under
  concept DOI `10.5281/zenodo.21419693`.

## Workflow

1. Read `docs/agent_instructions.md` and `docs/architecture.md` for source
   boundaries.
2. Read `docs/testing_philosophy.md` before changing tests.
3. Keep generator logic in `src/duckrabbit/`; keep CLI/file writes in
   `src/duckrabbit/media.py`, `src/duckrabbit/render.py`, or thin scripts.
4. Run the project test and coverage gate.
5. Run `uv run python -m duckrabbit synthetic-psychophysics` and the CLI
   generation smoke tests; verify the sidecar says `human_data=false`.
6. Run the sibling template linker/render
   checks when changing manuscript or pipeline-facing files.

### Shared-worktree reconciliation

The parent private monorepo may have another automation process switching its
branch while a project is being tested. Never run a long test or render from a
moving parent worktree. Use a disposable isolated worktree for the project:

```bash
git fetch origin
git worktree add /private/tmp/duckrabbit-cycle codex/duckrabbit
cd /private/tmp/duckrabbit-cycle/working/DuckRabbit
uv sync --extra dev
uv run ruff check src tests
uv run pytest tests/ --cov=src/duckrabbit --cov-fail-under=90
```

Before handoff, compare the local and remote branch with
`git rev-list --left-right --count codex/duckrabbit...origin/codex/duckrabbit`,
push only the project branch (the default branch for this checkout is `main`; and then refresh the parent worktree's
project path without staging unrelated parent changes. A test run
whose source tree changes during collection is invalid evidence, even if some
tests passed.

The independent verifier is `uv run python -m duckrabbit audit`. It checks the
live taxonomy/evidence graph, every registered generator, canonical digests,
metrics, formalism links, and—when generated—figure registry hashes. Use
`uv run python -m duckrabbit audit --output-root output --release` for the
fail-closed gate that also requires metadata consistency, cover provenance,
caption/table completeness, and all publication outputs.

## No perceptual overclaiming

The package generates reproducible stimuli intended to probe named mechanisms.
It does not infer observer reports, clinical effects, or universal percepts
from an encoded file alone. Input-dependent families remain explicitly
catalogued as `input_required` until fixtures and validation are available.

## Performance note (external-drive checkouts)

This checkout lives on `/Volumes/external_drive`. First `uv run` or a cold
`import duckrabbit` can take minutes (drive-bound I/O). For bounded commands
use generous timeouts; for the audit CLI prefer a background invocation. This
is an environment property, not a package defect — a fast local SSD checkout
does not exhibit it.
