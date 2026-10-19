# Changelog

## Unreleased — documentation and robustness improvement pass

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
- Bundled evidence resources for installed wheels, restored Python 3.10
  imports, included YAML in the dev extra, and expanded CI interpreter and
  installed-wheel checks.
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
