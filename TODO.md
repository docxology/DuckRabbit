# DuckRabbit release-readiness backlog

This backlog is intentionally narrower than the catalog. DuckRabbit is not an
exhaustive ontology of all known illusions; it is a typed, evidence-bounded
stimulus-construction platform.

The `0.5.0` version stamped in `pyproject.toml`, `CITATION.cff`, `codemeta.json`,
and `.zenodo.json` is a published, citable release. Public repository:
https://github.com/docxology/DuckRabbit (tag `v0.5.0`). Concept DOI:
`10.5281/zenodo.21419693`; version DOI: `10.5281/zenodo.21419694`.
"Completed through v0.5.0" below describes work merged into that release;
"External publication actions" (now complete for v0.5.0) lists the handoff
steps to repeat for the next version bump.

## Completed through v0.5.0

- Strict typed scalar parameters, canonical image/audio/video/audiovisual
  artifacts, deterministic hashing, parameter schemas, and immutable mappings.
- v2 manifests with v1 up-conversion, encoded hashes, decoded inspection,
  relational summary validation, backend identity, and explicit capability
  errors.
- Seventeen implemented generators covering visual, auditory, temporal, and
  audiovisual families; McGurk remains the one `input_required` catalog entry.
- Zöllner and auditory continuity promotion with typed parameters, finite media
  invariants, evidence records, objective metrics, and deterministic tests.
- Typed objective metrics and observer-protocol schemas, including future-study
  estimands, randomization, missingness, exclusions, and model templates.
- Transparent synthetic feature-observer diagnostics with serialized features,
  weights, temperature, seed, model identity, and `human_data=false`.
- Fifteen deterministic scientific figures, ten generated tables, source-data
  sidecars, figure/caption registries, formalism traceability, and the editorial
  cover asset with provenance variants.
- Methods-paper manuscript, source-tiered bibliography, evidence matrix,
  limitations, reproducibility documentation, and sibling-template rendering.

## External publication actions (completed for v0.5.0)

- published the exact release source to the public repository
  (https://github.com/docxology/DuckRabbit);
- created the `v0.5.0` GitHub release and archived the generated bundle;
- minted the DOI from the public record (concept `10.5281/zenodo.21419693`,
  version `10.5281/zenodo.21419694`); and
- replaced the empty DOI and `forthcoming` status atomically, then reran all
  metadata, scholarship, rendering, and release checks.

Repeat this same sequence for the next version bump.

## Future research and optional improvements

- Formalize canonical identity, encoding tolerance, decoded inspection, timing
  conventions, metric provenance, and verification as typed mathematical
  contracts with executable traceability.
- Add typed metric units, color-space declarations, spectral-window metadata,
  frame-delta normalization, decoded stream facts, tolerance provenance, and
  computation-version hashes.
- Expand the synthetic observer with feature ablations, metamorphic tests,
  zero-difference baselines, model-parameter sensitivity, and explicit model
  uncertainty without presenting it as human psychophysics.
- Improve the atlas with frequency axes, explicit units, color-independent
  annotations, visual-QA reports, and optional deterministic SVG companions.
- Extend the methods/software paper with additional empirical literature and
  domain-specific stimulus-fidelity audits as the catalog grows.
- Replace duplicated mutable test counts with live registry assertions plus one
  intentional versioned catalog snapshot.
- Add modular tests for identity metadata, scholarship resolution, claim lineage,
  caption contracts, visual QA, exact output equality, synthetic diagnostics,
  and strict release mode.

## Completed documentation polish

- `CHANGELOG.md`, publication/release guidance, terminology, author identity,
  citation examples, and machine-readable metadata are present.
- The candidate-future boundary is represented by the live `planned` and
  `input_required` taxonomy statuses; no breadth claim is implied.
- Additional WebP/SVG publication variants remain optional until their
  deterministic and accessibility checks exist.

## Evidence gates

### McGurk

Keep `audiovisual.mcgurk` as `input_required` until a lawful, consented or
licensed speech/audio-video fixture has a checksum manifest, playback contract,
validation protocol, and explicit ethical review status.

### New codecs

Add codecs only when backend availability, deterministic settings, decoded stream
facts, timing tolerances, and unavailable-backend failures are testable in the
target environment.

### Human psychophysics

Run participant studies separately from this package. Generated media and
synthetic observer outputs are not participant evidence, psychometric functions,
universal perceptual claims, or estimates of observer sensitivity.

## Release gate

A release is ready only when all metadata names Daniel Ari Friedman with ORCID
`0000-0001-6232-9096`, the DOI is either explicitly forthcoming (pre-release)
or a real minted Zenodo DOI (published), the live catalog is 17 implemented /
0 planned / 1 input-required, all 15 figures and 10 tables regenerate
byte-identically, scholarship statuses are independently auditable, captions
and claim lineage are complete, and package plus sibling-template checks pass
without participant data or universal perceptual claims. v0.5.0 meets this
gate and is published under DOI `10.5281/zenodo.21419693`.

## Agent-ergonomics pass (2026-08-31)

- Fixed 16 stale `../output/figures/` relative links in
  `docs/manuscript/03_results.md`, `docs/manuscript/07_publication_audit.md`,
  and `docs/manuscript/SYNTAX.md` after the `docs/manuscript/` relocation
  (Medium, fixed this pass).
- Updated stale `working/` sidecar-location claims in `README.md`,
  `AGENTS.md`, `STANDALONE.md` (Medium, fixed this pass).
- Added orientation ladder and performance note to `AGENTS.md` (Minor, fixed).
- Deferred: replace prose catalog counts ("17 implemented / 0 planned /
  1 input-required") above and in README with a live registry assertion —
  the in-repo TODO already lists this; blocked this pass only by
  external-drive cold-import cost, not by any design problem.
