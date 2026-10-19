# DuckRabbit current-source visual QA — part 3

## Scope and provenance
- Review date: 2026-10-19.
- Visually inspected each full-page 100-dpi PNG individually with the image tool: **41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61**.
- Inputs: `/tmp/duckrabbit-current-source-20261019/pages/page-{41..61}.png`, the immutable FIRST successful build. Corresponding frozen PDF identified by parent: `/tmp/duckrabbit-current-source-20261019/first-review.pdf`.
- No PDF was opened; in particular, the concurrently rebuilding `review/pdf/` PDF was not read. This report does not assess the discretionary-wrap rebuild or any later changed-page round.
- PNG/PDF ordinal pages 41–61 carry printed page numbers 40–60; findings below use PNG/PDF ordinals.
- No project, support-kit, renderer, source, historical artifact, or Git mutations. Only this report was created.

## Findings
1. **Low — right-margin overruns in Table 9 source identifiers (pages 47, 48, 49, 50, 51, 52, 53; printed 46–52).** Some unbroken `sources=...` strings extend beyond the table's right rule endpoint/body-text boundary. Concrete examples: page 47 `sources=brugger1999duckrabbit;`, page 48 `sources=wertheimer1912motion;`, page 49 `sources=bruns2019ventriloquist;`, page 50 `sources=kanizsa1976contours;`, page 51 `sources=zoellner1860pseudoscopy;` (especially conspicuous), page 52 `sources=warren1970continuity;`, and page 53 `sources=vroomen2004temporal;`. These remain on the sheet and readable; no page-edge clipping or adjacent-column collision observed. This is a visible layout defect, not a clean-overfull-warning pass. Parent reports a separate wrap-overlay rebuild is in progress; its correction is unverified here.
2. **Low — appendix heading overruns body width (page 56; printed 55).** The first line of “Appendix A. Complete catalog, source tiers, and evidence/implementation” extends farther right than the body/table boundary; “boundaries” occupies the next line. No page-edge clipping. Parent explicitly identifies this heading for the separate wrap-overlay rebuild; no claim that it is already fixed.
3. **Low — bibliography entry split after author list (pages 59–60; printed 58–59).** The Lamprecht et al. entry leaves its long author list at the bottom of page 59, while its title (“Towards FAIR principles for research software”), journal, DOI, and URL start page 60. Content remains readable and continuation indentation is consistent, but citation scanning requires crossing the page boundary. Keep entry together if publication polish warrants the whitespace cost.

## Other checks / no additional findings
- Pages 41–44: continuing evidence table has repeated headers and legible content; narrow keys/paths wrap aggressively but without clipping or overlap.
- Pages 45–46: Table 8 caption and continuation are separated correctly; equation/code/figure-label identifiers are visible. Raw `eq:`/`fig:` identifiers are traceability data, not evidence of unresolved cross-references. Table 9 caption stays with its header and first rows.
- Pages 47–54: claim-ledger headers repeat consistently; long rows remain intact and text is readable at full-page inspection, aside from margin-overrun findings above. Forced within-identifier breaks are visually awkward but do not lose visible text.
- Page 54: closing table rule and following prose are separated; blue table-number cross-references display normally.
- Page 55: section 9 and subsection 9.1 headings, paragraphs, author-year citations, and repository-link text display normally.
- Pages 56–57: Table 10 caption, repeated header, rows, and closing rule are intact; dense page 57 has no observed row collisions or bottom clipping.
- Page 58: subsection 10.2 has a short paragraph and substantial unused space before the references page. No stranded heading or missing visible continuation; no defect assigned solely for whitespace.
- Pages 59–61: bibliography text, accents, italics, DOI strings, and blue wrapped URLs are visible, with no black glyph boxes or visible unresolved citation placeholders. Citation appearance only was checked; URLs and destination correctness were not independently retested.
- Printed pagination progresses consecutively from 40 through 60. No blank or duplicate page observed in this assigned range.
- No scientific figure panels occur in these assigned pages; table-caption separation was checked. No observed black glyph boxes, overlapping body text, page-edge clipping, or illegibly tiny figure text.

## Assessment and limits
**No high- or medium-severity visual findings; three low-severity finding groups in the first build.** Do not use this as approval of the later rebuild.

Parent-supplied machine QA context (not independently rerun): 225 internal links, including 146 citation links; zero unresolved destinations/undefined/glyph warnings; ten overfull hboxes and a removed binary-units warning disclosed. This visual review confirms some overfull manifestations but does not map every compiler warning or validate the removed warning. Source closeout/template/support-kit provenance is parent-supplied, not re-audited here.
