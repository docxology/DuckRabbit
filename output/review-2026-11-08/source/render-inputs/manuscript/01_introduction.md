# Introduction {#sec:introduction}

An illusion stimulus is not the same thing as an illusion report. A stimulus
can be physically specified, generated, encoded, and inspected without
establishing what every observer will see or hear. This distinction is central
to reproducible cognitive science: the physical manipulation must be
auditable, while observer-level effects require a task, calibrated presentation
conditions, randomization, and data.

Visual illusion classifications are useful maps rather than exhaustive or
universally agreed ontologies [@gregory1997visual]. Auditory and audiovisual
families add spectral structure, channel separation, temporal coincidence, and
spatial alignment. The Sound-Induced Flash literature illustrates the boundary
particularly clearly: the physical contrast is a flash paired with different
beep counts, while the perceptual claim requires a listener, timing, and a
response task [@hirst2020sound; @shams2000sifi].

DuckRabbit therefore treats an illusion as a typed stimulus-construction
problem. Each catalog entry declares modality, mechanism, perceptual signature,
cognitive process, requirements, evidence status, output kind, and
implementation status. The taxonomy is orthogonal and explicitly provisional;
it is an engineering index linked to sources, not a replacement for
domain-specific theory.

The release also treats the package as research software rather than as an
unannotated collection of media files. Reproducible computational research
depends on preserving the code, inputs, environment assumptions, and execution
path needed to recreate a result [@sandve2013simple; @wilson2014bestpractices].
The FAIR literature extends that responsibility to algorithms, tools, and
workflows, while software-citation guidance emphasizes identifying the exact
software object and version used [@wilkinson2016fair; @lamprecht2020fairsoftware;
@smith2016software]. DuckRabbit applies these principles narrowly: it makes
the construction pipeline and its generated artifacts citable and inspectable,
but it does not treat metadata quality as evidence of a perceptual effect.

The package is organized around three falsifiable engineering hypotheses:

1. Identical typed requests produce identical canonical arrays and canonical
   digests.
2. Encoders and decoders preserve declared media facts within an explicit
   format-specific tolerance, or verification fails.
3. Parameter manipulations change measurable physical stimulus properties; any
   observer-level interpretation remains a preregistered hypothesis until data
   exist.

This boundary has a nineteenth-century scientific lineage. Fechner's
*Elemente der Psychophysik* formalized the problem of relating controlled
stimulus differences to measured sensation, while Wheatstone's binocular-vision
experiments made the distinction between the physical images delivered to two
eyes and the resulting depth interpretation experimentally explicit
[@fechner1860psychophysics; @wheatstone1838binocular]. Helmholtz's physiological
optics then integrated measurement of the eye, visual geometry, and theories of
perceptual inference [@helmholtz1867optics]. DuckRabbit does not reproduce those
historical experiments; it inherits their methodological lesson that stimulus
conditions and observer inferences must be represented as distinct objects.

That lineage has deeper and less geographically narrow roots. Ptolemy's
ancient *Optics*, Ibn al-Haytham's medieval Arabic optics, and the Mohist
Canon's early Chinese discussions of optics and mechanics show that questions
about image formation, geometry, knowledge, and evidence were developed across
multiple intellectual traditions [@ptolemy1996optics; @alhazen1989optics;
@mozi2023canons; @dai2015chinesescience]. Early-modern discussions sharpened
the distinction between a physical presentation and an inferred percept:
Kircher documented optical display, Berkeley analyzed learned spatial
inference, and the Molyneux--Cheselden record made cross-sensory transfer and
observer testimony explicit problems [@kircher1646light; @berkeley1709vision;
@molyneux2020problem; @cheselden1728sight]. DuckRabbit cites these sources as
historical and methodological precedents, not as evidence that its generated
files reproduce ancient, early-modern, or clinical observations.

The present catalog contains 18 entries, of which
17 are implemented, 0 are planned, and
1 require external fixtures. This status vocabulary
makes breadth visible without claiming that a finite package covers all known
phenomena.
