# Trace claims to sources and separate offline lineage from live identity

DuckRabbit treats scholarship as a typed evidence graph rather than as a list
of names attached to a generator. The checked-in
[`data/evidence_matrix.json`](../data/evidence_matrix.json) records source
lineage for the live catalog. Each source has a typed role
(`primary_demonstration`, `review_or_synthesis`,
`theoretical_account`, `engineering_basis`, `limitation`, or `input_gap`), a canonical URL or DOI, a
citation key, and an exact statement of what it supports. Each entry also
records an engineering basis, a limitation, and—when implementation is planned
or input-dependent—the missing contract that blocks promotion. The generated audit exposes
the full lineage `source → supported claim → engineering basis → limitation`
and marks planned or `input_required` entries as explicit evidence gaps; a
source citation is never treated as validation of a DuckRabbit implementation.

## Assign source roles without upgrading engineering claims

The audit uses the following source hierarchy:

- primary demonstrations anchor the historical stimulus family or paradigm;
- reviews and syntheses bound terminology, mechanism, and known task
  dependence;
- theoretical accounts are recorded as accounts, not as settled explanations;
- engineering basis is DuckRabbit code and is explicitly separated from the
  scholarly claim.

Representative anchors include Gregory’s non-exhaustive visual classification
([PubMed](https://pubmed.ncbi.nlm.nih.gov/21223901/)), the Sound-Induced Flash
review ([Hirst et al.](https://www.sciencedirect.com/science/article/pii/S0149763420305637)),
the ventriloquist review ([Bruns](https://pmc.ncbi.nlm.nih.gov/articles/PMC6751356/)),
and the primary temporal-ventriloquism study
([Vroomen and de Gelder](https://pubmed.ncbi.nlm.nih.gov/15161383/)). The
matrix additionally covers Ponzo, Kanizsa, Ebbinghaus, apparent motion,
Shepard-like tones, missing fundamentals, tritone and octave constructions,
Müller-Lyer, Poggendorff, sound-induced flash, McGurk, and auditory continuity.

The expanded audit adds Brugger's duck/rabbit study
([PubMed](https://pubmed.ncbi.nlm.nih.gov/10665033/)), the Ponzo synthesis by
Yildiz and colleagues ([PubMed](https://pubmed.ncbi.nlm.nih.gov/34613601/)),
Repp's tritone analysis ([PubMed](https://pubmed.ncbi.nlm.nih.gov/9488887/)),
and the purely temporal ventriloquism study by Hartcher-O'Brien and Alais
([PubMed](https://pubmed.ncbi.nlm.nih.gov/21728465/)). These records sharpen
the supported claim and limitation for each family; they do not validate the
DuckRabbit engineering variants as pixel- or task-identical replications.

The manuscript also cites methodological scholarship that is not assigned to a
single illusion entry. Sandve et al. and Wilson et al. motivate the separation
of executable inputs, procedures, dependencies, and tests from final media
files ([Sandve et al.](https://doi.org/10.1371/journal.pcbi.1003285), [Wilson
et al.](https://doi.org/10.1371/journal.pbio.1001745)). The FAIR literature
extends findability, accessibility, interoperability, and reusability to
algorithms and research software ([Wilkinson et al.](https://doi.org/10.1038/sdata.2016.18),
[Lamprecht et al.](https://doi.org/10.3233/DS-190026)), while the FORCE11
software-citation principles motivate version-specific citation of the package
itself ([Smith et al.](https://peerj.com/articles/cs-86/)). These references
support the release and provenance method; they do not elevate any catalog row
above its recorded source-supported claim.

Zöllner and auditory-continuity engineering contracts are bounded by direct primary sources. Earle
and Maskell describe long vertical lines crossed by short oblique lines in the
Zöllner--Judd family and explicitly discuss competing mechanistic accounts
([Perception](https://journals.sagepub.com/doi/10.1068/p241397)). Riecke and
colleagues distinguish sensory and decisional contributions in auditory
continuity using interrupted sounds and masking context
([PubMed](https://pubmed.ncbi.nlm.nih.gov/21276844/)). DuckRabbit uses these
papers to justify stimulus-family parameters and limitations, not to claim
that a rendered file reproduces their observer results.

For apparent motion, the historical Wertheimer record is paired with Sekuler's
DOI-indexed review of the 1912 monograph
([Perception](https://journals.sagepub.com/doi/10.1068/p251243)). This preserves
the foundational primary source while giving the audit a modern, resolvable
review anchor for the distinction between successive physical events and
observer-level apparent motion.

## Situate stimulus methods in worldwide historical scholarship

The bibliography now begins well before the nineteenth-century laboratory
tradition and treats the history of visual science as geographically distributed
rather than as a single European progression. Ptolemy's *Optics* provides an
ancient Greek source on visual perception and mathematical visual theory
[@ptolemy1996optics]. Ibn al-Haytham's Arabic *Book of Optics*, represented by
Sabra's translation and commentary, supplies a major medieval Islamicate source
on direct vision and image formation [@alhazen1989optics]. The Mohist Canon's
Warring States Chinese discussions of knowledge, geometry, mechanics, and optics
are represented through a modern text-and-translation study; a broader history
of Chinese science situates those optical records within a longer non-European
technical tradition [@mozi2023canons; @dai2015chinesescience].

Early-modern sources add distinct questions about optical display, visual
inference, and cross-sensory knowledge. Kircher's 1646 *Ars Magna Lucis et
Umbrae* is preserved here as a digitized record of early-modern work on light,
shadow, and optical display [@kircher1646light]. Berkeley's 1709 *Essay towards
a New Theory of Vision* makes visual distance and spatial interpretation an
explicit philosophical problem [@berkeley1709vision]. The Molyneux question,
first posed in 1688, asks whether tactilely learned shape distinctions transfer
to vision; Cheselden's 1728 case report became an early clinical observation
in that debate [@molyneux2020problem; @cheselden1728sight]. These sources make
the observer boundary historically visible: a stimulus or physical intervention
can be documented without treating an individual report as a property of the
stimulus file.

The nineteenth-century lineage remains important rather than being replaced.
Fechner's *Elemente der Psychophysik* (1860) anchors the measurement problem;
Wheatstone's 1838 binocular-vision paper anchors controlled differences between
the two retinal images; and Helmholtz's 1867 *Handbuch der physiologischen Optik*
connects optical measurement with theories of visual inference. Zöllner's 1860
primary report and Müller-Lyer's 1889 report anchor two geometrical-illusion
families, while Stumpf's 1883 *Tonpsychologie* broadens the historical record to
auditory psychology. Oppel's 1855 work is represented through a modern
translation and commentary [@fechner1860psychophysics;
@wheatstone1838binocular; @helmholtz1867optics;
@zoellner1860pseudoscopy; @mullerlyer1889optical;
@stumpf1883tonpsychology; @wade2017oppel]. These sources are historical anchors
for stimulus families and methods, not evidence that a modern generated
artifact reproduces their original apparatus, observers, or results. The set
is an intentionally expanding worldwide foundation, not an exhaustive history
of every culture's visual, auditory, or perceptual scholarship.

## Keep physical, source-supported, synthetic, and observer claims distinct

`canonical_stimulus`, `physical_metric`, and `encoded_media` describe facts
that can be derived from DuckRabbit artifacts and manifests. `source_supported`
describes the narrow statement supported by a cited source.
`synthetic_model_output` describes the serialized output of DuckRabbit's
hand-specified, no-training-data feature observer; it is not human data.
`observer_hypothesis` and `validated_observer_effect` are reserved for study
designs and future human data. A source record does not turn an engineering
approximation into a pixel-identical historical replication, and a deterministic
metric or synthetic model output does not turn a construction into a universal
perceptual effect.

## Separate offline lineage from live identity

The source audit is reproducible offline: `scripts/validate_scholarship.py`
checks matrix schema, source URL/DOI shape, citation identifiers, exact taxonomy
source edges, source roles and ordered literal BibTeX titles. Author order and
year are checked when the matrix supplies those fields; absent fields are not
invented. Unsupported BibTeX macros fail as uncertain rather than being erased.
`scripts/audit_scholarship.py` is an explicit network follow-up; DOI metadata
matches are distinct from reachable-but-unresolved, access-controlled,
mismatched and unavailable records. HEAD success for a DOI-less archive never
establishes bibliographic identity. The command fails until all identities are
verified; a dated report is evidence of observations, not automatic clearance.
Ordinary tests use the checked-in snapshot and no network. `snapshot_validated`
means offline lineage passed, not that a resolver or full source was inspected.

### Audit roster and retained unresolved observations

The native network command covers the **36 evidence-source records** for
**18 catalog entries**; the implemented generator registry has **17 entries**.
The manuscript bibliography has **47 references**, so its **11 additional
references** require a separate review rather than being silently omitted or
described as native-command coverage. The matrix, taxonomy/registry, and
`docs/manuscript/references.bib` are the source authorities for these distinct
inventories; figure counts are unrelated and live in [visualization](visualization.md).

The [dated November audit](audit-2026-11-08.md) records observations across the
whole bibliography: 35 DOI identities matched retained primary metadata, ten
reachable archival records remained unresolved, one retained an author-name
mismatch, and one failed TLS validation. These are **historical observations**,
not a fresh live audit of subsequent source. The retained
[prior bundle](../output/review-2026-11-08/) includes native and adjunct evidence;
the adjunct re-evaluation reused observed metadata, not a second network visit.
Those unresolved identities remain release blockers unless cleared by new
identity evidence; neither refreshed graphics nor offline replay clears them.
The [current visual-review bundle](../output/visual-review-2026-11-08/) requires
its own source binding and reports; graphics cannot substitute for live identity.

Ordered author comparison includes exact corporate author names. A record with
both a collective `name` and person `family`/`given` fields is ambiguous and
fails. Publisher attribution, including FORCE11 collective authorship, must not
be replaced by an individual contributor merely to simplify rendering.

## Inspect generated claim-to-source lineage

The generated `output/data/evidence_source_audit_table.{md,json}` records each
source tier, DOI/URL, exact supported claim, and verification status, followed
by entry-level engineering and limitation rows. The generated caption audit
and claim ledger apply the same rule to figures and tables: deterministic
construction facts are labeled as such, source-supported claims remain narrow,
and observer hypotheses are marked as future study targets. No figure caption
is permitted to imply a universal observer effect or participant result.

The explicit network command writes `output/reports/scholarship_audit.json`
with separate verified/reachable counts, HTTP observations, source roles,
catalog entries and evidence gaps. Responses 403, 401 and 405 mean
access-controlled, not verified or confirmed reachable content. Successful
transport alone cannot establish identity or support a scientific claim.

## Preserve open fixture, evidence, and observer-study gates

The taxonomy is provisional and orthogonal. Zöllner and auditory continuity
now have deterministic engineering contracts and are marked implemented, while
their output still supports only physical stimulus claims. McGurk remains
`input_required` until a checksummed, licensed or consented speech/audio-video
fixture and a perceptual validation contract exist. These are evidence and
engineering gates, not claims that the associated phenomena are unreal.
