# DuckRabbit 0.6.0 candidate evidence — UNRELEASED

This separately named, self-contained artifact/evidence snapshot is not a release,
portable installer, renderer distribution, projection deck, accessibility certificate,
or independent rerun. No tag, push, release, DOI deposit or historical overwrite is
performed by its curator. All original output files remain untouched.

## Provenance and chronology

Canonical figures/, data/, reports/ and manuscript/ are exact copies of
`dist/wfz-release/artifacts/current-citation-final`, not renderer-adapted inputs.
PDF, eleven PDF/HTML deck pairs and digital-review.css, and web/index.html with
its complete 374-file local asset closure are copied byte-for-byte from
`dist/wfz-release/render-review-citation-final/project/output` with their relative
paths preserved. Data JSON is authoritative for exact machine copying.

Package Python-source digest `459e77f7fb6d9715887ef1b9fdfec854a58eefcf6813441e9afda3f0e86115fe` binds sorted package .py paths/content
ONLY; it is not a whole-tree or bundle hash. Base revision is
`695b9b47d7ddc4621ca5ab3933fa8d8b29787334`, branch `audit/release-0.6.0`.
Qualified launch verified.json has its distinct actual source-tree receipt;
no package digest is substituted for that receipt. source/package/ preserves
source, tests, scripts, lock and metadata; packages/ contains the actual wheel
and sdist. The render receipt separately maps the frozen 1803 renderer files,
canonical inputs, tool/kit/font bindings and observed outputs. Adapted render
inputs, patches, loss-check audits and helper sources live under source/, not
under canonical manuscript/.

Retained native evidence records 866 tests on Python 3.11.18/3.12.16/3.14.10/3.15.2,
installed-wheel API/CLI and five real media formats, all six decoded MP4 frames,
AAC decoding and WAV spectrum observations. CP315 NumPy 2.4.2 reused the retained
locally built cached wheel, not a fresh source build; other three environments
used acquired official wheels. Profiling is one observed workload run, not a
speedup claim. Native command/results/logs/coverage remain the authority.

Final native render records 24 outputs: main 61 PDF pages and 573 slide frames,
plus main HTML and eleven HTML decks. Ten tables contain 161 rows (151 data plus
10 header), 727 cells (43 header), ten captions and 47 bibliography records.
Full-content archive slides intentionally scroll. Prior three visual reports
cover all 634 pages; final comparison reuses only 628 byte-identical rasters.
All 58 current contact sheets and six changed individual rasters are shipped.
`qa/raw-raster-inventory.json` maps ALL 634 raw rasters; the other 628 remain
ignored locally and are explicitly NOT shipped. No raw raster recreation was
run by the curator. Actual complete visual/refutation reports are copied under
evidence/agents/, retaining their original scope and confidence.

The earlier browser-delivery proof is preserved as earlier, not current-source
proof. The current browser observation's exact-whitespace FORCE11 group search
failed after its deck/main observations; that original failed receipt is
preserved separately. Current resumption receipt status at packaging: passed.
The preserved failure plus successful resumption document all twelve HTML outputs,
eleven decks/249 HTML slides, 38 main math targets, 15 decoded main images, actual
citation navigation, correct collective group credit and actual wheel scroll
top=700/client=700/total=1502. Receipt contents, source/HTML digests and failed-scenario scope govern any claim;
a later resumption never erases the original failure. No browser was run by the
curator. Repeated library version-tag warnings in earlier proof are not hidden.

## Blockers and limits

Native live scholarship scope is 36 sources (28 verified, seven reachable but
DOI-less unresolved, one Zöllner author mismatch). The separately observed and
retained-metadata-reevaluated eleven adjunct entries cover the remaining manuscript
bibliography: seven verified, three reachable unresolved, one Stumpf TLS-chain
failure (not bypassed). Across 47 entries: 35 verified, ten unresolved, one mismatch,
one unavailable. Adjunct coverage is not a fabricated native CLI expansion.
Wilson missing middle initial and FORCE11 collective authorship were corrected;
FAIR's valid abbreviated authors and Wheatstone's shortened title were normalized
for completeness, not declared fabricated. Primary refutation reports are retained.

Release remains blocked by unresolved scholarship and external policy gates.
Vault configuration enables issues writes only; PR/release writes require their
separate authorized plan and confirmation. Historical v0.5 tag/DOIs are immutable
by policy, not platform lock. The three distinct historical PDF byte streams are
preserved under evidence/history/ with their actual historical receipts, including
the initial failed Zenodo HTTP 406 and subsequent successful observation.
Seventeen pinned primary dependency versions had no advisory records at the
observation time; this is not a global security, native OS, decoder or external
renderer/transitive dependency audit. Generated stimuli/decoded samples establish
neither perception nor playback calibration nor participant evidence.

## Reproduction and exact commands

`evidence/native/commands.txt` and `evidence/receipts/citation-final-results.json`
contain every exact native argv, original cwd and return code. Final renderer
`evidence/render/actual-commands.jsonl` and command-logs contain actual subprocess
commands, compiler and bibliography outcomes. `evidence/executions/` preserves
qualified launch intents, source/runtime/exit/completion receipts and actual logs,
including failed prior attempts; prelaunch intent alone is NOT a passing result.
Prior baseline probe results, failed installed-wheel API probe logs, earlier
render failure, and prior successful receipts remain under evidence/prior/.
These are chronological evidence, not all observations of the final source.

For a fresh native reproduction from the corresponding source checkout, use the
exact commands above, a fresh destination, the pinned uv.lock/backend/interpreters,
required native ffmpeg/ffprobe and source resources. Canonical generation commands
are `.venv/bin/python -B scripts/generate_publication_outputs.py --output-dir DEST`
and `.venv/bin/python -B scripts/generate_manuscript_variables.py --output-dir DEST`.
The release audit entry point is `.venv/bin/python -B -m duckrabbit audit --output-root DEST --release`;
its recorded scope/gates remain unchanged. Do not overwrite this evidence snapshot.

Renderer reproduction requires the exact read-only external template Python
3.14.10, frozen 1803-file renderer snapshot, retained October TeX kit (48 files,
two pinned tool hashes), actual three TeX packages/fonts, pinned tools, prior
receipt-bound npm MathJax/newcm/Reveal closures and original mapped paths. These
prerequisites are recorded, not vendored or re-certified as a moving template.
With those exact prerequisites in place, the recorded source orchestrator is:
`../template/.venv/bin/python -B dist/wfz-release/render_candidate_final.py --source-sha 459e77f7fb6d9715887ef1b9fdfec854a58eefcf6813441e9afda3f0e86115fe --review-name render-review-FRESH_NAME`.
This deliberately refuses occupied destinations. Consult native commands/receipts
for all path bindings rather than assuming the bundle is a portable installer.
Raw huge TeX/aux, runtime caches, node_modules, profiles and external infrastructure
are omitted; final compiler/bibliography/recorder logs and binding maps are retained.

For local viewing, serve this bundle root with a static HTTP server, then open
web/index.html or slides/*_slides.html. All relative assets are in the bundle;
HTTP viewing is not a new browser verification. Product audit/UI/package/link
checks belong to the integrating parent; the curator only validated copy/hash
bindings and manifest membership, and ran no tests/build/render/lint/browser.

`manifest.json` maps every shipped regular file except itself to SHA-256, exact
bytes and source provenance. It rejects source symlinks and occupied targets.
Generated maps identify their actual input evidence; no fabricated source hash,
placeholder, token environment dump or claim of independent corroboration is used.
Method: CogSecSkills Claim Provenance Verification, applied to artifact custody;
multiple copies of one receipt are not independent proof. Weakest remaining link
is unresolved external bibliographic identity, not the copy operation. The next
discriminating evidence is primary publisher identity resolution without weakening
the existing comparator or bypassing TLS/policy gates.
