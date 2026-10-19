# Verification follow-up — October 18, 2026

This follow-up rechecks the [October 17 review](performance-review-2026-10-17.md).
It does not create a release, change the published version/DOIs, or certify the
historical PDF as current. Machine-readable results and source fingerprints are
in [`verification-2026-10-18.json`](verification-2026-10-18.json).

## Current-source verification

Before validation, the executing Python source map and both publication/audit
input maps exactly matched the final October 17 candidate profiling report.
Those measurements remain dated historical measurements, not new timings.
Adding the dated live-scholarship report changes the audit input map; compare
future profiling runs using fresh reports rather than silently reusing it.
Python 3.10/3.12/3.14 results remain the October 17 receipts; the Python 3.15
suite, offline scholarship, lint, and strict release audit were rerun today.
The native sampling permission limitation remains unchanged and no elevation
or attachment to another writer was attempted.

## Live scholarship

The supported network audit ran with an eight-second per-request timeout:

```bash
uv run python scripts/audit_scholarship.py \
  --output output/reports/scholarship_audit-2026-10-18.json --timeout 8
```

All 36 evidence-source records passed their respective checks: **29 DOI
metadata matches and seven DOI-less archival sources**. There were zero
access-controlled, mismatched, unavailable, or unresolved-reachable outcomes.
This is not a claim that all 47 bibliography entries have independently
verified DOIs. Archival reachability is not DOI identity verification, and
neither establishes the generator's observer-level effect. The checked-in
offline evidence snapshot and previous archival reports remain unchanged.

## Current-source PDF attempt

The available sibling template renderer was invoked on all 11 hydrated section
files through `PDFRenderer.render_combined`, with a separate temporary output
directory and review-only project name. The sibling source commit was
`3462d19761cc87d09a0b780ef978fa9efc142723`.
Pandoc conversion and figure-reference validation succeeded (16/16 references,
including the cover). The first XeLaTeX pass failed:

```text
Missing LaTeX package: algorithm2e
LaTeX Error: File `algorithm2e.sty' not found.
```

No current-source PDF was produced or visually certified. Subsequent font,
bibliography, page-layout, and citation-link checks therefore remain
unavailable. No shared TeX installation was modified; the historical PDF and
DOI metadata were not overwritten. HTML/slides were not rebuilt. To retry,
provide a complete template-compatible TeX environment (including
`algorithm2e` and the preamble's configured fonts), run the sibling combined
renderer against `output/manuscript/` into a separate review output, then
render and inspect every page and citation link. A successful package audit
does not replace that gate; this push is unreleased development, not a new
archival publication.

## Shared writer and publication

Local and live remote `main` initially both resolved to
`e16f8ea743ec6ba2ed41412ab7ed2a49bc179caa`; the index was empty.
The actual OS lock was still held even though its metadata recorded a finished
`configure-scope` operation. Finished metadata does not establish idle state
or identify the current owner. Publication must acquire the existing shared
writer protocol, recheck migration/clone-fetch guards, preserve concurrent
edits, and use an ordinary non-forced push. Git publication results are
reported separately; validation alone does not imply a commit or push.

The guarded October 18 attempt waited 120 seconds and timed out before
acquiring the OS lock. A subsequent nonblocking probe still found it held.
No Git mutation was attempted; the index remained empty, all 114 selected
working files retained their expected hashes, and a fresh remote read still
matched the base commit above. No owner was interrupted or inferred from the
finished metadata. Commit/push remains blocked on shared-writer availability;
the timeout is not a publication success receipt.
