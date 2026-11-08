# Appendix A. Complete catalog, source tiers, and evidence and implementation boundaries {#sec:appendix_catalog}

This appendix is the authoritative rendered snapshot of DuckRabbit's live
catalog. It is generated from the taxonomy registry and evidence matrix during
the publication build; the table is not hand-maintained. The snapshot records
the package's current scope, not a claim to enumerate every illusion described
in the literature.

## How to read the matrix

Each row identifies a registered illusion family and separates five questions
that are often collapsed in informal catalogs:

1. What modality, mechanism, and signature does the package assign to the construction?
2. What evidence and implementation status does the checked-in record support?
3. Which sources support the exact statement written in the row?
4. What physical claim is supported by the row?
5. What full source role, resolver, DOI status, and claim level are retained in the machine-readable record?

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

| ID | Construction | Evidence / status | Sources | Supported claim |
|---|---|---|---|---|
| visual.duck\_rabbit | visual; ambiguity; bistability | literature\_backed\_engineering\_entry; implemented | brugger1999duckrabbit, gregory1997visual | The entry instantiates a controllable ambiguous-figure stimulus family. |
| visual.simultaneous\_contrast | visual; contrast\_and\_context; contrast\_distortion | literature\_backed\_engineering\_entry; implemented | gregory1997visual | The physical center patches are matched while surround luminance differs. |
| visual.apparent\_motion | visual; temporal\_motion; illusory\_motion | literature\_backed\_engineering\_entry; implemented | wertheimer1912motion, sekuler1996wertheimer | The sequence contains controlled successive spatial events. |
| audio.shepard\_tone | auditory; spectral\_harmonic; continuity | literature\_backed\_engineering\_entry; implemented | shepard1984scale | The audio contains octave-related partials with controlled sweep parameters. |
| audio.missing\_fundamental | auditory; spectral\_harmonic; filling\_in | literature\_backed\_engineering\_entry; implemented | zatorre2005missing | The nominal fundamental component is absent from the canonical spectrum. |
| audiovisual.sound\_induced\_flash | audio_visual; crossmodal\_temporal; fusion\_or\_fission | review\_backed\_engineering\_entry; implemented | shams2000sifi, hirst2020sound | The declared beep/flash event counts and offsets are physically encoded. |
| audiovisual.ventriloquist | audio_visual; crossmodal\_spatial; spatial\_capture | review\_backed\_engineering\_entry; implemented | bruns2019ventriloquist, noppeney2018causal | The audio and visual channels carry a declared spatial discrepancy. |
| visual.muller\_lyer | visual; geometric\_alignment; geometric\_distortion | literature\_backed\_engineering\_entry; implemented | gregory1997visual, howe2005muller | The two bar lengths are equal in the canonical raster while wing geometry varies. |
| visual.poggendorff | visual; geometric\_alignment; geometric\_distortion | literature\_backed\_engineering\_entry; implemented | gregory1997visual, morgan1999poggendorff | The occluder and diagonal continuation are generated from explicit geometry. |
| visual.ponzo | visual; geometric\_alignment; geometric\_distortion | literature\_backed\_engineering\_entry; implemented | fisher1967ponzo, yildiz2022ponzo | Target bars are physically equal and rails converge toward a vanishing region. |
| visual.kanizsa\_triangle | visual; contrast\_and\_context, geometric\_alignment; filling\_in | literature\_backed\_engineering\_entry; implemented | kanizsa1976contours, wagemans2012gestalt | The image contains incomplete inducers with no explicitly drawn triangle edge. |
| visual.ebbinghaus | visual; contrast\_and\_context, geometric\_alignment; geometric\_distortion | literature\_backed\_engineering\_entry; implemented | mruczek2015ebbinghaus, weintraub1979ebbinghaus | Central target geometry is held equal while contextual circle geometry differs. |
| visual.zollner | visual; geometric\_alignment; geometric\_distortion | literature\_backed\_engineering\_entry; implemented | zoellner1860pseudoscopy, earle1995zollner, gregory1997visual | The entry instantiates a controlled crossing-line orientation stimulus family. |
| audio.tritone\_paradox | auditory; spectral\_harmonic; categorical\_recoding | literature\_backed\_engineering\_entry; implemented | deutsch1986tritone, repp1997tritone | The canonical pair has an explicit half-octave frequency relation. |
| audio.octave\_illusion | auditory; stream\_segregation; fusion\_or\_fission | literature\_backed\_engineering\_entry; implemented | deutsch1974octave | The two channels receive alternating octave-related tones. |
| audio.auditory\_continuity | auditory; stream\_segregation; continuity | literature\_backed\_engineering\_entry; implemented | warren1970continuity, riecke2011continuity | The canonical audio contains a reproducible interruption interval and masker family. |
| audiovisual.temporal\_ventriloquism | audio_visual; crossmodal\_temporal; temporal\_binding\_or\_recalibration | review\_backed\_engineering\_entry; implemented | vroomen2004temporal, hartcherobrien2011temporal, hirst2020sound, noppeney2018causal | Audio and video event timing and declared offset are deterministic and inspectable. |
| audiovisual.mcgurk | audio_visual; speech\_categorization; categorical\_recoding | literature\_backed\_input\_dependent\_entry; input\_required | mcgurk1976speech | The catalog identifies a speech-dependent audiovisual family without claiming implementation. |

: DuckRabbit catalog entries, source tiers, and evidence/implementation boundaries. {#tbl:catalog}

## Evidence boundary and future expansion

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
