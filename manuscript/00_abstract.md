# Abstract {#sec:abstract}

DuckRabbit is typed, deterministic research software by Daniel Ari Friedman
(Active Inference Institute) for constructing reproducible visual, auditory,
temporal, and audiovisual stimulus families. The intended public release will
be available at the following repository:

`https://github.com/docxology/DuckRabbit`

DuckRabbit is released under the MIT License.

Its basic unit is an immutable request containing an illusion identifier,
validated parameters, a seed, and an encoding specification. The request yields
a canonical artifact, objective media measurements, and a versioned provenance
manifest before any delivery codec is selected. This separation makes the
stimulus a testable computational object while reserving claims about
perception for controlled observer protocols.

The release situates its engineering choices within a deliberately broad
historical foundation spanning Greek, Arabic/Islamicate, Chinese, and
early-modern work on optics, visual inference, and cross-sensory knowledge,
alongside later psychophysics and illusion research. These traditions motivate
questions about construction, observation, and evidence; they are contextual
precedents, not evidence that a generated file reproduces an ancient,
early-modern, or clinical observation.

Version {{PACKAGE_VERSION}} contains {{IMPLEMENTED_GENERATORS}} implemented
generators and {{CATALOG_ENTRIES}} catalog entries, supported by
{{SCHOLARLY_SOURCES}} source records and {{EVIDENCE_RECORDS}} evidence records
in a checked-in audit snapshot. The package generates
{{PUBLICATION_FIGURES}} publication figures and {{PUBLICATION_TABLES}}
machine-derived tables from the live registry. It also provides a typed
observer-study harness and a transparent synthetic diagnostic: a
hand-specified feature observer with serialized weights, temperature, analytic
calibration, and `human_data=false`. {{OBSERVER_DATA_STATUS}}

DuckRabbit verifies physical stimulus properties, media round trips, hashes,
timing, and declared provenance. It does not infer a universal percept, effect
size, or cross-device perceptual equivalence from a generated artifact. Its
contribution is a reproducibility and epistemic boundary: source-backed family
descriptions, deterministic media facts, and future observer hypotheses remain
different typed records rather than being collapsed into one claim. DuckRabbit
is software for reproducible stimulus construction and audit, not a claim that
a generated file alone produces a universal perceptual effect.
