"""Copy a source-bound, unreleased evidence snapshot; never run product checks.

Requires exported, complete agent:// JSON reports. Refuses an occupied destination.
Only the new candidate bundle is written, under a short repository_operation lease.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT / "dist/wfz-release"
SOURCE_SHA = "459e77f7fb6d9715887ef1b9fdfec854a58eefcf6813441e9afda3f0e86115fe"
AGENTS = ("DuckRabbitDeliveryVisual-1", "DuckRabbitDeliveryVisual-2", "DuckRabbitDeliveryVisual-3",
          "DuckRabbitCitationRefute-1", "DuckRabbitCitationRefute-2")
SKIP = {"__pycache__", ".pytest_cache", ".ruff_cache", ".DS_Store"}


def curate(agent_reports: dict[str, bytes], failed_browser: bytes | None = None) -> dict:
    target = ROOT / "output/review-2026-11-08"
    if target.exists() or target.is_symlink():
        raise FileExistsError("Refusing occupied destination: " + str(target))
    files: dict[str, bytes] = {}
    sources: dict[str, str] = {}

    def add(name: str, data: bytes, source: str) -> None:
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or name in files:
            raise ValueError("Unsafe or duplicate destination: " + name)
        files[name] = data
        sources[name] = source

    def copy(path: Path, name: str) -> None:
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
            raise ValueError("Refusing source symlink: " + str(path))
        if not path.is_file():
            raise FileNotFoundError(path)
        try:
            source = path.relative_to(ROOT).as_posix()
        except ValueError:
            source = str(path)
        add(name, path.read_bytes(), source)

    def tree(path: Path, destination: str, select=lambda p: True) -> None:
        if path.is_symlink() or not path.is_dir():
            raise ValueError("Missing directory or symlink: " + str(path))
        for item in sorted(path.rglob("*")):
            rel = item.relative_to(path)
            if any(part in SKIP for part in rel.parts):
                continue
            if item.is_symlink():
                raise ValueError("Refusing source symlink: " + str(item))
            if item.is_file() and select(item):
                copy(item, destination + "/" + rel.as_posix())

    def generated(name: str, value, source: str) -> None:
        content = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
        add(name, content.encode(), "generated: " + source)

    render = PROOF / "render-review-citation-final"
    output = render / "project/output"
    canonical = PROOF / "artifacts/current-citation-final"
    receipt = json.loads((render / "render-receipt.json").read_text())
    if receipt["status"] != "passed" or receipt["source_binding"]["source_sha256"] != SOURCE_SHA:
        raise ValueError("Final render is not bound to the required passing source snapshot")
    for role in ("figures", "data", "reports", "manuscript"):
        tree(canonical / role, role)
        for item in (canonical / role).rglob("*"):
            if item.is_file():
                rel = item.relative_to(canonical).as_posix()
                if hashlib.sha256(files[rel]).hexdigest() != receipt["inputs"][rel]:
                    raise ValueError("Canonical/render-input binding differs: " + rel)
    tree(output / "pdf", "pdf", lambda p: p.suffix == ".pdf")
    tree(output / "slides", "slides", lambda p: p.suffix in {".pdf", ".html", ".css"})
    tree(output / "web", "web", lambda p: p.name != "_combined_manuscript.md")
    if sum(name.startswith("web/assets/") for name in files) != 374:
        raise ValueError("Expected the complete 374-file HTML asset closure")
    if sum(name.startswith("slides/") and name.endswith((".pdf", ".html")) for name in files) != 22:
        raise ValueError("Expected eleven native PDF/HTML deck pairs")
    for role in ("manuscript", "pdf-manuscript", "slides-manuscript", "slides-flat-manuscript"):
        tree(output / role, "source/render-inputs/" + role)
    tree(output / "html-overlay-evidence", "source/html-overlay-evidence")
    for item in sorted(render.iterdir()):
        if item.is_file():
            destination = "evidence/render/" if item.name in {"render-receipt.json", "actual-commands.jsonl", "html-overlay-receipt.json"} else "source/render-overlays/"
            copy(item, destination + item.name)
    tree(render / "command-logs", "evidence/render/command-logs")
    for role in ("pdf", "slides"):
        tree(output / role, "evidence/render/compiler/" + role,
             lambda p: p.suffix in {".log", ".blg", ".fls", ".bbl"})
    copy(output / "reports/manuscript_composition.json", "evidence/render/manuscript_composition.json")
    for name in ("package.json", "package-lock.json"):
        copy(render / "project" / name, "source/render-prerequisites/" + name)
    helpers = ("render_candidate_final.py", "final_html_overlay.py", "build_slide_overlay.py",
               "render_complete.py", "render_flat.py", "render_canonical_archive.py",
               "render_runtime_overrides.py", "qa_citation_final.py", "citation_final_proof.py",
               "observe_adjunct_bibliography.py", "observe_dependency_advisories.py",
               "browser_server.py", "curate_candidate_evidence.py")
    for name in helpers:
        copy(PROOF / name, "source/helpers/" + name)
    for name in ("pyproject.toml", "uv.lock", ".python-version", "CITATION.cff", "codemeta.json",
                 ".zenodo.json", "LICENSE", "README.md", "CHANGELOG.md"):
        copy(ROOT / name, "source/package/" + name)
    for name in ("src", "scripts", "tests"):
        tree(ROOT / name, "source/package/" + name)
    for name in ("render-review-complete", "render-review-delivery"):
        copy(PROOF / name / "render-receipt.json", "evidence/prior/" + name + "/render-receipt.json")
    copy(PROOF / "render-review-delivery/render-receipt.failed-finalizer.json",
         "evidence/prior/render-review-delivery/render-receipt.failed-finalizer.json")
    copy(PROOF / "render-review-delivery/qa/machine-review.json", "evidence/prior/delivery-machine-review.json")
    tree(PROOF / "receipts", "evidence/receipts", lambda p: p.suffix == ".json")
    tree(PROOF / "citation-final-logs", "evidence/native/logs")
    for item in sorted(PROOF.glob("coverage-citation-final-*.json")):
        copy(item, "evidence/native/" + item.name)
    tree(PROOF / "package-citation-final", "packages", lambda p: p.suffix in {".whl", ".gz"})
    copy(PROOF / "performance-citation-final/report.json", "evidence/performance/report.json")
    tree(PROOF / "artifacts/media-citation-final", "media")
    tree(PROOF / "wheel-smoke-citation-final", "evidence/native/installed-wheel-artifacts")
    copy(PROOF / "artifacts/scholarship_audit.json", "evidence/scholarship/scholarship_audit.json")
    tree(PROOF / "historical-byte-observation", "evidence/history")
    copy(ROOT / "output/pdf/DuckRabbit_combined.pdf", "evidence/history/preserved-root-output.pdf")
    for folder in ("probes-before", "final-probes-before"):
        copy(PROOF / folder / "results.json", "evidence/prior/" + folder + "/results.json")
    for name in ("native-results.json", "native-results-final.json", "native-results-integrated.json", "native-results-closeout.json", "matrix-results.json", "delivery-results.json"):
        copy(PROOF / "receipts" / name, "evidence/prior/" + name)
    tree(PROOF / "native-logs", "evidence/prior/initial-native-logs")
    qa = render / "qa"
    tree(qa, "qa", lambda p: p.suffix in {".json", ".txt"} or p.name.startswith("contact-"))
    comparisons = json.loads((qa / "source-correction-comparison.json").read_text())
    changed = {name for row in comparisons for name in row["changed_rasters"]}
    for name in sorted(changed):
        copy(qa / name, "qa/" + name)
    raw_map = []
    for row in json.loads((qa / "machine-review.json").read_text()):
        for name, digest in row["page_images"].items():
            path = qa / name
            if path.is_symlink() or not path.is_file():
                raise ValueError("Missing retained raw page raster: " + name)
            raw_map.append({"path": name, "sha256": digest, "bytes": path.stat().st_size,
                            "local_source": str(path.relative_to(ROOT)),
                            "shipped": name in changed,
                            "disposition": "shipped_changed_page" if name in changed else "retained_ignored_locally_not_shipped"})
    if len(raw_map) != 634 or len(changed) != 6:
        raise ValueError("Expected all 634 raster bindings and exactly six changed pages")
    generated("qa/raw-raster-inventory.json", raw_map, "final machine-review.json; local raster metadata; source-correction-comparison.json")
    for name in AGENTS:
        data = agent_reports[name]
        json.loads(data)
        add("evidence/agents/" + name + ".json", data, "agent://" + name + ":raw (complete report export)")
    for item in sorted(PROOF.glob("browser-delivery-*.png")):
        copy(item, "evidence/browser/prior-delivery/" + item.name)
    copy(PROOF / "browser-delivery-observation.json", "evidence/browser/prior-delivery/browser-delivery-observation.json")
    if failed_browser is None:
        failed_browser = (PROOF / "browser-citation-final-observation.json").read_bytes()
    if json.loads(failed_browser)["status"] != "failed":
        raise ValueError("Preserve the actual initially failed browser observation")
    add("evidence/browser/browser-citation-final-observation.failed-initial.json", failed_browser,
        "dist/wfz-release/browser-citation-final-observation.json (failed initial snapshot, not relabeled as passed)")
    for pattern in ("browser-citation-final-*.json", "browser-citation-final-*.png"):
        for item in sorted(PROOF.glob(pattern)):
            copy(item, "evidence/browser/" + item.name)
    launches = ROOT.parents[3] / "Local/execution-launches"
    allowed = {"intent.json", "prelaunch.json", "verified.json", "runtime-probe.json", "child.json",
               "child-runtime-storage.json", "exit.json", "completion.json", "stdout.raw", "stderr.raw"}
    for launch in sorted(launches.glob("wfz-duckrabbit-*")):
        tree(launch, "evidence/executions/" + launch.name,
             lambda p: p.name in allowed and len(p.relative_to(launch).parts) == 2)
    native_commands = json.loads((PROOF / "receipts/citation-final-results.json").read_text())
    command_text = "\n\n".join("# " + row["name"] + "; observed returncode=" + str(row["returncode"]) + "\n# cwd: " + row["cwd"] + "\n" + shlex.join(row["argv"]) for row in native_commands) + "\n"
    add("evidence/native/commands.txt", command_text.encode(), "generated: exact argv/cwd/returncode from evidence/receipts/citation-final-results.json")
    resumed = "evidence/browser/browser-citation-final-resumed.json"
    browser_status = json.loads(files[resumed]).get("status", "see actual receipt") if resumed in files else "not present at packaging snapshot"
    readme = f"""# DuckRabbit 0.6.0 candidate evidence — UNRELEASED

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

Package Python-source digest `{SOURCE_SHA}` binds sorted package .py paths/content
ONLY; it is not a whole-tree or bundle hash. Base revision is
`695b9b47d7ddc4621ca5ab3933fa8d8b29787334`, branch `audit/release-0.6.0`.
Qualified launch verified.json has its distinct actual source-tree receipt;
no package digest is substituted for that receipt. Source/package/ preserves
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
preserved separately. Current resumption receipt status at packaging: {browser_status}.
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
`../template/.venv/bin/python -B dist/wfz-release/render_candidate_final.py --source-sha {SOURCE_SHA} --review-name render-review-FRESH_NAME`.
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
"""
    add("README.md", readme.encode(), "generated: curated source/receipt custody and bounded reproduction instructions")
    generated("bundle-provenance.json", {"schema": "duckrabbit-candidate-evidence-1", "created_at": datetime.now(timezone.utc).isoformat(),
              "status": "unreleased_candidate_not_release", "package_python_source_sha256": SOURCE_SHA,
              "package_source_hash_scope": "sorted package .py paths/content only; parent-supplied binding, not whole tree or bundle",
              "base_revision": "695b9b47d7ddc4621ca5ab3933fa8d8b29787334", "branch": "audit/release-0.6.0",
              "render_receipt": "evidence/render/render-receipt.json", "canonical_source": "dist/wfz-release/artifacts/current-citation-final",
              "raw_rasters": {"mapped": len(raw_map), "shipped_changed": len(changed), "not_shipped_retained_locally": len(raw_map)-len(changed)},
              "browser_resumption_status": browser_status, "checks_run_by_curator": [],
              "limitations": ["not a release", "external exact renderer/kit prerequisites not vendored", "scholarship and policy blockers retained", "not perception/accessibility/security certification"]}, "source/render receipts and curation membership")
    entries = {name: {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "source": sources[name]}
               for name, data in sorted(files.items())}
    manifest = {"schema": "duckrabbit-sha256-manifest-1", "scope": "Every shipped file except manifest.json; no symlinks",
                "file_count": len(entries), "bytes_excluding_manifest": sum(len(data) for data in files.values()),
                "files": entries}
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode()
    sys.path.insert(0, "/Users/friedman/Documents/Git/gitvault/_tools")
    from vaultlib import configuration
    from vault_locks import repository_operation
    with repository_operation(configuration(), "docxology/DuckRabbit", "curate-candidate-evidence"):
        target.mkdir(exist_ok=False)
        for name, data in files.items():
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(data)
        with (target / "manifest.json").open("xb") as stream:
            stream.write(manifest_bytes)
    return {"destination": str(target.relative_to(ROOT)), "files": len(files) + 1,
            "bytes": sum(map(len, files.values())) + len(manifest_bytes),
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "counts_by_top_level": dict(Counter(name.split("/")[0] for name in files)),
            "source_sha256": SOURCE_SHA, "browser_resumption_status": browser_status}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-reports", required=True, type=Path,
                        help="Directory containing complete NAME.json exports of the five named agent:// reports")
    args = parser.parse_args()
    reports = {name: (args.agent_reports / (name + ".json")).read_bytes() for name in AGENTS}
    print(json.dumps(curate(reports), indent=2))
