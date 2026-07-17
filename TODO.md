# DuckRabbit release-readiness backlog

This backlog is intentionally narrower than the catalog. DuckRabbit is not an
exhaustive ontology of all known illusions; it is a typed, evidence-bounded
stimulus-construction platform.

The `0.5.0` version stamped in `pyproject.toml`, `CITATION.cff`, `codemeta.json`,
and `.zenodo.json` is a pre-release working version, not a published/citable
release. "Completed through v0.5.0" below describes work already merged into
that in-progress version; "External publication actions" lists what remains
after the local release gates pass.
The local release candidate is internally complete; this sidecar does not claim
that a public tag, repository mirror, archive deposit, or DOI already exists.

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

## External publication actions

The local source and publication gates are complete. These actions require an
external repository or archive and therefore cannot be completed inside this
private sidecar:

- publish or mirror the exact release source to the intended public repository;
- create the immutable public version tag and archive the generated bundle;
- mint a DOI only after the public record exists; and
- replace the empty DOI and `forthcoming` status atomically, then rerun all
  metadata, scholarship, rendering, and release checks.

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

The release is ready only when all metadata names Daniel Ari Friedman with ORCID
`0000-0001-6232-9096`, the DOI is explicitly forthcoming, the live catalog is
17 implemented / 0 planned / 1 input-required, all 15 figures and 10 tables
regenerate byte-identically, scholarship statuses are independently auditable,
captions and claim lineage are complete, and package plus sibling-template
checks pass without participant data or universal perceptual claims.
