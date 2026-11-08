# Publication Atlas, Caption Contract, and Scholarship Audit {#sec:publication_audit}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-canonical-table-note"}
Numbered-table references point to the [canonical manuscript](../web/index.html); they are not standalone local deck numbers.
:::

The publication layer is generated from the same typed package state as the
stimuli. It contains 15 scientific figures, 10
machine-readable tables, and a separately provenance-recorded editorial cover.
The cover is an illustration of the project's subject and methods aesthetic; it
is not a stimulus, a participant result, or evidence of a perceptual effect.

## Claim-level visualization {#claim-level-visualization}

![Four numbered boxes separate canonical stimulus, physical metric, encoded media, and observer hypothesis, with a boundary rule stating that observer effects require a separate study.](../../output/figures/claim_boundary.png){#fig:claim_boundary}

What this figure shows: Four numbered boxes separate canonical stimulus, physical metric, encoded media, and observer hypothesis, with a boundary rule stating that observer effects require a separate study. The four-stage boundary distinguishes what DuckRabbit can establish directly—canonical stimulus identity, physical/media metrics, and decoded encoded-media facts—from a future observer hypothesis. Source data output/data/claim_boundary.json records the stage definitions and boundary rule; the arrows describe increasing evidential requirements, not an inference that one stage establishes the next. Controls: claim levels in the taxonomy and manifest; seed not applicable to the explanatory diagram. Objective facts: no unit-bearing objective quantity is applicable; stage definitions and evidence boundaries are preserved in the sidecar. Claim level: source_supported. Source data: output/data/claim_boundary.json (SHA-256 digest recorded in the figure registry). Evidence lineage: formalism:eq:observer_estimand, formalism:eq:canonical_digest. Limitations: The diagram is a documentation contract and does not replace a preregistered observer study or empirical data. Boundary: A deterministic artifact can support a future hypothesis but cannot supply the observer data required to test it.

The claim boundary in [@fig:claim_boundary] is a typed epistemic interface. A
canonical digest identifies a deterministic buffer; objective metrics identify
properties of that buffer; encoded-media verification identifies facts of the
delivered file. A future observer hypothesis is a different object with its
own protocol, estimand, and uncertainty interval.

## Scholarship map and lineage {#scholarship-map-and-lineage}

![Rows map catalog entries to source tiers, exact supported claims, engineering bases, limitations, and implementation status.](../../output/figures/scholarship_map.png){#fig:scholarship_map}

What this figure shows: Rows map catalog entries to source tiers, exact supported claims, engineering bases, limitations, and implementation status. The map links every catalog entry to its primary, review, and theory records, then preserves the exact source-supported claim, engineering departure, limitation, and implementation status. Source data output/data/scholarship_map.json are generated from the checked-in evidence matrix; a source record supports only the statement written in that record and does not certify pixel- or task-identical replication. Controls: checked-in evidence matrix; source roles and entry statuses; audit date recorded in data/evidence_matrix.json. Objective facts: one evidence row per catalog entry (18 entries); source-tier counts, exact claim text, engineering basis, limitation, and gap status. Claim level: source_supported. Source data: output/data/scholarship_map.json (SHA-256 digest recorded in the figure registry). Evidence lineage: gregory1997visual, brugger1999duckrabbit, yildiz2022ponzo, hirst2020sound, bruns2019ventriloquist. Limitations: The offline snapshot validates citation and lineage structure; live resolver status is a separate audit, and classifications can remain contested. Boundary: Scholarship coverage bounds the package’s evidence record and does not establish that any generated stimulus produces a universal percept.

The source map [@fig:scholarship_map] and [@tbl:evidence_audit] make five
distinctions explicit: a primary demonstration, a review, a theoretical
account, DuckRabbit's engineering basis, and an evidence limitation. Brugger's
duck/rabbit study documents variation across figure variants and observers;
this supports a careful ambiguity-family record, not a universal bistability
claim [@brugger1999duckrabbit]. Yildiz et al. review competing explanations of
Ponzo-like illusions, so the catalog retains both a geometric construction and
an unresolved theoretical boundary [@yildiz2022ponzo]. Repp's tritone analysis
likewise motivates listener- and context-sensitive limitations
[@repp1997tritone].

The audit also treats software and its metadata as part of the scholarly
record. FAIR guidance emphasizes machine-actionable provenance and reuse, and
software-citation principles emphasize crediting an identifiable version rather
than citing an undifferentiated project name [@wilkinson2016fair; @smith2016software]. Accordingly, the release includes `CITATION.cff`,
CodeMeta, Zenodo metadata, versioned manifests, source-data sidecars, and
resolver-linked bibliography entries. These improve discoverability and
attribution; they do not increase the evidential level of any perceptual claim.

The public software identity is explicit: DuckRabbit is published and citable
at the [DuckRabbit public GitHub repository](https://github.com/docxology/DuckRabbit)
under the authorship of Daniel Ari Friedman, Active Inference Institute. The
development bundle is distinct from the already-published v0.5.0 archive.
Current source and manuscript corrections require a new versioned deposit;
optional template typesetting and page-level validation are separate gates,
not implied by a passing package audit.

## Formal traceability and objective metrics {#formal-traceability-and-objective-metrics}

![Rows connect equation labels to their mathematical definition, implementation paths, tests, figure labels, and claim levels.](../../output/figures/formalism_traceability.png){#fig:formalism_traceability}

What this figure shows: Rows connect equation labels to their mathematical definition, implementation paths, tests, figure labels, and claim levels. The traceability registry connects the nine numbered equations to symbols, implementation modules, tests, and registered figures. Source data output/data/formalism_traceability.json is the machine-readable crosswalk used by the manuscript; it demonstrates contract coverage and test linkage without converting formal notation into empirical evidence. Controls: formalism registry version; seed not applicable to the traceability diagram. Objective facts: nine equation records with implementation, test, figure, and claim-level fields; no unit-bearing measurement is plotted. Claim level: physical_metric. Source data: output/data/formalism_traceability.json (SHA-256 digest recorded in the figure registry). Evidence lineage: formalism:eq:canonical_digest, formalism:eq:clock_definition, formalism:eq:objective_statistics. Limitations: Traceability records documentation and verification scope; it does not establish the truth of an observer-level theory. Boundary: A linked equation and test can show an implemented contract, not a validated perceptual law.

The formalism registry [@fig:formalism_traceability] links equations
[@eq:typed_request; @eq:canonical_generation; @eq:canonical_digest; @eq:encoding_verification; @eq:clock_definition; @eq:objective_statistics; @eq:temporal_spectral_metrics; @eq:observer_estimand; @eq:synthetic_observer]
to implementation modules, tests, and figures. The contract is intentionally
auditable: equation labels point to code-owned records, while empirical claims
remain outside the generator's authority.

![Four artifact cards list image, audio, video, and audiovisual metrics with units, computation provenance, and claim level.](../../output/figures/metrics_dashboard.png){#fig:metrics_dashboard}

What this figure shows: Four artifact cards list image, audio, video, and audiovisual metrics with units, computation provenance, and claim level. The dashboard presents representative measurements from image, audio, video, and audiovisual canonical artifacts. Source data output/data/metrics_dashboard.json retains metric name, value, unit, computation version, tolerance, claim level, and canonical digest; image values are an uncalibrated grayscale/weighted-RGB proxy with explicit transfer/window definitions and definition hashes, amplitude is normalized, spectra are in hertz, frame differences are normalized pixel differences, and synchronization is in milliseconds. Controls: default canonical artifacts; metric computation version and tolerance recorded in the source-data sidecar; seed s=0. Objective facts: finite objective values with units: normalized luminance/amplitude, Hz, normalized pixel difference, ms, counts, and durations. Claim level: physical_metric. Source data: output/data/metrics_dashboard.json (SHA-256 digest recorded in the figure registry). Evidence lineage: formalism:eq:objective_statistics, formalism:eq:temporal_spectral_metrics. Limitations: Metrics are media properties and do not encode pitch, size, motion, localization, binding, or other observer interpretations. Boundary: Metric reproducibility is a package property; interpretation as perception requires a separate observer design and data.

The metrics dashboard [@fig:metrics_dashboard] reports units, computation
version, and canonical digests. Luminance statistics are normalized raster
properties; RMS and peak are normalized-amplitude properties; spectral values
are in Hz; frame deltas are normalized pixel differences; and synchronization
offsets are in milliseconds. None is a psychophysical score.

![Horizontal interval markers show typed domains for dimensions, luminance, levels, frequency, sampling, frame rate, synchronization, and spatial discrepancy.](../../output/figures/parameter_domains.png){#fig:parameter_domains}

What this figure shows: Horizontal interval markers show typed domains for dimensions, luminance, levels, frequency, sampling, frame rate, synchronization, and spatial discrepancy. The domain map shows the validated ranges for dimensions, luminance, grayscale and quantization levels, frequency, sampling rate, frame rate, synchronization offset, and spatial discrepancy. Source data output/data/parameter_domains.json records the type name, unit, interval, and engineering role; intervals prevent malformed media and are not proposed as sensitivity thresholds. Controls: parameter schema version and validated scalar domains; seed not applicable to the domain diagram. Objective facts: dimensionless, pixel, level, Hz, samples/s, frames/s, ms, and normalized spatial units as listed per parameter. Claim level: canonical_stimulus. Source data: output/data/parameter_domains.json (SHA-256 digest recorded in the figure registry). Evidence lineage: formalism:eq:typed_request. Limitations: The intervals are software validation bounds and do not encode safe listening levels, display limits, or psychophysical thresholds. Boundary: A valid parameter is a reproducible construction request, not evidence that the requested value is perceptually effective.

The domain map [@fig:parameter_domains] is a validation visualization. Bounds
are chosen to prevent malformed media and unsafe encodings, not to predict a
viewer, listener, or participant's sensitivity.

## Observer-design boundary {#observer-design-boundary}

![A flow diagram connects trial identity, randomization, stimulus manifest, response, aggregate estimand, and analysis-model templates, with a synthetic-only boundary.](../../output/figures/observer_protocol.png){#fig:observer_protocol}

What this figure shows: A flow diagram connects trial identity, randomization, stimulus manifest, response, aggregate estimand, and analysis-model templates, with a synthetic-only boundary. The data-free protocol template moves from pseudonymous trial identity and deterministic randomization to a stimulus manifest and encoded-file hash, typed response or missingness, and a preregistered estimand. Source data output/data/observer_protocol.json records the study design, randomization seed, model templates, and synthetic-only status; no participant record is included. Controls: study design and deterministic randomization seed recorded in the sidecar; synthetic response generation is separate from human data. Objective facts: trial counts, condition structure, estimand templates, response schemas, and model families; participant outcomes are not applicable. Claim level: observer_hypothesis. Source data: output/data/observer_protocol.json (SHA-256 digest recorded in the figure registry). Evidence lineage: observer:preregistered_estimands. Limitations: The scaffold specifies future data collection and analysis but supplies no participant responses, fitted coefficients, power claim, or validated observer effect. Boundary: The protocol requires ethical review, task and calibration specifications, and preregistration before human use, not evidence that the proposed effect exists.

The observer scaffold [@fig:observer_protocol] starts with a pseudonymous trial
identity and deterministic randomization, binds the stimulus manifest and
encoded hash, records a typed response or missingness state, and ends at a
preregistered estimand. The companion diagnostic
[@fig:synthetic_psychophysics] is a deterministic, hand-specified feature
observer with `training_data=none` and `human_data=false`; it is not a
pretrained vision model, psychometric function, or participant result. Human
psychophysics remains a future evidence layer requiring calibrated playback,
consent, preregistration, and observed responses.

## Generated audit tables {#generated-audit-tables}

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {#tbl:caption_audit data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1"}
::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-caption-long"}
Code-owned caption, source-data, and accessibility audit.
:::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-header-1"}
## Table 1 — header row 1 {#dr-slide-07_publication_audit-table-1-header-1-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-header-1-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-header-1-column-1"}
Figure / claim level
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-header-1-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-header-1-column-2"}
Source and evidence
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-header-1-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-header-1-column-3"}
Controls and objective facts
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-header-1-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-header-1-column-4"}
Limitations, boundary, and accessibility
:::
:::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-body-1"}
::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-1"}
## Table 1 — row 1 {#dr-slide-07_publication_audit-table-1-data-1-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-1-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-1-column-1"}
fig:architecture; canonical_stimulus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-1-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-1-column-2"}
output/data/architecture.json; formalism:eq:typed_request, formalism:eq:canonical_generation, formalism:eq:encoding_verification
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-1-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-1-column-3"}
Controls: typed request q=(i,θ,s,e) with seed s=0; default generator and delivery-independent canonicalization Objective: no unit-bearing objective quantity is applicable to this architecture diagram; stage identities and provenance fields are recorded in the sidecar
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-1-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-1-column-4"}
Limitations: The schematic abstracts implementation boundaries and does not represent an observer study or a causal theory of perception. Boundary: The pipeline verifies reproducible media facts, not what a person experiences. Accessibility: Stage names, mathematical symbols, and arrow direction are printed directly; color is redundant.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-2"}
## Table 1 — row 2 {#dr-slide-07_publication_audit-table-1-data-2-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-2-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-2-column-1"}
fig:catalog_matrix; source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-2-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-2-column-2"}
output/data/catalog_matrix.json; gregory1997visual, hirst2020sound, bruns2019ventriloquist
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-2-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-2-column-3"}
Controls: live taxonomy registry; evidence matrix snapshot; seed not applicable to the catalog diagram Objective: 18 catalog rows; categorical facets and statuses; no observer-level quantity is applicable
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-2-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-2-column-4"}
Limitations: Taxonomy facets are engineering classifications and remain provisional where the literature supports competing accounts. Boundary: Catalog coverage is bounded to this registered package and does not enumerate all known illusions. Accessibility: Every status and facet is written as text; color only reinforces the printed status.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-3"}
## Table 1 — row 3 {#dr-slide-07_publication_audit-table-1-data-3-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-3-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-3-column-1"}
fig:visual_panel; canonical_stimulus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-3-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-3-column-2"}
output/data/visual_panel.json; gregory1997visual, brugger1999duckrabbit, howe2005muller, morgan1999poggendorff, fisher1967ponzo, yildiz2022ponzo, kanizsa1976contours, mruczek2015ebbinghaus, earle1995zollner, wertheimer1912motion, sekuler1996wertheimer
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-3-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-3-column-3"}
Controls: one default typed parameter object per implemented visual entry; seed s=0; dimensions, luminance bounds, grayscale, and quantization controls remain in each generator schema; temporal entries display their first frame but retain sequence metrics Objective: per tile: mean and standard deviation of the declared uncalibrated channel-value proxy, unique raster levels, and canonical SHA-256 digest; temporal entries additionally retain frame count, frame rate, and frame deltas; definitions and units are in the source data JSON
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-3-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-3-column-4"}
Limitations: The gallery is complete for implemented visual entries in this package, not a complete survey of visual illusions; literature families, historical displays, and DuckRabbit rasters are not pixel-identical by default. Viewing scale, display calibration, viewing distance, and observer conditions can change the relevance of a construction; the gallery does not measure an observer's perceptual report. Boundary: The figure establishes coverage of the package's implemented visual constructions and their deterministic raster facts. It does not establish that any viewer will perceive the named signature, nor that the set is exhaustive of the visual-illusion literature. Accessibility: Each tile is labeled by stable illusion ID and accompanied by printed luminance, level-count, and digest fields; color only reinforces grouping and is not required to identify a stimulus.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-4"}
## Table 1 — row 4 {#dr-slide-07_publication_audit-table-1-data-4-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-4-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-4-column-1"}
fig:visual_sweep; physical_metric
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-4-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-4-column-2"}
output/data/visual_sweep.json; brugger1999duckrabbit, gregory1997visual
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-4-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-4-column-3"}
Controls: duck_weight ∈ {0,.25,.5,.75,1}; grayscale=quantization ∈ {2,4,8,16,32}; seed s=0 Objective: 25 canonical rasters; unique levels, normalized mean luminance, and effective dynamic range per cell
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-4-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-4-column-4"}
Limitations: The grid is a sensitivity of the construction parameters, not a psychophysical sensitivity curve or a validated observer effect. Boundary: The chosen grid is an engineering sampling of the parameter domain and does not imply an optimal or perceptually uniform spacing. Accessibility: Row and column labels state the parameter values; numerical metrics and units are available in the sidecar.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-5"}
## Table 1 — row 5 {#dr-slide-07_publication_audit-table-1-data-5-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-5-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-5-column-1"}
fig:temporal_sequence; physical_metric
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-5-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-5-column-2"}
output/data/temporal_sequence.json; wertheimer1912motion, sekuler1996wertheimer
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-5-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-5-column-3"}
Controls: visual.apparent_motion default typed parameters; frame rate and frame count from the canonical sequence; seed s=0 Objective: timestamps in seconds, frame rate in frames/s, frame count, rational timebase, and adjacent-frame normalized pixel difference
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-5-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-5-column-4"}
Limitations: Frame succession and frame deltas are physical file properties; playback timing, display persistence, and motion reports require a controlled observer task. Boundary: The figure documents temporal structure rather than the presence, direction, or strength of perceived motion. Accessibility: Frame index, seconds, frames per second, and normalized-difference labels remain interpretable without color.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-6"}
## Table 1 — row 6 {#dr-slide-07_publication_audit-table-1-data-6-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-6-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-6-column-1"}
fig:audio_signals; physical_metric
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-6-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-6-column-2"}
output/data/audio_signals.json; shepard1984scale, zatorre2005missing, deutsch1986tritone, repp1997tritone, deutsch1974octave, warren1970continuity, riecke2011continuity
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-6-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-6-column-3"}
Controls: default typed audio parameters; per-generator channel layout and sample rate; seed s=0; one-sided FFT display with 48 frequency-labelled peak-magnitude bands Objective: RMS and peak in normalized amplitude; spectral centroid and bandwidth in Hz; sample rate in samples/s; channel layout and canonical SHA-256 digest
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-6-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-6-column-4"}
Limitations: Playback level, transducer response, dichotic separation, masker design, and listener judgments are external to the canonical buffer. Boundary: The figure compares generated signal properties and literature-linked families; it does not establish pitch, continuity, or stream organization for a listener. Accessibility: Waveform, spectral, amplitude, and frequency labels are printed; bar color is not the sole encoding.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-7"}
## Table 1 — row 7 {#dr-slide-07_publication_audit-table-1-data-7-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-7-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-7-column-1"}
fig:audiovisual_timeline; physical_metric
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-7-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-7-column-2"}
output/data/audiovisual_timeline.json; shams2000sifi, hirst2020sound, vroomen2004temporal, hartcherobrien2011temporal
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-7-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-7-column-3"}
Controls: audiovisual.sound_induced_flash default shared timeline; declared sync offset ΔAV and spatial offset; seed s=0 Objective: video frame-hold grayscale/weighted-RGB proxy and mean-channel absolute audio amplitude on shared time in seconds; ΔAV in ms; spatial discrepancy in normalized units; frame and sample clocks in the sidecar
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-7-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-7-column-4"}
Limitations: Display refresh, audio hardware, event latency, and observer temporal binding are not measured by this figure. Boundary: A shared-clock construction is not evidence that observers bind the events at the declared or any other perceptual time. Accessibility: The two channels, time axis, signed offset convention, and normalized spatial discrepancy are labeled in text.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-8"}
## Table 1 — row 8 {#dr-slide-07_publication_audit-table-1-data-8-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-8-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-8-column-1"}
fig:encoding_verification; encoded_media
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-8-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-8-column-2"}
output/data/encoding_verification.json; engineering:typed_media_adapters
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-8-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-8-column-3"}
Controls: typed encoding profile selected per artifact; overwrite and backend capability checks; seed inherited from the stimulus request Objective: format availability and verification scope are environment observations; NPZ is exact while other formats are decoded and tolerance-checked
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-8-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-8-column-4"}
Limitations: Backend availability, codec versions, container metadata, and lossy tolerances are environment-dependent; playback software can expose additional behavior. Boundary: A successful encode or decode does not validate an observer effect or guarantee cross-device perceptual equivalence. Accessibility: Format, backend, preserved fact, and verification columns are textual and remain usable without color.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-9"}
## Table 1 — row 9 {#dr-slide-07_publication_audit-table-1-data-9-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-9-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-9-column-1"}
fig:synthetic_psychophysics; synthetic_model_output
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-9-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-9-column-2"}
output/data/synthetic_psychophysics.json; observer:preregistered_estimands
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-9-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-9-column-3"}
Controls: duck_weight comparison against fixed reference; serialized feature weights and temperature; seed s=0 Objective: model probability, null baseline, ablations, temperature sensitivity and exact-self control; full feature values, specifications and canonical stimulus digests; human_data=false; training_data=none
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-9-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-9-column-4"}
Limitations: The model is hand-specified, has no training data, has not been calibrated against observers, and does not estimate a human threshold or effect size. Its probabilities and the finite configuration range are model outputs, not participant responses, confidence intervals, or a psychometric function. Boundary: This diagnostic tests deterministic orchestration and metamorphic input-output behavior only; empirical psychophysics remains future work. Accessibility: Model scale, reference line, model identity, and `human\_data=false` are printed; color is not needed to interpret the curve.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-10"}
## Table 1 — row 10 {#dr-slide-07_publication_audit-table-1-data-10-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-10-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-10-column-1"}
fig:claim_boundary; source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-10-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-10-column-2"}
output/data/claim_boundary.json; formalism:eq:observer_estimand, formalism:eq:canonical_digest
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-10-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-10-column-3"}
Controls: claim levels in the taxonomy and manifest; seed not applicable to the explanatory diagram Objective: no unit-bearing objective quantity is applicable; stage definitions and evidence boundaries are preserved in the sidecar
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-10-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-10-column-4"}
Limitations: The diagram is a documentation contract and does not replace a preregistered observer study or empirical data. Boundary: A deterministic artifact can support a future hypothesis but cannot supply the observer data required to test it. Accessibility: Each stage is named, numbered, and described in text; the boundary rule is readable without color.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-11"}
## Table 1 — row 11 {#dr-slide-07_publication_audit-table-1-data-11-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-11-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-11-column-1"}
fig:scholarship_map; source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-11-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-11-column-2"}
output/data/scholarship_map.json; gregory1997visual, brugger1999duckrabbit, yildiz2022ponzo, hirst2020sound, bruns2019ventriloquist
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-11-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-11-column-3"}
Controls: checked-in evidence matrix; source roles and entry statuses; audit date recorded in data/evidence_matrix.json Objective: one evidence row per catalog entry (18 entries); source-tier counts, exact claim text, engineering basis, limitation, and gap status
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-11-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-11-column-4"}
Limitations: The offline snapshot validates citation and lineage structure; live resolver status is a separate audit, and classifications can remain contested. Boundary: Scholarship coverage bounds the package’s evidence record and does not establish that any generated stimulus produces a universal percept. Accessibility: Source roles, claims, limitations, and statuses are printed or available in the sidecar; no category is encoded by color alone.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-12"}
## Table 1 — row 12 {#dr-slide-07_publication_audit-table-1-data-12-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-12-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-12-column-1"}
fig:formalism_traceability; physical_metric
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-12-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-12-column-2"}
output/data/formalism_traceability.json; formalism:eq:canonical_digest, formalism:eq:clock_definition, formalism:eq:objective_statistics
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-12-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-12-column-3"}
Controls: formalism registry version; seed not applicable to the traceability diagram Objective: nine equation records with implementation, test, figure, and claim-level fields; no unit-bearing measurement is plotted
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-12-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-12-column-4"}
Limitations: Traceability records documentation and verification scope; it does not establish the truth of an observer-level theory. Boundary: A linked equation and test can show an implemented contract, not a validated perceptual law. Accessibility: Equation labels, code paths, tests, and figure labels are written as text.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-13"}
## Table 1 — row 13 {#dr-slide-07_publication_audit-table-1-data-13-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-13-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-13-column-1"}
fig:metrics_dashboard; physical_metric
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-13-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-13-column-2"}
output/data/metrics_dashboard.json; formalism:eq:objective_statistics, formalism:eq:temporal_spectral_metrics
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-13-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-13-column-3"}
Controls: default canonical artifacts; metric computation version and tolerance recorded in the source-data sidecar; seed s=0 Objective: finite objective values with units: normalized luminance/amplitude, Hz, normalized pixel difference, ms, counts, and durations
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-13-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-13-column-4"}
Limitations: Metrics are media properties and do not encode pitch, size, motion, localization, binding, or other observer interpretations. Boundary: Metric reproducibility is a package property; interpretation as perception requires a separate observer design and data. Accessibility: Every numerical value is paired with a printed unit or an explicit dimensionless definition.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-14"}
## Table 1 — row 14 {#dr-slide-07_publication_audit-table-1-data-14-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-14-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-14-column-1"}
fig:parameter_domains; canonical_stimulus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-14-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-14-column-2"}
output/data/parameter_domains.json; formalism:eq:typed_request
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-14-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-14-column-3"}
Controls: parameter schema version and validated scalar domains; seed not applicable to the domain diagram Objective: dimensionless, pixel, level, Hz, samples/s, frames/s, ms, and normalized spatial units as listed per parameter
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-14-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-14-column-4"}
Limitations: The intervals are software validation bounds and do not encode safe listening levels, display limits, or psychophysical thresholds. Boundary: A valid parameter is a reproducible construction request, not evidence that the requested value is perceptually effective. Accessibility: Type names, endpoints, units, and roles are printed; interval color is redundant.
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-15"}
## Table 1 — row 15 {#dr-slide-07_publication_audit-table-1-data-15-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-15-column-1-label"}
Column 1 — header:

Figure / claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-15-column-1"}
fig:observer_protocol; observer_hypothesis
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-15-column-2-label"}
Column 2 — header:

Source and evidence

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-15-column-2"}
output/data/observer_protocol.json; observer:preregistered_estimands
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-15-column-3-label"}
Column 3 — header:

Controls and objective facts

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-15-column-3"}
Controls: study design and deterministic randomization seed recorded in the sidecar; synthetic response generation is separate from human data Objective: trial counts, condition structure, estimand templates, response schemas, and model families; participant outcomes are not applicable
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-15-column-4-label"}
Column 4 — header:

Limitations, boundary, and accessibility

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-1-data-15-column-4"}
Limitations: The scaffold specifies future data collection and analysis but supplies no participant responses, fitted coefficients, power claim, or validated observer effect. Boundary: The protocol requires ethical review, task and calibration specifications, and preregistration before human use, not evidence that the proposed effect exists. Accessibility: Every protocol step and the no-participant-data boundary is stated in text; arrows and labels remain legible without color.
:::
:::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {#tbl:evidence_audit data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2"}
::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-caption-long"}
Source-tiered evidence, DOI/URL verification, exact supported claims, engineering departures, limitations, and explicit planned/input-required gaps.
:::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1"}
## Table 2 — header row 1 {#dr-slide-07_publication_audit-table-2-header-1-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1-column-1"}
Key
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1-column-2"}
Record and citations
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1-column-3"}
DOI and URL
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1-column-4"}
Verification
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-header-1-column-5"}
Supported claim / engineering / limitation
:::
:::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-body-1"}
::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1"}
## Table 2 — row 1 {#dr-slide-07_publication_audit-table-2-data-1-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1-column-1"}
gregory1997visual
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1-column-2"}
review; gregory1997visual
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1-column-3"}
DOI: 10.1016/S1364-6613(97)01060-7; URL: <https://pubmed.ncbi.nlm.nih.gov/21223901/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-1-column-5"}
A non-exhaustive classification of visual illusion families.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2"}
## Table 2 — row 2 {#dr-slide-07_publication_audit-table-2-data-2-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2-column-1"}
hirst2020sound
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2-column-2"}
review; hirst2020sound
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2-column-3"}
DOI: 10.1016/j.neubiorev.2020.09.006; URL: <https://www.sciencedirect.com/science/article/pii/S0149763420305637>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-2-column-5"}
A review of sound-induced flash paradigms and multisensory temporal inference.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3"}
## Table 2 — row 3 {#dr-slide-07_publication_audit-table-2-data-3-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3-column-1"}
howe2005muller
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3-column-2"}
theory; howe2005muller
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3-column-3"}
DOI: 10.1073/pnas.0409314102; URL: <https://doi.org/10.1073/pnas.0409314102>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-3-column-5"}
A statistical image-source account of Müller-Lyer geometry.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4"}
## Table 2 — row 4 {#dr-slide-07_publication_audit-table-2-data-4-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4-column-1"}
morgan1999poggendorff
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4-column-2"}
theory; morgan1999poggendorff
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4-column-3"}
DOI: 10.1016/S0042-6989(98)00243-0; URL: <https://doi.org/10.1016/S0042-6989(98)00243-0>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-4-column-5"}
A mechanistic account of Poggendorff orientation estimation.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5"}
## Table 2 — row 5 {#dr-slide-07_publication_audit-table-2-data-5-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5-column-1"}
fisher1967ponzo
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5-column-2"}
primary; fisher1967ponzo
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5-column-3"}
DOI: 10.1038/215553a0; URL: <https://www.nature.com/articles/215553a0>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-5-column-5"}
A primary investigation of identical targets embedded in an angular context.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6"}
## Table 2 — row 6 {#dr-slide-07_publication_audit-table-2-data-6-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6-column-1"}
kanizsa1976contours
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6-column-2"}
primary; kanizsa1976contours
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6-column-3"}
DOI: 10.1038/scientificamerican0476-48; URL: <https://pubmed.ncbi.nlm.nih.gov/1257734/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-6-column-5"}
Canonical illusory-contour inducer arrangements.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7"}
## Table 2 — row 7 {#dr-slide-07_publication_audit-table-2-data-7-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7-column-1"}
mruczek2015ebbinghaus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7-column-2"}
primary; mruczek2015ebbinghaus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7-column-3"}
DOI: 10.3389/fnhum.2015.00077; URL: <https://pmc.ncbi.nlm.nih.gov/articles/PMC4332331/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-7-column-5"}
Context-dependent size judgments in Ebbinghaus-family stimuli.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8"}
## Table 2 — row 8 {#dr-slide-07_publication_audit-table-2-data-8-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8-column-1"}
wertheimer1912motion
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8-column-2"}
primary; wertheimer1912motion
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8-column-3"}
DOI: not_recorded; URL: <https://bibbase.org/network/publication/wertheimer-experimentellestudienberdassehenvonbewegung-1912>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-8-column-5"}
Foundational apparent-motion experiments using successive spatial events.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9"}
## Table 2 — row 9 {#dr-slide-07_publication_audit-table-2-data-9-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9-column-1"}
sekuler1996wertheimer
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9-column-2"}
review; sekuler1996wertheimer
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9-column-3"}
DOI: 10.1068/p251243; URL: <https://journals.sagepub.com/doi/10.1068/p251243>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-9-column-5"}
A review connecting Wertheimer's successive-event findings to later apparent-motion research and clarifying their historical scope.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10"}
## Table 2 — row 10 {#dr-slide-07_publication_audit-table-2-data-10-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10-column-1"}
shepard1984scale
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10-column-2"}
primary; shepard1984scale
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10-column-3"}
DOI: 10.1126/science.226.4680.1333; URL: <https://doi.org/10.1126/science.226.4680.1333>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-10-column-5"}
Auditory scale and pitch-class organization in Shepard-like tones.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11"}
## Table 2 — row 11 {#dr-slide-07_publication_audit-table-2-data-11-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11-column-1"}
zatorre2005missing
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11-column-2"}
review; zatorre2005missing
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11-column-3"}
DOI: 10.1038/4361093a; URL: <https://doi.org/10.1038/4361093a>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-11-column-5"}
The missing-fundamental problem as a pitch-inference phenomenon.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12"}
## Table 2 — row 12 {#dr-slide-07_publication_audit-table-2-data-12-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12-column-1"}
deutsch1986tritone
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12-column-2"}
primary; deutsch1986tritone
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12-column-3"}
DOI: 10.2307/40285337; URL: <https://online.ucpress.edu/mp/article-abstract/3/3/275/62718/A-Musical-Paradox>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-12-column-5"}
The tritone paradox and dependence on pitch-class context and listener.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13"}
## Table 2 — row 13 {#dr-slide-07_publication_audit-table-2-data-13-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13-column-1"}
deutsch1974octave
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13-column-2"}
primary; deutsch1974octave
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13-column-3"}
DOI: 10.1121/1.1919587; URL: <https://doi.org/10.1121/1.1919587>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-13-column-5"}
Dichotic alternating high/low tone construction underlying the octave illusion.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14"}
## Table 2 — row 14 {#dr-slide-07_publication_audit-table-2-data-14-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14-column-1"}
shams2000sifi
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14-column-2"}
primary; shams2000sifi
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14-column-3"}
DOI: 10.1038/35048669; URL: <https://doi.org/10.1038/35048669>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-14-column-5"}
The one-flash/two-beep sound-induced flash contrast.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15"}
## Table 2 — row 15 {#dr-slide-07_publication_audit-table-2-data-15-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15-column-1"}
bruns2019ventriloquist
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15-column-2"}
review; bruns2019ventriloquist
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15-column-3"}
DOI: 10.3389/fnint.2019.00051; URL: <https://pmc.ncbi.nlm.nih.gov/articles/PMC6751356/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-15-column-5"}
Spatial audiovisual capture and multisensory integration constraints.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16"}
## Table 2 — row 16 {#dr-slide-07_publication_audit-table-2-data-16-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16-column-1"}
vroomen2004temporal
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16-column-2"}
primary; vroomen2004temporal
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16-column-3"}
DOI: 10.1037/0096-1523.30.3.513; URL: <https://pubmed.ncbi.nlm.nih.gov/15161383/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-16-column-5"}
Sound timing can alter the apparent temporal structure of a visual event.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17"}
## Table 2 — row 17 {#dr-slide-07_publication_audit-table-2-data-17-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17-column-1"}
mcgurk1976speech
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17-column-2"}
primary; mcgurk1976speech
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17-column-3"}
DOI: 10.1038/264746a0; URL: <https://doi.org/10.1038/264746a0>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-17-column-5"}
Speech-dependent audiovisual categorical integration, requiring validated fixtures.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18"}
## Table 2 — row 18 {#dr-slide-07_publication_audit-table-2-data-18-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18-column-1"}
warren1970continuity
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18-column-2"}
primary; warren1970continuity
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18-column-3"}
DOI: 10.1126/science.167.3917.392; URL: <https://doi.org/10.1126/science.167.3917.392>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-18-column-5"}
Auditory continuity/restoration as a future calibrated masker family.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19"}
## Table 2 — row 19 {#dr-slide-07_publication_audit-table-2-data-19-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19-column-1"}
brugger1999duckrabbit
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19-column-2"}
primary; brugger1999duckrabbit
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19-column-3"}
DOI: 10.2466/pms.1999.89.3.973; URL: <https://pubmed.ncbi.nlm.nih.gov/10665033/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-19-column-5"}
Variation in duck/rabbit ambiguity across figure variants and observers.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20"}
## Table 2 — row 20 {#dr-slide-07_publication_audit-table-2-data-20-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20-column-1"}
yildiz2022ponzo
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20-column-2"}
review; yildiz2022ponzo
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20-column-3"}
DOI: 10.3758/s13423-021-02007-7; URL: <https://pubmed.ncbi.nlm.nih.gov/34613601/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-20-column-5"}
Competing depth-based and non-depth-based explanations of Ponzo-like illusions.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21"}
## Table 2 — row 21 {#dr-slide-07_publication_audit-table-2-data-21-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21-column-1"}
repp1997tritone
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21-column-2"}
primary; repp1997tritone
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21-column-3"}
DOI: 10.1068/p260645; URL: <https://pubmed.ncbi.nlm.nih.gov/9488887/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-21-column-5"}
Listener- and context-dependent effects of spectral envelope and pitch-class structure in tritone judgments.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22"}
## Table 2 — row 22 {#dr-slide-07_publication_audit-table-2-data-22-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22-column-1"}
hartcherobrien2011temporal
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22-column-2"}
primary; hartcherobrien2011temporal
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22-column-3"}
DOI: 10.1037/a0024234; URL: <https://pubmed.ncbi.nlm.nih.gov/21728465/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-22-column-5"}
Audiovisual timing can shift temporal judgments in a purely temporal context without spatial grounding.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23"}
## Table 2 — row 23 {#dr-slide-07_publication_audit-table-2-data-23-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23-column-1"}
earle1995zollner
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23-column-2"}
primary; earle1995zollner
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23-column-3"}
DOI: 10.1068/p241397; URL: <https://journals.sagepub.com/doi/10.1068/p241397>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-23-column-5"}
Crossing oblique and long-line geometry used to measure orientation interactions in the Zöllner family.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24"}
## Table 2 — row 24 {#dr-slide-07_publication_audit-table-2-data-24-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24-column-1"}
zoellner1860pseudoscopy
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24-column-2"}
primary; zoellner1860pseudoscopy
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24-column-3"}
DOI: 10.1002/andp.18601860712; URL: <https://onlinelibrary.wiley.com/doi/10.1002/andp.18601860712>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-24-column-5"}
The nineteenth-century primary description of the crossing-line orientation family later known as the Zöllner illusion.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25"}
## Table 2 — row 25 {#dr-slide-07_publication_audit-table-2-data-25-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25-column-1"}
riecke2011continuity
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25-column-2"}
primary; riecke2011continuity
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25-column-3"}
DOI: 10.1016/j.heares.2011.01.013; URL: <https://doi.org/10.1016/j.heares.2011.01.013>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-25-column-5"}
Interrupted sounds with masking context and the separation of sensory and decisional contributions.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26"}
## Table 2 — row 26 {#dr-slide-07_publication_audit-table-2-data-26-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26-column-1"}
wagemans2012gestalt
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26-column-2"}
review; wagemans2012gestalt
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26-column-3"}
DOI: 10.1037/a0029333; URL: <https://pubmed.ncbi.nlm.nih.gov/22845751/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-26-column-5"}
Contemporary perceptual-grouping, contour-completion, and figure-ground accounts relevant to Kanizsa-type constructions.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27"}
## Table 2 — row 27 {#dr-slide-07_publication_audit-table-2-data-27-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27-column-1"}
weintraub1979ebbinghaus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27-column-2"}
primary; weintraub1979ebbinghaus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27-column-3"}
DOI: 10.1037/0096-1523.5.2.353; URL: <https://pubmed.ncbi.nlm.nih.gov/528945/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-27-column-5"}
A classic contextual-size experiment varying surround geometry and comparison conditions in Ebbinghaus-family displays.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28"}
## Table 2 — row 28 {#dr-slide-07_publication_audit-table-2-data-28-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28-column-1"}
noppeney2018causal
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28-column-2"}
review; noppeney2018causal
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28-column-3"}
DOI: 10.1111/nyas.13615; URL: <https://doi.org/10.1111/nyas.13615>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-28-column-5"}
Causal-inference and temporal-prediction accounts of audiovisual integration and segregation.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29"}
## Table 2 — row 29 {#dr-slide-07_publication_audit-table-2-data-29-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29-column-1"}
alhazen1989optics
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29-column-2"}
primary; alhazen1989optics
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29-column-3"}
DOI: not_recorded; URL: <https://www.cca.qc.ca/en/search/details/library/publication/21530166>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-29-column-5"}
The English translation and commentary preserves Ibn al-Haytham's eleventh-century Arabic optics as a historical source on direct vision and geometrical image formation.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30"}
## Table 2 — row 30 {#dr-slide-07_publication_audit-table-2-data-30-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30-column-1"}
mozi2023canons
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30-column-2"}
review; mozi2023canons
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30-column-3"}
DOI: 10.1007/978-3-031-08797-4_3; URL: <https://link.springer.com/chapter/10.1007/978-3-031-08797-4_3>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-30-column-5"}
A modern translation and commentary documents Mohist Canon sections on knowledge, optics, and mechanics, providing a Chinese Warring States-period context for early technical reasoning about vision.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31"}
## Table 2 — row 31 {#dr-slide-07_publication_audit-table-2-data-31-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31-column-1"}
ptolemy1996optics
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31-column-2"}
primary; ptolemy1996optics
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31-column-3"}
DOI: not_recorded; URL: <https://sites.dlib.nyu.edu/viewer/books/isaw_aphs000027>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-31-column-5"}
The scholarly translation makes Ptolemy's second-century Optics available as an early work on visual perception and mathematical visual theory.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32"}
## Table 2 — row 32 {#dr-slide-07_publication_audit-table-2-data-32-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32-column-1"}
berkeley1709vision
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32-column-2"}
primary; berkeley1709vision
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32-column-3"}
DOI: not_recorded; URL: <https://www.maths.tcd.ie/~dwilkins/Berkeley/Vision/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-32-column-5"}
Berkeley's 1709 essay treats visual distance and space as mediated by learned associations rather than as a simple direct readout of visual geometry.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33"}
## Table 2 — row 33 {#dr-slide-07_publication_audit-table-2-data-33-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33-column-1"}
kircher1646light
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33-column-2"}
primary; kircher1646light
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33-column-3"}
DOI: not_recorded; URL: <https://collections.st-andrews.ac.uk/item/ars-magna-lucis-et-umbrae/606862>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-33-column-5"}
The digitized record anchors Kircher's 1646 Ars magna lucis et umbrae as an early-modern work on light, shadow, and optical display.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34"}
## Table 2 — row 34 {#dr-slide-07_publication_audit-table-2-data-34-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34-column-1"}
molyneux2020problem
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34-column-2"}
review; molyneux2020problem
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34-column-3"}
DOI: not_recorded; URL: <https://plato.stanford.edu/archives/fall2020/entries/molyneux-problem/>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-34-column-5"}
The historical account documents Molyneux's 1688 question separating tactile learning from visual recognition and its long cross-sensory afterlife.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35"}
## Table 2 — row 35 {#dr-slide-07_publication_audit-table-2-data-35-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35-column-1"}
cheselden1728sight
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35-column-2"}
primary; cheselden1728sight
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35-column-3"}
DOI: not_recorded; URL: <https://archive.org/details/jstor-103697>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-35-column-5"}
The digitized Philosophical Transactions record preserves Cheselden's 1728 case report as a historical observation relevant to visual access and the separation of observer evidence from stimulus description.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36"}
## Table 2 — row 36 {#dr-slide-07_publication_audit-table-2-data-36-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36-column-1"}
dai2015chinesescience
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36-column-2"}
review; dai2015chinesescience
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36-column-3"}
DOI: 10.1007/978-3-662-44257-9_5; URL: <https://link.springer.com/chapter/10.1007/978-3-662-44257-9_5>
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-36-column-5"}
A history of Chinese science and technology surveys ancient Chinese physics and records optical phenomena as part of a non-European history of visual science.
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37"}
## Table 2 — row 37 {#dr-slide-07_publication_audit-table-2-data-37-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37-column-1"}
entry:visual.duck_rabbit
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37-column-2"}
engineering+limitation+gap; brugger1999duckrabbit, gregory1997visual
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-37-column-5"}
The entry instantiates a controllable ambiguous-figure stimulus family. Engineering basis: Parameterized ambiguous silhouette; not a pixel-identical reproduction of a historical plate. Limitation: The generator verifies geometry and luminance, not bistable reports. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38"}
## Table 2 — row 38 {#dr-slide-07_publication_audit-table-2-data-38-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38-column-1"}
entry:visual.simultaneous_contrast
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38-column-2"}
engineering+limitation+gap; gregory1997visual
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-38-column-5"}
The physical center patches are matched while surround luminance differs. Engineering basis: Equal central patches on unequal luminance surrounds. Limitation: Display calibration and observer adaptation are not modeled. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39"}
## Table 2 — row 39 {#dr-slide-07_publication_audit-table-2-data-39-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39-column-1"}
entry:visual.apparent_motion
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39-column-2"}
engineering+limitation+gap; wertheimer1912motion, sekuler1996wertheimer
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-39-column-5"}
The sequence contains controlled successive spatial events. Engineering basis: Alternating rectangular masks at a fixed rational frame rate. Limitation: The artifact establishes temporal succession, not perceived motion. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40"}
## Table 2 — row 40 {#dr-slide-07_publication_audit-table-2-data-40-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40-column-1"}
entry:audio.shepard_tone
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40-column-2"}
engineering+limitation+gap; shepard1984scale
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-40-column-5"}
The audio contains octave-related partials with controlled sweep parameters. Engineering basis: Additive octave-spaced partials with a deterministic envelope. Limitation: Playback transducers and listener pitch judgments are external. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41"}
## Table 2 — row 41 {#dr-slide-07_publication_audit-table-2-data-41-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41-column-1"}
entry:audio.missing_fundamental
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41-column-2"}
engineering+limitation+gap; zatorre2005missing
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-41-column-5"}
The nominal fundamental component is absent from the canonical spectrum. Engineering basis: Harmonic components are synthesized while the nominal fundamental is omitted. Limitation: Pitch completion is an observer-level inference. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42"}
## Table 2 — row 42 {#dr-slide-07_publication_audit-table-2-data-42-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42-column-1"}
entry:audiovisual.sound_induced_flash
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42-column-2"}
engineering+limitation+gap; shams2000sifi, hirst2020sound
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-42-column-5"}
The declared beep/flash event counts and offsets are physically encoded. Engineering basis: One flash paired with one or two timed beeps on a shared clock. Limitation: The stimulus does not establish a reported flash count. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43"}
## Table 2 — row 43 {#dr-slide-07_publication_audit-table-2-data-43-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43-column-1"}
entry:audiovisual.ventriloquist
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43-column-2"}
engineering+limitation+gap; bruns2019ventriloquist, noppeney2018causal
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-43-column-5"}
The audio and visual channels carry a declared spatial discrepancy. Engineering basis: Stereo panning and visual displacement encode a spatial discrepancy. Limitation: Perceived localization depends on room, headphones, display, and observer. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44"}
## Table 2 — row 44 {#dr-slide-07_publication_audit-table-2-data-44-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44-column-1"}
entry:visual.muller_lyer
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44-column-2"}
engineering+limitation+gap; gregory1997visual, howe2005muller
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-44-column-5"}
The two bar lengths are equal in the canonical raster while wing geometry varies. Engineering basis: Equal bars with controlled arrow-wing geometry. Limitation: The chosen normalized geometry is one engineering variant. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45"}
## Table 2 — row 45 {#dr-slide-07_publication_audit-table-2-data-45-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45-column-1"}
entry:visual.poggendorff
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45-column-2"}
engineering+limitation+gap; gregory1997visual, morgan1999poggendorff
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-45-column-5"}
The occluder and diagonal continuation are generated from explicit geometry. Engineering basis: A diagonal continuation is separated by a rectangular occluder. Limitation: Alignment judgments and orientation filters are not measured. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46"}
## Table 2 — row 46 {#dr-slide-07_publication_audit-table-2-data-46-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46-column-1"}
entry:visual.ponzo
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46-column-2"}
engineering+limitation+gap; fisher1967ponzo, yildiz2022ponzo
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-46-column-5"}
Target bars are physically equal and rails converge toward a vanishing region. Engineering basis: Equal target bars are placed inside converging rails. Limitation: Perspective interpretation is observer- and display-dependent. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47"}
## Table 2 — row 47 {#dr-slide-07_publication_audit-table-2-data-47-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47-column-1"}
entry:visual.kanizsa_triangle
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47-column-2"}
engineering+limitation+gap; kanizsa1976contours, wagemans2012gestalt
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-47-column-5"}
The image contains incomplete inducers with no explicitly drawn triangle edge. Engineering basis: Three incomplete circular inducers are rasterized around a triangular gap. Limitation: Illusory contour completion is not directly measured. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48"}
## Table 2 — row 48 {#dr-slide-07_publication_audit-table-2-data-48-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48-column-1"}
entry:visual.ebbinghaus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48-column-2"}
engineering+limitation+gap; mruczek2015ebbinghaus, weintraub1979ebbinghaus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-48-column-5"}
Central target geometry is held equal while contextual circle geometry differs. Engineering basis: Equal central targets are surrounded by different context-circle sizes. Limitation: Perceived size depends on viewing scale and context. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49"}
## Table 2 — row 49 {#dr-slide-07_publication_audit-table-2-data-49-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49-column-1"}
entry:visual.zollner
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49-column-2"}
engineering+limitation+gap; zoellner1860pseudoscopy, earle1995zollner, gregory1997visual
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-49-column-5"}
The entry instantiates a controlled crossing-line orientation stimulus family. Engineering basis: Vertical long lines crossed by short oblique inducers with explicit normalized spacing and angle. Limitation: The raster verifies line geometry, not orientation judgments or a pixel-identical historical reproduction. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50"}
## Table 2 — row 50 {#dr-slide-07_publication_audit-table-2-data-50-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50-column-1"}
entry:audio.tritone_paradox
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50-column-2"}
engineering+limitation+gap; deutsch1986tritone, repp1997tritone
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-50-column-5"}
The canonical pair has an explicit half-octave frequency relation. Engineering basis: Two octave-complex tones are separated by a half-octave interval. Limitation: Ascending/descending reports vary across listeners and contexts. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51"}
## Table 2 — row 51 {#dr-slide-07_publication_audit-table-2-data-51-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51-column-1"}
entry:audio.octave_illusion
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51-column-2"}
engineering+limitation+gap; deutsch1974octave
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-51-column-5"}
The two channels receive alternating octave-related tones. Engineering basis: Alternating high and low tones are assigned to opposite stereo channels. Limitation: The auditory percept depends on dichotic presentation and listener. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52"}
## Table 2 — row 52 {#dr-slide-07_publication_audit-table-2-data-52-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52-column-1"}
entry:audio.auditory_continuity
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52-column-2"}
engineering+limitation+gap; warren1970continuity, riecke2011continuity
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-52-column-5"}
The canonical audio contains a reproducible interruption interval and masker family. Engineering basis: An interrupted sinusoidal carrier is replaced during a declared gap by a deterministic tone or white-noise masker with typed amplitude. Limitation: The generator reports the physical interruption and masker, not a listener's continuity judgment or sensory-versus-decisional effect. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53"}
## Table 2 — row 53 {#dr-slide-07_publication_audit-table-2-data-53-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53-column-1"}
entry:audiovisual.temporal_ventriloquism
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53-column-2"}
engineering+limitation+gap; vroomen2004temporal, hartcherobrien2011temporal, hirst2020sound, noppeney2018causal
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-53-column-5"}
Audio and video event timing and declared offset are deterministic and inspectable. Engineering basis: A visual flash and audio click share a clock with explicit offset. Limitation: The generated single-event pair is a simplified engineering stimulus. Missing contract: none
:::
:::::::::::::

::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54"}
## Table 2 — row 54 {#dr-slide-07_publication_audit-table-2-data-54-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54-column-1-label"}
Column 1 — header:

Key

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54-column-1"}
entry:audiovisual.mcgurk
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54-column-2-label"}
Column 2 — header:

Record and citations

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54-column-2"}
engineering+limitation+gap; mcgurk1976speech
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54-column-3-label"}
Column 3 — header:

DOI and URL

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54-column-3"}
DOI: not_applicable; URL: data/evidence_matrix.json
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54-column-4-label"}
Column 4 — header:

Verification

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54-column-4"}
snapshot_validated; offline_snapshot
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54-column-5-label"}
Column 5 — header:

Supported claim / engineering / limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-2-data-54-column-5"}
The catalog identifies a speech-dependent audiovisual family without claiming implementation. Engineering basis: Requires validated speech audio/video fixtures and licensing records. Limitation: No fixture, consent record, or perceptual validation contract is bundled. Missing contract: A licensed or consented checksummed speech audio/video fixture, synchronization contract, and preregistered perceptual validation protocol are required.
:::
:::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {#tbl:formalism data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3"}
::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-caption-long"}
Formal equation-to-code traceability.
:::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-header-1"}
## Table 3 — header row 1 {#dr-slide-07_publication_audit-table-3-header-1-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-header-1-column-1-label"}
Column 1 — header:

Label

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-header-1-column-1"}
Label
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-header-1-column-2-label"}
Column 2 — header:

Definition and symbols

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-header-1-column-2"}
Definition and symbols
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-header-1-column-3-label"}
Column 3 — header:

Implementation and tests

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-header-1-column-3"}
Implementation and tests
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-header-1-column-4-label"}
Column 4 — header:

Figures and claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-header-1-column-4"}
Figures and claim level
:::
:::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-body-1"}
::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-1"}
## Table 3 — row 1 {#dr-slide-07_publication_audit-table-3-data-1-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-1-column-1-label"}
Column 1 — header:

Label

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-1-column-1"}
eq:typed_request
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-1-column-2-label"}
Column 2 — header:

Definition and symbols

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-1-column-2"}
q = (i, θ, s, e) Symbols: i, θ, s, e
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-1-column-3-label"}
Column 3 — header:

Implementation and tests

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-1-column-3"}
Code: registry.py, schema.py; Tests: test_generators.py
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-1-column-4-label"}
Column 4 — header:

Figures and claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-1-column-4"}
Figures: fig:architecture, fig:formalism_traceability; Level: canonical_stimulus
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-2"}
## Table 3 — row 2 {#dr-slide-07_publication_audit-table-3-data-2-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-2-column-1-label"}
Column 1 — header:

Label

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-2-column-1"}
eq:canonical_generation
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-2-column-2-label"}
Column 2 — header:

Definition and symbols

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-2-column-2"}
A = Gᵢ(θ; s) Symbols: A, Gᵢ, θ, s
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-2-column-3-label"}
Column 3 — header:

Implementation and tests

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-2-column-3"}
Code: registry.py, generators.py; Tests: test_generators.py, test_v03_contracts.py
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-2-column-4-label"}
Column 4 — header:

Figures and claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-2-column-4"}
Figures: fig:architecture, fig:visual_panel; Level: canonical_stimulus
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-3"}
## Table 3 — row 3 {#dr-slide-07_publication_audit-table-3-data-3-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-3-column-1-label"}
Column 1 — header:

Label

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-3-column-1"}
eq:canonical_digest
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-3-column-2-label"}
Column 2 — header:

Definition and symbols

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-3-column-2"}
c(A) = Serialize_LE,float32(A, shape, clock, units); h_c(A) = H(c(A)) Symbols: c(A), h_c, H
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-3-column-3-label"}
Column 3 — header:

Implementation and tests

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-3-column-3"}
Code: canonical.py, manifest.py; Tests: test_v03_contracts.py
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-3-column-4-label"}
Column 4 — header:

Figures and claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-3-column-4"}
Figures: fig:architecture, fig:encoding_verification; Level: physical_metric
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-4"}
## Table 3 — row 4 {#dr-slide-07_publication_audit-table-3-data-4-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-4-column-1-label"}
Column 1 — header:

Label

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-4-column-1"}
eq:encoding_verification
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-4-column-2-label"}
Column 2 — header:

Definition and symbols

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-4-column-2"}
F = Eₑ(A), I = D(F), V(F, M) in {verified, failed, unverified} Symbols: F, Eₑ, D, I, V, M
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-4-column-3-label"}
Column 3 — header:

Implementation and tests

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-4-column-3"}
Code: render.py, inspection.py, manifest.py; Tests: test_media_and_render.py, test_v03_contracts.py, test_final_integrity.py
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-4-column-4-label"}
Column 4 — header:

Figures and claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-4-column-4"}
Figures: fig:encoding_verification; Level: encoded_media
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-5"}
## Table 3 — row 5 {#dr-slide-07_publication_audit-table-3-data-5-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-5-column-1-label"}
Column 1 — header:

Label

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-5-column-1"}
eq:clock_definition
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-5-column-2-label"}
Column 2 — header:

Definition and symbols

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-5-column-2"}
N = round(f_s T), t_k = k/f_r, Δ_AV = t_audio − t_video Symbols: N, f_s, T, t_k, f_r, Δ_AV
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-5-column-3-label"}
Column 3 — header:

Implementation and tests

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-5-column-3"}
Code: parameters.py, artifacts.py; Tests: test_parameters.py, test_media_and_render.py
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-5-column-4-label"}
Column 4 — header:

Figures and claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-5-column-4"}
Figures: fig:temporal_sequence, fig:audiovisual_timeline; Level: physical_metric
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-6"}
## Table 3 — row 6 {#dr-slide-07_publication_audit-table-3-data-6-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-6-column-1-label"}
Column 1 — header:

Label

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-6-column-1"}
eq:objective_statistics
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-6-column-2-label"}
Column 2 — header:

Definition and symbols

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-6-column-2"}
μ_Y, σ_Y, RMS_X = M(A; units, tolerance, version) Symbols: μ_Y, σ_Y, RMS_X, M
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-6-column-3-label"}
Column 3 — header:

Implementation and tests

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-6-column-3"}
Code: metrics.py, publication.py; Tests: test_v04_scholarly.py
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-6-column-4-label"}
Column 4 — header:

Figures and claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-6-column-4"}
Figures: fig:metrics_dashboard, fig:audio_signals; Level: physical_metric
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-7"}
## Table 3 — row 7 {#dr-slide-07_publication_audit-table-3-data-7-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-7-column-1-label"}
Column 1 — header:

Label

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-7-column-1"}
eq:temporal_spectral_metrics
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-7-column-2-label"}
Column 2 — header:

Definition and symbols

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-7-column-2"}
D_k = mean given Y\_(k+1) − Y_k given ; centroid(X) = Σ fM_X(f)/max(ΣM_X(f), 1e-12); M_X = channel-mean given rFFT(X) given Symbols: D_k, M_X, f
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-7-column-3-label"}
Column 3 — header:

Implementation and tests

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-7-column-3"}
Code: metrics.py, artifacts.py; Tests: test_v04_scholarly.py
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-7-column-4-label"}
Column 4 — header:

Figures and claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-7-column-4"}
Figures: fig:temporal_sequence, fig:metrics_dashboard; Level: physical_metric
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-8"}
## Table 3 — row 8 {#dr-slide-07_publication_audit-table-3-data-8-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-8-column-1-label"}
Column 1 — header:

Label

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-8-column-1"}
eq:observer_estimand
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-8-column-2-label"}
Column 2 — header:

Definition and symbols

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-8-column-2"}
ψ = E\[Y conditional on condition and protocol\] Symbols: ψ, Y, condition, protocol
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-8-column-3-label"}
Column 3 — header:

Implementation and tests

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-8-column-3"}
Code: observer_analysis.py, observer.py; Tests: test_v04_scholarly.py
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-8-column-4-label"}
Column 4 — header:

Figures and claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-8-column-4"}
Figures: fig:synthetic_psychophysics, fig:observer_protocol; Level: observer_hypothesis
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-9"}
## Table 3 — row 9 {#dr-slide-07_publication_audit-table-3-data-9-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-9-column-1-label"}
Column 1 — header:

Label

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-9-column-1"}
eq:synthetic_observer
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-9-column-2-label"}
Column 2 — header:

Definition and symbols

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-9-column-2"}
p_M(c given A_r,A_c) = σ(clip((w·φ(A_c) − w·φ(A_r))/τ, −60, 60)) Symbols: p_M, c, A_r, A_c, w, φ, τ, clip
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-9-column-3-label"}
Column 3 — header:

Implementation and tests

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-9-column-3"}
Code: synthetic_psychophysics.py, metrics.py; Tests: test_synthetic_psychophysics.py
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-9-column-4-label"}
Column 4 — header:

Figures and claim level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-3-data-9-column-4"}
Figures: fig:synthetic_psychophysics; Level: synthetic_model_output
:::
:::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {#tbl:claim_ledger data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4"}
::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-caption-long"}
Claim ledger separating code-derived facts, scholarship, engineering departures, limitations, scope, and observer hypotheses.
:::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-header-1"}
## Table 4 — header row 1 {#dr-slide-07_publication_audit-table-4-header-1-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-header-1-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-header-1-column-1"}
Claim ID
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-header-1-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-header-1-column-2"}
Claim and level
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-header-1-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-header-1-column-3"}
Basis
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-header-1-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-header-1-column-4"}
Lineage and limitation
:::
:::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-body-1"}
::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-1"}
## Table 4 — row 1 {#dr-slide-07_publication_audit-table-4-data-1-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-1-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-1-column-1"}
catalog:count
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-1-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-1-column-2"}
The catalog contains 18 entries. Level: canonical_stimulus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-1-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-1-column-3"}
derived_from_code
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-1-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-1-column-4"}
Lineage: taxonomy_entries() Limitation: Catalog membership is not a completeness claim about all known illusions. Manuscript: docs/manuscript/09_appendix_catalog.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-2"}
## Table 4 — row 2 {#dr-slide-07_publication_audit-table-4-data-2-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-2-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-2-column-1"}
evidence:source_count
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-2-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-2-column-2"}
The checked-in evidence matrix contains 36 source records. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-2-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-2-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-2-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-2-column-4"}
Lineage: data/evidence_matrix.json::sources Limitation: The offline snapshot does not imply that every URL is currently reachable or that a source supports more than its exact record. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-3"}
## Table 4 — row 3 {#dr-slide-07_publication_audit-table-4-data-3-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-3-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-3-column-1"}
scope:no_participant_data
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-3-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-3-column-2"}
No participant data are bundled with the package. Level: observer_hypothesis
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-3-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-3-column-3"}
derived_from_code
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-3-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-3-column-4"}
Lineage: experiments/observer_protocol.md; output/data/synthetic_psychophysics.json Limitation: Future observer studies require preregistration, consent, calibrated presentation, and separate data governance. Manuscript: docs/manuscript/07_publication_audit.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-4"}
## Table 4 — row 4 {#dr-slide-07_publication_audit-table-4-data-4-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-4-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-4-column-1"}
synthetic:diagnostic_boundary
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-4-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-4-column-2"}
The synthetic observer is a deterministic model-output diagnostic, not human psychophysics. Level: synthetic_model_output
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-4-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-4-column-3"}
synthetic_model_output
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-4-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-4-column-4"}
Lineage: src/duckrabbit/synthetic_psychophysics.py; output/data/synthetic_psychophysics.json Limitation: The hand-specified model has no training data and has not been calibrated against observers. Manuscript: docs/manuscript/02_methodology.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-5"}
## Table 4 — row 5 {#dr-slide-07_publication_audit-table-4-data-5-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-5-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-5-column-1"}
cover:editorial_boundary
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-5-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-5-column-2"}
The cover is a publication illustration, not an experimental stimulus or observer result. Level: publication_illustration
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-5-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-5-column-3"}
publication_illustration
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-5-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-5-column-4"}
Lineage: output/reports/cover_visualization.json Limitation: The editorial asset is not part of the deterministic scientific stimulus registry. Manuscript: docs/manuscript/07_publication_audit.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-6"}
## Table 4 — row 6 {#dr-slide-07_publication_audit-table-4-data-6-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-6-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-6-column-1"}
evidence:visual.duck_rabbit
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-6-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-6-column-2"}
The entry instantiates a controllable ambiguous-figure stimulus family. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-6-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-6-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-6-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-6-column-4"}
Lineage: sources=brugger1999duckrabbit; gregory1997visual; data/evidence_matrix.json; engineering=Parameterized ambiguous silhouette; not a pixel-identical reproduction of a historical plate.; limitation=The generator verifies geometry and luminance, not bistable reports.; missing_contract=none Limitation: The generator verifies geometry and luminance, not bistable reports. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-7"}
## Table 4 — row 7 {#dr-slide-07_publication_audit-table-4-data-7-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-7-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-7-column-1"}
evidence:visual.simultaneous_contrast
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-7-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-7-column-2"}
The physical center patches are matched while surround luminance differs. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-7-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-7-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-7-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-7-column-4"}
Lineage: sources=gregory1997visual; data/evidence_matrix.json; engineering=Equal central patches on unequal luminance surrounds.; limitation=Display calibration and observer adaptation are not modeled.; missing_contract=none Limitation: Display calibration and observer adaptation are not modeled. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-8"}
## Table 4 — row 8 {#dr-slide-07_publication_audit-table-4-data-8-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-8-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-8-column-1"}
evidence:visual.apparent_motion
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-8-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-8-column-2"}
The sequence contains controlled successive spatial events. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-8-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-8-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-8-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-8-column-4"}
Lineage: sources=wertheimer1912motion; sekuler1996wertheimer; data/evidence_matrix.json; engineering=Alternating rectangular masks at a fixed rational frame rate.; limitation=The artifact establishes temporal succession, not perceived motion.; missing_contract=none Limitation: The artifact establishes temporal succession, not perceived motion. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-9"}
## Table 4 — row 9 {#dr-slide-07_publication_audit-table-4-data-9-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-9-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-9-column-1"}
evidence:audio.shepard_tone
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-9-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-9-column-2"}
The audio contains octave-related partials with controlled sweep parameters. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-9-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-9-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-9-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-9-column-4"}
Lineage: sources=shepard1984scale; data/evidence_matrix.json; engineering=Additive octave-spaced partials with a deterministic envelope.; limitation=Playback transducers and listener pitch judgments are external.; missing_contract=none Limitation: Playback transducers and listener pitch judgments are external. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-10"}
## Table 4 — row 10 {#dr-slide-07_publication_audit-table-4-data-10-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-10-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-10-column-1"}
evidence:audio.missing_fundamental
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-10-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-10-column-2"}
The nominal fundamental component is absent from the canonical spectrum. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-10-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-10-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-10-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-10-column-4"}
Lineage: sources=zatorre2005missing; data/evidence_matrix.json; engineering=Harmonic components are synthesized while the nominal fundamental is omitted.; limitation=Pitch completion is an observer-level inference.; missing_contract=none Limitation: Pitch completion is an observer-level inference. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-11"}
## Table 4 — row 11 {#dr-slide-07_publication_audit-table-4-data-11-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-11-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-11-column-1"}
evidence:audiovisual.sound_induced_flash
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-11-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-11-column-2"}
The declared beep/flash event counts and offsets are physically encoded. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-11-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-11-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-11-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-11-column-4"}
Lineage: sources=shams2000sifi; hirst2020sound; data/evidence_matrix.json; engineering=One flash paired with one or two timed beeps on a shared clock.; limitation=The stimulus does not establish a reported flash count.; missing_contract=none Limitation: The stimulus does not establish a reported flash count. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-12"}
## Table 4 — row 12 {#dr-slide-07_publication_audit-table-4-data-12-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-12-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-12-column-1"}
evidence:audiovisual.ventriloquist
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-12-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-12-column-2"}
The audio and visual channels carry a declared spatial discrepancy. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-12-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-12-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-12-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-12-column-4"}
Lineage: sources=bruns2019ventriloquist; noppeney2018causal; data/evidence_matrix.json; engineering=Stereo panning and visual displacement encode a spatial discrepancy.; limitation=Perceived localization depends on room, headphones, display, and observer.; missing_contract=none Limitation: Perceived localization depends on room, headphones, display, and observer. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-13"}
## Table 4 — row 13 {#dr-slide-07_publication_audit-table-4-data-13-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-13-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-13-column-1"}
evidence:visual.muller_lyer
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-13-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-13-column-2"}
The two bar lengths are equal in the canonical raster while wing geometry varies. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-13-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-13-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-13-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-13-column-4"}
Lineage: sources=gregory1997visual; howe2005muller; data/evidence_matrix.json; engineering=Equal bars with controlled arrow-wing geometry.; limitation=The chosen normalized geometry is one engineering variant.; missing_contract=none Limitation: The chosen normalized geometry is one engineering variant. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-14"}
## Table 4 — row 14 {#dr-slide-07_publication_audit-table-4-data-14-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-14-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-14-column-1"}
evidence:visual.poggendorff
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-14-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-14-column-2"}
The occluder and diagonal continuation are generated from explicit geometry. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-14-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-14-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-14-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-14-column-4"}
Lineage: sources=gregory1997visual; morgan1999poggendorff; data/evidence_matrix.json; engineering=A diagonal continuation is separated by a rectangular occluder.; limitation=Alignment judgments and orientation filters are not measured.; missing_contract=none Limitation: Alignment judgments and orientation filters are not measured. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-15"}
## Table 4 — row 15 {#dr-slide-07_publication_audit-table-4-data-15-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-15-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-15-column-1"}
evidence:visual.ponzo
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-15-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-15-column-2"}
Target bars are physically equal and rails converge toward a vanishing region. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-15-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-15-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-15-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-15-column-4"}
Lineage: sources=fisher1967ponzo; yildiz2022ponzo; data/evidence_matrix.json; engineering=Equal target bars are placed inside converging rails.; limitation=Perspective interpretation is observer- and display-dependent.; missing_contract=none Limitation: Perspective interpretation is observer- and display-dependent. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-16"}
## Table 4 — row 16 {#dr-slide-07_publication_audit-table-4-data-16-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-16-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-16-column-1"}
evidence:visual.kanizsa_triangle
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-16-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-16-column-2"}
The image contains incomplete inducers with no explicitly drawn triangle edge. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-16-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-16-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-16-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-16-column-4"}
Lineage: sources=kanizsa1976contours; wagemans2012gestalt; data/evidence_matrix.json; engineering=Three incomplete circular inducers are rasterized around a triangular gap.; limitation=Illusory contour completion is not directly measured.; missing_contract=none Limitation: Illusory contour completion is not directly measured. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-17"}
## Table 4 — row 17 {#dr-slide-07_publication_audit-table-4-data-17-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-17-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-17-column-1"}
evidence:visual.ebbinghaus
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-17-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-17-column-2"}
Central target geometry is held equal while contextual circle geometry differs. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-17-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-17-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-17-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-17-column-4"}
Lineage: sources=mruczek2015ebbinghaus; weintraub1979ebbinghaus; data/evidence_matrix.json; engineering=Equal central targets are surrounded by different context-circle sizes.; limitation=Perceived size depends on viewing scale and context.; missing_contract=none Limitation: Perceived size depends on viewing scale and context. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-18"}
## Table 4 — row 18 {#dr-slide-07_publication_audit-table-4-data-18-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-18-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-18-column-1"}
evidence:visual.zollner
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-18-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-18-column-2"}
The entry instantiates a controlled crossing-line orientation stimulus family. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-18-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-18-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-18-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-18-column-4"}
Lineage: sources=zoellner1860pseudoscopy; earle1995zollner; gregory1997visual; data/evidence_matrix.json; engineering=Vertical long lines crossed by short oblique inducers with explicit normalized spacing and angle.; limitation=The raster verifies line geometry, not orientation judgments or a pixel-identical historical reproduction.; missing_contract=none Limitation: The raster verifies line geometry, not orientation judgments or a pixel-identical historical reproduction. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-19"}
## Table 4 — row 19 {#dr-slide-07_publication_audit-table-4-data-19-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-19-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-19-column-1"}
evidence:audio.tritone_paradox
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-19-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-19-column-2"}
The canonical pair has an explicit half-octave frequency relation. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-19-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-19-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-19-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-19-column-4"}
Lineage: sources=deutsch1986tritone; repp1997tritone; data/evidence_matrix.json; engineering=Two octave-complex tones are separated by a half-octave interval.; limitation=Ascending/descending reports vary across listeners and contexts.; missing_contract=none Limitation: Ascending/descending reports vary across listeners and contexts. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-20"}
## Table 4 — row 20 {#dr-slide-07_publication_audit-table-4-data-20-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-20-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-20-column-1"}
evidence:audio.octave_illusion
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-20-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-20-column-2"}
The two channels receive alternating octave-related tones. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-20-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-20-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-20-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-20-column-4"}
Lineage: sources=deutsch1974octave; data/evidence_matrix.json; engineering=Alternating high and low tones are assigned to opposite stereo channels.; limitation=The auditory percept depends on dichotic presentation and listener.; missing_contract=none Limitation: The auditory percept depends on dichotic presentation and listener. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-21"}
## Table 4 — row 21 {#dr-slide-07_publication_audit-table-4-data-21-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-21-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-21-column-1"}
evidence:audio.auditory_continuity
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-21-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-21-column-2"}
The canonical audio contains a reproducible interruption interval and masker family. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-21-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-21-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-21-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-21-column-4"}
Lineage: sources=warren1970continuity; riecke2011continuity; data/evidence_matrix.json; engineering=An interrupted sinusoidal carrier is replaced during a declared gap by a deterministic tone or white-noise masker with typed amplitude.; limitation=The generator reports the physical interruption and masker, not a listener's continuity judgment or sensory-versus-decisional effect.; missing_contract=none Limitation: The generator reports the physical interruption and masker, not a listener's continuity judgment or sensory-versus-decisional effect. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-22"}
## Table 4 — row 22 {#dr-slide-07_publication_audit-table-4-data-22-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-22-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-22-column-1"}
evidence:audiovisual.temporal_ventriloquism
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-22-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-22-column-2"}
Audio and video event timing and declared offset are deterministic and inspectable. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-22-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-22-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-22-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-22-column-4"}
Lineage: sources=vroomen2004temporal; hartcherobrien2011temporal; hirst2020sound; noppeney2018causal; data/evidence_matrix.json; engineering=A visual flash and audio click share a clock with explicit offset.; limitation=The generated single-event pair is a simplified engineering stimulus.; missing_contract=none Limitation: The generated single-event pair is a simplified engineering stimulus. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-23"}
## Table 4 — row 23 {#dr-slide-07_publication_audit-table-4-data-23-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-23-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-23-column-1"}
evidence:audiovisual.mcgurk
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-23-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-23-column-2"}
The catalog identifies a speech-dependent audiovisual family without claiming implementation. Level: source_supported
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-23-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-23-column-3"}
checked_in_scholarship
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-23-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-23-column-4"}
Lineage: sources=mcgurk1976speech; data/evidence_matrix.json; engineering=Requires validated speech audio/video fixtures and licensing records.; limitation=No fixture, consent record, or perceptual validation contract is bundled.; missing_contract=A licensed or consented checksummed speech audio/video fixture, synchronization contract, and preregistered perceptual validation protocol are required. Limitation: No fixture, consent record, or perceptual validation contract is bundled. Manuscript: docs/manuscript/06_scope_and_related_work.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-24"}
## Table 4 — row 24 {#dr-slide-07_publication_audit-table-4-data-24-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-24-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-24-column-1"}
publication:figure_count
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-24-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-24-column-2"}
The publication atlas contains 15 registered scientific figures. Level: physical_metric
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-24-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-24-column-3"}
derived_from_code
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-24-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-24-column-4"}
Lineage: publication_caption_specs() Limitation: The count is a package-state fact, not evidence of empirical validity. Manuscript: docs/manuscript/07_publication_audit.md
:::
:::::::::::

::::::::::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-25"}
## Table 4 — row 25 {#dr-slide-07_publication_audit-table-4-data-25-heading}

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-25-column-1-label"}
Column 1 — header:

Claim ID

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-25-column-1"}
publication:table_count
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-25-column-2-label"}
Column 2 — header:

Claim and level

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-25-column-2"}
The publication appendix contains the generated table set defined by the publication table payload registry. Level: physical_metric
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-25-column-3-label"}
Column 3 — header:

Basis

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-25-column-3"}
derived_from_code
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-25-column-4-label"}
Column 4 — header:

Lineage and limitation

Value:
:::

::: {data-duckrabbit-slide-proof="dr-slide-07_publication_audit-table-4-data-25-column-4"}
Lineage: publication_table_payloads() Limitation: Generated tables summarize package state and do not replace source or observer evidence. Manuscript: docs/manuscript/07_publication_audit.md
:::
:::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

The source-tiered evidence table [@tbl:evidence_audit], caption audit
[@tbl:caption_audit], formalism registry [@tbl:formalism], and claim ledger
[@tbl:claim_ledger] are generated sidecars. They provide a publication appendix
without duplicating mutable counts or silently converting literature statements
into package results.

Scientific panels and data are compared with fresh derivations from the trusted
current code. Renderer, font and dependency identities bound exact raster replay;
tables and hydrated prose are separately compared with their current definitions.
This detects coordinated data/hash substitutions but does not authenticate authorship
or establish empirical scientific validity. Human page inspection remains separate.

The cover's real source asset, dimensions, PNG/WebP/thumbnail roles and transforms
are verified. Its historical prompt/model/candidate history is explicitly reported
and unverified rather than inferred from the pixels. Arbitrary supplied images
receive no such history. Neither scientific nor editorial output supplies an
observer result or replaces display calibration or behavioral data.

Formalism checks resolve contained package/test paths, manuscript labels and
figure links; file existence is traceability, not proof of mathematical equivalence.
The network evidence audit covers 36 evidence sources, not every
manuscript reference. URL reachability, bibliographic identity, full-text support
and observer validity remain distinct evidence obligations.
