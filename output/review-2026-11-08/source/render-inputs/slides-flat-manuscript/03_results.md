# Results {#sec:results}

Numbered-table references point to the [canonical manuscript](../web/index.html); they are not standalone local deck numbers.

## Generated catalog, metrics, and outputs {#generated-catalog-metrics-and-outputs}

The live registry reports 17 implemented generators,
18 catalog entries, 18 evidence records, and
36 source records in the checked-in scholarship audit
snapshot. The complete catalog is
generated in Appendix A rather than copied into prose. The companion figure
keeps the categorical registry, source namespace, and implementation statuses
visible at a glance.

![A matrix lists all catalog entries with modality, mechanism, signature, input requirement, and implementation status.](../../output/figures/catalog_matrix.png){#fig:catalog_matrix}

What this figure shows: A matrix lists all catalog entries with modality, mechanism, signature, input requirement, and implementation status. The live catalog matrix contains 18 entries and keeps modality, mechanism, perceptual signature, input requirement, evidence status, and implementation status as separate facets. Source data output/data/catalog_matrix.json preserve the exact taxonomy snapshot and its source-reference namespace; status is not a proxy for perceptual validation. Controls: live taxonomy registry; evidence matrix snapshot; seed not applicable to the catalog diagram. Objective facts: 18 catalog rows; categorical facets and statuses; no observer-level quantity is applicable. Claim level: source_supported. Source data: output/data/catalog_matrix.json (SHA-256 digest recorded in the figure registry). Evidence lineage: gregory1997visual, hirst2020sound, bruns2019ventriloquist. Limitations: Taxonomy facets are engineering classifications and remain provisional where the literature supports competing accounts. Boundary: Catalog coverage is bounded to this registered package and does not enumerate all known illusions.

The complete catalog matrix [@fig:catalog_matrix] is tabulated in the standalone
Appendix A [@sec:appendix_catalog] and in [@tbl:catalog]. The corresponding
machine-readable evidence matrix records the source role, exact supported claim,
engineering departure, and limitation for every entry. Keeping the table in an
appendix gives the main results narrative room to explain the contract without
turning a mutable registry snapshot into a prose claim.

## Typed domains and delivery profiles {#typed-domains-and-delivery-profiles}

::: {#tbl:parameters}
:::

Typed parameter domains and units.

## Table 1 — header row 1 {#dr-slide-03_results-table-1-header-1-heading}

Column 1 — header:

Type

Value:

Type

Column 2 — header:

Unit

Value:

Unit

Column 3 — header:

Validated domain

Value:

Validated domain

Column 4 — header:

Role

Value:

Role

## Table 1 — row 1 {#dr-slide-03_results-table-1-data-1-heading}

Column 1 — header:

Type

Value:

PixelDimension

Column 2 — header:

Unit

Value:

pixels

Column 3 — header:

Validated domain

Value:

8–4096

Column 4 — header:

Role

Value:

image/video width and height

## Table 1 — row 2 {#dr-slide-03_results-table-1-data-2-heading}

Column 1 — header:

Type

Value:

GrayscaleLevels

Column 2 — header:

Unit

Value:

levels

Column 3 — header:

Validated domain

Value:

2–256

Column 4 — header:

Role

Value:

representable grayscale levels

## Table 1 — row 3 {#dr-slide-03_results-table-1-data-3-heading}

Column 1 — header:

Type

Value:

QuantizationLevels

Column 2 — header:

Unit

Value:

levels

Column 3 — header:

Validated domain

Value:

2–256

Column 4 — header:

Role

Value:

output quantization buckets

## Table 1 — row 4 {#dr-slide-03_results-table-1-data-4-heading}

Column 1 — header:

Type

Value:

FrequencyHz

Column 2 — header:

Unit

Value:

Hz

Column 3 — header:

Validated domain

Value:

\> 0 and finite

Column 4 — header:

Role

Value:

oscillator and harmonic frequencies

## Table 1 — row 5 {#dr-slide-03_results-table-1-data-5-heading}

Column 1 — header:

Type

Value:

SampleRate

Column 2 — header:

Unit

Value:

samples/s

Column 3 — header:

Validated domain

Value:

1,000–384,000

Column 4 — header:

Role

Value:

audio sampling clock

## Table 1 — row 6 {#dr-slide-03_results-table-1-data-6-heading}

Column 1 — header:

Type

Value:

FrameRate

Column 2 — header:

Unit

Value:

frames/s

Column 3 — header:

Validated domain

Value:

1–240

Column 4 — header:

Role

Value:

video presentation clock

## Table 1 — row 7 {#dr-slide-03_results-table-1-data-7-heading}

Column 1 — header:

Type

Value:

SyncOffsetMs

Column 2 — header:

Unit

Value:

ms

Column 3 — header:

Validated domain

Value:

−10,000–10,000

Column 4 — header:

Role

Value:

audio relative to video

## Table 1 — row 8 {#dr-slide-03_results-table-1-data-8-heading}

Column 1 — header:

Type

Value:

SpatialOffset

Column 2 — header:

Unit

Value:

normalized

Column 3 — header:

Validated domain

Value:

−1–1

Column 4 — header:

Role

Value:

declared crossmodal spatial discrepancy

The parameter contracts are summarized in [@tbl:parameters]. They constrain
physical construction and serialization; they are not psychophysical scales.

::: {#tbl:encodings}
:::

Encoding profiles and backend capabilities.

## Table 2 — header row 1 {#dr-slide-03_results-table-2-header-1-heading}

Column 1 — header:

Format

Value:

Format

Column 2 — header:

Backend

Value:

Backend

Column 3 — header:

Artifact

Value:

Artifact

Column 4 — header:

Profile

Value:

Profile

Column 5 — header:

Status

Value:

Status

## Table 2 — row 1 {#dr-slide-03_results-table-2-data-1-heading}

Column 1 — header:

Format

Value:

PNG

Column 2 — header:

Backend

Value:

Pillow

Column 3 — header:

Artifact

Value:

image

Column 4 — header:

Profile

Value:

lossless uint8 raster

Column 5 — header:

Status

Value:

available

## Table 2 — row 2 {#dr-slide-03_results-table-2-data-2-heading}

Column 1 — header:

Format

Value:

WAV

Column 2 — header:

Backend

Value:

python wave

Column 3 — header:

Artifact

Value:

audio

Column 4 — header:

Profile

Value:

PCM 8/16/24/32-bit

Column 5 — header:

Status

Value:

available

## Table 2 — row 3 {#dr-slide-03_results-table-2-data-3-heading}

Column 1 — header:

Format

Value:

GIF

Column 2 — header:

Backend

Value:

Pillow

Column 3 — header:

Artifact

Value:

video

Column 4 — header:

Profile

Value:

palette animation with declared duration

Column 5 — header:

Status

Value:

available

## Table 2 — row 4 {#dr-slide-03_results-table-2-data-4-heading}

Column 1 — header:

Format

Value:

NPZ

Column 2 — header:

Backend

Value:

NumPy

Column 3 — header:

Artifact

Value:

canonical artifact

Column 4 — header:

Profile

Value:

exact little-endian float32 archive

Column 5 — header:

Status

Value:

available

## Table 2 — row 5 {#dr-slide-03_results-table-2-data-5-heading}

Column 1 — header:

Format

Value:

MP4

Column 2 — header:

Backend

Value:

ffmpeg

Column 3 — header:

Artifact

Value:

video/audiovisual

Column 4 — header:

Profile

Value:

H.264 or muxed MP4; decode inspected

Column 5 — header:

Status

Value:

available

The delivery profiles are summarized in [@tbl:encodings]. Backend availability
is environment-dependent and is recorded at generation time.

The catalog distinguishes a physical construction from an observer claim. For
example, the sound-induced-flash generator establishes one flash and one or two
beep events on a shared clock; it does not establish a reported flash count.
Similarly, the temporal-ventriloquism generator exposes a declared timing
offset, while the literature reports observer-dependent temporal judgments
under specific tasks and timing conditions [@vroomen2004temporal].

## Pipeline and provenance {#pipeline-and-provenance}

![Five labeled stages connect a typed request to a deterministic canonical artifact, encoded media, decoded inspection, and a verification manifest.](../../output/figures/architecture.png){#fig:architecture}

What this figure shows: Five labeled stages connect a typed request to a deterministic canonical artifact, encoded media, decoded inspection, and a verification manifest. This schematic separates a typed request from the canonical artifact it generates, the optional delivery encoder, decoded inspection, and the manifest-level verification decision. Arrows indicate data and provenance dependencies rather than a causal model of perception; the seed is 0 and the complete stage record is in source data output/data/architecture.json. Controls: typed request q=(i,θ,s,e) with seed s=0; default generator and delivery-independent canonicalization. Objective facts: no unit-bearing objective quantity is applicable to this architecture diagram; stage identities and provenance fields are recorded in the sidecar. Claim level: canonical_stimulus. Source data: output/data/architecture.json (SHA-256 digest recorded in the figure registry). Evidence lineage: formalism:eq:typed_request, formalism:eq:canonical_generation, formalism:eq:encoding_verification. Limitations: The schematic abstracts implementation boundaries and does not represent an observer study or a causal theory of perception. Boundary: The pipeline verifies reproducible media facts, not what a person experiences.

The generated architecture figure [@fig:architecture] shows the separation between request,
canonical artifact, delivery adapter, decoded inspection, and manifest. The
canonical digest is the identity of the in-memory stimulus; an encoded hash is
the identity of the delivered file. The difference is intentional.

## Visual constructions and parameter sweeps {#visual-constructions-and-parameter-sweeps}

![A 9-panel gallery shows every currently implemented visual catalog entry, with stable IDs and physical raster summaries: Duck-rabbit ambiguous figure, Simultaneous contrast stimulus, Apparent-motion frame sequence, Müller-Lyer geometric illusion, Poggendorff geometric illusion, Ponzo perspective illusion, Kanizsa illusory-contour triangle, Ebbinghaus context-size illusion, Zöllner orientation illusion.](../../output/figures/visual_panel.png){#fig:visual_panel}

What this figure shows: A 9-panel gallery shows every currently implemented visual catalog entry, with stable IDs and physical raster summaries: Duck-rabbit ambiguous figure, Simultaneous contrast stimulus, Apparent-motion frame sequence, Müller-Lyer geometric illusion, Poggendorff geometric illusion, Ponzo perspective illusion, Kanizsa illusory-contour triangle, Ebbinghaus context-size illusion, Zöllner orientation illusion. This complete gallery presents one deterministic representative from each of the 9 currently implemented visual catalog entries: Duck-rabbit ambiguous figure, Simultaneous contrast stimulus, Apparent-motion frame sequence, Müller-Lyer geometric illusion, Poggendorff geometric illusion, Ponzo perspective illusion, Kanizsa illusory-contour triangle, Ebbinghaus context-size illusion, Zöllner orientation illusion. The panel therefore covers the package's available visual families—ambiguous figure, contrast, apparent motion, geometric context, illusory contour, contextual size, and orientation-related constructions—using typed defaults at seed 0. For the temporally expressed apparent-motion entry, the displayed tile is its first frame and the source data preserve the full sequence. The source data sidecar output/data/visual_panel.json records the stable ID, generator parameters, canonical SHA-256 digest, grayscale code-value or Rec. 709-weighted RGB proxy statistics (no transfer conversion or display calibration), raster-level counts, and parameter boundary for every tile. Controls: one default typed parameter object per implemented visual entry; seed s=0; dimensions, luminance bounds, grayscale, and quantization controls remain in each generator schema; temporal entries display their first frame but retain sequence metrics. Objective facts: per tile: mean and standard deviation of the declared uncalibrated channel-value proxy, unique raster levels, and canonical SHA-256 digest; temporal entries additionally retain frame count, frame rate, and frame deltas; definitions and units are in the source data JSON. Claim level: canonical_stimulus. Source data: output/data/visual_panel.json (SHA-256 digest recorded in the figure registry). Evidence lineage: gregory1997visual, brugger1999duckrabbit, howe2005muller, morgan1999poggendorff, fisher1967ponzo, yildiz2022ponzo, kanizsa1976contours, mruczek2015ebbinghaus, earle1995zollner, wertheimer1912motion, sekuler1996wertheimer. Limitations: The gallery is complete for implemented visual entries in this package, not a complete survey of visual illusions; literature families, historical displays, and DuckRabbit rasters are not pixel-identical by default. Viewing scale, display calibration, viewing distance, and observer conditions can change the relevance of a construction; the gallery does not measure an observer's perceptual report. Boundary: The figure establishes coverage of the package's implemented visual constructions and their deterministic raster facts. It does not establish that any viewer will perceive the named signature, nor that the set is exhaustive of the visual-illusion literature.

The visual panel [@fig:visual_panel] is deliberately a coverage figure: it
contains one deterministic representative for every currently implemented
visual entry, including apparent motion and Zöllner in addition to the static
ambiguous-figure, contrast, geometric-context, illusory-contour, and contextual-
size families. Equalities, masks, line geometry, luminance bounds, and temporal
positions are properties of the typed rasters or sequences. They are not
observer scores, and the gallery is not an exhaustive ontology of visual
illusions.

![A labeled grid crosses five duck–rabbit blend weights with five grayscale and quantization settings, with physical metrics recorded for each cell.](../../output/figures/visual_sweep.png){#fig:visual_sweep}

What this figure shows: A labeled grid crosses five duck–rabbit blend weights with five grayscale and quantization settings, with physical metrics recorded for each cell. This 5×5 sweep varies duck–rabbit blend weight across rows and jointly varies grayscale and quantization levels across columns. Each cell is regenerated from an immutable typed parameter object at seed 0; source data output/data/visual_sweep.json records canonical digests, unique-level counts, normalized luminance, and effective dynamic range for every condition. Controls: duck_weight ∈ {0,.25,.5,.75,1}; grayscale=quantization ∈ {2,4,8,16,32}; seed s=0. Objective facts: 25 canonical rasters; unique levels, normalized mean luminance, and effective dynamic range per cell. Claim level: physical_metric. Source data: output/data/visual_sweep.json (SHA-256 digest recorded in the figure registry). Evidence lineage: brugger1999duckrabbit, gregory1997visual. Limitations: The grid is a sensitivity of the construction parameters, not a psychophysical sensitivity curve or a validated observer effect. Boundary: The chosen grid is an engineering sampling of the parameter domain and does not imply an optimal or perceptually uniform spacing.

The sweep [@fig:visual_sweep] varies duck-weight from 0 to 1 and jointly varies representable
grayscale and quantization levels. The source data preserve canonical digests
and unique-value counts; no perceptual score is assigned to a sweep cell.

## Temporal and auditory constructions {#temporal-and-auditory-constructions}

![Six ordered frames are labeled with timestamps and paired with a line plot of adjacent-frame normalized pixel differences.](../../output/figures/temporal_sequence.png){#fig:temporal_sequence}

What this figure shows: Six ordered frames are labeled with timestamps and paired with a line plot of adjacent-frame normalized pixel differences. The frame strip exposes the order and timestamps of the apparent-motion construction, while the lower trace reports adjacent-frame mean absolute pixel differences. Source data output/data/temporal_sequence.json preserve frame count, frame rate, reduced rational timebase, timestamps in seconds, and the nonzero transition series; seed 0 identifies the generated sequence. Controls: visual.apparent_motion default typed parameters; frame rate and frame count from the canonical sequence; seed s=0. Objective facts: timestamps in seconds, frame rate in frames/s, frame count, rational timebase, and adjacent-frame normalized pixel difference. Claim level: physical_metric. Source data: output/data/temporal_sequence.json (SHA-256 digest recorded in the figure registry). Evidence lineage: wertheimer1912motion, sekuler1996wertheimer. Limitations: Frame succession and frame deltas are physical file properties; playback timing, display persistence, and motion reports require a controlled observer task. Boundary: The figure documents temporal structure rather than the presence, direction, or strength of perceived motion.

The temporal figure [@fig:temporal_sequence] reports frame succession, rational frame rate, and
frame-to-frame mean absolute differences. These facts establish temporal
structure in the file, not the presence or strength of perceived motion.

![Five labeled rows show canonical audio waveforms, relative one-sided spectral bars, RMS and peak in normalized amplitude, and spectral summaries in hertz.](../../output/figures/audio_signals.png){#fig:audio_signals}

What this figure shows: Five labeled rows show canonical audio waveforms, relative one-sided spectral bars, RMS and peak in normalized amplitude, and spectral summaries in hertz. Five implemented auditory constructions—Shepard tone, missing fundamental, tritone paradox, octave illusion, and auditory continuity—are shown as canonical waveforms with compact one-sided FFT summaries. Source data output/data/audio_signals.json records sample rate, channel layout, RMS, peak, spectral centroid, bandwidth, crest factor, canonical digest, and the declared display-bin convention; no pitch or stream report is inferred. Controls: default typed audio parameters; per-generator channel layout and sample rate; seed s=0; one-sided FFT display with 48 frequency-labelled peak-magnitude bands. Objective facts: RMS and peak in normalized amplitude; spectral centroid and bandwidth in Hz; sample rate in samples/s; channel layout and canonical SHA-256 digest. Claim level: physical_metric. Source data: output/data/audio_signals.json (SHA-256 digest recorded in the figure registry). Evidence lineage: shepard1984scale, zatorre2005missing, deutsch1986tritone, repp1997tritone, deutsch1974octave, warren1970continuity, riecke2011continuity. Limitations: Playback level, transducer response, dichotic separation, masker design, and listener judgments are external to the canonical buffer. Boundary: The figure compares generated signal properties and literature-linked families; it does not establish pitch, continuity, or stream organization for a listener.

The auditory figure [@fig:audio_signals] shows canonical waveforms and spectral
summaries for Shepard, missing-fundamental, tritone, octave, and continuity
constructions. RMS, peak, spectral centroid, bandwidth, and channel layout are
calculated from the canonical buffer with explicit units and windowing rules.
Pitch direction, pitch height, continuity, and stream organization remain
observer-level outcomes that depend on playback and task conditions.

## Audiovisual timing and encoding {#audiovisual-timing-and-encoding}

![Two labeled traces share a time axis in seconds: video mean channel-value proxy and audio absolute amplitude, with signed synchronization and spatial offsets printed below.](../../output/figures/audiovisual_timeline.png){#fig:audiovisual_timeline}

What this figure shows: Two labeled traces share a time axis in seconds: video mean channel-value proxy and audio absolute amplitude, with signed synchronization and spatial offsets printed below. Video mean channel-value proxy and rectified audio amplitude are placed on a common time axis in seconds with video frame holds and actual audio sample timestamps for the sound-induced-flash construction. Source data output/data/audiovisual_timeline.json records the video frame clock, audio sampling clock, event traces, signed audio-minus-video synchronization offset in milliseconds, and normalized spatial discrepancy; alignment is declared by the generator, not estimated from perception. Controls: audiovisual.sound_induced_flash default shared timeline; declared sync offset ΔAV and spatial offset; seed s=0. Objective facts: video frame-hold grayscale/weighted-RGB proxy and mean-channel absolute audio amplitude on shared time in seconds; ΔAV in ms; spatial discrepancy in normalized units; frame and sample clocks in the sidecar. Claim level: physical_metric. Source data: output/data/audiovisual_timeline.json (SHA-256 digest recorded in the figure registry). Evidence lineage: shams2000sifi, hirst2020sound, vroomen2004temporal, hartcherobrien2011temporal. Limitations: Display refresh, audio hardware, event latency, and observer temporal binding are not measured by this figure. Boundary: A shared-clock construction is not evidence that observers bind the events at the declared or any other perceptual time.

The audiovisual timeline [@fig:audiovisual_timeline] displays video luminance and audio amplitude against
the shared clock, alongside declared synchronization and spatial offsets.
Ventriloquist stimuli require stereo playback and spatially resolved display;
temporal binding requires controlled timing and an observer task
[@bruns2019ventriloquist; @vroomen2004temporal].

![A five-row comparison lists format, backend, preserved canonical facts, and the corresponding decoded verification checks.](../../output/figures/encoding_verification.png){#fig:encoding_verification}

What this figure shows: A five-row comparison lists format, backend, preserved canonical facts, and the corresponding decoded verification checks. The comparison separates the canonical artifact from delivery containers: PNG, WAV, GIF, NPZ, and optional MP4/muxed MP4. Source data output/data/encoding_verification.json records backend identity, preserved canonical facts, decoded inspection targets, and capability status as observed in the generation environment; the table therefore describes an adapter contract rather than a claim about codec quality. Controls: typed encoding profile selected per artifact; overwrite and backend capability checks; seed inherited from the stimulus request. Objective facts: format availability and verification scope are environment observations; NPZ is exact while other formats are decoded and tolerance-checked. Claim level: encoded_media. Source data: output/data/encoding_verification.json (SHA-256 digest recorded in the figure registry). Evidence lineage: engineering:typed_media_adapters. Limitations: Backend availability, codec versions, container metadata, and lossy tolerances are environment-dependent; playback software can expose additional behavior. Boundary: A successful encode or decode does not validate an observer effect or guarantee cross-device perceptual equivalence.

The encoding matrix [@fig:encoding_verification] makes backend capability and verification scope visible.
NPZ is the exact canonical archive; PNG, WAV, GIF, and MP4 are delivery
containers whose decoded facts are checked against the manifest.

## Objective metric results {#sec:objective_metric_results}

::: {#tbl:metrics}
:::

Objective metric definitions and epistemic boundary.

## Table 3 — header row 1 {#dr-slide-03_results-table-3-header-1-heading}

Column 1 — header:

Metric

Value:

Metric

Column 2 — header:

Unit

Value:

Unit

Column 3 — header:

Definition

Value:

Definition

Column 4 — header:

Tolerance

Value:

Tolerance

Column 5 — header:

Claim level

Value:

Claim level

## Table 3 — row 1 {#dr-slide-03_results-table-3-data-1-heading}

Column 1 — header:

Metric

Value:

mean_luminance

Column 2 — header:

Unit

Value:

normalized_luminance

Column 3 — header:

Definition

Value:

mean grayscale value or Rec.709-weighted RGB code-value proxy; no transfer conversion or display calibration

Column 4 — header:

Tolerance

Value:

exact canonical

Column 5 — header:

Claim level

Value:

physical_metric

## Table 3 — row 2 {#dr-slide-03_results-table-3-data-2-heading}

Column 1 — header:

Metric

Value:

unique_values

Column 2 — header:

Unit

Value:

levels

Column 3 — header:

Definition

Value:

count of distinct canonical image values

Column 4 — header:

Tolerance

Value:

exact integer

Column 5 — header:

Claim level

Value:

physical_metric

## Table 3 — row 3 {#dr-slide-03_results-table-3-data-3-heading}

Column 1 — header:

Metric

Value:

rms

Column 2 — header:

Unit

Value:

normalized_amplitude

Column 3 — header:

Definition

Value:

root-mean-square audio amplitude

Column 4 — header:

Tolerance

Value:

finite scalar

Column 5 — header:

Claim level

Value:

physical_metric

## Table 3 — row 4 {#dr-slide-03_results-table-3-data-4-heading}

Column 1 — header:

Metric

Value:

peak

Column 2 — header:

Unit

Value:

normalized_amplitude

Column 3 — header:

Definition

Value:

maximum absolute audio amplitude

Column 4 — header:

Tolerance

Value:

finite scalar

Column 5 — header:

Claim level

Value:

physical_metric

## Table 3 — row 5 {#dr-slide-03_results-table-3-data-5-heading}

Column 1 — header:

Metric

Value:

spectral_centroid_hz

Column 2 — header:

Unit

Value:

Hz

Column 3 — header:

Definition

Value:

one-sided frequency mean weighted by mean-channel abs(unwindowed rFFT) magnitude, not energy

Column 4 — header:

Tolerance

Value:

finite scalar

Column 5 — header:

Claim level

Value:

physical_metric

## Table 3 — row 6 {#dr-slide-03_results-table-3-data-6-heading}

Column 1 — header:

Metric

Value:

spectral_bandwidth_hz

Column 2 — header:

Unit

Value:

Hz

Column 3 — header:

Definition

Value:

spectral standard deviation around the one-sided centroid

Column 4 — header:

Tolerance

Value:

finite scalar

Column 5 — header:

Claim level

Value:

physical_metric

## Table 3 — row 7 {#dr-slide-03_results-table-3-data-7-heading}

Column 1 — header:

Metric

Value:

crest_factor

Column 2 — header:

Unit

Value:

ratio

Column 3 — header:

Definition

Value:

audio peak divided by RMS with zero-RMS guard

Column 4 — header:

Tolerance

Value:

finite scalar

Column 5 — header:

Claim level

Value:

physical_metric

## Table 3 — row 8 {#dr-slide-03_results-table-3-data-8-heading}

Column 1 — header:

Metric

Value:

mean_temporal_delta

Column 2 — header:

Unit

Value:

normalized_pixel_difference

Column 3 — header:

Definition

Value:

mean adjacent-frame absolute difference

Column 4 — header:

Tolerance

Value:

finite scalar

Column 5 — header:

Claim level

Value:

physical_metric

## Table 3 — row 9 {#dr-slide-03_results-table-3-data-9-heading}

Column 1 — header:

Metric

Value:

sync_offset

Column 2 — header:

Unit

Value:

ms

Column 3 — header:

Definition

Value:

declared audio-minus-video offset

Column 4 — header:

Tolerance

Value:

typed value

Column 5 — header:

Claim level

Value:

physical_metric

The metric definitions in [@tbl:metrics] are computed from canonical or
decoded artifacts and do not encode observer interpretations.

The default duck-rabbit artifact contains 3
unique raster levels and has mean normalized luminance 0.7770.
These values are live generated facts, not perceptual effect sizes.

## Observer estimands and verification controls {#observer-estimands-and-verification-controls}

::: {#tbl:observer_estimands}
:::

Data-free observer outcomes and preregistered estimands.

## Table 4 — header row 1 {#dr-slide-03_results-table-4-header-1-heading}

Column 1 — header:

Estimand

Value:

Estimand

Column 2 — header:

Response and model

Value:

Response and model

Column 3 — header:

Reference and contrast

Value:

Reference and contrast

Column 4 — header:

Uncertainty

Value:

Uncertainty

## Table 4 — row 1 {#dr-slide-03_results-table-4-data-1-heading}

Column 1 — header:

Estimand

Value:

sifi_flash_count_contrast

Column 2 — header:

Response and model

Value:

forced_choice; logistic_mixed

Column 3 — header:

Reference and contrast

Value:

sifi_one_beep; log odds of choosing 'two': sifi_two_beep minus sifi_one_beep

Column 4 — header:

Uncertainty

Value:

95% confidence interval

## Table 4 — row 2 {#dr-slide-03_results-table-4-data-2-heading}

Column 1 — header:

Estimand

Value:

temporal_binding_offset_contrast

Column 2 — header:

Response and model

Value:

forced_choice; logistic_mixed

Column 3 — header:

Reference and contrast

Value:

temporal_sync; log odds of choosing 'late': temporal_early and temporal_late versus temporal_sync (categorical offsets -120/0/+120 ms)

Column 4 — header:

Uncertainty

Value:

95% confidence interval

The analysis contract in [@tbl:observer_estimands] specifies estimands and
uncertainty procedures without asserting any result.

::: {#tbl:verification}
:::

Verification failure modes and negative controls.

## Table 5 — header row 1 {#dr-slide-03_results-table-5-header-1-heading}

Column 1 — header:

Failure mode

Value:

Failure mode

Column 2 — header:

Control

Value:

Control

Column 3 — header:

Expected result

Value:

Expected result

## Table 5 — row 1 {#dr-slide-03_results-table-5-data-1-heading}

Column 1 — header:

Failure mode

Value:

altered encoded file

Column 2 — header:

Control

Value:

recompute encoded SHA-256

Column 3 — header:

Expected result

Value:

fail

## Table 5 — row 2 {#dr-slide-03_results-table-5-data-2-heading}

Column 1 — header:

Failure mode

Value:

stale canonical digest

Column 2 — header:

Control

Value:

recompute canonical little-endian float32 digest

Column 3 — header:

Expected result

Value:

fail

## Table 5 — row 3 {#dr-slide-03_results-table-5-data-3-heading}

Column 1 — header:

Failure mode

Value:

incorrect decoded dimensions

Column 2 — header:

Control

Value:

compare inspection facts with manifest summary

Column 3 — header:

Expected result

Value:

fail

## Table 5 — row 4 {#dr-slide-03_results-table-5-data-4-heading}

Column 1 — header:

Failure mode

Value:

stream timing mismatch

Column 2 — header:

Control

Value:

compare duration/timebase and declared sync offset

Column 3 — header:

Expected result

Value:

fail

## Table 5 — row 5 {#dr-slide-03_results-table-5-data-5-heading}

Column 1 — header:

Failure mode

Value:

unsupported backend

Column 2 — header:

Control

Value:

capability probe before encoding

Column 3 — header:

Expected result

Value:

explicit capability error

## Table 5 — row 6 {#dr-slide-03_results-table-5-data-6-heading}

Column 1 — header:

Failure mode

Value:

conflicting format requests

Column 2 — header:

Control

Value:

reject format_name/output_spec disagreement

Column 3 — header:

Expected result

Value:

parameter error

The negative controls in [@tbl:verification] test package integrity and media
contracts; they are not null findings about perception.

## Synthetic psychophysics model diagnostic {#synthetic-psychophysics-model-diagnostic}

![A line plot and model-sensitivity range show deterministic model probability across duck_weight values beside the model identity, temperature, no-training-data statement, and human-data boundary.](../../output/figures/synthetic_psychophysics.png){#fig:synthetic_psychophysics}

What this figure shows: A line plot and model-sensitivity range show deterministic model probability across duck_weight values beside the model identity, temperature, no-training-data statement, and human-data boundary. The hand-specified feature observer compares duck_weight variants with a fixed canonical reference. Its probability trace is computed analytically from serialized features, weights, and temperature; source data output/data/synthetic_psychophysics.json records model ID/version, reference and comparison digests, seed, calibration, `training_data=none`, and `human_data=false`. The shaded range covers the declared zero-weight control, one-at-a-time weight ablations, and temperature multipliers 0.5, 1, and 2; it is model sensitivity, not a confidence interval. Controls: duck_weight comparison against fixed reference; serialized feature weights and temperature; seed s=0. Objective facts: model probability, null baseline, ablations, temperature sensitivity and exact-self control; full feature values, specifications and canonical stimulus digests; human_data=false; training_data=none. Claim level: synthetic_model_output. Source data: output/data/synthetic_psychophysics.json (SHA-256 digest recorded in the figure registry). Evidence lineage: observer:preregistered_estimands. Limitations: The model is hand-specified, has no training data, has not been calibrated against observers, and does not estimate a human threshold or effect size. Its probabilities and the finite configuration range are model outputs, not participant responses, confidence intervals, or a psychometric function. Boundary: This diagnostic tests deterministic orchestration and metamorphic input-output behavior only; empirical psychophysics remains future work.

The diagnostic [@fig:synthetic_psychophysics] evaluates a fully serialized,
hand-specified feature observer against a fixed canonical reference while
varying `duck_weight`. Its logistic probabilities are model outputs generated
from explicit features, weights, temperature, and seed; they are not a
pretrained vision-model score, a human psychometric function, an assumed human
effect size, or participant data. A future human study would require a
preregistered task, calibrated display and playback, consented participants,
exclusion and missingness rules, and an analysis contract before any observer
claim could be made.
