"""Fresh source-bound native PDF/HTML and full-content archive-deck render.

Run with the retained template Python, --source-sha CURRENT_PACKAGE_SOURCE_SHA256,
inside the parent's qualified bounded runner. Canonical staging must already exist.
Only a fresh repository-local render-review-* destination is created; occupied paths refuse.
The renderer, TeX kit, native runtime and prior asset closure remain read-only.
Visual/page-layout and browser acceptance belong to the parent, not this receipt.
"""
from __future__ import annotations

import argparse
import copy
from dataclasses import asdict, replace
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import traceback


IGNORED = {"__pycache__", ".pytest_cache", ".ruff_cache", ".DS_Store"}
FONT_SUFFIXES = {".ttf", ".otf", ".ttc", ".pfb", ".pfa", ".tfm", ".vf"}
KIT = Path("/Users/friedman/Documents/Codex/2026-10-17/fix/work/duckrabbit-tex-unblock")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def hashes(directory):
    directory = Path(directory)
    require(directory.is_dir(), "Missing directory: " + str(directory))
    return {p.relative_to(directory).as_posix(): sha(p)
            for p in sorted(directory.rglob("*")) if p.is_file()
            and not any(part in IGNORED for part in p.relative_to(directory).parts)
            and p.suffix not in {".pyc", ".pyo"}}


def no_symlinks(directory):
    require(not directory.is_symlink(), "Symlink source: " + str(directory))
    require(not any(p.is_symlink() for p in directory.rglob("*")),
            "Symlink in source tree: " + str(directory))


def json_write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_text(original, updated, source, destination):
    return "".join(difflib.unified_diff(original.splitlines(True), updated.splitlines(True),
                                     fromfile=source, tofile=destination))


def pdf_table_overlay(manuscript, destination, sections, pandoc):
    """Reuse render_complete.py's table-only, invertible seqsplit AST wrapper."""
    shutil.copytree(manuscript, destination)
    wrappers, audit, patches = {}, [], []
    escapes = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "_": r"\_",
               "#": r"\#", "&": r"\&", "$": r"\$", "%": r"\%",
               "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}

    def convert(text, source, target):
        return subprocess.run([str(pandoc), "--from", source, "--to", target, "--wrap=none"],
                              input=text, capture_output=True, text=True, encoding="utf-8",
                              check=True, timeout=60).stdout

    def wrap(value):
        if isinstance(value, dict):
            if value.get("t") in {"Str", "Code"}:
                text = value["c"] if value["t"] == "Str" else value["c"][1]
                if len(text) >= 13 and (any(char in text for char in "_./:=+")
                                       or re.search(r"\d", text) or re.fullmatch(r"[0-9a-f]{32,}", text)):
                    escaped = "".join(escapes.get(char, char) for char in text)
                    rendered = (r"\texttt{\breakseq{" + escaped + "}}") if value["t"] == "Code" else r"\breakseq{" + escaped + "}"
                    require(rendered not in wrappers or wrappers[rendered] == value,
                            "Ambiguous PDF table wrapper mapping")
                    wrappers[rendered] = copy.deepcopy(value)
                    return {"t": "RawInline", "c": ["latex", rendered]}
            return {key: wrap(child) for key, child in value.items()}
        if isinstance(value, list):
            return [wrap(child) for child in value]
        return value

    def restore(value):
        if isinstance(value, dict):
            if value.get("t") == "RawInline" and value["c"][0] == "latex" and value["c"][1] in wrappers:
                return wrappers[value["c"][1]]
            return {key: restore(child) for key, child in value.items()}
        if isinstance(value, list):
            return [restore(child) for child in value]
        return value

    for section in sections:
        path = destination / section.name
        original = path.read_text(encoding="utf-8")
        lines, result, index = original.splitlines(True), [], 0
        while index < len(lines):
            if not lines[index].lstrip().startswith("|"):
                result.append(lines[index])
                index += 1
                continue
            stop = index
            while stop < len(lines) and lines[stop].lstrip().startswith("|"):
                stop += 1
            fragment = "".join(lines[index:stop])
            parsed = json.loads(convert(fragment, "markdown", "json"))
            if not any(block.get("t") == "Table" for block in parsed["blocks"]):
                result.append(fragment)
                index = stop
                continue
            adapted = wrap(parsed)
            require(restore(adapted) == parsed, "PDF table wrapper changed semantic AST")
            rendered = convert(json.dumps(adapted), "json", "markdown+pipe_tables-simple_tables-multiline_tables-grid_tables")
            roundtrip = json.loads(convert(rendered, "markdown", "json"))
            require(restore(roundtrip) == parsed, "PDF table Markdown roundtrip changed semantic AST")
            audit.append({"file": path.name, "source_line": index + 1,
                          "semantic_ast_sha256": hashlib.sha256(json.dumps(parsed, sort_keys=True).encode()).hexdigest(),
                          "roundtrip_semantics_preserved": True})
            result.append(rendered.rstrip() + "\n")
            index = stop
        updated = "".join(result)
        path.write_text(updated, encoding="utf-8")
        patches.append(patch_text(original, updated, "manuscript/" + path.name, "pdf-manuscript/" + path.name))
    path = destination / "preamble.md"
    original = path.read_text(encoding="utf-8")
    position = original.rfind("\n```")
    require(position >= 0, "PDF preamble has no closing source fence")
    updated = original[:position] + "\n" + r"\usepackage{seqsplit}" + "\n" + r"\providecommand{\breakseq}[1]{\seqsplit{#1}}" + "\n" + original[position:]
    path.write_text(updated, encoding="utf-8")
    patches.append(patch_text(original, updated, "manuscript/preamble.md", "pdf-manuscript/preamble.md"))
    require(len(audit) == 10, "Expected all 10 PDF table source wrappers")
    return {"scope": "render_complete.py invertible table-only AST wrapper; exact restored JSON, including URI/math/code; no generated-TeX edits",
            "tables": audit, "distinct_wrapped_literals": len(wrappers), "patch": "".join(patches)}


def flatten_slide_overlay(source, destination, pandoc, adapter):
    """Reuse render_flat.py's proof-Div lift, reference anchors and loss checks."""
    shutil.copytree(source, destination)
    audit, patches = [], []

    def convert(text, source_format, target_format):
        return subprocess.run([str(pandoc), "--from", source_format, "--to", target_format,
                               "--wrap=preserve", "--standalone"], input=text, text=True,
                              encoding="utf-8", capture_output=True, check=True, timeout=60).stdout

    def leaves(document):
        kinds = {"Str", "Space", "SoftBreak", "LineBreak", "Code", "CodeBlock", "Math",
                 "RawInline", "RawBlock", "Cite", "Link", "Image"}
        return [node for node in adapter._nodes(document) if node["t"] in kinds]

    for section in sorted(source.glob("[0-9][0-9]_*.md")):
        document = json.loads(convert(section.read_text(encoding="utf-8"), adapter._READER, "json"))
        original, renames = copy.deepcopy(document), {}

        def lift(blocks):
            result = []
            for block in blocks:
                if block["t"] == "Div":
                    attr, children = block["c"]
                    if attr[0].startswith("ref-") and section.name == "99_references.md":
                        renamed = "slide-source-" + attr[0][4:]
                        renames[attr[0]] = renamed
                        attr[0] = renamed
                    if any(key == adapter._MARKER for key, _ in attr[2]):
                        kept = [attr[0], attr[1], [[key, value] for key, value in attr[2] if key != adapter._MARKER]]
                        if kept != ["", [], []]:
                            result.append({"t": "Div", "c": [kept, []]})
                        result.extend(lift(children))
                    else:
                        block["c"][1] = lift(children)
                        result.append(block)
                else:
                    result.append(block)
            return result

        document["blocks"] = lift(document["blocks"])
        for node in adapter._nodes(document):
            if node["t"] == "Link" and node["c"][2][0].startswith("#"):
                target = node["c"][2][0][1:]
                if target in renames:
                    node["c"][2][0] = "#" + renames[target]
        restored = copy.deepcopy(document)
        for node in adapter._nodes(restored):
            if node["t"] == "Link":
                for old, new in renames.items():
                    if node["c"][2][0] == "#" + new:
                        node["c"][2][0] = "#" + old
        adapter._require_equal(leaves(original), leaves(restored), section.name + " flat-render visible/literal content")
        text = convert(json.dumps(document), "json", adapter._WRITER)
        decoded = json.loads(convert(text, adapter._READER, "json"))
        adapter._require_equal(document, decoded, section.name + " flat-render complete source roundtrip")
        require(not adapter._marked(decoded), "Proof Div marker survived flattening")
        (destination / section.name).write_text(text, encoding="utf-8")
        patches.append(patch_text(section.read_text(encoding="utf-8"), text,
                                  "slides-manuscript/" + section.name, "slides-flat-manuscript/" + section.name))
        audit.append({"file": section.name, "source_sha256": sha(section),
                      "render_source_sha256": sha(destination / section.name),
                      "visible_and_literal_content_unchanged": True,
                      "roundtrip_preserved": True, "reserved_anchor_renames": renames})
    return audit, "".join(patches)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-sha", required=True, help="Parent-supplied current package-source SHA-256; full tree receipt is supplied separately")
    parser.add_argument("--review-name", default="render-review-delivery")
    args = parser.parse_args()
    require(re.fullmatch(r"[0-9a-f]{64}", args.source_sha) is not None,
            "--source-sha must be a lowercase SHA-256 digest")
    root = Path(__file__).resolve().parents[2]
    proof = root / "dist/wfz-release"
    prior = proof / "render-review-complete"
    current = proof / "artifacts/current-citation-final"
    require(Path(args.review_name).name == args.review_name and args.review_name.startswith("render-review-"), "Review name must be a repository-local render-review-* basename")
    review = proof / args.review_name
    prior_receipt = prior / "render-receipt.json"
    previous = json.loads(prior_receipt.read_text(encoding="utf-8"))
    require(current.is_dir(), "Canonical current-citation-final staging does not exist")
    require(not review.exists() and not review.is_symlink(), "Refusing occupied destination: " + str(review))
    require(sys.version.split()[0] == "3.14.10", "Use retained ../template/.venv/bin/python (3.14.10), not package Python")
    sys.dont_write_bytecode = True
    no_symlinks(current)
    inputs = hashes(current)
    renderer_source = prior / "project/infrastructure"
    require(len(previous["renderer_files"]) == 1803, "Unexpected frozen renderer receipt size")
    require(hashes(renderer_source) == previous["renderer_files"], "Frozen renderer differs from prior exact receipt")
    review.mkdir(exist_ok=False)
    project = review / "project"
    output = project / "output"
    state = {"schema": "duckrabbit-final-native-render-1", "started": datetime.now(timezone.utc).isoformat(),
             "status": "running", "source_binding": {"source_sha256": args.source_sha,
             "binding_authority": "parent-supplied package-source digest; full source-tree receipt supplied separately"},
             "canonical_staging": str(current), "inputs": inputs,
             "prior_receipt": {"path": str(prior_receipt), "sha256": sha(prior_receipt)},
             "renderer_files": previous["renderer_files"], "outcomes": [], "commands": [],
             "profile": "full-content scrollable digital archive; not projection/accessibility certified",
             "visual_acceptance": "not performed by this orchestrator; parent owns PDF and browser review"}
    active_step = "preparation"
    real_run = subprocess.run
    command_log = None
    old_cwd = Path.cwd()

    def save():
        json_write(review / "render-receipt.json", state)

    def record_run(argv, *positional, **kwargs):
        nonlocal active_step
        require(not isinstance(argv, (str, bytes)) and not kwargs.get("shell"), "Only real argv subprocesses are admitted")
        command = [os.fspath(item) for item in argv]
        # Public process-boundary flag records the actual TeX inputs, without a TeX edit.
        if Path(command[0]).name in {"xelatex", "xetex"} and "-recorder" not in command:
            command.insert(1, "-recorder")
        index = len(state["commands"]) + 1
        record = {"id": index, "step": active_step, "argv": command,
                  "cwd": str(Path(kwargs.get("cwd") or Path.cwd()).resolve()),
                  "started": datetime.now(timezone.utc).isoformat(), "timeout": kwargs.get("timeout")}
        executable = shutil.which(command[0], path=(kwargs.get("env") or os.environ).get("PATH"))
        if executable:
            record["executable"] = {"path": executable, "resolved": str(Path(executable).resolve()), "sha256": sha(executable)}
        if kwargs.get("input") is not None:
            value = kwargs["input"]
            record["stdin_sha256"] = hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()
        state["commands"].append(record)
        begun = time.monotonic()
        kwargs.setdefault("stdin", subprocess.DEVNULL) if "input" not in kwargs else None
        try:
            result = real_run(command, *positional, **kwargs)
            record["returncode"] = result.returncode
            return result
        except BaseException as error:
            record["error"] = type(error).__name__ + ": " + str(error)
            if isinstance(error, subprocess.CalledProcessError):
                record["returncode"] = error.returncode
            result = error
            raise
        finally:
            record["duration_seconds"] = time.monotonic() - begun
            for channel in ("stdout", "stderr"):
                value = getattr(locals().get("result"), channel, None)
                if value is None:
                    sink = kwargs.get(channel)
                    if hasattr(sink, "flush") and hasattr(sink, "name"):
                        sink.flush()
                        sink_path = Path(sink.name)
                        if sink_path.is_file():
                            value = sink_path.read_bytes()
                if isinstance(value, (str, bytes)):
                    data = value.encode("utf-8") if isinstance(value, str) else value
                    path = review / "command-logs" / (f"{index:04d}." + channel)
                    path.write_bytes(data)
                    record[channel] = {"path": str(path.relative_to(review)), "sha256": sha(path), "bytes": len(data)}
            command_log.write(json.dumps(record, ensure_ascii=False) + "\n")
            command_log.flush()

    def step(name, function):
        nonlocal active_step
        active_step = name
        start = len(state["commands"])
        try:
            path = Path(function())
            require(path.is_file() and path.stat().st_size > 0, "Native renderer returned no nonempty output: " + str(path))
            row = {"name": name, "status": "passed", "output": str(path), "native_sha256": sha(path),
                   "command_ids": [entry["id"] for entry in state["commands"][start:]]}
            state["outcomes"].append(row)
            print(name, "passed", path, flush=True)
            save()
            return path
        except BaseException as error:
            state["outcomes"].append({"name": name, "status": "failed", "error": type(error).__name__ + ": " + str(error),
                                      "traceback": traceback.format_exc(),
                                      "command_ids": [entry["id"] for entry in state["commands"][start:]]})
            save()
            raise

    save()
    try:
        project.mkdir()
        shutil.copytree(renderer_source, project / "infrastructure", ignore=shutil.ignore_patterns(*IGNORED, "*.pyc", "*.pyo"))
        require(hashes(project / "infrastructure") == previous["renderer_files"], "Renderer copy changed bytes")
        for role in ("manuscript", "figures", "data", "reports"):
            shutil.copytree(current / role, output / role)
            require(hashes(current / role) == hashes(output / role), "Canonical staged copy differs: " + role)
        asset_inputs = previous["external_web_dependencies"]
        for name in ("package.json", "package-lock.json"):
            source = prior / "project" / name
            require(sha(source) == asset_inputs[name], "Prior npm declaration digest differs: " + name)
            shutil.copy2(source, project / name)
        for name in ("mathjax", "@mathjax/mathjax-newcm-font"):
            source = prior / "project/node_modules" / name
            no_symlinks(source)
            require(hashes(source) == asset_inputs[name], "Prior native npm closure differs: " + name)
            shutil.copytree(source, project / "node_modules" / name)
        state["external_web_dependencies"] = asset_inputs
        manifest = json.loads((KIT / "kit-manifest.json").read_text(encoding="utf-8"))
        kit_files = {name: sha(KIT / name) for name in manifest["kit_files_sha256"]}
        require(kit_files == manifest["kit_files_sha256"], "Retained TeX kit differs from manifest")
        state["tex_kit"] = {"path": str(KIT), "manifest_sha256": sha(KIT / "kit-manifest.json"), "files": kit_files}
        runtime = review / "runtime"
        for name in ("var", "config", "cache", "fonts", "tmp", "mpl", "xdg-config", "pycache"):
            (runtime / name).mkdir(parents=True)
        environment = {"TEXMFHOME": str(KIT / "texmf"), "TEXMFVAR": str(runtime / "var"),
                       "TEXMFCONFIG": str(runtime / "config"), "TEXMFOUTPUT": str(output / "pdf"),
                       "VARTEXFONTS": str(runtime / "fonts"), "TEXMFCACHE": str(runtime / "cache"),
                       "XDG_CACHE_HOME": str(runtime / "cache"), "XDG_CONFIG_HOME": str(runtime / "xdg-config"),
                       "MPLCONFIGDIR": str(runtime / "mpl"), "TMPDIR": str(runtime / "tmp"),
                       "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPYCACHEPREFIX": str(runtime / "pycache"),
                       "PATH": "/Users/friedman/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"}
        os.environ.update(environment)
        state["environment"] = environment
        tools = {}
        for name, binding in previous["tools"].items():
            path = shutil.which(name)
            require(path is not None, "Missing native render tool: " + name)
            tools[name] = {"path": path, "resolved": str(Path(path).resolve()), "sha256": sha(path)}
            require(tools[name]["sha256"] == binding["sha256"], "Native tool differs from prior verified binding: " + name)
        for name in ("xelatex", "kpsewhich"):
            require(tools[name]["sha256"] == manifest["pinned_toolchain_sha256"][name]["sha256"], "TeX tool differs from kit: " + name)
        crossref = shutil.which("pandoc-crossref")
        require(crossref is not None, "pandoc-crossref is required")
        tools["pandoc-crossref"] = {"path": crossref, "resolved": str(Path(crossref).resolve()), "sha256": sha(crossref)}
        state["tools"] = tools
        state["python"] = {"version": sys.version, "executable": sys.executable,
                           "resolved": str(Path(sys.executable).resolve()), "sha256": sha(sys.executable)}
        helper_paths = [Path(__file__), proof / "final_html_overlay.py", proof / "build_slide_overlay.py",
                        proof / "render_complete.py", proof / "render_flat.py", proof / "render_canonical_archive.py"]
        state["overlay_helpers"] = {str(path.relative_to(root)): sha(path) for path in helper_paths}
        require(sha(proof / "build_slide_overlay.py") == previous["slides_source_overlay"]["helper_sha256"],
                "Semantic preservation helper differs from prior binding")
        (review / "command-logs").mkdir()
        command_log = (review / "actual-commands.jsonl").open("x", encoding="utf-8")
        subprocess.run = record_run
        sys.path.insert(0, str(project))
        sys.path.insert(0, str(proof))
        import yaml
        import build_slide_overlay as adapter
        from final_html_overlay import finalize_html
        from infrastructure.rendering.config import RenderingConfig
        from infrastructure.rendering.pdf_renderer import PDFRenderer
        from infrastructure.rendering.web_renderer import WebRenderer
        from infrastructure.rendering.slides_renderer import SlidesRenderer
        from infrastructure.rendering._slides_crossref import parse_aux_label_numbers
        from infrastructure.rendering._slides_reveal_content import (
            activate_hardened_reveal_mathjax, promote_display_math_labels,
            resolve_reveal_cross_references, reveal_reference_and_math_issues)
        from infrastructure.rendering._web_postprocess import normalize_figure_paths
        from infrastructure.rendering._web_assets import MATHJAX_URL, harden_mathjax_script
        from pypdf import PdfReader
        os.chdir(project)
        manuscript = output / "manuscript"
        sections = sorted(p for p in manuscript.glob("*.md") if re.match(r"^\d{2}_", p.name))
        require(len(sections) == 11 and sections[-1].name == "99_references.md", "Expected all 11 canonical chapters")
        state["sections"] = [p.name for p in sections]
        source_patches = []
        path = manuscript / "preamble.md"
        old = path.read_text(encoding="utf-8")
        canonical_font_path = "/usr/local/texlive/2026/texmf-dist/fonts/truetype/public/juliamono/"
        retained_font_path = str(KIT / "texmf/fonts/truetype/public/juliamono") + "/"
        updated = old.replace(canonical_font_path, retained_font_path)
        require(retained_font_path in updated, "Preamble does not bind the retained JuliaMono font")
        path.write_text(updated, encoding="utf-8")
        source_patches.append(patch_text(old, updated, "canonical/preamble.md", "manuscript/preamble.md"))
        path = manuscript / "config.yaml"
        old = path.read_text(encoding="utf-8")
        config_data = yaml.safe_load(old)
        config_data["paper"]["subtitle"] += " — unreleased 0.6.0 digital review; source " + args.source_sha[:16]
        updated = yaml.safe_dump(config_data, sort_keys=False, allow_unicode=True)
        path.write_text(updated, encoding="utf-8")
        source_patches.append(patch_text(old, updated, "canonical/config.yaml", "manuscript/config.yaml"))
        (review / "review-overlay.patch").write_text("".join(source_patches), encoding="utf-8")
        state["overlay_sha256"] = sha(review / "review-overlay.patch")
        config = RenderingConfig(manuscript_dir=str(manuscript), figures_dir=str(output / "figures"),
                                 output_dir=str(output), pdf_dir=str(output / "pdf"), web_dir=str(output / "web"),
                                 slides_dir=str(output / "slides"), template_dir=str(project / "infrastructure/rendering/templates"),
                                 latex_compiler="xelatex", pandoc_path=tools["pandoc"]["path"],
                                 security_profile="trusted-local", web_asset_mode="local", slides_profile="archive")
        state["config"] = asdict(config)
        packages = {}
        for name in ("seqsplit.sty", "newunicodechar.sty", "latinmodern-math.otf"):
            located = subprocess.run([tools["kpsewhich"]["path"], name], capture_output=True,
                                     text=True, check=True, timeout=30).stdout.strip()
            require(bool(located) and Path(located).is_file(), "Missing required read-only TeX input: " + name)
            packages[name] = {"path": located, "sha256": sha(located)}
        require(packages["seqsplit.sty"]["sha256"] == previous["pdf_source_overlay"]["seqsplit_sha256"],
                "seqsplit differs from prior PDF source wrapper binding")
        state["tex_packages"] = packages
        pdf_source = output / "pdf-manuscript"
        pdf_audit = pdf_table_overlay(manuscript, pdf_source, sections, tools["pandoc"]["path"])
        (review / "pdf-source-overlay.patch").write_text(pdf_audit.pop("patch"), encoding="utf-8")
        state["pdf_source_overlay"] = pdf_audit
        state["pdf_source_overlay"]["patch_sha256"] = sha(review / "pdf-source-overlay.patch")
        slide_source = output / "slides-manuscript"
        slide_audit = adapter.make_slide_overlay(manuscript, slide_source, Path(tools["pandoc"]["path"]))
        expected_counts = {"tables": 10, "rows": 161, "data_rows": 151, "header_rows": 10,
                           "footer_rows": 0, "cells": 727, "header_cells": 43, "captions": 10}
        require(slide_audit["counts"] == expected_counts, "Archive overlay table/row/cell totals differ from contract")
        bibliography = [entry["bibliography"] for entry in slide_audit["files"] if entry["bibliography"]]
        require(len(bibliography) == 1 and bibliography[0]["records"] == 47 and bibliography[0]["all_source_ids_present"],
                "References deck must materialize all 47 bibliography entries")
        json_write(review / "slides-overlay-audit.json", slide_audit)
        (review / "slides-overlay.patch").write_text("".join(slide_audit["patches"].values()), encoding="utf-8")
        state["slides_source_overlay"] = {"helper_sha256": sha(proof / "build_slide_overlay.py"),
                                          "audit_sha256": sha(review / "slides-overlay-audit.json"),
                                          "counts": slide_audit["counts"], "assertions": slide_audit["assertions"],
                                          "bibliography_records": bibliography[0]["records"]}
        flat = output / "slides-flat-manuscript"
        flat_audit, flat_patch = flatten_slide_overlay(slide_source, flat, tools["pandoc"]["path"], adapter)
        json_write(review / "flat-slide-source-audit.json", flat_audit)
        (review / "flat-slide-source.patch").write_text(flat_patch, encoding="utf-8")
        state["flat_slide_source"] = {"audit_sha256": sha(review / "flat-slide-source-audit.json"),
                                      "patch_sha256": sha(review / "flat-slide-source.patch"),
                                      "used_decks": [p.stem for p in sections]}
        save()
        pdf_config = replace(config, manuscript_dir=str(pdf_source))
        main_pdf = step("pdf", lambda: PDFRenderer(pdf_config, process_runner=record_run).render_combined(
            [pdf_source / p.name for p in sections], pdf_source, project_name="DuckRabbit-0.6.0-review"))
        labels = parse_aux_label_numbers(output / "pdf/_combined_manuscript.aux")
        require(bool(labels), "Fresh main AUX has no canonical labels")
        require(len([key for key in labels if key.startswith("tbl:")]) >= 10, "Fresh main AUX omits canonical table labels")
        json_write(review / "canonical-reference-map.json", labels)
        lua = review / "canonical-table-references.lua"
        header = review / "subscript-source-header.tex"
        for path in (lua, header):
            shutil.copy2(prior / path.name, path)
        require(sha(lua) == previous["canonical_reference_overlay"]["lua_sha256"], "Canonical Lua helper differs from prior binding")
        require(sha(header) == previous["canonical_reference_overlay"]["source_header_sha256"], "Unicode source header differs from prior binding")
        state["canonical_reference_overlay"] = {"fresh_aux_sha256": sha(output / "pdf/_combined_manuscript.aux"),
                                                "map_sha256": sha(review / "canonical-reference-map.json"),
                                                "lua_sha256": sha(lua), "source_header_sha256": sha(header),
                                                "scope": "Fresh main AUX label map; existing source Lua helper; actual Beamer -H header; no generated-TeX edits"}
        main_html = step("html", lambda: WebRenderer(config).render_combined(sections, manuscript, project_name="DuckRabbit-0.6.0-review"))

        def slide_runner(argv, *positional, **kwargs):
            command = list(argv)
            if "-t" in command:
                kind = command[command.index("-t") + 1]
                command[1:1] = ["--lua-filter", str(lua)]
                if kind == "beamer":
                    command.extend(["-H", str(header)])
                elif kind == "revealjs":
                    command.extend(["--slide-level=2", "-V", "revealjs-url=https://unpkg.com/reveal.js@5.2.1",
                                    "--mathjax=" + MATHJAX_URL, "--css=digital-review.css"])
            return record_run(command, *positional, **kwargs)

        beamer = SlidesRenderer(replace(config, manuscript_dir=str(flat)), process_runner=slide_runner)
        reveal = SlidesRenderer(replace(config, manuscript_dir=str(flat), slide_theme="white"), process_runner=slide_runner)
        state["reveal_config"] = asdict(reveal.config)
        hardening = []
        for source_section in sections:
            section = flat / source_section.name
            step("slides-" + section.stem + "-beamer", lambda section=section: beamer.render(
                section, output_format="beamer", manuscript_dir=flat, figures_dir=output / "figures",
                strict_cross_deck_refs=True))
            path = step("slides-" + section.stem + "-revealjs", lambda section=section: reveal.render(
                section, output_format="revealjs", manuscript_dir=flat, figures_dir=output / "figures"))
            original = path.read_text(encoding="utf-8")
            content = normalize_figure_paths(original).replace('data-src="../../output/figures/', 'data-src="../figures/')
            content = activate_hardened_reveal_mathjax(content)
            content = promote_display_math_labels(content)
            content = resolve_reveal_cross_references(content, labels, strict=True)
            path.write_text(content, encoding="utf-8")
            harden_mathjax_script(path)
            content = path.read_text(encoding="utf-8")
            issues = reveal_reference_and_math_issues(content)
            require(not issues, "Native Reveal math/reference hardening failed: " + str(issues))
            patch = review / (section.stem + "-native-html-hardening.patch")
            patch.write_text(patch_text(original, content, "native/" + path.name, "hardened/" + path.name), encoding="utf-8")
            hardening.append({"file": str(path.relative_to(output)), "native_sha256": hashlib.sha256(original.encode()).hexdigest(),
                              "hardened_sha256": sha(path), "patch_sha256": sha(patch), "issues": list(issues)})
            save()
        state["native_html_hardening"] = hardening
        active_step = "final-html-overlay"
        state["html_overlay"] = finalize_html(output, prior / "project/output/web/assets")
        json_write(review / "html-overlay-receipt.json", state["html_overlay"])
        state["html_overlay_receipt_sha256"] = sha(review / "html-overlay-receipt.json")
        active_step = "final-receipt"
        expected = [main_pdf, main_html]
        expected += [output / "slides" / (p.stem + "_slides" + suffix)
                     for p in sections for suffix in (".pdf", ".html")]
        require(len(expected) == 24 and all(path.is_file() and path.stat().st_size for path in expected),
                "Fresh render must contain main PDF/HTML and all 22 deck outputs")
        pdf_pages = {}
        for path in expected:
            if path.suffix == ".pdf":
                pages = len(PdfReader(path, strict=True).pages)
                require(pages > 0, "Empty native PDF: " + str(path))
                pdf_pages[str(path.relative_to(output))] = pages
        state["pdf_pages"] = pdf_pages
        font_inputs = {}
        recorder_files = sorted(output.rglob("*.fls"))
        require(len(recorder_files) >= 12, "Missing native TeX recorder input lists")
        for recorder in recorder_files:
            for line in recorder.read_text(encoding="utf-8", errors="strict").splitlines():
                if line.startswith("INPUT "):
                    path = Path(line[6:])
                    if not path.is_absolute():
                        path = recorder.parent / path
                    if path.suffix.lower() in FONT_SUFFIXES and path.is_file():
                        font_inputs[str(path.resolve())] = sha(path)
        require(bool(font_inputs), "Native TeX recorder did not bind any font files")
        state["font_inputs"] = font_inputs
        state["tex_recorder_files"] = {str(path.relative_to(output)): sha(path) for path in recorder_files}
        for name, module in list(sys.modules.items()):
            if (name == "infrastructure" or name.startswith("infrastructure.")) and getattr(module, "__file__", None):
                require(Path(module.__file__).resolve().is_relative_to(project), "Native module escaped repository-local frozen copy: " + name)
        require(hashes(renderer_source) == hashes(project / "infrastructure") == previous["renderer_files"], "Frozen renderer changed during render")
        require(hashes(current) == inputs, "Canonical staging changed during render")
        require({name: sha(KIT / name) for name in kit_files} == kit_files, "Retained TeX kit changed during render")
        for name in ("package.json", "package-lock.json"):
            require(sha(project / name) == asset_inputs[name], "npm declaration changed during render")
        for name in ("mathjax", "@mathjax/mathjax-newcm-font"):
            require(hashes(project / "node_modules" / name) == asset_inputs[name], "Native npm dependency changed during render")
        require({name: sha(root / name) for name in state["overlay_helpers"]} == state["overlay_helpers"], "Orchestrator/overlay source changed during render")
        state["canonical_inputs_unchanged"] = True
        state["frozen_renderer_unchanged"] = True
        state["outputs"] = hashes(output)
        for row in state["outcomes"]:
            row["sha256"] = sha(row["output"])
        state["status"] = "passed"
        state["finished"] = datetime.now(timezone.utc).isoformat()
        save()
        return 0
    except BaseException as error:
        state["status"] = "failed"
        state["failed_step"] = active_step
        state["error"] = type(error).__name__ + ": " + str(error)
        state["traceback"] = traceback.format_exc()
        state["finished"] = datetime.now(timezone.utc).isoformat()
        save()
        raise
    finally:
        subprocess.run = real_run
        os.chdir(old_cwd)
        if command_log is not None:
            command_log.close()


if __name__ == "__main__":
    raise SystemExit(main())
