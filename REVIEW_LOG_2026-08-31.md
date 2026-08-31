# Review Log — 2026-08-31 (agent-ergonomics deep pass)

One parallel-fleet agent ("duckrabbit") performed a cold-start ergonomics
audit and documentation pass on this date. Scope: documentation, navigation,
TODO hygiene, doc-accuracy fixes. No source refactors.

## Phase 0 — preflight

- Branch `main`, remote `origin` = https://github.com/docxology/DuckRabbit.git.
- 52 pre-existing dirty files at dispatch (uncommitted `manuscript/` ->
  `docs/manuscript/` relocation + README path edits + many new README/AGENTS
  files). All treated as pre-existing; never staged by this pass.

## Phase 1 — cold-start audit

Read README.md first as a cold agent.

- (a) Current status: PASS — TODO.md + CHANGELOG.md state v0.5.0 published
  with DOI; verification path given.
- (b) What to do next: PASS — TODO.md "Future research" + evidence gates.
- (c) Primary verification command: PASS — README "Tests and coverage" gives
  the exact pytest command.
- Environment caveat: cold imports of the package from this external drive
  take >90s; `uv run` may exceed a 300s foreground timeout on first run.

### Findings

1. **Medium** - 16 broken relative figure links after the manuscript move:
   `docs/manuscript/03_results.md` (9), `07_publication_audit.md` (6), and
   `SYNTAX.md` (1) reference `../output/figures/...` which resolves to
   nonexistent `docs/output/`. Fixed to `../../output/figures/`.
2. **Medium** - Stale sidecar-location claims: README.md and AGENTS.md said
   `working/`; the tree now lives under `projects/ongoing/docxology/`.
   STANDALONE.md copy command also wrote to `projects/working/DuckRabbit`.
3. **Minor** - AGENTS.md "Shared-worktree reconciliation" describes branch
   `codex/duckrabbit` while the default branch is `main`; clarified.
4. **Minor** - No dated status surface beyond TODO.md/CHANGELOG.md prose;
   addressed via orientation ladder in AGENTS.md pointing at canonical files.
5. **Minor** - Slow cold imports are an ergonomics trap for agents; noted in
   AGENTS.md and TODO.md.

## Phase 3 — implemented

- Fixed all 16 figure-path references (03_results, 07_publication_audit, SYNTAX).
- Updated stale `working/` location claims in README.md, AGENTS.md,
  STANDALONE.md.
- Added an orientation ladder (status / next actions / verification) to
  AGENTS.md and a push-target signpost (`main`).
- Appended dated section to TODO.md.

## Phase 4 — verification

- Relative-link check re-run across tracked .md: figure links resolve.
- Registry/catalog live-count check attempted (see TODO entry); cold-import
  cost on the external drive is the blocker for a fast in-session check.
