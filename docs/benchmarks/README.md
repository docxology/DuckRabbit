# Engineering benchmark receipts

`2026-10-17.json` retains real Python 3.15 workload samples, source maps,
configuration/result fingerprints, environment details, traced allocation peaks,
and selected diagnostic profile rows from the dated review. Earlier hardened
batches remain visible alongside the final presentation-equivalent comparison
and separate alternating startup measurements.

This compact receipt is not a `duckrabbit/performance/v1` baseline. CLI
comparisons accept the original full `report.json`, with complete scenario/input
maps. Profile rows are instrumented diagnostics, never ordinary timing samples.
Absolute checkout/dependency paths are normalized; no executable/pickle profile
data is included.

These are measured snapshots, not every future checkout. Generate fresh local
reports before claiming improvements in another environment or revision. No
timing threshold gates correctness tests, and no result is human evidence.
