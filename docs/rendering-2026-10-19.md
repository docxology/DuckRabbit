# Current-source rendering review — October 19, 2026

The [source closeout](closeout-2026-10-19.md) was committed and pushed as
`5c25ffc31999c256b9d28d83942c41bb0fad33a5`; remote equality and a clean
worktree were verified under GitVault repository-specific admission. This
follow-up builds that source for **digital manuscript review**, not a new
release or archival/print-accessibility certification.

## Build and identity

The current-source PDF, source/tool fingerprints, declared overlay, compiler
and bibliography logs, and citation QA are kept separately under
[`output/review-2026-10-19/`](../output/review-2026-10-19/). The historical
`output/pdf/DuckRabbit_combined.pdf`, version 0.5.0 metadata, and published DOI
identities were not overwritten. The review title page explicitly identifies
the date, source commit, unreleased status, and distinction from that archive.

The independent isolated TeX helper handoff was read before use. Its read-only
integrity verifier passed **57 bindings with zero errors**, both before and
after the build. Pinned TeX Live 2026 packages and JuliaMono faces came from
the verified kit; no installation, system symlink, home configuration, or
project-source font change was made.

The renderer was a frozen copy of the available sibling infrastructure. Its
HEAD was **`a19556c54f98ffc7a29eed664a4117e018064166`**, with uncommitted
changes; the full runtime/resource hash map in `build-receipt.json`, not HEAD
alone, identifies this snapshot. It is **not** the earlier October 18 renderer
`3462d19761cc87d09a0b780ef978fa9efc142723`. The frozen map was checked again
after rendering. Reproduction requires that matching external snapshot; this
repository does not vendor or certify the moving sibling checkout.
The renderer environment used CPython **3.14.8**; this is separate from the
CPython **3.15.0** package tests and historical profiling measurements.

## Declared review overlay

Current generated manuscript, figure, and data inputs were copied to isolated
staging, hashed, and checked against the canonical source before packaging.
Only the following review-overlay changes were applied:

1. Resolve the absent absolute JuliaMono directory to the exact pinned faces
   in the isolated kit, without a system symlink.
2. Mark the title-page subtitle/date as an unreleased current-source review.
3. Add discretionary wrapping to a long architecture path, evidence IDs, and
   source keys in the audit tables; use “evidence and implementation” rather
   than an unbreakable slash phrase in the appendix heading.

The exact generated `review-overlay.patch` is retained. No scientific values,
canonical stimuli, metric algorithms, evidence records, or participant claims
were changed. Figure assets were copied unchanged to the renderer-expected
review output layout. An initial isolated-layout attempt lacked the cover at
that relative location and failed in `xdvipdfmx`; that attempt is not counted
as successful PDF validation.

## Reproduction boundary

With the verified kit and matching frozen renderer snapshot available:

1. Copy current `output/manuscript`, `output/figures`, and `output/data` to an
   isolated project tree; verify the receipt input hashes before adaptation.
2. Apply `review-overlay.patch` to that copy only, resolving the font directory
   to the same hash-verified kit fonts. Keep the review identity explicit.
3. Provide unchanged figure assets under the review output adjacent to `pdf/`;
   this includes the cover, not only the 15 scientific panels.
4. Prefix the matching renderer Python command with the helper-provided
   `with-tex-env.sh`. Invoke `PDFRenderer.render_combined` on the 11 ordered
   hydrated section files, using separate review output and figure directories.
   The existing renderer uses XeLaTeX with `-no-shell-escape` and BibTeX.
5. Require successful completion, recheck source/renderer/kit hashes, render
   every page to PNG, and rerun citation destinations and visual QA. Do not
   treat a partial PDF or the dependency-only helper probes as a manuscript
   success.

## Machine checks

The completed review build has **61 pages**. Strict PDF parsing found:

- 47 cited bibliography keys, each with a matching bibliography entry and
  citation destination;
- 146 citation links within 225 resolved internal links;
- 73 external URI annotations with supported schemes;
- zero broken internal destinations, missing bibliography keys, empty pages,
  unresolved tokens, replacement-glyph markers, or final undefined/missing-
  character compiler warnings; and
- **zero final overfull boxes**, after the declared wrapping corrections.

External URI presence is not a fresh network or DOI-identity check. The dated
October 18 network audit separately verified 29 DOI metadata matches and seven
DOI-less archival sources among 36 evidence sources; it did not independently
verify a DOI for every bibliography entry.

## Visual assessment and remaining polish

The first successful build was inspected page-by-page in three independent
ranges covering all 61 pages. Final raster comparison identifies which pages
changed after wrapping; unchanged page images retain their original inspection
coverage, while changed pages receive a separate final review. The individual
reports and exact coverage/hash maps accompany the review artifact.
Specifically, 49 final page PNGs are byte-identical to the individually
inspected first build; all 12 changed pages were independently inspected in
the final round. The final reviewer also rechecked five small-annotation
pages, verified the displayed contents/page targets, and confirmed the margin
and gutter fixes. No new high/moderate layout defect was observed; the
unchanged readability findings below were not declared fixed.

This is a digital-review artifact, **not a claim of flawless publication
layout**. Small figure annotations (especially the catalog, visual-gallery,
audio, metrics, and parameter panels) require magnification; full-resolution
assets and source-data companions remain in `output/figures` and `output/data`.
Narrow table identifiers can fragment awkwardly. Figure floats interrupt some
explanatory paragraphs, and the Lamprecht bibliography entry crosses a page
boundary after its author list. These remain publication-polish tasks, rather
than being silently cleared by the successful compiler or citation checks.
Tagged-PDF accessibility, print legibility, HTML, and slides were not certified.

Two non-layout warnings remain explicitly disclosed:

- `siunitx` 3.6.4 removed the preamble option `binary-units`. The option was
  retained so the warning remains visible. No siunitx quantity/unit commands
  occur in the manuscript body, and this build makes no binary-unit formatting
  claim; the package metrics and units were not recalculated by TeX.
- BibTeX warns that its selected style cannot use both `volume` and `number`
  for `ptolemy1996optics`. The original source metadata fields were preserved;
  citation/reference linkage still resolves. A future editorial pass should
  select an appropriate series/volume/issue presentation rather than delete
  source information merely to suppress a warning.
