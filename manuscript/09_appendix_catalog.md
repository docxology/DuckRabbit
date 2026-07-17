# Appendix A. Complete catalog, source tiers, and evidence/implementation boundaries {#sec:appendix_catalog}

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
{{CATALOG_TABLE_ROWS}}

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
