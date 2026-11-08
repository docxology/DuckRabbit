# Qualify a candidate before creating a release or DOI

**Current candidate: 0.6.0, unreleased; DOI forthcoming.** Local gates,
source integration, or a green main branch do not publish it. The released
v0.5.0 [concept DOI](https://doi.org/10.5281/zenodo.21419693) and
[version DOI](https://doi.org/10.5281/zenodo.21419694), tags, assets, and
historical review bundles remain immutable.

The [publication guide](publication.md) owns native generation and isolated
rendering; this checklist owns acceptance and external sequencing. Read
[TODO](../TODO.md) and [CHANGELOG](../CHANGELOG.md) for current status, not a
historical gate count copied into this checklist.

## Bind the exact candidate and its public metadata

- Preserve package, tests, manuscript, bibliography, evidence, license,
  changelog, citation, CodeMeta, and Zenodo metadata in the public source.
- Require Daniel Ari Friedman, Active Inference Institute, ORCID
  `0000-0001-6232-9096`, and `https://github.com/docxology/DuckRabbit` consistently.
- Require version, title, license, and DOI state to agree. Before deposit,
  use empty DOI fields and `forthcoming`; never fabricate a placeholder.
  Do not attach the old archive's identifiers to this candidate.
- Exclude participant data, private fixtures, credentials, and temporary
  environments/caches/profiles from release contents. Declare curated review
  bundles separately from archived release assets.
- Freeze the source revision before verification; record source/input/output
  hashes, actual commands, runtime/dependency/font identities, and failures.
  Verification against a changing tree cannot bind the final source.

## Pass native software and offline publication gates

From the repository root, use the locked development environment:

```bash
uv lock --check
uv sync --locked --extra dev
uv run ruff check src scripts tests
uv run pytest tests/ --cov=src/duckrabbit --cov-fail-under=90
uv build --out-dir dist/package-candidate
```

Use a fresh repository-local package directory rather than mixing historical
builds. Run the [canonical native publication recipe](publication.md#generate-and-audit-a-native-bundle)
in a separate fresh owned bundle. It includes offline scholarship validation,
hydration, the nonhuman synthetic sidecar, and strict `audit --release`.
Do not use destructive cleaning or overwrite retained outputs.

Also perform an independent installed-wheel API/CLI smoke outside the source
import path on the supported Python 3.11 floor, including bundled evidence,
actual generation, inspection, and verification. Exercise supported development
runtimes separately; `.python-version` selects 3.15, not a patch. A retained
3.15.2 run is not a fresh clean-environment result. Missing compatible wheels,
unsuccessful locked sync, optional codec gaps, or an unrun compatibility lane
are explicit gaps. There is no native type-checker gate; do not invent one.

Review current dependency/security advisories and native decoder/tool exposure.
Passing tests, finite parameter validation, and hashes are not a sandbox,
resource-exhaustion guarantee, or security certificate. Keep measured advisory
outcomes tied to exact installed versions and the observation date.

## Clear live scholarship and actual delivery review separately

- Run the [explicit live scholarship gate](publication.md#separate-offline-replay-visual-review-and-live-scholarship)
  and review all additional manuscript citations outside its native roster.
  [Scholarship](scholarship.md#separate-offline-lineage-from-live-identity)
  owns coverage and the retained unresolved identity observations. URL
  reachability, archive access, and display abbreviations do not establish
  ordered title/author/year identity, including collective authors.
- Preserve unresolved, mismatched, blocked, or unavailable identities as
  failures. They still block release; a local offline audit cannot waive them.
- Typeset from the exact hydrated inputs using a declared read-only renderer
  snapshot and repository-local overlays, outputs, caches, and temporary state.
  Record transformations without modifying canonical inputs or sibling files.
- Inspect every PDF page, HTML view, and slide deck; review scientific figures
  at intended delivery scales, captions, tables, diacritics, citation targets,
  browser behavior, accessibility, and clipping. See the
  [visual review criteria](visualization.md#inspect-readability-at-delivery-scale).
  Compilation, same-code replay, and `visual_qa` are not visual acceptance.
- Bind the [current review bundle](../output/visual-review-2026-11-08/) to fresh
  evidence. The [retained prior baseline](../output/review-2026-11-08/) and all
  [dated receipts](README.md#dated-historical-receipts) verify only their own
  recorded source, not later edits.

## Publish only after authorized acceptance

1. Integrate the exact verified source through the repository's authorized
   ordinary fast-forward/branch-protection process; confirm required CI.
2. Create the immutable version tag and archive that exact source and generated
   publication bundle. Verify remote commit/tag and asset byte identities.
3. Mint real DOI identifiers from the public deposit.
4. Update DOI fields and `doi_status: published` atomically across manuscript
   configuration, `CITATION.cff`, `.zenodo.json`, and `codemeta.json`; rerun the
   affected metadata, scholarship, render, and release gates against final assets.
5. Record the actual public release/deposit and final metadata-to-asset binding.
   Do not describe a local build, branch push, or draft PR as released.

The [dated November audit](audit-2026-11-08.md) distinguishes multiple historical
PDF identities; earlier prose does not establish their equivalence. Preserve
those artifacts rather than replacing them with the candidate. A future human
study needs its own consent/governance, preregistration, calibrated presentation,
observed responses, estimand, and analysis; no publication check supplies them.
