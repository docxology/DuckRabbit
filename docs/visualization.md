# Build and inspect scientific figures without overstating evidence

This guide owns graphic interfaces, display interpretation, and readability
review. Use the [publication recipe](publication.md#generate-and-audit-a-native-bundle)
for commands; use [architecture](architecture.md) for module ownership and
[scholarship](scholarship.md) for the source/claim boundary.

## Live roster and historical baseline

The refreshed source has **16 scientific figures and 10 tables**. The added
figure is `fig:graphical_abstract`, stem `graphical_abstract`; it summarizes
deterministic multimodal stimulus construction and verification. Existing
figure labels/filenames and manuscript section/equation labels stay stable.
Adding this overview does not add a generator, catalog family, evidence source,
or participant dataset. Query the live registries for those inventories;
do not derive them from the number of panels or illustrations.

The [current visual-review bundle](../output/visual-review-2026-11-08/) carries
its own generation, source, runtime and visual-review receipts; consult their scope.
The [retained November baseline](../output/review-2026-11-08/) contains the
previous **15** scientific figures. That historical count and its dated
receipts remain correct for their bound inputs; neither those outputs nor the
[October render](rendering-2026-10-19.md) verifies the refreshed source.

### Scientific graphical abstract versus editorial cover

The graphical abstract is a registered, source-owned scientific overview:
it connects typed requests, canonical image/audio/video/audiovisual media,
encoding/decoded inspection, and explicit verification/claim boundaries. Its
PNG and source-data JSON participate in caption, hash, and derivation checks
like the rest of the scientific roster. It is not an observer experiment or a
new empirical result.

The cover is a separate editorial illustration, not a scientific stimulus,
measured percept, or substitute for the graphical abstract. Its source bytes,
variant transforms/dimensions, and hashes are checkable; reported historical
image-generation provenance remains unverified. Arbitrary replacement art must
not acquire invented model/prompt/history claims. See
[`cover.py`](../src/duckrabbit/cover.py).

## Source-owned figure interfaces

| Source authority | Interface |
| --- | --- |
| [`publication_specs.py`](../src/duckrabbit/publication_specs.py) | `PUBLICATION_FIGURE_LABELS`, `CaptionSpec`, stable stem/label and caption-variable naming. |
| [`publication.py`](../src/duckrabbit/publication.py) | Builders, `publication_caption_specs()`, source-data production, tables, registry/report validators, raster QA. |
| [`publication_panels.py`](../src/duckrabbit/publication_panels.py) | Source-derived readable detail variants, their exact source/font/code provenance and replay; not additional scientific figures. |
| [`manuscript_variables.py`](../src/duckrabbit/manuscript_variables.py) | Registry-derived figure/table counts, captions/alt text, and exact Markdown hydration. |
| [`formalism.py`](../src/duckrabbit/formalism.py) | Executable links between equations, modules, tests, manuscript labels, and figures. |
| [`audit.py`](../src/duckrabbit/audit.py) | Native structural/hash contracts, scientific data/raster replay, and exact delivery checks. |

Within a selected bundle, `figures/<stem>.png` pairs with
`data/<stem>.json` (`duckrabbit/figure-source/v1`) and a record in
`figures/figure_registry.json`. Each record binds raster and source-data
SHA-256, title, full caption, alt text, controls, objective facts, seed/parameters,
claim level, limitations, evidence lineage, and structural visual-QA facts.
Logical `output/figures/...` and `output/data/...` paths rebase to that bundle.
Treat JSON as the authority for exact machine-copy values, not wrapped PDF text.

Keep captions and alt text beside the registered builders. Captions must name
source data/digest lineage, controls, objective units or explicit
non-applicability, `Limitations:`, and `Boundary:`. A title should tell the
reader what construction, comparison, or verification is shown; a stable
identifier is not a sufficiently informative title on its own.

## Read dense details without shrinking audit content

The catalog, audio atlas, scholarship map and formalism crosswalk have
source-derived readability panels in addition to their complete overview PNGs.
Native publication generation writes `reports/readable_figure_panels.json`; its
`panel_count`, figure labels and `record_ids` are the inventory authority. These
are representational variants, not new generators, datasets or scientific claims.
The registered scientific figure count remains 16.

Each `figures/<stem>-detail-XX.png` binds an exact source-data record and retains
complete identifiers, displayed facts and units at a larger effective scale.
Audio panels preserve channel-separated extrema and declared spectral values,
not the original sample-by-sample signals. The report binds actual dimensions,
PNG/source-data hashes, font, dependencies and renderer implementation. Each
source digest is computed from the same snapshot bytes whose records are
replayed, so a staged file replaced after loading cannot be certified against
an unvalidated hash. Strict replay must reject missing, stale, substituted or
unsafe variants even when a contributor refreshes their declared hashes.

Declared renderer-source adapters retain the canonical overviews and captions,
then add readable panels in explicit contexts without creating new numbered
scientific figures. Table captions receive their own correct table context, and
following narrative leaves the preceding row-heading scope. These are layout
adaptations, not edits to canonical data, manuscript facts or frozen renderers.


## Interpret signal displays as summaries of canonical data

- **Image panels:** float32 canonical pixels differ from uint8 PNG delivery.
  NPZ preserves exact arrays. A representative first frame cannot stand in for
  a full temporal sequence or its clock/transition data.
- **Audio envelopes:** use per-channel min/max bins covering all samples,
  including the final partial bin. This peak-preserving display summary avoids
  dropping impulses between decimated points. It is an envelope, not an exact
  sample-by-sample waveform or a downmixed listening result. Source data must
  expose the bin/sample/time convention and channel extrema; RMS/peak metrics
  still refer to the canonical buffer, not the compact display.
- **Spectral summaries:** the compact display declares band edges, aggregation,
  channel handling, normalization, and plotted values. Peak-aggregated display
  bands are not substitutes for full-resolution magnitude-weighted spectral
  metrics; their heights do not constitute pitch or hearing reports.
- **Audiovisual traces:** use seconds on one shared axis, actual sample/frame
  timestamps, frame-held video values, and declared signed stream starts.
  Rec.709-weighted RGB channel values are uncalibrated code-value proxies, not
  linearized or physically measured display luminance. Rectified audio amplitude
  is not a calibrated sound-pressure level or an observer response.
- **Synthetic diagnostics:** serialize model identity, features, weights,
  temperature, seed, canonical digests, controls, and `human_data=false`.
  Ablations and finite temperature sensitivity show model behavior only;
  their envelope is not a confidence interval or human uncertainty.

Display regression acceptance should retain skipped impulses, alternating
signals, stereo channel separation, and final partial bins. Replay must reject
coordinated raster/sidecar/hash substitutions rather than trusting a refreshed
container hash. These requirements concern faithful signal communication;
they cannot demonstrate that an intended illusion was perceived.

## Inspect readability at delivery scale

Publication rasters use NumPy/Pillow primitives. Set `DUCKRABBIT_FONT_PATH` to
bind an explicit TrueType font when reproducible typography matters; record
its bytes/hash alongside runtime, Pillow/FreeType, source, and parameters.
The first available platform font is not a cross-environment byte guarantee.

Review every primary figure and readable detail at full resolution and actual
manuscript/slide size; thumbnail views establish hierarchy, not detail legibility.
Review their placement on every delivered PDF/HTML/slide surface. Check title
hierarchy, readable units/legends, contrast, channel
separation beyond color alone, intentional margins, complete text, and absence
of overlap/clipping. At thumbnail scale, check recognizable hierarchy rather
than pretending all detailed labels remain readable. Alt text should explain
the construction without requiring color vision or claiming an observer effect.

Inspect the full scientific roster, captions, tables, equation/citation targets,
identifiers, and complete reference payloads. A claim of actual review must
record which files/pages/scales were seen, their bound inputs, observed defects,
and remaining limits. Browser behavior, print readiness, and accessibility
need their own observed acceptance; do not infer them from a compiled file.

`reports/visual_qa.json` records structural image facts and deterministic
thumbnail hashes. The native audit can recompute them and replay trusted
builders, but cannot see clipping, assess semantic legibility, authenticate
provenance, perform live scholarship verification, or establish a human percept.
Optional typesetting uses the [isolated renderer boundary](publication.md#isolate-optional-typesetting),
never sibling writes or modified historical deliveries.
