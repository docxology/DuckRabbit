# Publication Atlas, Caption Contract, and Scholarship Audit {#sec:publication_audit}

The publication layer is generated from the same typed package state as the
stimuli. It contains {{PUBLICATION_FIGURES}} scientific figures, {{PUBLICATION_TABLES}}
machine-readable tables, and a separately provenance-recorded editorial cover.
The cover is an illustration of the project's subject and methods aesthetic; it
is not a stimulus, a participant result, or evidence of a perceptual effect.

## Claim-level visualization

![{{FIGURE_ALT_CLAIM_BOUNDARY}}](../output/figures/claim_boundary.png){#fig:claim_boundary}

{{FIGURE_CAPTION_CLAIM_BOUNDARY}}

The claim boundary in [@fig:claim_boundary] is a typed epistemic interface. A
canonical digest identifies a deterministic buffer; objective metrics identify
properties of that buffer; encoded-media verification identifies facts of the
delivered file. A future observer hypothesis is a different object with its
own protocol, estimand, and uncertainty interval.

## Scholarship map and lineage

![{{FIGURE_ALT_SCHOLARSHIP_MAP}}](../output/figures/scholarship_map.png){#fig:scholarship_map}

{{FIGURE_CAPTION_SCHOLARSHIP_MAP}}

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
than citing an undifferentiated project name [@wilkinson2016fair;
@smith2016software]. Accordingly, the release includes `CITATION.cff`,
CodeMeta, Zenodo metadata, versioned manifests, source-data sidecars, and
resolver-linked bibliography entries. These improve discoverability and
attribution; they do not increase the evidential level of any perceptual claim.

The intended public software identity is explicit: DuckRabbit will be released
at the [DuckRabbit public GitHub repository](https://github.com/docxology/DuckRabbit)
under the authorship of Daniel Ari Friedman, Active Inference Institute. The
repository URL identifies the future citable software object; it is not a claim
that the private sidecar has already been publicly mirrored.

## Formal traceability and objective metrics

![{{FIGURE_ALT_FORMALISM_TRACEABILITY}}](../output/figures/formalism_traceability.png){#fig:formalism_traceability}

{{FIGURE_CAPTION_FORMALISM_TRACEABILITY}}

The formalism registry [@fig:formalism_traceability] links equations
[@eq:typed_request; @eq:canonical_generation; @eq:canonical_digest; @eq:encoding_verification; @eq:clock_definition; @eq:objective_statistics; @eq:temporal_spectral_metrics; @eq:observer_estimand; @eq:synthetic_observer]
to implementation modules, tests, and figures. The contract is intentionally
auditable: equation labels point to code-owned records, while empirical claims
remain outside the generator's authority.

![{{FIGURE_ALT_METRICS_DASHBOARD}}](../output/figures/metrics_dashboard.png){#fig:metrics_dashboard}

{{FIGURE_CAPTION_METRICS_DASHBOARD}}

The metrics dashboard [@fig:metrics_dashboard] reports units, computation
version, and canonical digests. Luminance statistics are normalized raster
properties; RMS and peak are normalized-amplitude properties; spectral values
are in Hz; frame deltas are normalized pixel differences; and synchronization
offsets are in milliseconds. None is a psychophysical score.

![{{FIGURE_ALT_PARAMETER_DOMAINS}}](../output/figures/parameter_domains.png){#fig:parameter_domains}

{{FIGURE_CAPTION_PARAMETER_DOMAINS}}

The domain map [@fig:parameter_domains] is a validation visualization. Bounds
are chosen to prevent malformed media and unsafe encodings, not to predict a
viewer, listener, or participant's sensitivity.

## Observer-design boundary

![{{FIGURE_ALT_OBSERVER_PROTOCOL}}](../output/figures/observer_protocol.png){#fig:observer_protocol}

{{FIGURE_CAPTION_OBSERVER_PROTOCOL}}

The observer scaffold [@fig:observer_protocol] starts with a pseudonymous trial
identity and deterministic randomization, binds the stimulus manifest and
encoded hash, records a typed response or missingness state, and ends at a
preregistered estimand. The companion diagnostic
[@fig:synthetic_psychophysics] is a deterministic, hand-specified feature
observer with `training_data=none` and `human_data=false`; it is not a
pretrained vision model, psychometric function, or participant result. Human
psychophysics remains a future evidence layer requiring calibrated playback,
consent, preregistration, and observed responses.

## Generated audit tables

| Figure / claim level | Source and evidence | Controls and objective facts | Limitations, boundary, and accessibility |
|---|---|---|---|
{{CAPTION_AUDIT_TABLE_ROWS}}

: Code-owned caption, source-data, and accessibility audit. {#tbl:caption_audit}

| Key | Record and citations | DOI and URL | Verification | Supported claim / engineering / limitation |
|---|---|---|---|---|
{{EVIDENCE_AUDIT_TABLE_ROWS}}

: Source-tiered evidence, DOI/URL verification, exact supported claims, engineering departures, limitations, and explicit planned/input-required gaps. {#tbl:evidence_audit}

| Label | Definition and symbols | Implementation and tests | Figures and claim level |
|---|---|---|---|
{{FORMALISM_TABLE_ROWS}}

: Formal equation-to-code traceability. {#tbl:formalism}

| Claim ID | Claim and level | Basis | Lineage and limitation |
|---|---|---|---|
{{CLAIM_LEDGER_TABLE_ROWS}}

: Claim ledger separating code-derived facts, scholarship, engineering departures, limitations, scope, and observer hypotheses. {#tbl:claim_ledger}

The source-tiered evidence table [@tbl:evidence_audit], caption audit
[@tbl:caption_audit], formalism registry [@tbl:formalism], and claim ledger
[@tbl:claim_ledger] are generated sidecars. They provide a publication appendix
without duplicating mutable counts or silently converting literature statements
into package results.

The publication artifacts have two distinct provenance boundaries. Scientific
figures are deterministic PNG renders whose source-data JSON and SHA-256
digests are checked against the code-owned registry. The cover is an editorial
charcoal illustration: its selected candidate, prompt fingerprint, source
asset digest, dimensions, variants, and provenance boundary are recorded in
`output/reports/cover_visualization.json`. Neither boundary is an observer
result, and neither substitutes for display calibration or behavioral data.

The publication audit additionally resolves every formalism edge to a real
package module, test file, manuscript equation label, and registered figure.
Figure source-data sidecars use a versioned schema with figure identity,
generator, seed, and nested data payload; the registry verifies this identity
and hash independently of the renderer. This makes a visually plausible but
stale or relabeled figure fail the same provenance gate as a tampered stimulus.
