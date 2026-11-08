# Changelog

## 0.6.0 — unreleased candidate (2026-11-08)

- Reject missing/extra MP4 streams, transparent or mismatched PNG containers,
  malformed legacy downgrades and NPZ summary/digest/byte-count tampering.
  Reconstruct exact canonical arrays and reject silently coerced NPZ dtypes;
  retain failed encoding evidence.
- Correct PCM32 endpoint conversion, short high-rate GIF timing, optional typed
  parameter restoration and finite-duration overflow before allocation.
- Restore visible Poggendorff occluder contrast instead of white-on-white
  erasure. This intentionally changes that family's canonical raster and metrics;
  it does not demonstrate an observer-level illusion effect.
- Add metrics/v3 explicit uncalibrated color/transfer/window/channel provenance
  and computation-definition hashes; align audiovisual RGB traces with images.
- Replay declared NPZ metrics, distinguish unsupported historical computations,
  and make temporal summaries independent of input array memory layout. C-order
  float32 reductions can change older Fortran-layout rounding, not canonical bytes.
  Reject unrepresentable JSON numerics through structured domain errors.
- Add synthetic zero-difference controls, per-weight ablations and temperature
  sensitivity, with complete features and finite, non-empirical envelopes.
- Make observer plans coherent illustrative forced-choice designs; use exact
  two-sided Fisher tests for binary power, report Monte Carlo intervals, retain
  zero response categories and leave singleton variance/intervals unavailable.
- Validate actual HTML citation anchors, ordered bibliographic identity and
  exact taxonomy/source-role relationships. URL reachability no longer passes
  as DOI-less archival identity; release gates retain unresolved failures.
- Replace fabricated cover-generation certainty with cover/v2 byte/variant
  verification, replayed WebP derivation and unverified historical reports.
- Require consistent single-author metadata on every current release surface;
  reject equal-valued boolean/number substitutions in scientific source data.
- Replay scientific figure data/raster derivations and source-owned manuscript
  hydration during strict release audits; refuse auditing another checkout with
  the executing package's code. Record the renderer/runtime boundary honestly.
- Set the supported floor to Python 3.11 and CI through 3.15; synchronize 0.6.0
  metadata without reusing the immutable v0.5.0 DOI or claiming a new deposit.
- Preserve literal table identifiers, citation keys and complete DOI/URL values;
  add lossless line breaks instead of deleting characters or source locators.
- Correct publisher-verified author credit and initials, retain the complete
  53-author FAIR record and complete Wheatstone title, and accept exact ordered
  corporate authors while rejecting ambiguous person/group metadata.
- Deliver a separately named current-source manuscript/PDF/HTML/slide review
  with source-only semantic-preservation overlays, canonical table references,
  intact equation glyphs, local pinned web assets and scroll-accessible content.
  Digital review is not projection, accessibility or human-perception certification.
- Pin the qualified build backend, hydrate the manuscript before CI release
  auditing, and retain failed live bibliographic identities and the three distinct
  historical PDF identities rather than declaring or rewriting a release.

- Corrected audiovisual plots to use actual shared-clock seconds and frame
  holds; audio spectra now expose frequency-labelled peak-aggregated bands,
  real plotted values, channel rules, and normalization in source data.
- Aligned spectral-centroid equations and tables with the existing
  mean-channel magnitude calculation, and separated PNG quantization from
  exact NPZ canonical preservation in the encoding figure.
- Replaced workspace-specific manuscript instructions with the standalone
  workflow, clarified archived-versus-development revision status, and
  preserved output guides during manuscript hydration.
- Added reproducible workload profiling with source/environment/result bindings,
  separate cProfile and allocation passes, and Python 3.15 CI coverage.
- Removed canonical-array hash copies and repeated video/audio reductions;
  public canonical bytes, seeded results, and metric values remain unchanged.
- Deferred analysis/publication imports from the public facade without changing
  exported identities, and preserved guides/manuscript variables during cleanup.
- Corrected Müller–Lyer, Poggendorff, Kanizsa, and Ebbinghaus geometry;
  added objective stimulus-fidelity regression tests and Nyquist checks.
- Hardened manifest validation, full media decoding, GIF timing, NPZ writes,
  audiovisual verification, and atomic no-overwrite publication.
- Closed release-audit gaps for publication tables, visual QA, source lineage,
  producer identity, and required reports; metadata audits now enforce
  concept/version DOI roles and reject malformed author records.
- Fixed observer overrides, nested immutability, response provenance and
  validation, duplicate submissions, large-rate Poisson sampling, and
  impossible power assumptions. Synthetic outputs remain non-human data.
- Bundled evidence resources for installed wheels, included YAML in the dev
  extra, and expanded CI interpreter and installed-wheel checks. The supported
  Python floor is now 3.11, not the older README's 3.10 claim.
- Made canonical hashing incremental and enforced finite, unambiguous JSON
  serialization and typed nested schema constraints. See the dated review
  in `docs/review-2026-10-17.md` for scope and validation.

- Fixed the methodology power-calculation path so future-study power
  scenarios derive from the declared estimand rather than a hard-coded
  approximation.
- Hardened figure font fallback (explicit `DUCKRABBIT_FONT_PATH` pinning
  plus platform font search) and fixed label-collision issues in the atlas.
- Corrected script paths and thin-contract boundaries; renamed
  `scripts/z_generate_manuscript_variables.py` to
  `scripts/generate_manuscript_variables.py` with the manuscript-variables
  flow living in `duckrabbit.manuscript_variables`.
- Aligned `docs/publication.md`, `docs/public-release-checklist.md`, and
  `docs/quickstart.md` on one canonical regeneration sequence; removed stale
  local-only claims and personal paths from the boilerplate READMEs.
- Added a CI workflow and drift-guard tests that enforce
  `experiment_plan.yaml`, `domain_profile.yaml`, and the claim ledger
  against the live registries.
- Refreshed the CI toolchain to the current action versions
  (`actions/checkout@v7` and the pinned `astral-sh/setup-uv@v10.3.2`
  release).

## 0.5.0 — publication-readiness cycle, published

- Published to the public repository
  [docxology/DuckRabbit](https://github.com/docxology/DuckRabbit) (tag
  `v0.5.0`) and archived on Zenodo: concept DOI
  [10.5281/zenodo.21419693](https://doi.org/10.5281/zenodo.21419693), version
  DOI [10.5281/zenodo.21419694](https://doi.org/10.5281/zenodo.21419694).
- Added the 15-figure visualization atlas, 10 generated tables, cover
  provenance, source-data sidecars, and visual-QA metadata.
- Added typed claim lineage, source verification statuses, explicit evidence
  roles, metadata consistency validation, and strict release auditing.
- Expanded the catalog scholarship with contemporary reviews of perceptual
  organization, classic contextual-size evidence, and audiovisual causal
  inference; added methodological references for reproducible computation,
  FAIR research objects, FAIR research software, and software citation.
- Added prose and metadata checks that keep source links, rendered citation
  anchors, resolver links, and live package counts aligned.
- Synchronized authorship to Daniel Ari Friedman and ORCID
  `0000-0001-6232-9096`; DOI is real and minted, never a fabricated value.
- Preserved the synthetic observer as deterministic model output only with no
  participant data.

## 0.4.0 — scholarly methods expansion

- Added formalism traceability, objective metrics, observer-protocol schemas,
  and source-tiered publication outputs.

## 0.3.0 — typed multimodal stimulus platform

- Added strict canonical artifacts, manifests, encoders, decoded inspection,
  verification, and representative visual, auditory, temporal, and
  audiovisual generators.

## Next release targets

- Complete lawful, checksummed speech fixtures and a validation contract
  before promoting McGurk.
- Add empirical observer data only through a separately approved study.
