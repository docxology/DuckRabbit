# Discussion and Conclusion {#sec:discussion}

DuckRabbit's principal result is a reproducibility boundary rather than a new
psychophysical finding. The same typed request can be regenerated, hashed,
encoded, decoded, and audited, while the evidence graph and observer layer
remain explicit about what the package cannot infer. This makes the atlas
useful for stimulus construction, source comparison, and preregistration
without treating a rendered image or sound as behavioral evidence.

The scholarly contribution is correspondingly modest but operational. Rather
than flattening visual, auditory, temporal, and multisensory families into a
single “illusion” label, the package keeps mechanism, perceptual signature,
requirements, evidence role, engineering basis, and implementation status
separate. A primary demonstration, a review, a theoretical account, and a
source describing the DuckRabbit implementation answer different questions.
The appendix and source-data sidecars make those distinctions inspectable at
the same time as the generated media.

The work is best understood as a research-software artifact with a bounded
methods contribution. Its novelty claim is not that it discovers a new illusion
or resolves a disputed mechanism; it is that a heterogeneous stimulus catalog
can be represented as typed, reproducible, source-linked, and release-audited
objects. This framing is consistent with software-citation and FAIR guidance,
which treats versioned software, metadata, provenance, and reuse conditions as
part of the research record [@smith2016software; @wilkinson2016fair;
@lamprecht2020fairsoftware].

The release is authored by Daniel Ari Friedman of the Active Inference
Institute, and its intended public home is
[the DuckRabbit public GitHub repository](https://github.com/docxology/DuckRabbit).
That repository statement is part of the software's citation identity; until
the external handoff occurs, the private sidecar and its generated bundle are
the authoritative release candidate.

## Conclusion {#sec:conclusion}

DuckRabbit v0.5.0 turns multimodal illusion generation into an auditable typed
pipeline. A request produces a canonical artifact, objective metrics, optional
delivery files, decoded inspection, and a versioned evidence-bounded manifest.
The catalog now records not only what is implemented, but also what the
literature supports and what remains unvalidated.

The main scientific contribution is a boundary: deterministic stimulus facts
are reproducible software outputs, while perceptual effects are hypotheses that
require observer conditions and data. This boundary permits broad generator
coverage without overclaiming. Future additions should contribute a typed
parameter contract, a literature record, an engineering-fidelity statement,
objective invariants, generated documentation, and tests before entering the
implemented registry. Promotion is a release decision about software
readiness, not a verdict on whether a perceptual phenomenon is real.

The synthetic-psychophysics layer extends this boundary without crossing it. A
transparent feature observer makes model inputs, weights, calibration, and
output hashes inspectable, so the full orchestration can be tested today. Its
small curve is a diagnostic of that specified model, not evidence that humans
share its feature map or response function. Empirical observer work remains a
separate, ethically and methodologically governed stage.
