# Durable workload profiling

For the October 17, 2026 measured results, source-bound receipts, limitations,
and figure corrections, see [the dated review](performance-review-2026-10-17.md).

Run from the checkout root with its installed environment. No timing assertion
is a correctness test. Use an idle machine and the same interpreter, dependency
versions, fonts, power settings, thread settings, and storage for comparisons.

```bash
uv run python scripts/profile_workloads.py --workloads canonical video_metrics observer --iterations 3 --output-dir /tmp/duckrabbit-baseline
uv run python scripts/profile_workloads.py --workloads canonical video_metrics observer --iterations 5 --output-dir /tmp/duckrabbit-candidate --compare /tmp/duckrabbit-baseline/report.json
uv run python scripts/profile_workloads.py --workloads catalog --iterations 3 --profile --memory --output-dir /tmp/duckrabbit-instrumented
```

`--output-dir` is mandatory. `--workloads` takes one or more space-separated
names (default: all). The integer iteration count defaults to 3; 1–30 is accepted,
with 3 or 5 recommended for manual investigation. Duplicate, empty, and unknown
selections fail. Inputs cannot request arbitrary sizes, seeds, callables, or
commands. JSON baselines are size bounded and validated before workloads run.

## Scenarios

| Name | Measured operation | Setup outside measurement |
| --- | --- | --- |
| `catalog` | Generate every registered default, canonical digest, objective metrics | Default typed requests and registry discovery |
| `canonical` | Canonical SHA-256 hashing | Prebuilt 24-frame 512×384 apparent-motion video |
| `video_metrics` | Objective video metrics | Same prebuilt video |
| `synthetic` | Full default duck–rabbit synthetic diagnostic | Imported implementation; no empirical observer evidence |
| `observer` | Trial construction and seeded binary simulation | Default design, 24 observer keys, probability 0.65 per condition |
| `media` | NPZ encode/decode and exact digest check; PNG/GIF/WAV encode/decode inspection | Video/audio buffers and fresh temporary directory |
| `publication` | Generate complete figures, tables, registry, cover and reports | Fresh temporary directory; never checkout `output/` |
| `audit` | `run_audit(..., release=True)` of checkout output; fail if not passed | Checkout output file hashes |

The default all-workload run includes expensive publication and strict audit.
Missing/stale release output is an error, not a skipped or successful audit.
The harness never regenerates checkout output. Use the inexpensive selections
in the first command when measuring a focused change. Media adapters use the
real NumPy/Pillow/WAV paths; ffmpeg is not required. The PNG/GIF/WAV inspectors
decode their media and NPZ must preserve canonical content exactly.

## What the report means

One excluded warm-up runs per scenario. Each iteration gets its own setup and
temporary directory before `perf_counter` starts. Timer boundaries contain only
the operation; result serialization, signature checks, report writing, setup,
and cleanup are excluded. File creation/decoding belongs inside media and
publication operations. This is warm-process, warm-filesystem measurement,
not cold-start latency or a cache-free benchmark. No global benchmark cache is
introduced. Warm-ups can populate normal library caches.

`report.json` records individual uninstrumented `samples_seconds`, median and
min/max range, exact Python/platform/dependency versions, resolved font identity
and content SHA-256, FreeType/zlib versions, workload configurations, and
deterministic result signatures. Source files have per-file SHA-256 and an
aggregate content binding, including uncommitted Python changes. Preserve the
report alongside the exact source checkout; it is not a Git-clean assertion.
The root must be the executing source checkout, with the project, wrapper,
package and harness anchors present; loaded DuckRabbit modules must resolve to
that checkout's package paths. An arbitrary directory cannot label code imported
from elsewhere. Baselines require a nonempty relative-path SHA-256 source map,
all required anchors, and an aggregate SHA-256 consistent with that map.
Changes to bound source files during measurement fail the run instead of
writing a report with an ambiguous source binding. JSON reports are published
atomically through the shared filesystem helper.

Publication and audit configurations also bind runtime input files: checkout
data (including evidence), manuscript and bibliography, cover assets, project
metadata (`pyproject.toml`, `codemeta.json`, `CITATION.cff`, `.zenodo.json`), and
bundled resources. Audit additionally binds every checkout output file. These
maps are rehashed after measurement, detecting additions, removals and content
changes before publishing the report. The publication scenario writes only to
fresh temporary output, not checkout output.

Comparisons calculate current/baseline median ratios only for matching
environment, workload configuration, and result signature. Ratios below one
mean a lower median, not statistical significance. Source hashes may differ:
optimization is the purpose. Scenario identity includes the workload-definition
hash, typed default requests or input buffer digest where applicable, and strict
audit output hashes. Changed scenarios or results are reported as mismatches,
never compared. The CLI exits with status 2 for any incompatible requested
comparison, retaining the report and mismatch reasons; no speedup is claimed.
Publication signatures hash every generated file, normalizing
only the temporary-directory prefix in embedded paths.

`--profile` adds **one separate cProfile invocation** per workload and writes
top 25 cumulative-time function rows to JSON plus a local `.pstats` file. Those
function times are instrumented diagnostic data, **not benchmark timings**.
`--memory` adds **one separate tracemalloc invocation** and reports its traced
peak bytes. Tracemalloc is **not full RSS** and does not describe all native
allocations or the prebuilt inputs. Both passes must reproduce the warm-up's
result signature. The harness never loads user-supplied `.pstats`/pickle files;
`--compare` accepts JSON only. Active Python tracing/profiling is rejected so
its overhead cannot silently enter the ordinary timing samples.

## Correctness tests under coverage

The public `run_workloads()` entry point and CLI always reject active tracing,
profiling or tracemalloc, and any registered `sys.monitoring` tool on runtimes
that expose PEP 669. Tool IDs 0–5 are checked (locally verified on Python 3.15);
even an idle reservation is rejected rather than risking mislabeled timing
samples. The guard never disables instrumentation or frees another tool's ID.
Coverage is not exempted, including its `sys.monitoring` backend. Functional tests exercise
the private `_run_workloads()` measurement engine directly so coverage can
observe real validation, computation, encoding, and report-writing paths.
Those temporary outputs are correctness-test artifacts, **not benchmark
evidence**, and their timings must not support performance claims. No public
flag bypasses the instrumentation preflight. CLI success and incompatible
comparison integration tests launch real uninstrumented subprocesses without
coverage startup environment hooks; guard tests call the public entry point.
Instability tests instrument real operation-return boundaries in disposable
checkout copies and mutate real input files; they never alter the source
checkout or its generated outputs.

## Optional Python 3.15 native sampling

The portable core targets Python 3.10+. Native sampling is a separate optional
Python 3.15 capability, not a replacement for uninstrumented measurements.
These flags were checked against the local Python 3.15.0 help on October 17,
2026; confirm them on your runtime before use:

```bash
uv run python -m profiling.sampling --help
uv run python -m profiling.sampling run --help
uv run python -m profiling.sampling run --sampling-rate 1khz --mode wall --collapsed --output /tmp/duckrabbit-sampling.txt scripts/profile_workloads.py --workloads canonical --iterations 5 --output-dir /tmp/duckrabbit-sampled
```

Treat the entire externally sampled run as instrumented: **do not compare its
report's timing samples** with ordinary reports. An out-of-process sampler is
not detectable via Python's tracing/profile hooks. Obtain the baseline and
candidate medians in separate unsampled runs. Missing `profiling.sampling`
means this capability is unavailable (use `--profile` instead), not that a
sampling profile succeeded. macOS process-inspection permissions can also
explicitly deny sampling; retain the command/error as a capability failure,
do not silently substitute another profiler or describe it as successful.

The parent run on this macOS host explicitly failed with
`Permission Error: Unable to access process memory on macOS`.
No elevation was attempted. This is a recorded capability failure, not a
successful sampling measurement.
