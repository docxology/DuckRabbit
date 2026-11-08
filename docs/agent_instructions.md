# Change DuckRabbit source without crossing evidence boundaries

Read [AGENTS.md](../AGENTS.md), [architecture](architecture.md), and
[testing contracts](testing_philosophy.md) before editing. The
[documentation index](README.md) routes current tasks; dated reviews are not
current acceptance records.

## Put each change in its owning layer

- Validated immutable parameters precede generator logic. Core generators
  return canonical objects, remain deterministic, and perform no filesystem I/O.
- Register implemented generators with taxonomy facets, source-tiered evidence,
  objective invariants, and tests. Do not upgrade `planned` or `input_required`
  from a demonstration alone. McGurk still needs real checksummed speech assets
  and the fixture/validation contract.
- Keep codec imports lazy in media adapters; file coordination belongs in the
  render layer, not in generators. Thin scripts delegate to package behavior.
- Change figures/captions/source-data builders together. The
  [visualization interfaces](visualization.md#source-owned-figure-interfaces)
  own labels, sidecar lineage, readable delivery, and scientific limits.
- Keep manuscript section/equation/figure labels stable when improving titles.
  Generate counts, captions, and tables from their source registries rather
  than copying changing numbers into more guides.

## Preserve source and output custody

Do not hand-edit generated output. Choose a fresh, wholly owned repository-local
bundle and use the [native publication recipe](publication.md#generate-and-audit-a-native-bundle).
Do not use `--clean` by default, overwrite dated review trees, modify sibling
checkouts, or use external temporary-output lanes. Hydration also replaces its
owned manuscript delivery files, so it must not target a mixed-use directory.
Optional renderers are read-only inputs with separately recorded overlays,
outputs, fonts, tools, and caches inside this repository.

Use the interpreter line selected by `.python-version` for development; preserve
`pyproject.toml`'s Python 3.11 support floor. A retained 3.15.2 run is evidence
for that runtime, not a promise that an unprovisioned environment will resolve.

## Hand off bounded evidence, not confidence language

When assigned verification, use the [native testing gates](testing_philosophy.md#run-the-native-software-gates)
and report actual commands, environment, source/output bindings, outcomes,
skips, and failures. When assigned source-only work, do not run builds, tests,
linters, formatters, or renderers; name the required integration checks instead.
Do not run verification against a tree another writer is changing.

Offline schema/hash/replay checks, actual visual inspection, and live scholarly
identity checks are separate. `visual_qa` is structural raster evidence, not a
human readability verdict. Preserve `human_data=false`; neither metrics nor a
synthetic sensitivity envelope establishes a participant result or confidence
interval. Report unavailable capabilities and unresolved source identities
without lowering their gates.

0.6.0 remains unreleased with DOI forthcoming until the authorized
[release sequence](public-release-checklist.md) finishes. Do not relabel older
PDFs or historical receipts as evidence for new source.
