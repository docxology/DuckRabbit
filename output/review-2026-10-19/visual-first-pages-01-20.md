# DuckRabbit first-build visual QA: PDF pages 1–20

Reviewed 2026-10-19. **Every physical PDF page inspected individually at full-page view:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, using the supplied 100-dpi `pages/page-01.png` through `page-20.png` images. Physical page 3 bears printed page 2; subsequent printed numbers are one below physical page numbers.

Scope is the immutable FIRST successful build, identified by the parent as `/tmp/duckrabbit-current-source-20261019/first-review.pdf`. No PDF was opened, no rebuild output inspected, and no project, support-kit, renderer, historical artifact, or Git state was modified. This report does not approve the later discretionary-wrap overlay or pages beyond 20.

## Findings

1. **Moderate — undersized embedded figure text, most pronounced on physical pages 7, 10, and 12 (Figures 1, 3, 6).** The catalog matrix on page 7 has extremely small row IDs/facets and status labels; some mechanism strings visibly end in ellipses, so the figure alone does not expose their full text. The nine-panel gallery on page 10 has very small luminance/level/digest annotations. The auditory panel on page 12 has very small metric values, axis labels, and spectral annotations. These are substantially smaller than surrounding body/caption text and require magnification; the plots themselves and captions remain distinguishable. Smaller secondary labels also occur in Figures 2, 4, 5, 7, 8, and 9 on pages 9, 11, 12, 13, 14, and 16. No exact point-size or higher-resolution legibility claim is made from 100-dpi PNGs.

2. **Minor — awkward identifier wrapping in Table 3, physical pages 14–15.** Page 14 splits `normalized_luminance` and `normalized_amplitude` so their final `e` occupies a separate line. Page 15 splits `mean_temporal_delta` with a lone final `a`, and splits `spectral_bandwidth_hz` before `hz`. Values are not visibly lost or overlapped, but the isolated fragments impair table scanning. Continuation column headers are present on page 15.

3. **Minor — figure floats interrupt continuous explanatory sentences.** The Figure 4 explanatory paragraph ends page 9 with “jointly varies” and resumes page 11 with “grayscale and quantization levels,” with full-page Figure 3 on page 10 between them. The Figure 6 explanation ends page 11 with “no” and resumes page 13 with “pitch or stream report is inferred,” with the figures on page 12 intervening. The Figure 9 explanation ends page 15 with “The y-axis is” and resumes below the figure on page 16 with “deliberately a narrow model-output range.” These are reading-flow issues, not missing text. All actual Figure 1–9 numbered captions remain on the same page as their respective figures.

## Checks without findings

- Page 1 clearly identifies “Unreleased current-source review,” date 2026-10-19, source 5c25ffc, and “not the archived v0.5.0 PDF.” Subtitle wraps to a second line but does not overlap the author block or cover art.
- No visible clipped body text, intersecting text/table/figure elements, missing-glyph black boxes, or obstructed page numbers on inspected pages. Black stimulus bars and filled shapes are recognizable intentional figure content, not missing-glyph evidence.
- Visible author–year citations render in blue with recognizable names, years, punctuation, and accents; no unresolved citation placeholders were seen. Physical page 20 ends mid-citation (`[Weintraub,`); continuation on unassigned page 21 was not inspected. Visual inspection does not independently verify citation destinations or reference correctness.
- Section headings, table rules, equation numbering, and printed pagination appear consistent. Page 19 is mostly blank after section 6.2, followed by section 7 on page 20; this is whitespace, not a demonstrated missing-page defect.

## Assessment boundary

No critical/high-severity visual defect found on pages 1–20. Findings above concern first-build readability and flow. The supplied machine-QA totals (225 internal links, including 146 citation links; zero unresolved destinations/undefined/glyph warnings) and ten overfull-hbox warnings were not independently rerun or mapped to individual boxes. Absence of visible clipping here does not clear those warnings or the removed binary-units warning. Later changed pages require a separate review.
