# DuckRabbit current-source visual QA — part 2

Date: 2026-10-19. **Scope: immutable FIRST successful build only.**

Inspected individually at full-page size using the image viewer: **PDF pages 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40** (`pages/page-21.png` through `page-40.png`, 100 dpi). Printed folios are 20–39, consistently one less than PDF page numbers. No other pages are claimed inspected.

These PNGs correspond to `/tmp/duckrabbit-current-source-20261019/first-review.pdf`, per parent clarification. No PDF was opened; in particular the actively rebuilt `review/pdf/` PDF was not read. This is not approval of the later discretionary-wrap rebuild.

## Findings

1. **Medium — PDF p.24 (folio 23), Figure 11:** The 18-row scholarship map has extremely small row labels, claim text, and especially limitation/engineering-basis subtext. Those details are difficult to read at the supplied full-page resolution, although the caption is normal size and unobstructed. This is an embedded-figure legibility issue, not observed page-edge clipping. Enlarge/split the map or provide readable detail panels in a future revision.
2. **Medium — PDF p.26 (folio 25), Figure 12:** The formalism traceability figure similarly reduces equations, implementation/test paths, and figure references to very small text. The long temporal/spectral label crowds its equation column. Full-page reading is substantially harder than the surrounding manuscript text; no definite lost glyph or page-edge truncation is visible. Enlarge/split or typeset as a readable table.
3. **Low — PDF p.29 (folio 28), Table 6, first architecture row:** `output/data/architecture.json;` extends into the intercolumn gutter and nearly touches the following `Controls:` text, visually producing `...json;Controls:` without a clear column gap. This is the clearest visible long-token overflow in this assigned range. Recheck this row in the separate discretionary-wrap build.
4. **Low — PDF pp.23, 27, 28 (folios 22, 26, 27), Figures 10, 13–15:** Secondary box annotations, metric/unit labels, domain endpoints, and model-template/footer text are small relative to body/caption type. The diagrams remain structurally understandable, with no observed overlaps or caption collisions, but detailed reading benefits from zoom. Less severe than Figures 11–12.
5. **Low — PDF pp.32, 34–40 (folios 31, 33–39), generated tables:** Aggressive wrapping fragments machine identifiers/hosts and occasionally ordinary words without a visible hyphen. Examples: p.32 synthetic-psychophysics accessibility cell breaks the identifier into `human d` / `ata=false`; p.36 Warren claim breaks `continuity/r` / `estoration`; p.38 Kircher host leaves a lone final `k`; p.40 sound-induced-flash key breaks `so` / `und`. Content stays inside the page, but exact identifiers/URLs are harder to scan or transcribe. Distinguish these readability issues from unresolved citations.

## Other checks / limits

- No visually observed black glyph boxes, page-edge clipping, text superposition obscuring content, or figure/caption collisions across the 20 inspected pages.
- Blue author/year citations in prose are visibly readable; no visible `??` citation/reference placeholders were found. Tables show raw source keys as table data rather than formatted author/year citations. Bibliographic correctness and destination validity were not independently tested here.
- Section hierarchy and folios are consistent. Page 22 has substantial lower whitespace before section 8 starts on p.23; this is not by itself a defect. The generated tables continue with repeated column headers. The p.28-to-p.29 code-value continuation (`human_data=` then `false`) is awkward but visibly present, not clipped.
- Parent-supplied machine QA reports 225 internal links (146 citation), zero unresolved destinations/undefined/glyph warnings, ten overfull hboxes, and a removed binary-units warning. These are supplied facts, not independently rerun checks; this visual review does not clear all ten hboxes or assess the removed warning.
- No high/critical visual findings in this range. Re-review changed pages separately after the discretionary-wrap rebuild. No project, support-kit, renderer, historical artifact, or Git changes were made; only this report was written.
