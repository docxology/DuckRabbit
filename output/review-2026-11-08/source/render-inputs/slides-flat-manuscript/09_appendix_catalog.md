# Appendix A. Complete catalog, source tiers, and evidence and implementation boundaries {#sec:appendix_catalog}

Numbered-table references point to the [canonical manuscript](../web/index.html); they are not standalone local deck numbers.

This appendix is the authoritative rendered snapshot of DuckRabbit's live
catalog. It is generated from the taxonomy registry and evidence matrix during
the publication build; the table is not hand-maintained. The snapshot records
the package's current scope, not a claim to enumerate every illusion described
in the literature.

## How to read the matrix {#how-to-read-the-matrix}

Each row identifies a registered illusion family and separates five questions
that are often collapsed in informal catalogs:

1.  What modality, mechanism, and signature does the package assign to the construction?
2.  What evidence and implementation status does the checked-in record support?
3.  Which sources support the exact statement written in the row?
4.  What physical claim is supported by the row?
5.  What full source role, resolver, DOI status, and claim level are retained in the machine-readable record?

`implemented` means that DuckRabbit has a deterministic generator and a
validated canonical artifact contract. It does not mean that the generated
stimulus is a pixel-identical reproduction of a historical experiment or that
an observer effect has been re-established. `input_required` means that the
family remains catalogued but lacks a lawful, checksummed input fixture and/or
the validation contract required for deterministic generation. Evidence status
and implementation status are deliberately independent.

The source column is a compact citation-key view. The full source role,
resolver or DOI status, exact supported claim, engineering departure, and
limitation are retained in the machine-readable evidence matrix and in the
generated evidence audit [@tbl:evidence_audit]. A source supports only the
narrow claim recorded for it; a review or theory record is not evidence that a
DuckRabbit rendering produces a universal perceptual effect.

::: {#tbl:catalog}
:::

DuckRabbit catalog entries, source tiers, and evidence/implementation boundaries.

## Table 1 — header row 1 {#dr-slide-09_appendix_catalog-table-1-header-1-heading}

Column 1 — header:

ID

Value:

ID

Column 2 — header:

Construction

Value:

Construction

Column 3 — header:

Evidence / status

Value:

Evidence / status

Column 4 — header:

Sources

Value:

Sources

Column 5 — header:

Supported claim

Value:

Supported claim

## Table 1 — row 1 {#dr-slide-09_appendix_catalog-table-1-data-1-heading}

Column 1 — header:

ID

Value:

visual.duck_rabbit

Column 2 — header:

Construction

Value:

visual; ambiguity; bistability

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

brugger1999duckrabbit, gregory1997visual

Column 5 — header:

Supported claim

Value:

The entry instantiates a controllable ambiguous-figure stimulus family.

## Table 1 — row 2 {#dr-slide-09_appendix_catalog-table-1-data-2-heading}

Column 1 — header:

ID

Value:

visual.simultaneous_contrast

Column 2 — header:

Construction

Value:

visual; contrast_and_context; contrast_distortion

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

gregory1997visual

Column 5 — header:

Supported claim

Value:

The physical center patches are matched while surround luminance differs.

## Table 1 — row 3 {#dr-slide-09_appendix_catalog-table-1-data-3-heading}

Column 1 — header:

ID

Value:

visual.apparent_motion

Column 2 — header:

Construction

Value:

visual; temporal_motion; illusory_motion

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

wertheimer1912motion, sekuler1996wertheimer

Column 5 — header:

Supported claim

Value:

The sequence contains controlled successive spatial events.

## Table 1 — row 4 {#dr-slide-09_appendix_catalog-table-1-data-4-heading}

Column 1 — header:

ID

Value:

audio.shepard_tone

Column 2 — header:

Construction

Value:

auditory; spectral_harmonic; continuity

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

shepard1984scale

Column 5 — header:

Supported claim

Value:

The audio contains octave-related partials with controlled sweep parameters.

## Table 1 — row 5 {#dr-slide-09_appendix_catalog-table-1-data-5-heading}

Column 1 — header:

ID

Value:

audio.missing_fundamental

Column 2 — header:

Construction

Value:

auditory; spectral_harmonic; filling_in

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

zatorre2005missing

Column 5 — header:

Supported claim

Value:

The nominal fundamental component is absent from the canonical spectrum.

## Table 1 — row 6 {#dr-slide-09_appendix_catalog-table-1-data-6-heading}

Column 1 — header:

ID

Value:

audiovisual.sound_induced_flash

Column 2 — header:

Construction

Value:

audio_visual; crossmodal_temporal; fusion_or_fission

Column 3 — header:

Evidence / status

Value:

review_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

shams2000sifi, hirst2020sound

Column 5 — header:

Supported claim

Value:

The declared beep/flash event counts and offsets are physically encoded.

## Table 1 — row 7 {#dr-slide-09_appendix_catalog-table-1-data-7-heading}

Column 1 — header:

ID

Value:

audiovisual.ventriloquist

Column 2 — header:

Construction

Value:

audio_visual; crossmodal_spatial; spatial_capture

Column 3 — header:

Evidence / status

Value:

review_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

bruns2019ventriloquist, noppeney2018causal

Column 5 — header:

Supported claim

Value:

The audio and visual channels carry a declared spatial discrepancy.

## Table 1 — row 8 {#dr-slide-09_appendix_catalog-table-1-data-8-heading}

Column 1 — header:

ID

Value:

visual.muller_lyer

Column 2 — header:

Construction

Value:

visual; geometric_alignment; geometric_distortion

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

gregory1997visual, howe2005muller

Column 5 — header:

Supported claim

Value:

The two bar lengths are equal in the canonical raster while wing geometry varies.

## Table 1 — row 9 {#dr-slide-09_appendix_catalog-table-1-data-9-heading}

Column 1 — header:

ID

Value:

visual.poggendorff

Column 2 — header:

Construction

Value:

visual; geometric_alignment; geometric_distortion

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

gregory1997visual, morgan1999poggendorff

Column 5 — header:

Supported claim

Value:

The occluder and diagonal continuation are generated from explicit geometry.

## Table 1 — row 10 {#dr-slide-09_appendix_catalog-table-1-data-10-heading}

Column 1 — header:

ID

Value:

visual.ponzo

Column 2 — header:

Construction

Value:

visual; geometric_alignment; geometric_distortion

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

fisher1967ponzo, yildiz2022ponzo

Column 5 — header:

Supported claim

Value:

Target bars are physically equal and rails converge toward a vanishing region.

## Table 1 — row 11 {#dr-slide-09_appendix_catalog-table-1-data-11-heading}

Column 1 — header:

ID

Value:

visual.kanizsa_triangle

Column 2 — header:

Construction

Value:

visual; contrast_and_context, geometric_alignment; filling_in

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

kanizsa1976contours, wagemans2012gestalt

Column 5 — header:

Supported claim

Value:

The image contains incomplete inducers with no explicitly drawn triangle edge.

## Table 1 — row 12 {#dr-slide-09_appendix_catalog-table-1-data-12-heading}

Column 1 — header:

ID

Value:

visual.ebbinghaus

Column 2 — header:

Construction

Value:

visual; contrast_and_context, geometric_alignment; geometric_distortion

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

mruczek2015ebbinghaus, weintraub1979ebbinghaus

Column 5 — header:

Supported claim

Value:

Central target geometry is held equal while contextual circle geometry differs.

## Table 1 — row 13 {#dr-slide-09_appendix_catalog-table-1-data-13-heading}

Column 1 — header:

ID

Value:

visual.zollner

Column 2 — header:

Construction

Value:

visual; geometric_alignment; geometric_distortion

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

zoellner1860pseudoscopy, earle1995zollner, gregory1997visual

Column 5 — header:

Supported claim

Value:

The entry instantiates a controlled crossing-line orientation stimulus family.

## Table 1 — row 14 {#dr-slide-09_appendix_catalog-table-1-data-14-heading}

Column 1 — header:

ID

Value:

audio.tritone_paradox

Column 2 — header:

Construction

Value:

auditory; spectral_harmonic; categorical_recoding

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

deutsch1986tritone, repp1997tritone

Column 5 — header:

Supported claim

Value:

The canonical pair has an explicit half-octave frequency relation.

## Table 1 — row 15 {#dr-slide-09_appendix_catalog-table-1-data-15-heading}

Column 1 — header:

ID

Value:

audio.octave_illusion

Column 2 — header:

Construction

Value:

auditory; stream_segregation; fusion_or_fission

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

deutsch1974octave

Column 5 — header:

Supported claim

Value:

The two channels receive alternating octave-related tones.

## Table 1 — row 16 {#dr-slide-09_appendix_catalog-table-1-data-16-heading}

Column 1 — header:

ID

Value:

audio.auditory_continuity

Column 2 — header:

Construction

Value:

auditory; stream_segregation; continuity

Column 3 — header:

Evidence / status

Value:

literature_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

warren1970continuity, riecke2011continuity

Column 5 — header:

Supported claim

Value:

The canonical audio contains a reproducible interruption interval and masker family.

## Table 1 — row 17 {#dr-slide-09_appendix_catalog-table-1-data-17-heading}

Column 1 — header:

ID

Value:

audiovisual.temporal_ventriloquism

Column 2 — header:

Construction

Value:

audio_visual; crossmodal_temporal; temporal_binding_or_recalibration

Column 3 — header:

Evidence / status

Value:

review_backed_engineering_entry; implemented

Column 4 — header:

Sources

Value:

vroomen2004temporal, hartcherobrien2011temporal, hirst2020sound, noppeney2018causal

Column 5 — header:

Supported claim

Value:

Audio and video event timing and declared offset are deterministic and inspectable.

## Table 1 — row 18 {#dr-slide-09_appendix_catalog-table-1-data-18-heading}

Column 1 — header:

ID

Value:

audiovisual.mcgurk

Column 2 — header:

Construction

Value:

audio_visual; speech_categorization; categorical_recoding

Column 3 — header:

Evidence / status

Value:

literature_backed_input_dependent_entry; input_required

Column 4 — header:

Sources

Value:

mcgurk1976speech

Column 5 — header:

Supported claim

Value:

The catalog identifies a speech-dependent audiovisual family without claiming implementation.

## Evidence boundary and future expansion {#evidence-boundary-and-future-expansion}

The matrix is intentionally a living registry snapshot. New families may be
added when the package can state a typed parameter contract, deterministic
canonicalization rule, validation invariant, and evidence boundary. Planned or
input-dependent families are not silently promoted because a source exists:
promotion requires an implementable contract, reproducible fixtures where
needed, and an explicit statement of what remains unvalidated. McGurk therefore
remains `input_required` pending a consented or licensed, checksummed speech/
video fixture and a study-ready validation protocol. The candidate-future
catalog is documented separately from this live matrix so that absence is not
misread as a claim that a phenomenon is unknown or unimportant.
