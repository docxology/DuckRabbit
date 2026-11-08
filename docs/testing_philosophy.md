# Test real media contracts and state what verification cannot establish

## Run the native software gates

When assigned verification, run from the checkout root in the locked native
development environment. The supported floor is Python 3.11;
`.python-version` selects the 3.15 development line.

```bash
uv sync --locked --extra dev
uv run ruff check src scripts tests
uv run pytest tests/ --cov=src/duckrabbit --cov-report=term-missing --cov-fail-under=90
```

The 90% gate is combined statement/branch coverage, not branch-only coverage or
exhaustive behavioral assurance. Tests use real arrays, files, encoders, decode
round trips, and subprocesses rather than mock frameworks. Optional backend
absence must remain an explicit capability result. Do not verify a moving
source tree; report exact runtime, source binding, skips, failures, and commands.
Source-only assignments leave integration verification to their owner.

## Preserve deterministic and adversarial contracts

The package tests the irreducible contracts of stimulus generation:

1. invalid typed values fail before generation;
2. canonical arrays are finite, normalized, shape-valid, and read-only;
3. repeated requests produce identical buffers and digests;
4. audio/video durations and declared offsets remain coherent;
5. real encoders produce nonempty files or clear capability errors;
6. every implemented registry entry has taxonomy metadata and a callable.
7. every encoded manifest contains an actual file digest and media type;
8. each supported PCM depth produces a readable WAV with the declared width;
9. canonical NPZ archives preserve exact normalized arrays and clock metadata;
10. v2 manifests reject inconsistent taxonomy, canonical, encoding, and
    decoded-media facts;
11. stale encoded hashes and malformed v1/v2 records fail as negative controls;
12. CLI discovery, inspection, verification, and malformed parameter files fail
    with structured, actionable behavior.
13. exact NPZ content cannot be changed while merely refreshing its container
    hash; canonical rehydration must agree with the manifest digest;
14. generated figure and cover registries are independently checked for
    caption/evidence lineage, dimensions, source-data hashes, and variant hashes.
15. v2 summary relationships are negative-tested for shape/dtype/nbyte,
    duration/rate, frame-delta, RMS/peak, and audiovisual offset inconsistencies.
16. recursively frozen manifest/inspection mappings and reduced rational
    timebases are tested as API immutability and clock-identity contracts.
17. formalism implementation paths, test paths, manuscript equation labels,
    and figure labels are resolved by an independent traceability validator.
18. strict evidence loaders reject malformed JSON types instead of coercing
    numbers or nulls into plausible citation strings;
19. the package-level audit regenerates every implemented default with trusted
    code, recomputes canonical hashes, checks metrics, and reports missing
    disposable output as a warning outside fail-closed release mode;
20. synthetic psychophysics model contracts reject unknown features,
    non-finite weights, invalid probabilities, malformed digests, and human
    claim levels, while repeated model diagnostics preserve exact predictions
    and explicit `human_data=false` provenance;
21. the synthetic CLI writes a JSON diagnostic whose model identity, feature
    schema, seed, canonical digests, and epistemic boundary can be inspected
    without participant data or network dependency.

Tests do not assert that every observer experiences an illusion. That requires
separate human or behavioral validation under controlled presentation
conditions. The package records stimulus intent and evidence status instead.

## Distinguish structural QA from actual visual inspection

Use the [native publication recipe](publication.md#generate-and-audit-a-native-bundle)
for an isolated generated bundle and strict `audit --release`. The release
audit replays registered scientific raster/data builders and exact hydrated
delivery; it can detect coordinated corruption against trusted source but is
not an independent implementation. Structural `visual_qa` facts and thumbnail
hashes do not establish readable labels, unclipped layout, contrast, page fit,
browser behavior, accessibility, or print readiness.

[Visualization](visualization.md) owns signal-envelope regression expectations
and actual full/column/thumbnail inspection criteria. Typeset outputs need
their own bound renderer execution and page/deck review. Historical receipts
certify only their recorded source, never later edits.

## Keep security and scholarly assurance bounded

Manifest validation treats paths, hashes, shapes, dtypes, clocks, source-data
relations, and decoded facts as untrusted declarations. Real negative controls
must reject incompatible containers, stale/refresh-only hashes, inconsistent
summaries, and canonical NPZ substitutions. These guards do not sandbox native
decoders, bound every hostile allocation/workload, authenticate authorship, or
replace dependency/security-advisory review.

Offline [scholarship validation](scholarship.md#separate-offline-lineage-from-live-identity)
uses checked-in source lineage, without network identity claims. Explicit live
title/author/year checks are a separate release gate; reachability alone is not
verification. Neither software checks nor model diagnostics establish human
perception. Synthetic diagnostics retain `human_data=false`; human studies need
their own calibrated presentation, consent/governance, design, and observed data.
