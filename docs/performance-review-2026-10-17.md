# Performance and presentation review — October 17, 2026

The [October 18 verification follow-up](verification-2026-10-18.md) separately
records live scholarship and current-source PDF availability. The measurements
and evidence boundaries below describe the October 17 snapshot.

This unreleased follow-up builds on the [correctness review](review-2026-10-17.md).
It changes engineering implementation and scientific presentation, not the
archived v0.5.0 release, DOI record, or participant-evidence status.

## Measurement design

- CPython 3.15.0 on macOS arm64, NumPy 2.4.2, Pillow 12.1.1,
  FreeType 2.15.0, zlib 1.2.12, and the same SHA-256-bound Arial font.
- Each workload has an excluded warm-up, five ordinary timing samples, one
  separate cProfile invocation, and one separate tracemalloc invocation.
  Instrumented timings are never ordinary benchmark samples.
- The controlled baseline is the frozen **post-correctness, pre-performance**
  implementation, not the archived release or unmodified `main`. Both sides
  use the identical final harness and share final publication, formalism,
  manuscript-hydration, manuscript-source, and generated-output corrections.
  This keeps changed scientific presentation out of the comparison.
- Executing source trees are validated and hashed before/after each run.
  Publication/audit input maps bind data, manuscript/bibliography, cover assets,
  metadata, bundled resources, and audit output. All eight final comparisons
  require identical environments, configurations, and deterministic results.
- Sequential batches on a shared workstation are not a controlled hardware
  experiment. Filesystem caches, system activity, and thermal conditions remain
  possible confounders. Ratios are descriptive medians, not confidence intervals,
  additive gains, or statistical significance.

See [the harness guide](performance.md) for commands and instrumentation guards.
[The durable receipt](benchmarks/2026-10-17.json) retains timing samples, source
maps, configuration/result fingerprints, environment details, traced allocation
peaks, and diagnostic profile rows. It is a compact engineering receipt, not a
`--compare` baseline report or a scientific evidence-matrix entry. Binary
profiles are neither loaded from untrusted input nor checked into the repository.

## Measured outcomes

| Workload | Baseline median (ms) | Candidate median (ms) | Candidate / baseline |
| --- | ---: | ---: | ---: |
| `catalog` | 42.296 | 38.210 | 0.903 |
| `canonical` | 15.341 | 15.098 | 0.984 |
| `video_metrics` | 4.034 | 1.989 | 0.493 |
| `synthetic` | 8.717 | 7.159 | 0.821 |
| `observer` | 7.774 | 6.693 | 0.861 |
| `media` | 131.951 | 123.423 | 0.935 |
| `publication` | 3390.664 | 3472.113 | 1.024 |
| `audit` | 1006.799 | 995.351 | 0.989 |

All eight final comparisons have matching configurations and result signatures.
Video metric median time is about half the controlled baseline; canonical
hash timing is nearly flat in this final batch despite the allocation gain.
The earlier retained batches show variability, not additional independent
experiments or evidence of a universal speedup.

Canonical traced peak: 3,146,308 → 1,574,081 bytes.
The noncontiguous video still needs layout normalization. Publication is
slightly slower and audit nearly flat in this batch; no improvement is claimed.

## Mechanisms and invariants

Canonical hashing consumes contiguous little-endian buffers through memoryviews
and shares digest/byte-count traversal with manifest construction. The public
byte serializer keeps its schema, bytes, and chunk boundaries. Noncontiguous or
differently endian arrays still require normalization; zero-copy is not claimed
for those cases. A real-allocation regression covers a contiguous 4 MiB image
without an image-sized temporary byte copy.

Video metrics and summaries compute adjacent-frame deltas once rather than
twice. Contiguous frames reuse scratch space; non-C layouts preserve the old
NumPy reduction order and exact values. Audio metrics reuse peak/RMS reductions.
Call-count and exact-array regressions establish these mechanisms independently
of wall-clock evidence.

Observer construction uses `collections.abc.Mapping` for runtime checks and
normalizes overrides once before recursively freezing JSON. Validation,
immutability, RNG algorithms, and draw order remain intact. Research runs
retained complete ordered equality across 13 workloads. Paired 12,288-trial
construction varied substantially; prototype gains are not treated as additive.

The facade defers analysis/publication imports while retaining public exports
and owning-module identities. Heavy CLI imports occur only in the selected
command. Eleven alternating fresh-interpreter pairs measured package import at
246.660 → 134.166 ms and CLI import/catalog listing at 200.539 → 129.146 ms.
These child timers exclude interpreter launch; they are not cold-disk or complete
process-startup measurements. Their hashes still match the final facade/CLI.

## Remaining measured costs

Publication remains dominated by Pillow PNG encoding and cover delivery.
Strict audits spend most time decoding/resizing and verifying figure QA.
Repeated batches do **not** establish a publication/audit speedup. Compression
quality, deterministic encodings, independent checks, and evidence freshness
are retained rather than weakened for a headline gain. Tracemalloc peaks are
traced temporary allocations, not RSS, all native memory, or prebuilt arrays.

Python 3.15 native sampling of an owned child process failed with
`Permission Error: Unable to access process memory on macOS`. No elevation was
attempted and no successful sampling capture is claimed. cProfile/tracemalloc
captures succeeded separately. Exit status alone is not proof of collected samples.

## Scientific presentation and documentation

- Audiovisual traces share actual seconds, signed stream starts, frame-held
  video values, and actual audio timestamps. The default flash starts at 0.25 s
  on a 0.5 s timeline, not an independently normalized sequence coordinate.
- Spectra span DC–Nyquist in 48 peak-aggregated bands with explicit frequency,
  channel/window/normalization rules and retained plotted values. Sparse
  selection no longer discards narrow peaks; the display is not a power spectrum.
- Centroid equations, the formalism registry, and metric tables describe the
  unchanged mean-channel magnitude weighting, including the silence floor.
- PNG delivery is uint8 quantization with retained canonical provenance, not
  exact float32 recovery. NPZ preserves exact canonical arrays. A textual
  mathematical relation avoids an unavailable font glyph, and spectrum
  headings no longer intersect panel rules.
- Standalone manuscript commands replace private workspace prerequisites.
  Markdown is regenerated, output guides survive cleanup, and prose separates
  the published archive from unreleased source corrections.

Tests use real arrays, actual raster coordinates, real codec round trips, and
serialized plot data. Final independent scoped reviews found no remaining
actionable profiling-provenance or corrected figure/manuscript defects; those
reviews are not universal certification.

## Final validation

Final combined suites ran against stable sources after publication regeneration:

| Interpreter | Tests | Branch-inclusive coverage |
| --- | ---: | ---: |
| Python 3.10 | 540 passed | 91.09% |
| Python 3.12 | 540 passed | 91.07% |
| Python 3.14 | 540 passed | 91.08% |
| Python 3.15 | 540 passed | 91.08% |

- Ruff, `git diff --check`, and locked dependency synchronization passed.
- Offline scholarship passed: 18 catalog/evidence entries, 36 sources, and
  47 bibliography entries. The strict release audit passed all ten check
  groups with zero errors and zero warnings.
- All 15 scientific figures, ten tables, sidecars, registries, and hydrated
  manuscript Markdown were regenerated from current sources. Repeated
  publication workload invocations retained identical output signatures.
  Actual regenerated timing, audio, encoding, and formalism figures were
  visually inspected in addition to numerical/raster regression tests.
- The final wheel was rebuilt, reinstalled into an isolated Python 3.10
  environment, and exercised outside the checkout: generation, bundled
  evidence/bibliography, claims, lazy-export identities, and publication
  imports passed.
- Profiling-source maps were rechecked against the final package checkout;
  ordinary timings remained separate from instrumented correctness tests.

## Evidence boundaries

Offline scholarship checks local shape, citation keys, and lineage; it does not
newly establish live DOI resolution. All 47 bibliography entries and 36
evidence-source keys remain linked without invented references. No participant
evidence, trained observer, or McGurk fixture is introduced. Synthetic output
retains `human_data=false`. The optional sibling template and a current-source
PDF/HTML/slides build are not certified by package checks; the historical
DOI-bearing PDF is intentionally not rewritten.
