# Test guidance — DuckRabbit

Tests validate the package with real deterministic arrays, real temporary files,
Pillow round trips, and ffmpeg when available. Do not use `unittest.mock`,
`MagicMock`, `@patch`, or fake generated media. `monkeypatch` is allowed only
for explicit capability/error boundaries such as an absent executable, or for
sealing the network-transport seam at the module boundary (for example,
replacing `urlopen` in `test_scholarship_audit.py`).
Media and data outputs must still be real: never mock generated media or data.

Keep the coverage gate at or above 90% for `src/duckrabbit/`. Prefer invariant
assertions over brittle pixel snapshots: shapes, ranges, frame deltas, timing,
canonical digests, and codec-readable files are the meaningful contracts.

Keep new tests in the narrowest contract module listed in `README.md`. Add a
new module when a concern has a distinct oracle (for example evidence parsing,
objective metrics, or the project audit), rather than extending a historical
catch-all file. Every new generator promotion needs deterministic output,
boundary failures, taxonomy/evidence coverage, and at least one objective
invariant.
