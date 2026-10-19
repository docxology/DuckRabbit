# DuckRabbit documentation

For reproducible workload profiling and interpretation, see
[`performance.md`](performance.md). Correctness/integrity findings and their
evidence boundaries are recorded in [`review-2026-10-17.md`](review-2026-10-17.md).
The [performance and presentation follow-up](performance-review-2026-10-17.md)
includes final validation, measured gains and non-gains, and
[structured benchmark receipts](benchmarks/README.md).
The [October 18 verification](verification-2026-10-18.md) records fresh live
scholarship, package gates, and the explicitly unsuccessful current-source PDF
attempt without replacing archived artifacts.
The [October 19 source closeout](closeout-2026-10-19.md) records successful
repository-specific lease admission and fresh source gates; the older exclusive
lock blocker is not treated as current.

- [`quickstart.md`](quickstart.md) — install, list, validate, and generate.
- [`architecture.md`](architecture.md) — typed pipeline and package layers.
- [`testing_philosophy.md`](testing_philosophy.md) — real-media test policy.
- [`agent_instructions.md`](agent_instructions.md) — contributor boundaries.
- [`scholarship.md`](scholarship.md) — source tiers, citation audit, and claim boundaries.
- [`publication.md`](publication.md) — author identity, DOI status, release metadata, and publication gates.
- [`public-release-checklist.md`](public-release-checklist.md) — external-publication handoff and DOI sequencing.
- [`review-2026-10-17.md`](review-2026-10-17.md) — correctness review, regression coverage, and remaining evidence boundaries.
- [`../CHANGELOG.md`](../CHANGELOG.md) — versioned release history and next evidence gates.

The sibling `template` checkout owns rendering and publication infrastructure.
This repository owns its package, tests, manuscript, and generated
artifacts; it does not copy the infrastructure payload.
