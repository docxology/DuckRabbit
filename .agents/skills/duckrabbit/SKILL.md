---
name: duckrabbit
description: Extend the typed multimodal audio, image, video, and audiovisual illusion generator.
---

## Workflow

1. Read the project `AGENTS.md` and `docs/architecture.md`.
2. Add or update immutable typed parameters before generator logic.
3. Register every new generator with taxonomy facets and an explicit evidence
   status.
4. Keep canonical output in memory; put encoding in lazy adapters.
5. Add no-mock tests for boundaries, determinism, invariants, and round trips.
6. Run the project test and CLI smoke commands before handing off.

## Claim boundary

Generated media is a reproducible stimulus. It is not evidence that every
observer will perceive the intended illusion. Use `input_required` for families
that need a fixture or validation contract not present in the package.
