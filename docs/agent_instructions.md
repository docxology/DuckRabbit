# Agent instructions for DuckRabbit

Read the project `AGENTS.md`, `docs/architecture.md`, and
`docs/testing_philosophy.md` before editing. The implementation is a typed
media-generation package focused on reproducible multimodal stimulus construction.

Core generators must remain deterministic, infrastructure-independent, and
free of filesystem side effects. Optional codecs belong behind explicit lazy
adapters. Tests must use real computations and files, with a 90% coverage gate.

Do not edit `output/` by hand. Change source/configuration and regenerate it.
Do not promote a planned or input-dependent taxonomy entry without a concrete
typed generator or fixture contract, source-tiered evidence, objective
invariants, deterministic tests, and an explicit limitation. The Zöllner and
auditory-continuity promotions are examples of this gate; McGurk remains
input-dependent because its speech fixture and validation contract are absent.
