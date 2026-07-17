# DuckRabbit testing philosophy

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
19. the package-level audit independently regenerates every implemented default,
    recomputes canonical hashes, checks metrics, and reports missing disposable
    publication output as a warning rather than silently skipping the release
    surface;
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
