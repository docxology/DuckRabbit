# Reproducibility and Provenance {#sec:reproducibility}

The reproducibility contract is:

1. construct the same frozen parameter dataclass;
2. use the same generator ID and the same deterministic seed;
3. compare the canonical artifact digest;
4. record the parameter schema, typed parameters, taxonomy, evidence boundary,
   canonical byte serialization, objective metrics, and encoding request;
5. if a file is written, inspect the decoded media and compare dimensions,
   channels, rates, frame counts, durations, timing offsets, and encoded hash;
6. retain the v2 manifest and source-data sidecars with the generated figure or
   table.

The contract is deliberately stronger than “the file can be downloaded.”
Research-software guidance treats versioned code, executable procedures,
dependencies, and retained inputs as part of the reproducible object
[@sandve2013simple; @wilson2014bestpractices]. FAIR guidance further asks that
digital research objects be findable, accessible, interoperable, and reusable,
while noting that software has lifecycle and maintenance constraints that are
not identical to those of static data [@wilkinson2016fair;
@lamprecht2020fairsoftware]. DuckRabbit operationalizes those principles with
typed metadata, deterministic hashes, source-data sidecars, explicit licenses,
and release gates rather than by implying that a generated media file is a
complete scientific replication.

The package reports {{STATUS_LABELS}} as its catalog status vocabulary and
currently covers {{MODALITIES}}. The evidence layer contains {{EVIDENCE_RECORDS}}
entry records backed by {{SCHOLARLY_SOURCES}} source records. The publication
workflow produces {{PUBLICATION_FIGURES}} figures and {{PUBLICATION_TABLES}}
tables from the live registry.

The public software record is
[the DuckRabbit public GitHub repository](https://github.com/docxology/DuckRabbit),
with Daniel Ari Friedman of the Active Inference Institute as author. The
release is archived on Zenodo at
[10.5281/zenodo.21419693](https://doi.org/10.5281/zenodo.21419693) (concept
DOI, always resolves to the latest version), with
[10.5281/zenodo.21419694](https://doi.org/10.5281/zenodo.21419694) identifying
this v0.5.0 release specifically.

The canonical buffer is the primary identity of a stimulus. Encoded files are
delivery artifacts with format-specific tolerances. The observer protocol is a
separate evidence layer: a manifest can prove what was presented without
proving what an observer experienced.

Synthetic psychophysics is a third, deliberately bounded object. The model
identity, version, feature schema, weights, temperature, seed, calibration
statement, canonical reference/comparison digests, and `human_data=false` flag
are retained in `output/data/synthetic_psychophysics.json`. Re-running this
diagnostic checks deterministic model orchestration and stimulus-feature
sensitivity; it does not estimate a human observer or replace empirical
psychophysics.

The v2 verifier is a relational check rather than a field-presence check. It
rejects summaries whose dimensions, dtype, byte count, rates, duration, signal
range, frame deltas, or signed audiovisual offset disagree. Public manifest and
inspection mappings are recursively frozen after validation, and rational frame
rates are reduced before entering the clock contract. The read-only capability
probe records whether Pillow, NumPy, ffmpeg, or ffprobe are available in the
current environment; unavailable delivery paths remain explicit rather than
being silently downgraded.

The minimal regeneration commands are:

```bash
uv run pytest -q --cov=src/duckrabbit --cov-fail-under=90
uv run python scripts/generate_publication_outputs.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Data availability and software citation

No participant records, fitted observer coefficients, or human psychophysics
are bundled. The synthetic diagnostic is explicitly model output with
`human_data=false` and `training_data=none`. Reuse should cite Daniel Ari
Friedman and the release metadata in `CITATION.cff`, together with the
source-specific scholarship in `references.bib`. Software-citation principles
recommend citing the software object itself, with enough version and identity
information to distinguish one release from another [@smith2016software]. The
DOI field carries the real, minted concept DOI
(`10.5281/zenodo.21419693`) and `doi_status` is `published`; no resolver URL
was manufactured before that identifier existed.
