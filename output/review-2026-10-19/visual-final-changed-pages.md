# DuckRabbit independent final changed-page QA - round 2

Date: 2026-10-19. Review-only; no edits to project, kit, renderer, PDF, PNGs, historical artifacts, or Git. Only this report was created.

## Decision and scope

**Accept the targeted wrapping corrections for the explicitly labeled, zoom-capable digital current-source review artifact, with residual readability limitations disclosed. No new high- or moderate-severity layout defect was observed on the changed pages. This is not a flawless-layout, print-accessibility, archival-conformance, scientific-validity, or publication-ready certification.**

Final PDF: `/tmp/duckrabbit-current-source-20261019/review/pdf/DuckRabbit-current-source-review-20261019_combined.pdf`.

Independently computed final PDF SHA-256: `c7dcea5fb5fb87db89ed8de5a8201443e2dc5fb0b0d6d722e9eb4c88bc98d57f`, matching `citation-qa.json`.

Every changed final PNG was opened and visually inspected individually at its supplied full-page resolution: **2, 29, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56** in `/tmp/duckrabbit-current-source-20261019/pages-final/page-NN.png`. Additional unchanged final pages **7, 10, 12, 24, 26** were individually viewed to independently assess the outstanding small-annotation findings. All page references here are physical PDF/PNG ordinals; body folios are one less.

Independently compared SHA-256 hashes of all 61 first-build PNGs in `pages/` against all 61 `pages-final/` PNGs: exactly the twelve pages above changed; **49 are byte-identical**. Read all three prior reports in `/tmp/duckrabbit-visual-qa-part{1,2,3}/report.md`. Their individual first-build inspections plus the hash identity support coverage continuity for unchanged pages, not a claim that this reviewer personally re-viewed all 61 final pages. Text extraction of the final PDF independently returned 61 nonempty pages.

## Changed-page inspection log

| Physical page (folio) | Individual visual observation |
| --- | --- |
| 2 (TOC) | Heading hierarchy, leader dots, and right-aligned page numbers are intact. The longer appendix title with “evidence and implementation boundaries” fits on one line without colliding with folio 55. Matches the revised section 10 wording after removing its body-heading line-break hyphen. |
| 29 (28) | Table 6 architecture path now wraps inside the Source and evidence column. A clear gap separates it from Controls; the prior near-concatenation is resolved. Header, caption, row content, and footer are unobstructed. The path breaks within `json` (`architecture.js` / `on;`), an awkward but readable wrapping tradeoff, not clipping. |
| 46 (45) | Table 8 closes cleanly; Table 9 caption remains with header and first rows. Four columns are distinct. Wrapped paths/evidence identifiers remain within their columns; no rule, caption, or footer collision. |
| 47 (46) | Claim-ledger source strings, including Brugger and Gregory, stay inside the final column. Source-key breaks such as `brugger19` / `99duckrabbit` remain visually reconstructable. No right-margin overrun or collision. Long simultaneous-contrast ID wraps awkwardly in the first column. |
| 48 (47) | Wertheimer, Shepard, and Zatorre lineage strings wrap inside the last column. Header repeats, rows remain distinguishable, and no bottom clipping or overlap is visible. |
| 49 (48) | Shams, Bruns, and other source strings stay within the table width. The ventriloquist claim ID splits within the word. This is a minor scanability cost, not lost text or intercolumn intrusion. |
| 50 (49) | Gregory, Morgan, Fisher, Yildiz, Kanizsa, and Wagemans keys remain within the last column. Three long rows fit; headers and folio are clear. No right-margin overflow. |
| 51 (50) | Mruczek, Weintraub, Zoellner, Deutsch, and Repp source strings are contained. The formerly conspicuous Zoellner overrun is resolved. Rows and footer do not collide. |
| 52 (51) | Deutsch, Warren, and Riecke source strings wrap inside the last column. Both rows and continuation header are intact, with ample bottom clearance. |
| 53 (52) | Vroomen and Hartcher-O'Brien-related source keys are contained; no previous margin overrun remains. First-column temporal-ventriloquism ID wraps within a word; McGurk ID leaves a lone final `k` on its second line, a concrete low-severity scanability issue. Publication-figure-count row fits below. |
| 54 (53) | Final claim-ledger row and bottom rule are intact. Following paragraphs and blue table cross-references are clearly separated. Monospaced provenance path fits within body width. No introduced collision or clipping. |
| 56 (55) | Revised appendix heading fits body width on two lines, breaking `imple-` / `mentation`; no former right-margin overrun remains. Section 10.1, numbered questions, explanatory prose, Table 10 caption/header, six rows, and footer remain visually separated. Heading hyphenation is cosmetically less elegant than a semantic phrase break but not a blocking defect. |

Across these twelve changed pages, no visible missing-glyph boxes, unresolved citation placeholders, page-edge text clipping, obscured page numbers, row collisions, or caption/header separation defect was observed. This observation is bounded by supplied PNG resolution; zero compiler overfull boxes is complementary evidence, not a substitute for visual review.

## TOC consistency check

Compared every numbered TOC entry on physical page 2 with the corresponding heading and folio in final-PDF text extraction. All matched:

- Sections 1, 2, 3: folios 2, 3, 4; 3.1-3.3: 4; 3.4, 3.5, 3.5.1: 5.
- Section 4 and 4.1: 6; 4.2-4.3: 7; 4.4: 8; 4.5: 10; 4.6: 12; 4.7: 13; 4.8-4.9: 14.
- Sections 5 and 6: 16 and 17; 6.1: 17; 6.2: 18.
- Section 7 and 7.1-7.2: 19; 7.3-7.5: 20; 7.6: 21.
- Section 8 and 8.1-8.2: 22; 8.3: 24; 8.4: 27; 8.5: 28.
- Section 9 and 9.1: 54; section 10 and 10.1: 55; 10.2: 57.

This checks displayed wording and pagination, not independent interactive activation of every TOC hyperlink.

## Remaining issues and severity

1. **Moderate, unchanged - small embedded figure annotations, physical pages 7, 10, 12, 24, 26.** Independently confirmed by individual final-PNG views. Figure 1 catalog labels/status/facets and some ellipsized strings; Figure 3 nine-panel metrics/digests; Figure 6 waveform/spectral metrics and axes; Figure 11 scholarship claims/limitation subtext; and Figure 12 equations, paths, and label columns are much smaller than captions/body text. Figure 12's long temporal/spectral label is crowded near its equation column. Full-page viewing is insufficient for comfortable detail reading. No claim is made that these were fixed, that zoom recovers every raster detail, or that ellipsized figure strings become complete when magnified. For digital review, consult searchable manuscript tables and available source-data records for exact details; print-ready or accessible presentation needs enlarged/split or separately typeset detail, not just a clean LaTeX log.
2. **Low - awkward machine-token wrapping persists, including on changed pages.** Concrete final examples: architecture path split inside `json` on page 29; source key split inside year/name on page 47; ventriloquist ID on page 49; lone final `k` of McGurk ID on page 53. These are contained and reconstructable, with no visible lost text, but manual scanning/transcription is worse than for semantically wrapped identifiers. The wrap corrections cure margin/gutter defects, not all table typography. Other unchanged aggressive identifier/URL wrapping on pages 32 and 34-40 remains documented by round 1.
3. **Low, unchanged, carried from first-build reports via hash identity - Table 3 isolated identifier fragments on pages 14-15; sentence interruptions by floats across pages 9-13 and 15-16; Lamprecht author/title split across bibliography pages 59-60.** These pages were not personally re-viewed in this round. No evidence that these issues were corrected, and no claim that they were.
4. **Low, unchanged - other small diagram labels** on pages identified by the prior reviewers remain disclosed; only the five most significant figure pages were personally reassessed in this round.

The targeted Table 6 gutter crowding, Table 9 right-margin source-key overruns, and appendix-heading overrun are **visually resolved on inspected final pages**. Residual within-token wrapping is a low-severity tradeoff; no newly observed high/moderate regression blocks the limited digital-review use stated above.

## Citation, build, and provenance limits

Read the final `citation-qa.json` and verified its PDF hash against the actual final PDF. It reports 61 pages, 47 bibliography entries/cited keys, 146 citation links, 225 internal links total, 73 external URI links, no broken links, missing bibliography keys, empty pages, undefined markers, unresolved text markers, or overfull hboxes. The 146 citation links are included within 225 internal links, not additional to them. These are results of the supplied machine-QA report, not independently rerun link-destination or bibliography-correctness tests. Visible raw `sources=` keys and traceability `eq:`/`fig:` labels in tables are data, not necessarily unresolved citations.

External checks are expressly URI presence/scheme only. No live DOI/URL reachability or new bibliographic-source verification was performed. The removed siunitx binary-units-option warning remains reported; parent states there are no siunitx commands in use. Parent also discloses the Ptolemy BibTeX volume-plus-number warning. This reviewer did not independently rerun the compiler or BibTeX, audit source changes/scientific values, verify PDF-to-PNG rendering equivalence beyond the supplied artifact relationship, or inspect archival PDF conformance, tagging, reading order, assistive-technology behavior, color/contrast compliance, or print-size point measurements.

Historical archived release artifacts remain outside this artifact's certification boundary and were not modified. The current-source review must retain its unreleased/non-archived labeling and its residual-layout disclosures; do not present this report as certification of the archived v0.5.0 PDF or of flawless publication quality.
