"""Build an auditable, source-only archive-slide overlay; never render TeX.

The caller owns the vault write lease and all rendering/visual verification.
Only the fresh destination is written. Pandoc is the sole non-stdlib dependency.
"""
from __future__ import annotations

import copy
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


_READER = "markdown-smart+fenced_divs+bracketed_spans+raw_attribute+yaml_metadata_block"
_WRITER = "markdown-smart-auto_identifiers+fenced_divs+bracketed_spans+raw_attribute"
_MARKER = "data-duckrabbit-slide-proof"


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _hashes(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob("*")) if p.is_file()}


def _nodes(value):
    if isinstance(value, dict):
        if "t" in value:
            yield value
        for child in value.values():
            yield from _nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nodes(child)


def _normalize(value, in_table=False):
    """Canonicalize display-only inline grouping; never code/math/URI literals."""
    if isinstance(value, dict):
        inside = in_table or value.get("t") == "Table"
        result = {key: _normalize(child, inside) for key, child in value.items()}
        if not inside and result.get("t") == "Plain":
            result["t"] = "Para"
        if result.get("t") == "SoftBreak":
            return {"t": "Space"}
        return result
    if isinstance(value, list):
        result = []
        for child in value:
            if isinstance(child, dict) and child.get("t") == "Quoted":
                kind, body = child["c"]
                opening, closing = ("“", "”") if kind["t"] == "DoubleQuote" else ("‘", "’")
                additions = [{"t": "Str", "c": opening}, *_normalize(body, in_table),
                             {"t": "Str", "c": closing}]
            else:
                additions = [_normalize(child, in_table)]
            for item in additions:
                if (isinstance(item, dict) and item.get("t") == "Str" and result
                        and isinstance(result[-1], dict) and result[-1].get("t") == "Str"):
                    result[-1]["c"] += item["c"]
                else:
                    result.append(item)
        return result
    return value


def _require_equal(expected, actual, description):
    if _normalize(expected) != _normalize(actual):
        raise ValueError(description + ": semantic JSON changed (expected " +
                         _digest(_normalize(expected)) + ", got " +
                         _digest(_normalize(actual)) + ")")


def _para(text):
    inlines = []
    for index, word in enumerate(text.split(" ")):
        if index:
            inlines.append({"t": "Space"})
        if word:
            inlines.append({"t": "Str", "c": word})
    return {"t": "Para", "c": inlines}


def _div(token, blocks, attr=None):
    attr = copy.deepcopy(attr) if attr is not None else ["", [], []]
    if any(key == _MARKER for key, _ in attr[2]):
        raise ValueError("Source uses reserved proof marker")
    attr[2].append([_MARKER, token])
    return {"t": "Div", "c": [attr, blocks]}


def _token(node):
    if node.get("t") != "Div":
        return None
    return dict(node["c"][0][2]).get(_MARKER)


def _marked(document):
    found = {}
    for node in _nodes(document):
        token = _token(node)
        if token is not None:
            if token in found:
                raise ValueError("Duplicate proof marker: " + token)
            found[token] = node
    return found


def _sensitive(value):
    """Keep full inline payloads, including URI targets/titles and math modes."""
    return [copy.deepcopy(node) for node in _nodes(value)
            if node["t"] in {"Link", "Image", "Math", "Code", "RawInline"}]


def make_slide_overlay(source_dir: Path, destination: Path, pandoc: Path) -> dict:
    """Copy manuscript inputs and convert every table to loss-checked prose.

    Returns a JSON-serializable audit with every input/output digest and patch.
    A failed preservation assertion raises; a partial destination is not reusable.
    There are no assertions that disappear under Python's optimization flag.
    """
    source_dir = Path(source_dir).resolve(strict=True)
    destination = Path(destination).absolute()
    pandoc = Path(pandoc).resolve(strict=True)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    if destination.resolve().is_relative_to(source_dir):
        raise ValueError("Destination must not be inside the canonical source")
    if not source_dir.is_dir():
        raise NotADirectoryError(source_dir)
    if any(p.is_symlink() for p in source_dir.rglob("*")):
        raise ValueError("Manuscript inputs must not contain symlinks")
    sections = sorted(p for p in source_dir.glob("*.md")
                      if re.match(r"^\d{2}_", p.name))
    if not sections or not any(p.name == "99_references.md" for p in sections):
        raise ValueError("Expected numbered chapters including 99_references.md")
    source_hashes = _hashes(source_dir)
    shutil.copytree(source_dir, destination)
    if _hashes(destination) != source_hashes:
        raise ValueError("Initial manuscript copy differs from source")
    commands = []

    def run(text, source_format, target_format, *extra):
        command = [str(pandoc), "--from=" + source_format,
                   "--to=" + target_format, "--wrap=preserve", *extra]
        result = subprocess.run(command, input=text, capture_output=True,
                                text=True, encoding="utf-8", check=True,
                                cwd=source_dir, timeout=180)
        commands.append({"argv": command, "stderr": result.stderr,
                         "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest()})
        return result.stdout

    audit = {"schema": "duckrabbit-slide-source-overlay-1", "source_dir": str(source_dir),
             "destination": str(destination), "pandoc": str(pandoc),
             "pandoc_sha256": hashlib.sha256(pandoc.read_bytes()).hexdigest(),
             "source_hashes": source_hashes, "normalization":
             "Plain -> Para outside tables; SoftBreak -> Space; English Quoted nodes -> identical curly quotation glyphs; adjacent Str coalescing. Hard breaks, character values, code/math/raw literals and URI targets unchanged.",
             "files": [], "patches": {}, "counts":
             {"tables": 0, "rows": 0, "data_rows": 0, "header_rows": 0,
              "footer_rows": 0, "cells": 0, "header_cells": 0, "captions": 0},
             "commands": commands}

    for section in sections:
        original_text = section.read_text(encoding="utf-8")
        original = json.loads(run(original_text, _READER, "json"))
        if original.get("pandoc-api-version", [0]) < [1, 22]:
            raise ValueError("Modern Pandoc Table AST (API >= 1.22) is required")
        if _marked(original):
            raise ValueError("Source contains reserved overlay markers")
        prefix = "dr-slide-" + section.stem
        table_records = []
        payloads = {}
        added_tokens = set()
        source_ids = set()
        for node in _nodes(original):
            if node["t"] in {"Div", "Span", "Code", "CodeBlock", "Link", "Image", "Table"}:
                attr = node["c"][0]
            elif node["t"] == "Header":
                attr = node["c"][1]
            else:
                continue
            if attr[0]:
                source_ids.add(attr[0])

        def heading(text, identity):
            if identity in source_ids:
                raise ValueError("Generated slide heading collides with source ID " + identity)
            source_ids.add(identity)
            return {"t": "Header", "c": [2, [identity, [], []], _para(text)["c"]]}

        def payload(token, blocks, attr=None, kind="cell"):
            if token in payloads:
                raise ValueError("Duplicate expected payload " + token)
            payloads[token] = {"blocks": copy.deepcopy(blocks), "kind": kind,
                               "attributes": copy.deepcopy(attr)}
            return _div(token, copy.deepcopy(blocks), attr)

        def convert_table(table):
            if any(node["t"] == "Table" for node in _nodes(table["c"])):
                raise ValueError("Nested tables require a separate source-format composition")
            number = len(table_records) + 1
            token = prefix + "-table-" + str(number)
            attr, caption, colspecs, head, bodies, foot = copy.deepcopy(table["c"])
            record = {"token": token, "table": copy.deepcopy(table), "rows": [],
                      "columns": len(colspecs), "attributes": copy.deepcopy(attr),
                      "caption_sha256": _digest(caption), "caption_tokens": []}
            table_records.append(record)
            audit["counts"]["tables"] += 1
            content = []
            if not attr[0]:
                caption_text = " ".join(node["c"] for node in _nodes(caption)
                                        if node["t"] == "Str")
                identifiers = re.findall(r"\{#([^}\s]+)\}", caption_text)
                if identifiers:
                    attr[0] = identifiers[0]
                    for identifier in identifiers[1:]:
                        content.append({"t": "Div", "c": [[identifier, [], []], []]})
            if caption[0] is not None:
                cap_token = token + "-caption-short"
                record["caption_tokens"].append(cap_token)
                content.append(payload(cap_token, [{"t": "Para", "c": caption[0]}], kind="caption"))
                audit["counts"]["captions"] += 1
            if caption[1]:
                cap_token = token + "-caption-long"
                record["caption_tokens"].append(cap_token)
                content.append(payload(cap_token, caption[1], kind="caption"))
                audit["counts"]["captions"] += 1
            # Markdown archive inputs use simple cells. Refuse spans rather than
            # silently assigning a source header to the wrong column.
            all_rows = list(head[1]) + [row for body in bodies for row in body[2] + body[3]] + list(foot[1])
            if any(cell[2] != 1 or cell[3] != 1 for row in all_rows for cell in row[1]):
                raise ValueError("Spanning table cells need explicit column-label mapping")
            labels = [[] for _ in colspecs]
            for row in head[1]:
                if len(row[1]) != len(colspecs):
                    raise ValueError("Header width differs from declared table columns")
                for column, cell in enumerate(row[1]):
                    labels[column].extend(copy.deepcopy(cell[4]))

            def add_row(row, role, index):
                if len(row[1]) != len(colspecs):
                    raise ValueError("Row width differs from declared table columns")
                row_token = token + "-" + role + "-" + str(index)
                title = ("Table " + str(number) + " — " +
                         ("row " if role == "data" else role + " row ") + str(index))
                blocks = [heading(title, row_token + "-heading")]
                for column, cell in enumerate(row[1]):
                    cell_attr, alignment, rowspan, colspan, cell_blocks = cell
                    cell_token = row_token + "-column-" + str(column + 1)
                    label_token = cell_token + "-label"
                    label_blocks = [_para("Column " + str(column + 1) + " — header:")]
                    label_blocks.extend(copy.deepcopy(labels[column]))
                    label_blocks.append(_para("Value:"))
                    blocks.append(_div(label_token, label_blocks))
                    blocks.append(payload(cell_token, cell_blocks, cell_attr,
                                          "header" if role == "header" else "cell"))
                    record["rows"].append({"token": cell_token, "role": role,
                                            "row": index, "column": column + 1,
                                            "source_blocks_sha256": _digest(cell_blocks),
                                            "alignment": alignment, "rowspan": rowspan,
                                            "colspan": colspan})
                    audit["counts"]["cells"] += 1
                    if role == "header":
                        audit["counts"]["header_cells"] += 1
                content.append(_div(row_token, blocks, row[0]))
                audit["counts"]["rows"] += 1
                audit["counts"][{"data": "data_rows", "header": "header_rows",
                                  "footer": "footer_rows"}[role]] += 1

            for index, row in enumerate(head[1], 1):
                add_row(row, "header", index)
            data_index = 0
            header_index = len(head[1])
            for body_index, body in enumerate(bodies, 1):
                body_content_start = len(content)
                for row in body[2]:
                    header_index += 1
                    add_row(row, "header", header_index)
                for row in body[3]:
                    data_index += 1
                    add_row(row, "data", data_index)
                body_content = content[body_content_start:]
                del content[body_content_start:]
                content.append(_div(token + "-body-" + str(body_index), body_content, body[0]))
            for index, row in enumerate(foot[1], 1):
                add_row(row, "footer", index)
            # Preserve head/foot attributes without putting the prose in a table,
            # minipage, block quote, or any other indivisible layout container.
            if head[0] != ["", [], []]:
                content.insert(0, _div(token + "-head-attributes", [], head[0]))
            if foot[0] != ["", [], []]:
                content.append(_div(token + "-foot-attributes", [], foot[0]))
            return _div(token, content, attr)

        def transform(value):
            if isinstance(value, dict):
                if value.get("t") == "Table":
                    return convert_table(value)
                return {key: transform(child) for key, child in value.items()}
            if isinstance(value, list):
                return [transform(child) for child in value]
            return value

        adapted = transform(original)
        note_token = prefix + "-canonical-table-note"
        note_doc = json.loads(run("Numbered-table references point to the "
                                  "[canonical manuscript](../web/index.html); "
                                  "they are not standalone local deck numbers.\n", _READER, "json"))
        note = note_doc["blocks"][0]
        adapted["blocks"].insert(1 if adapted["blocks"] and adapted["blocks"][0]["t"] == "Header" else 0,
                                 _div(note_token, [note]))
        added_tokens.add(note_token)
        bibliography = None
        if section.name == "99_references.md":
            bibfiles = sorted(source_dir.glob("*.bib"))
            if not bibfiles:
                raise ValueError("References chapter has no bibliography inputs")
            ids = []
            for bibfile in bibfiles:
                entries = json.loads(run(bibfile.read_text(encoding="utf-8"), "biblatex", "csljson"))
                ids.extend(entry["id"] for entry in entries)
            if not ids or len({key.casefold() for key in ids}) != len(ids):
                raise ValueError("Bibliography IDs must be nonempty and unique")
            nocite = json.loads(run("---\nnocite: '@*'\n---\n", _READER, "json"))["meta"]["nocite"]
            native_input = copy.deepcopy(original)
            native_input["meta"]["nocite"] = nocite
            native = json.loads(run(json.dumps(native_input), "json", "json", "--citeproc",
                                    "--metadata=suppress-bibliography=false",
                                    *("--bibliography=" + str(path) for path in bibfiles)))
            entries = [node for node in _nodes(native) if node["t"] == "Div"
                       and "csl-entry" in node["c"][0][1]]
            actual_ids = [entry["c"][0][0].removeprefix("ref-") for entry in entries]
            if len(actual_ids) != len(ids) or set(actual_ids) != set(ids):
                raise ValueError("Native nocite bibliography omitted or duplicated records")
            entry_digests = []
            for index, entry in enumerate(entries, 1):
                entry_token = prefix + "-bibliography-" + str(index)
                # Materialize native citeproc content as normal prose. The frozen
                # renderer suppresses its own bibliography even for this chapter;
                # reserved refs/csl wrappers would allow a second citeproc to erase it.
                entry_blocks = copy.deepcopy(entry["c"][1])
                for node in _nodes(entry_blocks):
                    if (node["t"] == "Link" and node["c"][0] == ["", [], []]
                            and node["c"][1] == [{"t": "Str", "c": node["c"][2][0]}]):
                        node["c"][0][1].append("uri")
                    if node["t"] == "Span" and node["c"][0] == ["", [], []]:
                        node["c"][0][1].append("citation-literal")
                entry_document = {"pandoc-api-version": native["pandoc-api-version"],
                                  "meta": {}, "blocks": entry_blocks}
                entry_markdown = run(json.dumps(entry_document), "json", _WRITER)
                canonical_entry = json.loads(run(entry_markdown, _READER, "json"))
                before_plain = run(json.dumps({**entry_document, "blocks": _normalize(entry_blocks)}),
                                   "json", "plain", "--wrap=none")
                after_plain = run(json.dumps({**canonical_entry, "blocks": _normalize(canonical_entry["blocks"])}),
                                  "json", "plain", "--wrap=none")
                if before_plain != after_plain:
                    raise ValueError("Native bibliography materialization changed citation text: " + actual_ids[index - 1] + repr((before_plain, after_plain)))
                def literals(blocks):
                    return [[node["t"], node["c"][2] if node["t"] in {"Link", "Image"} else node["c"]]
                            for node in _nodes(blocks)
                            if node["t"] in {"Link", "Image", "Math", "Code", "CodeBlock", "RawInline"}]
                if literals(entry_blocks) != literals(canonical_entry["blocks"]):
                    raise ValueError("Native bibliography materialization changed URI/math/code literals")
                entry_blocks = canonical_entry["blocks"]
                adapted["blocks"].append(_div(entry_token, [
                    heading("Reference " + str(index), entry_token + "-heading"),
                    _div(entry_token + "-content", entry_blocks,
                         [entry["c"][0][0], [], []])]))
                added_tokens.add(entry_token)
                entry_digests.append({"id": actual_ids[index - 1],
                                      "blocks_sha256": _digest(entry["c"][1]),
                                      "display_blocks_sha256": _digest(entry_blocks)})
            adapted["meta"]["nocite"] = nocite
            bibliography = {"native_nocite": "@*", "records": len(entries),
                            "all_source_ids_present": True, "entries": entry_digests,
                            "source_ids": ids, "native_order": actual_ids,
                            "native_ast_sha256": _digest(native),
                            "materialized_as_ordinary_prose": True,
                            "display_style": "Explicit uri class on self-labelled URLs and citation-literal class on otherwise empty spans; citation text and URI targets unchanged."}

        if any(node["t"] == "Table" for node in _nodes(adapted)):
            raise ValueError("A table survived the prose transformation")
        serialized = run(json.dumps(adapted, ensure_ascii=False), "json", _WRITER, "--standalone")
        decoded = json.loads(run(serialized, _READER, "json"))
        _require_equal(adapted, decoded, section.name + " complete overlay roundtrip")
        decoded_markers = _marked(decoded)
        payload_evidence = []
        for token, expected in payloads.items():
            if token not in decoded_markers:
                raise ValueError("Converted payload disappeared: " + token)
            actual_blocks = decoded_markers[token]["c"][1]
            _require_equal(expected["blocks"], actual_blocks, token)
            payload_evidence.append({"token": token, "kind": expected["kind"],
                                     "source_blocks_sha256": _digest(expected["blocks"]),
                                     "normalized_source_sha256": _digest(_normalize(expected["blocks"])),
                                     "decoded_blocks_sha256": _digest(_normalize(actual_blocks)),
                                     "exact_content_preserved": True,
                                     "source_attributes": expected["attributes"]})
        table_by_token = {record["token"]: record["table"] for record in table_records}
        removed = object()
        def restore(value):
            if isinstance(value, dict):
                token = _token(value)
                if token in table_by_token:
                    return copy.deepcopy(table_by_token[token])
                if token in added_tokens:
                    return removed
                return {key: restore(child) for key, child in value.items()}
            if isinstance(value, list):
                result = []
                for child in value:
                    restored = restore(child)
                    if restored is not removed:
                        result.append(restored)
                return result
            return value
        restored = restore(decoded)
        restored["meta"] = copy.deepcopy(original["meta"])
        _require_equal(original, restored, section.name + " original non-table content")
        _require_equal(_sensitive(adapted), _sensitive(decoded), section.name + " URI/math content")
        file_audit = {"file": section.name, "tables": [], "payloads": payload_evidence,
                      "complete_overlay_roundtrip_exact": True,
                      "non_table_content_roundtrip_exact": True,
                      "uri_math_code_raw_inline_roundtrip_exact": True,
                      "original_ast_sha256": _digest(original),
                      "restored_ast_sha256": _digest(restored),
                      "normalized_original_ast_sha256": _digest(_normalize(original)),
                      "normalized_restored_ast_sha256": _digest(_normalize(restored)),
                      "expected_overlay_ast_sha256": _digest(_normalize(adapted)),
                      "decoded_overlay_ast_sha256": _digest(_normalize(decoded)),
                      "sensitive_inline_count": len(_sensitive(adapted)),
                      "sensitive_inline_sha256": _digest(_sensitive(decoded)),
                      "bibliography": bibliography}
        for record in table_records:
            file_audit["tables"].append({key: value for key, value in record.items() if key != "table"})
        (destination / section.name).write_text(serialized, encoding="utf-8")
        audit["patches"][section.name] = "".join(difflib.unified_diff(
            original_text.splitlines(keepends=True), serialized.splitlines(keepends=True),
            fromfile="canonical/" + section.name, tofile="slide-overlay/" + section.name))
        audit["files"].append(file_audit)
    if _hashes(source_dir) != source_hashes:
        raise ValueError("Canonical manuscript inputs changed during overlay creation")
    audit["destination_hashes"] = _hashes(destination)
    changed = {section.name for section in sections}
    if any(audit["destination_hashes"].get(name) != digest
           for name, digest in source_hashes.items() if name not in changed):
        raise ValueError("Non-chapter input bytes changed in copied destination")
    audit["assertions"] = {"source_bytes_unchanged": True, "copied_inputs_unchanged": True,
                           "no_remaining_tables": True, "all_cell_caption_payloads_exact": True,
                           "all_non_table_content_exact": True, "uri_math_unchanged": True,
                           "full_overlay_markdown_roundtrip_exact": True,
                           "bibliography_complete": True}
    return audit
