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
|---------------|---------------|---------------|---------------|---------------|
| `\breakseq{visual.duck\_rabbit}`{=latex} | visual; ambiguity; bistability | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{brugger1999duckrabbit,}`{=latex} `\breakseq{gregory1997visual}`{=latex} | The entry instantiates a controllable ambiguous-figure stimulus family. |
| `\breakseq{visual.simultaneous\_contrast}`{=latex} | visual; `\breakseq{contrast\_and\_context;}`{=latex} `\breakseq{contrast\_distortion}`{=latex} | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{gregory1997visual}`{=latex} | The physical center patches are matched while surround luminance differs. |
| `\breakseq{visual.apparent\_motion}`{=latex} | visual; `\breakseq{temporal\_motion;}`{=latex} `\breakseq{illusory\_motion}`{=latex} | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{wertheimer1912motion,}`{=latex} `\breakseq{sekuler1996wertheimer}`{=latex} | The sequence contains controlled successive spatial events. |
| `\breakseq{audio.shepard\_tone}`{=latex} | auditory; `\breakseq{spectral\_harmonic;}`{=latex} continuity | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{shepard1984scale}`{=latex} | The audio contains octave-related partials with controlled sweep parameters. |
| `\breakseq{audio.missing\_fundamental}`{=latex} | auditory; `\breakseq{spectral\_harmonic;}`{=latex} filling_in | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{zatorre2005missing}`{=latex} | The nominal fundamental component is absent from the canonical spectrum. |
| `\breakseq{audiovisual.sound\_induced\_flash}`{=latex} | `\breakseq{audio\_visual;}`{=latex} `\breakseq{crossmodal\_temporal;}`{=latex} `\breakseq{fusion\_or\_fission}`{=latex} | `\breakseq{review\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{shams2000sifi,}`{=latex} `\breakseq{hirst2020sound}`{=latex} | The declared beep/flash event counts and offsets are physically encoded. |
| `\breakseq{audiovisual.ventriloquist}`{=latex} | `\breakseq{audio\_visual;}`{=latex} `\breakseq{crossmodal\_spatial;}`{=latex} `\breakseq{spatial\_capture}`{=latex} | `\breakseq{review\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{bruns2019ventriloquist,}`{=latex} `\breakseq{noppeney2018causal}`{=latex} | The audio and visual channels carry a declared spatial discrepancy. |
| `\breakseq{visual.muller\_lyer}`{=latex} | visual; `\breakseq{geometric\_alignment;}`{=latex} `\breakseq{geometric\_distortion}`{=latex} | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{gregory1997visual,}`{=latex} `\breakseq{howe2005muller}`{=latex} | The two bar lengths are equal in the canonical raster while wing geometry varies. |
| `\breakseq{visual.poggendorff}`{=latex} | visual; `\breakseq{geometric\_alignment;}`{=latex} `\breakseq{geometric\_distortion}`{=latex} | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{gregory1997visual,}`{=latex} `\breakseq{morgan1999poggendorff}`{=latex} | The occluder and diagonal continuation are generated from explicit geometry. |
| visual.ponzo | visual; `\breakseq{geometric\_alignment;}`{=latex} `\breakseq{geometric\_distortion}`{=latex} | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{fisher1967ponzo,}`{=latex} `\breakseq{yildiz2022ponzo}`{=latex} | Target bars are physically equal and rails converge toward a vanishing region. |
| `\breakseq{visual.kanizsa\_triangle}`{=latex} | visual; `\breakseq{contrast\_and\_context,}`{=latex} `\breakseq{geometric\_alignment;}`{=latex} filling_in | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{kanizsa1976contours,}`{=latex} `\breakseq{wagemans2012gestalt}`{=latex} | The image contains incomplete inducers with no explicitly drawn triangle edge. |
| `\breakseq{visual.ebbinghaus}`{=latex} | visual; `\breakseq{contrast\_and\_context,}`{=latex} `\breakseq{geometric\_alignment;}`{=latex} `\breakseq{geometric\_distortion}`{=latex} | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{mruczek2015ebbinghaus,}`{=latex} `\breakseq{weintraub1979ebbinghaus}`{=latex} | Central target geometry is held equal while contextual circle geometry differs. |
| `\breakseq{visual.zollner}`{=latex} | visual; `\breakseq{geometric\_alignment;}`{=latex} `\breakseq{geometric\_distortion}`{=latex} | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{zoellner1860pseudoscopy,}`{=latex} `\breakseq{earle1995zollner,}`{=latex} `\breakseq{gregory1997visual}`{=latex} | The entry instantiates a controlled crossing-line orientation stimulus family. |
| `\breakseq{audio.tritone\_paradox}`{=latex} | auditory; `\breakseq{spectral\_harmonic;}`{=latex} `\breakseq{categorical\_recoding}`{=latex} | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{deutsch1986tritone,}`{=latex} `\breakseq{repp1997tritone}`{=latex} | The canonical pair has an explicit half-octave frequency relation. |
| `\breakseq{audio.octave\_illusion}`{=latex} | auditory; `\breakseq{stream\_segregation;}`{=latex} `\breakseq{fusion\_or\_fission}`{=latex} | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{deutsch1974octave}`{=latex} | The two channels receive alternating octave-related tones. |
| `\breakseq{audio.auditory\_continuity}`{=latex} | auditory; `\breakseq{stream\_segregation;}`{=latex} continuity | `\breakseq{literature\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{warren1970continuity,}`{=latex} `\breakseq{riecke2011continuity}`{=latex} | The canonical audio contains a reproducible interruption interval and masker family. |
| `\breakseq{audiovisual.temporal\_ventriloquism}`{=latex} | `\breakseq{audio\_visual;}`{=latex} `\breakseq{crossmodal\_temporal;}`{=latex} `\breakseq{temporal\_binding\_or\_recalibration}`{=latex} | `\breakseq{review\_backed\_engineering\_entry;}`{=latex} implemented | `\breakseq{vroomen2004temporal,}`{=latex} `\breakseq{hartcherobrien2011temporal,}`{=latex} `\breakseq{hirst2020sound,}`{=latex} `\breakseq{noppeney2018causal}`{=latex} | Audio and video event timing and declared offset are deterministic and inspectable. |
| `\breakseq{audiovisual.mcgurk}`{=latex} | `\breakseq{audio\_visual;}`{=latex} `\breakseq{speech\_categorization;}`{=latex} `\breakseq{categorical\_recoding}`{=latex} | `\breakseq{literature\_backed\_input\_dependent\_entry;}`{=latex} `\breakseq{input\_required}`{=latex} | `\breakseq{mcgurk1976speech}`{=latex} | The catalog identifies a speech-dependent audiovisual family without claiming `\breakseq{implementation.}`{=latex} |

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
