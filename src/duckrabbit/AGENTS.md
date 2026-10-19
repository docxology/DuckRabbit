# AGENTS.md — `DuckRabbit/src/duckrabbit`

> Tracked package sources in the public DuckRabbit repository. Follow
> `../../AGENTS.md` and `../AGENTS.md` for repository and core-layer contracts.

## What this is

Python package `duckrabbit` — the project's business logic (src-layout).

## Boundaries

- `__init__.py` keeps the public API stable while loading analysis and
  publication exports on demand. Preserve class/function identity and
  `__all__`, including installed-wheel behavior.
- Canonical byte serialization is versioned. Hashing may avoid copies, but
  must retain byte-for-byte identity, length prefixes, and endian normalization.
- Runtime evidence resources in `_resources/` mirror their source files;
  tests enforce equality. Never cache mutable checkout evidence globally.
- Profiling orchestration lives in `performance.py`, not script wrappers.
  Performance tests assert results, allocations, and call counts rather than
  machine-dependent wall-clock limits.
