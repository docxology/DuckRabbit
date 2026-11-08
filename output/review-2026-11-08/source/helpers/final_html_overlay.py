"""Relocate native HTML into the retained, hash-bound offline asset closure.

Called once by render_candidate_final after native rendering and math hardening.
This is a full-content scrollable archive, not a projection/accessibility claim.
"""
from __future__ import annotations

import base64
import difflib
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit


_MATHJAX = "https://cdn.jsdelivr.net/npm/mathjax@4.0.0/tex-chtml.js"
_FONT = "https://cdn.jsdelivr.net/npm/@mathjax/mathjax-newcm-font@4.0.0/chtml/woff2"
_DYNAMIC = "https://cdn.jsdelivr.net/npm/@mathjax/mathjax-newcm-font@4.0.0/chtml/dynamic"
_REVEAL = "https://unpkg.com/reveal.js@5.2.1"
_SRI = "sha384-2BWc4dVaHADUocwKrUrK9u3iDwHxVMKXWEcoRmUkXYSFKhAsgVAYClu9ydNuo5Oz"
_CONFIG = re.compile(r"(<script\b[^>]*\bdata-template-mathjax-config\b[^>]*>)(.*?)(</script\s*>)", re.S | re.I)
_SCRIPT = re.compile(r"<script\b[^>]*\bsrc\s*=\s*([\"'])([^\"']+)\1[^>]*>\s*</script\s*>[ \t]*\n?", re.I)
_CSS_URL = re.compile(r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s)]+))\s*\)", re.I)
_CSS_IMPORT = re.compile(r"@import\s+(?:\"([^\"]+)\"|'([^']+)')", re.I)
_CSS_COMMENTS = re.compile(r"/\*.*?\*/", re.S)
_SLIDE_CSS = """.reveal{font-size:28px;background:#fff;color:#222}
.reveal .slides section:not(.stack){height:100%;max-height:100%;overflow-y:auto!important;overflow-x:auto!important;box-sizing:border-box;padding:0 20px 40px;text-align:left}
.reveal .slides section.stack{overflow:visible}
.reveal h1,.reveal h2{font-size:1.4em}
.reveal img{max-width:100%;max-height:55vh;object-fit:contain}
.reveal p,.reveal li,.reveal code,.reveal a{overflow-wrap:anywhere;word-break:break-word;max-width:none}
.reveal pre{white-space:pre-wrap;max-width:100%;overflow:auto}
.reveal mjx-container[display=\"true\"]{max-width:100%;overflow-x:auto;overflow-y:visible}
"""
_WEB_CSS = """<style data-duckrabbit-final-overflow>
html,body{overflow-x:auto!important}
main,.table-scroll,div.sourceCode,pre,mjx-container[display=\"true\"]{max-width:100%;overflow-x:auto;overflow-y:visible}
</style>
"""


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _text_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _confined(path: Path, root: Path) -> Path:
    """Reject symlinks as well as path escapes, including symlink ancestors."""
    absolute = Path(os.path.abspath(path))
    if not absolute.is_relative_to(root):
        raise ValueError(f"path escapes output boundary: {path}")
    for part in (absolute, *absolute.parents):
        if part.is_symlink():
            raise ValueError(f"symlink in asset path: {part}")
        if part == root:
            break
    if not absolute.resolve().is_relative_to(root):
        raise ValueError(f"resolved path escapes output boundary: {path}")
    return absolute


def _manifest(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        _confined(path, root)
        if path.is_file():
            result[path.relative_to(root).as_posix()] = _sha(path)
        elif not path.is_dir():
            raise ValueError(f"nonregular asset: {path}")
    return result


def _require_equal(actual: dict, expected: dict, context: str) -> None:
    if actual != expected:
        raise ValueError(f"{context}: missing={sorted(expected.keys() - actual.keys())}, "
                         f"extra={sorted(actual.keys() - expected.keys())}, "
                         f"changed={sorted(k for k in actual.keys() & expected.keys() if actual[k] != expected[k])}")


def _licenses(assets: Path, manifest: dict[str, str]) -> dict:
    notices = {
        "reveal.js-5.2.1/LICENSE": "Permission is hereby granted",
        "reveal.js-5.2.1/dist/theme/fonts/source-sans-pro/LICENSE": "SIL OPEN FONT LICENSE",
        "reveal.js-5.2.1/dist/theme/fonts/league-gothic/LICENSE": "SIL Open Font License (OFL)",
        "mathjax-4.0.0/mathjax/LICENSE": "Apache License",
    }
    result = {}
    for name, marker in notices.items():
        if marker not in (assets / name).read_text(encoding="utf-8"):
            raise ValueError(f"missing license notice: {name}")
        result[name] = {"sha256": manifest[name], "required_notice": marker}
    packages = (
        ("reveal.js-5.2.1/package.json", "reveal.js", "5.2.1", "MIT"),
        ("mathjax-4.0.0/mathjax/package.json", "mathjax", "4.0.0", "Apache-2.0"),
        ("mathjax-4.0.0/newcm/package.json", "@mathjax/mathjax-newcm-font", "4.0.0", "Apache-2.0"),
    )
    for name, identity, version, license_name in packages:
        metadata = json.loads((assets / name).read_text(encoding="utf-8"))
        if (metadata.get("name"), metadata.get("version"), metadata.get("license")) != (identity, version, license_name):
            raise ValueError(f"unexpected pinned asset package/license: {name}")
        result[name] = {"sha256": manifest[name], "name": identity, "version": version, "license": license_name}
    # The retained NewCM closure carries its license declaration in package.json;
    # do not invent a separate notice file or modify the retained package bytes.
    font_script = (assets / "source-web-fonts.js").read_text(encoding="utf-8")
    marker = 'node.textContent=JSON.stringify('
    if font_script.count(marker) != 1:
        raise ValueError("unexpected embedded source font metadata")
    font_metadata, _ = json.JSONDecoder().raw_decode(font_script.split(marker, 1)[1])
    if "SIL OPEN FONT LICENSE Version 1.1" not in font_metadata.get("license", ""):
        raise ValueError("source font loader lost embedded OFL notice")
    result["source-web-fonts.js"] = {
        "sha256": manifest["source-web-fonts.js"],
        "embedded_license_sha256": _text_sha(font_metadata["license"]),
        "embedded_font_faces": font_metadata["faces"],
    }
    return result


class _Assets(HTMLParser):
    """Validate browser resources without mistaking scholarly links for loads."""

    def __init__(self, path: Path, root: Path, text: str, css_seen: set[Path]):
        super().__init__(convert_charrefs=True)
        self.path, self.root, self.css_seen = path, root, css_seen
        self.references: list[dict] = []
        self.external_links = 0
        self.mathjax: list[dict] = []
        self.in_style = False
        self.feed(text)
        self.close()

    def resource(self, value: str, *, hyperlink: bool = False, inline: bool = False) -> Path | None:
        value = value.strip()
        if not value:
            raise ValueError(f"empty resource reference in {self.path}")
        if any(ord(char) < 32 for char in value) or "\\" in value:
            raise ValueError(f"invalid resource URL in {self.path}: {value!r}")
        parts = urlsplit(value)
        if parts.scheme or parts.netloc:
            if hyperlink and (parts.scheme.lower() in {"http", "https", "mailto", "tel", "ftp", "urn", "doi"} or (parts.netloc and not parts.scheme)):
                self.external_links += 1
                return None
            if inline and parts.scheme.lower() == "data" and not parts.netloc:
                return None
            raise ValueError(f"nonlocal browser resource in {self.path}: {value}")
        if not parts.path:
            if parts.fragment:
                return None
            raise ValueError(f"invalid resource path in {self.path}: {value}")
        decoded = unquote(parts.path, errors="strict")
        if decoded.startswith("/") or "\\" in decoded or any(ord(c) < 32 for c in decoded):
            raise ValueError(f"nonportable resource path in {self.path}: {value}")
        target = _confined(self.path.parent / decoded, self.root)
        if not target.is_file():
            raise ValueError(f"missing local resource in {self.path}: {value}")
        self.references.append({"url": value, "path": target.relative_to(self.root).as_posix(), "sha256": _sha(target)})
        return target

    def css(self, text: str, origin: Path | None = None) -> None:
        previous = self.path
        if origin is not None:
            self.path = origin
        try:
            text = _CSS_COMMENTS.sub("", text)
            if "\\" in text:
                # Browser CSS escapes must not hide a network resource from this
                # validator. Frozen runtime CSS has no escaped URL spellings.
                for match in _CSS_URL.finditer(text):
                    if "\\" in match.group(0):
                        raise ValueError(f"escaped CSS resource URL: {self.path}")
            for pattern in (_CSS_URL, _CSS_IMPORT):
                for match in pattern.finditer(text):
                    target = self.resource(next(group for group in match.groups() if group is not None), inline=True)
                    if target is not None and target.suffix.lower() == ".css":
                        self.stylesheet(target)
        finally:
            self.path = previous

    def stylesheet(self, path: Path) -> None:
        if path not in self.css_seen:
            self.css_seen.add(path)
            self.css(path.read_text(encoding="utf-8"), path)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "base":
            raise ValueError(f"base URL defeats document-relative portability: {self.path}")
        if tag == "style":
            self.in_style = True
        if tag == "meta" and values.get("http-equiv", "").lower() == "refresh":
            raise ValueError(f"unexpected HTML refresh: {self.path}")
        for attribute in ("src", "href", "data-src", "poster", "xlink:href", "data-background-image", "data-background-video", "data-background-iframe"):
            if attribute not in values:
                continue
            value = values[attribute]
            if value is None:
                raise ValueError(f"missing {attribute} value in {self.path}")
            target = self.resource(value, hyperlink=tag in {"a", "area"} and attribute == "href", inline=tag in {"img", "source", "image"})
            if target is not None and tag == "link" and "stylesheet" in values.get("rel", "").split():
                self.stylesheet(target)
            if target is not None and attribute == "src" and "integrity" in values:
                tokens = values["integrity"].split()
                if not tokens:
                    raise ValueError(f"empty integrity declaration: {self.path}")
                for token in tokens:
                    algorithm, _, expected = token.partition("-")
                    if algorithm not in {"sha256", "sha384", "sha512"}:
                        raise ValueError(f"unsupported integrity token: {token}")
                    actual = base64.b64encode(hashlib.new(algorithm, target.read_bytes()).digest()).decode("ascii")
                    if actual != expected:
                        raise ValueError(f"resource SRI mismatch: {target}")
            if tag == "script" and attribute == "src" and "mathjax-4.0.0/mathjax/tex-chtml.js" in value:
                if values.get("integrity") != _SRI or values.get("crossorigin") != "anonymous":
                    raise ValueError(f"MathJax loader hardening changed: {self.path}")
                self.mathjax.append({"src": value, "integrity": values["integrity"], "sha256": _sha(target)})
        if "srcset" in values or "data-srcset" in values:
            for attribute in ("srcset", "data-srcset"):
                if attribute in values:
                    for candidate in values[attribute].split(","):
                        self.resource(candidate.strip().split()[0])
        if "style" in values:
            self.css(values["style"])
        if tag == "object" and "data" in values:
            self.resource(values["data"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self.in_style = False

    def handle_data(self, data: str) -> None:
        if self.in_style:
            self.css(data)


def _relocate(text: str, slide: bool, assets: Path) -> tuple[str, list[dict]]:
    prefix = "../web/assets/" if slide else "assets/"
    changes: list[dict] = []
    for old, new in (
        (_REVEAL, prefix + "reveal.js-5.2.1"),
        (_MATHJAX, prefix + "mathjax-4.0.0/mathjax/tex-chtml.js"),
        (_FONT, prefix + "mathjax-4.0.0/newcm/chtml/woff2"),
        (_DYNAMIC, prefix + "mathjax-4.0.0/newcm/chtml/dynamic"),
    ):
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            changes.append({"old": old, "new": new, "occurrences": count})
    if slide:
        for plugin in ("notes", "search", "zoom"):
            old = prefix + f"reveal.js-5.2.1/dist/plugin/{plugin}.js"
            new = prefix + f"reveal.js-5.2.1/plugin/{plugin}/{plugin}.js"
            if text.count(old) != 1:
                raise ValueError(f"unexpected native Reveal plugin route: {plugin}")
            text = text.replace(old, new)
            changes.append({"old": old, "new": new, "occurrences": 1,
                            "asset_sha256": _sha(assets / f"reveal.js-5.2.1/plugin/{plugin}/{plugin}.js")})
        legacy = prefix + "reveal.js-5.2.1/dist/plugin/math.js"
        matches = [match for match in _SCRIPT.finditer(text) if match.group(2) == legacy]
        if len(matches) != 1 or "RevealMath" in text:
            raise ValueError("unexpected legacy Reveal math plugin configuration")
        text = text[:matches[0].start()] + text[matches[0].end():]
        changes.append({"old": matches[0].group(0), "new": "", "occurrences": 1})
        if prefix + "reveal.js-5.2.1/dist/theme/white.css" not in text:
            raise ValueError("native archive did not use pinned Reveal white theme")
        if 'href="digital-review.css"' not in text:
            raise ValueError("native archive did not include digital-review.css")
    configs = list(_CONFIG.finditer(text))
    if len(configs) != 1:
        raise ValueError("expected exactly one hardened MathJax configuration")
    match = configs[0]
    config = match.group(2)
    if not re.search(r"\bmathjax\s*:", config):
        old = "window.MathJax = window.MathJax || {};"
        if config.count(old) != 1:
            raise ValueError("unexpected MathJax initialization")
        new = old + "\nwindow.MathJax.loader = Object.assign({},window.MathJax.loader,{paths:{mathjax:" + json.dumps(prefix + "mathjax-4.0.0/mathjax") + "}});"
        config = config.replace(old, new)
        changes.append({"old": old, "new": new, "occurrences": 1})
    for key, suffix in (("mathjax", "mathjax"), ("fontURL", "newcm/chtml/woff2"), ("dynamicPrefix", "newcm/chtml/dynamic")):
        relative = prefix + "mathjax-4.0.0/" + suffix
        pattern = re.compile(r"(\b" + key + r"\s*:\s*)([\"'])" + re.escape(relative) + r"\2")
        hits = list(pattern.finditer(config))
        if len(hits) != 1:
            raise ValueError(f"unexpected local MathJax {key} configuration")
        target = assets / "mathjax-4.0.0" / suffix
        if not target.is_dir():
            raise ValueError(f"missing dynamic MathJax asset root: {target}")
        old = hits[0].group(0)
        new = hits[0].group(1) + "new URL(" + json.dumps(relative) + ",document.baseURI).href"
        config = config.replace(old, new, 1)
        changes.append({"old": old, "new": new, "occurrences": 1})
    text = text[:match.start(2)] + config + text[match.end(2):]
    if not slide:
        # Native web CSS clips both document roots. Remove those declarations,
        # rather than relying on a later override to mask hidden overflow.
        def open_overflow(style: re.Match) -> str:
            body = style.group(2)
            pattern = re.compile(r"\boverflow-x\s*:\s*(?:hidden|clip)\b", re.I)
            for hit in pattern.finditer(body):
                changes.append({"old": hit.group(0), "new": "overflow-x: auto", "occurrences": 1})
            return style.group(1) + pattern.sub("overflow-x: auto", body) + style.group(3)
        text = re.sub(r"(<style\b[^>]*>)(.*?)(</style\s*>)", open_overflow, text, flags=re.S | re.I)
        if text.count("</head>") != 1 or "data-duckrabbit-final-overflow" in text:
            raise ValueError("unexpected native HTML head or repeated finalization")
        text = text.replace("</head>", _WEB_CSS + "</head>", 1)
        changes.append({"old": "</head>", "new": _WEB_CSS + "</head>", "occurrences": 1})
    return text, changes


def finalize_html(output: Path, source_assets: Path) -> dict:
    """Copy the exact prior closure, relocate twelve pages, and return evidence.

    Raises on missing/changed assets, unexpected native routes, nonlocal browser
    loads, path escapes, lost loader SRI, or an incomplete page roster. Ordinary
    external scholarly hyperlinks remain untouched. No renderer is invoked.
    """
    output, source_assets = Path(output).absolute(), Path(source_assets).absolute()
    if not output.is_dir() or not source_assets.is_dir():
        raise ValueError("finalization requires existing output and retained asset directories")
    for root in (output, source_assets):
        if any(path.is_symlink() for path in (root, *root.parents)):
            raise ValueError(f"symlink in finalization root: {root}")
    output, source_assets = output.resolve(), source_assets.resolve()
    assets = _confined(output / "web/assets", output)
    if assets == source_assets or assets.is_relative_to(source_assets) or source_assets.is_relative_to(output):
        raise ValueError("retained asset closure must be outside the fresh output tree")
    receipt = source_assets.parents[3] / "render-receipt.json"
    receipt_bytes = receipt.read_bytes()
    prior = json.loads(receipt_bytes)
    expected = {name.removeprefix("web/assets/"): digest for name, digest in prior["outputs"].items() if name.startswith("web/assets/")}
    if not expected:
        raise ValueError("prior receipt does not bind the local asset closure")
    source_manifest = _manifest(source_assets)
    _require_equal(source_manifest, expected, "retained local asset closure differs from prior receipt")
    licenses = _licenses(source_assets, source_manifest)
    native_manifest = json.loads((source_assets / "mathjax-4.0.0/asset-manifest.json").read_text(encoding="utf-8"))
    if native_manifest.get("packages") != {"mathjax": "4.0.0", "@mathjax/mathjax-newcm-font": "4.0.0"}:
        raise ValueError("unexpected native MathJax closure identities")
    for row in native_manifest["files"]:
        name = row["path"].removeprefix("assets/")
        if source_manifest.get(name) != row["sha256"]:
            raise ValueError(f"native MathJax manifest mismatch: {name}")
    loader = source_assets / "mathjax-4.0.0/mathjax/tex-chtml.js"
    loader_sri = "sha384-" + base64.b64encode(hashlib.sha384(loader.read_bytes()).digest()).decode("ascii")
    if loader_sri != _SRI:
        raise ValueError("retained MathJax loader differs from pinned SRI")
    slides = sorted((output / "slides").glob("*_slides.html"))
    pages = [output / "web/index.html", *slides]
    if len(slides) != 11 or not pages[0].is_file():
        raise ValueError("final HTML roster must contain the manuscript and eleven decks")
    for path in pages:
        _confined(path, output)
    evidence = _confined(output / "html-overlay-evidence", output)
    if evidence.exists():
        raise FileExistsError(f"HTML finalization evidence already exists: {evidence}")
    if assets.exists():
        for name, digest in _manifest(assets).items():
            if expected.get(name) != digest:
                raise ValueError(f"native local asset differs from retained closure: {name}")
    for name in source_manifest:
        destination = _confined(assets / name, output)
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_assets / name, destination)
    _require_equal(_manifest(assets), source_manifest, "copied local asset closure changed")
    css_path = _confined(output / "slides/digital-review.css", output)
    old_css = css_path.read_bytes().decode("utf-8") if css_path.exists() else ""
    css_path.write_text(_SLIDE_CSS, encoding="utf-8")
    evidence.mkdir()
    records = []
    css_seen: set[Path] = set()
    for path in pages:
        original = path.read_bytes().decode("utf-8")
        updated, replacements = _relocate(original, path in slides, assets)
        validator = _Assets(path, output, updated, css_seen)
        if len(validator.mathjax) != 1:
            raise ValueError(f"missing or duplicate pinned MathJax loader: {path}")
        path.write_text(updated, encoding="utf-8")
        patch = "".join(difflib.unified_diff(original.splitlines(True), updated.splitlines(True),
                       fromfile="native/" + path.relative_to(output).as_posix(),
                       tofile="offline/" + path.relative_to(output).as_posix()))
        patch_path = evidence / (path.parent.name + "-" + path.stem + ".patch")
        patch_path.write_text(patch, encoding="utf-8")
        records.append({"path": path.relative_to(output).as_posix(), "before_sha256": _text_sha(original),
                        "after_sha256": _text_sha(updated), "patch": patch_path.relative_to(output).as_posix(),
                        "patch_sha256": _text_sha(patch), "relocations": replacements,
                        "local_references": validator.references, "external_hyperlinks_retained": validator.external_links,
                        "mathjax_loader": validator.mathjax[0]})
    css_patch = "".join(difflib.unified_diff(old_css.splitlines(True), _SLIDE_CSS.splitlines(True),
                       fromfile="native/slides/digital-review.css", tofile="offline/slides/digital-review.css"))
    css_patch_path = evidence / "digital-review.css.patch"
    css_patch_path.write_text(css_patch, encoding="utf-8")
    _require_equal(_manifest(source_assets), source_manifest, "retained asset closure changed during relocation")
    _require_equal(_manifest(assets), source_manifest, "destination asset closure changed during relocation")
    result = {
        "schema_version": "duckrabbit-final-html-overlay-v1",
        "profile": "full-content scrollable archive; not projection/accessibility certified",
        "helper_sha256": _sha(Path(__file__)), "source_assets": str(source_assets),
        "source_receipt": str(receipt), "source_receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "asset_manifest": source_manifest, "asset_file_count": len(source_manifest), "licenses": licenses,
        "mathjax_loader_sri": loader_sri, "html": records,
        "css": {"path": "slides/digital-review.css", "before_sha256": _text_sha(old_css),
                "after_sha256": _text_sha(_SLIDE_CSS), "patch": css_patch_path.relative_to(output).as_posix(),
                "patch_sha256": _text_sha(css_patch)},
        "validation": {"html_count": len(records), "exact_prior_closure": True,
                       "document_relative_mathjax_roots_per_page": 3,
                       "local_resource_paths_and_sri": True, "linked_stylesheets_checked": len(css_seen),
                       "external_browser_resource_loads": 0, "plugin_shims_created": False},
    }
    manifest_path = evidence / "asset-manifest.json"
    manifest_path.write_text(json.dumps(source_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["asset_manifest_file"] = {"path": manifest_path.relative_to(output).as_posix(), "sha256": _sha(manifest_path)}
    (evidence / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
