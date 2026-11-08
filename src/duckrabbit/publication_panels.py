"""Source-bound readability variants, not additional scientific figures.

The verifier is a same-code replay oracle, not independent visual or observer
validation. Complete source records and plotted summary arrays remain in the
original source sidecars; audio extrema do not reconstruct full sample arrays.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, features

from . import publication as pub
from .render import jsonable

SCHEMA_VERSION = "duckrabbit/readable-panels/v1"
ROLE = "readability_detail_not_new_scientific_figure"
REPORT_PATH = "reports/readable_figure_panels.json"
# The sequence determines delivery order; record counts come only from source.
_COLLECTIONS = {
    "catalog_matrix": ("entries", "illusion_id"),
    "audio_signals": ("signals", "illusion_id"),
    "scholarship_map": ("rows", "illusion_id"),
    "formalism_traceability": ("definitions", "label"),
}
WIDTH = 1200
BODY_SIZE = 24
MARGIN = 36
GAP = 24
_TITLES = {
    "catalog_matrix": "Catalog facets",
    "audio_signals": "Canonical audio summaries",
    "scholarship_map": "Source roles and limitations",
    "formalism_traceability": "Equation-to-code traceability",
}


def _canonical(value: object) -> str:
    # Unlike Python equality, JSON equality does not equate True with 1.
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_path(root: Path, relative: str, *, existing: bool = True) -> Path:
    """No traversal, aliases, or symlinks, including intermediate directories."""
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("invalid readable-panel path")
    parts = relative.split("/")
    if any(part in {"", ".", ".."} for part in parts) or Path(relative).is_absolute():
        raise ValueError("unsafe readable-panel path")
    root = Path(root).absolute()
    if root.is_symlink():
        raise ValueError("readable-panel output root is a symlink")
    candidate = root
    for part in parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError("readable-panel path contains a symlink")
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError("readable-panel path escapes output root")
    if existing and not candidate.is_file():
        raise ValueError(f"missing readable-panel file: {relative}")
    return candidate


def _environment() -> dict[str, object]:
    return {
        **pub._render_environment(),
        "panel_producer": "duckrabbit.publication_panels.generate_readable_figure_panels",
        "panel_producer_sha256": _digest(Path(__file__)),
        "python": sys.version,
        "platform": platform.platform(),
        "freetype": features.version("freetype2"),
        "zlib": features.version("zlib"),
        "helpers": "duckrabbit.publication: measured _text_height/_text_block/_font, _draw_waveform, _draw_spectrum, _save",
    }


def _load_sources(root: Path) -> dict[str, dict[str, object]]:
    sources = {}
    builders = {stem: builder for _, stem, builder in pub._figure_builders()}
    for stem, (collection, identity) in _COLLECTIONS.items():
        path = _safe_path(root, f"data/{stem}.json")
        raw = path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict) or (
            payload.get("schema_version") != "duckrabbit/figure-source/v1"
            or payload.get("figure_label") != f"fig:{stem}"
            or payload.get("figure_stem") != stem
            or payload.get("generator") != f"duckrabbit.publication.{builders[stem].__name__}"
            or type(payload.get("seed")) is not int or payload["seed"] != 0
            or _canonical(payload.get("parameters")) != _canonical({"seed": 0, "figure_stem": stem})
            or not isinstance(payload.get("data"), dict)
        ):
            raise ValueError(f"stale readable-panel source identity: {stem}")
        records = payload["data"].get(collection)
        if not isinstance(records, list) or not records:
            raise ValueError(f"missing readable-panel source records: {stem}")
        seen = set()
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get(identity), str) or not record[identity].strip():
                raise ValueError(f"invalid readable-panel record identity: {stem}")
            if record[identity] in seen:
                raise ValueError(f"duplicate readable-panel record identity: {stem}")
            seen.add(record[identity])
        # Bind the digest to exactly these bytes: a concurrent staged
        # replacement must not certify records that were never replayed.
        sources[stem] = {"payload": payload,
                         "sha256": hashlib.sha256(raw).hexdigest()}
    return sources


def _value(value: object) -> str:
    if isinstance(value, list):
        return "; ".join(_value(item) for item in value) if value else "none (empty list)"
    if isinstance(value, dict):
        return "; ".join(f"{key}: {_value(item)}" for key, item in value.items())
    if value is None:
        return "not specified (null)"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _block(text: str, x: int, y: int, width: int, size: int = BODY_SIZE) -> dict[str, object]:
    return {"text": text, "x": x, "y": y, "width": width,
            "height": pub._text_height(text, width, size), "font_size": size}


def _columns(texts: list[str], y: int) -> tuple[list[dict[str, object]], int]:
    """Balance complete fields; never split or abbreviate a field's contents."""
    width = (WIDTH - 2 * MARGIN - GAP) // 2
    heights = [pub._text_height(text, width, BODY_SIZE) + 12 for text in texts]
    split = min(range(len(texts) + 1), key=lambda n: max(sum(heights[:n]), sum(heights[n:])))
    blocks = []
    bottoms = []
    for column, group in enumerate((texts[:split], texts[split:])):
        top = y
        for text in group:
            block = _block(text, MARGIN + column * (width + GAP), top, width)
            blocks.append(block)
            top += block["height"] + 12
        bottoms.append(top)
    return blocks, max(bottoms)


def _audio_content(record: dict[str, object], y: int) -> tuple[list[dict[str, object]], int, int]:
    waveform, spectrum = record["waveform"], record["spectrum"]
    blocks = []
    # These are real extrema bins and mean-channel spectral magnitudes, not
    # reconstructed sample arrays. Each source channel gets its own lane.
    channels = waveform["channel_indices"]
    blocks.append(_block("Per-channel extrema; normalized amplitude", MARGIN, y, 540))
    blocks.append(_block("Relative spectral band peak (0–1)", 632, y, 532))
    plot_top = max(block["y"] + block["height"] for block in blocks) + 14
    plot_bottom = plot_top + max(150, len(channels) * 74)
    blocks.append(_block(f"Time: 0–{waveform['duration_seconds']} s; range −1 to +1", MARGIN, plot_bottom + 16, 540))
    blocks.append(_block(f"Frequency: 0–{spectrum['band_edges_hz'][-1]} Hz", 632, plot_bottom + 16, 532))
    for lane, channel in enumerate(channels):
        blocks.append(_block(f"ch{channel}", MARGIN, plot_top + lane * 74 + 12, 75))
    metric_texts = [f"{metric['name']}: {_value(metric['value'])} {metric['unit']}"
                    for metric in record["metrics"]["records"]]
    metric_top = max(block["y"] + block["height"] for block in blocks) + 18
    metrics, bottom = _columns(metric_texts, metric_top)
    blocks.extend(metrics)
    notes = [
        f"Canonical SHA-256: {record['canonical_digest']}",
        "All samples contribute to half-open extrema bins; vertical ranges are not an exact waveform or event time. No listener data.",
        f"Spectrum: {len(spectrum['band_values'])} band maxima of mean-channel |rFFT|/N, unwindowed, no doubling; DC–Nyquist, relative to largest band. Full definitions: source JSON.",
    ]
    note_blocks, bottom = _columns(notes, bottom + 8)
    blocks.extend(note_blocks)
    return blocks, bottom, plot_top


def _render_panel(stem: str, record: dict[str, object], path: Path) -> dict[str, object]:
    identity = _COLLECTIONS[stem][1]
    record_id = record[identity]
    title = f"{_TITLES[stem]} — {record_id}"
    blocks = [_block(title, MARGIN, 28, WIDTH - 2 * MARGIN, 32)]
    top = blocks[0]["y"] + blocks[0]["height"] + 24
    plot_top = None
    if stem == "audio_signals":
        content, bottom, plot_top = _audio_content(record, top)
    else:
        texts = [f"{key}: {_value(value)}" for key, value in record.items() if key != identity]
        content, bottom = _columns(texts, top)
    blocks.extend(content)
    boundary = {
        "catalog_matrix": "Catalog facets describe construction and status, not observed perception.",
        "audio_signals": "Synthetic signal summaries; complete extrema/spectral arrays and definitions: source JSON. No listener data.",
        "scholarship_map": "Source roles are not evidence-strength scores; engineering and limitations remain distinct.",
        "formalism_traceability": "Formal definitions link implementation and tests; they are not empirical observer evidence.",
    }[stem]
    footer = _block(boundary, MARGIN, bottom + 16, WIDTH - 2 * MARGIN)
    blocks.append(footer)
    height = footer["y"] + footer["height"] + MARGIN
    # Fail visibly rather than shrinking typography or silently clipping new
    # source records beyond the declared delivery boundary.
    scale = min(807 / WIDTH, 605 / height)
    minimum_text_px = pub._font(BODY_SIZE).size * scale
    if minimum_text_px < 16:
        raise ValueError(f"readable panel exceeds 807×605 text-fit boundary: {title} ({height}px tall)")
    image = Image.new("RGB", (WIDTH, height), pub.CANVAS)
    draw = ImageDraw.Draw(image)
    for block in blocks:
        pub._text_block(draw, (block["x"], block["y"]), block["text"], block["width"], block["font_size"])
    if plot_top is not None:
        waveform, spectrum = record["waveform"], record["spectrum"]
        for lane, channel in enumerate(waveform["channel_indices"]):
            box = (120, plot_top + lane * 74, 576, plot_top + lane * 74 + 60)
            draw.rectangle(box, outline=pub.MUTED, width=1)
            pub._draw_waveform(draw, waveform, box, channel=channel, color=pub.ACCENT,
                               x_range=(0.0, waveform["duration_seconds"]))
        spectrum_bottom = plot_top + max(150, len(waveform["channel_indices"]) * 74)
        box = (632, plot_top, 1164, spectrum_bottom)
        draw.rectangle(box, outline=pub.MUTED, width=1)
        pub._draw_spectrum(draw, spectrum, box)
    digest = pub._save(image, path)
    return {"sha256": digest, "title": title,
            "alt_text": "\n".join(block["text"] for block in blocks),
            "width_px": WIDTH, "height_px": height, "record_ids": [record_id],
            "display": {"fit_width_px": 807, "fit_height_px": 605,
                        "minimum_text_px": minimum_text_px, "text_blocks": blocks}}


def _build(destination: Path, sources: dict[str, dict[str, object]]) -> dict[str, object]:
    figures = []
    for stem, (collection, _) in _COLLECTIONS.items():
        panels = []
        for index, record in enumerate(sources[stem]["payload"]["data"][collection], 1):
            relative = f"figures/{stem}-detail-{index:02d}.png"
            target = _safe_path(destination, relative, existing=False)
            panel = _render_panel(stem, record, target)
            panels.append({"path": f"output/{relative}", "index": index, **panel})
        figures.append({"label": f"fig:{stem}", "stem": stem,
                        "source_data": f"output/data/{stem}.json",
                        "source_data_sha256": sources[stem]["sha256"],
                        "panels": panels})
    return {"schema_version": SCHEMA_VERSION, "role": ROLE,
            "panel_count": sum(len(figure["panels"]) for figure in figures),
            "render_environment": _environment(), "figures": figures}


def generate_readable_figure_panels(output_dir: Path) -> dict[str, object]:
    """Render detail variants from the just-generated canonical sidecars."""
    root = Path(output_dir)
    report = _build(root, _load_sources(root))
    pub._write_json(_safe_path(root, REPORT_PATH, existing=False), report)
    return report


def validate_readable_figure_panels(output_dir: Path, *, replay_sources: bool = True) -> dict[str, object]:
    """Reject missing/extra/tampered panels and stale code/font/source identity.

    By default replay the four trusted scientific builders too, so updating
    report and source hashes together cannot certify substituted facts. The
    publication derivation gate may disable that duplicate source replay only
    after it has itself replayed every scientific source and raster.
    """
    root = Path(output_dir)
    report = json.loads(_safe_path(root, REPORT_PATH).read_text(encoding="utf-8"))
    if not isinstance(report, dict) or report.get("render_environment") != _environment():
        raise ValueError("readable-panel renderer/font/dependency provenance is stale")
    sources = _load_sources(root)
    with TemporaryDirectory(prefix=".duckrabbit-panels-replay-", dir=root.parent) as temporary:
        destination = Path(temporary)
        if replay_sources:
            for label, stem, builder in pub._figure_builders():
                if stem not in _COLLECTIONS:
                    continue
                _, data = builder(destination / f"{stem}.png")
                expected = jsonable({"schema_version": "duckrabbit/figure-source/v1",
                    "figure_label": label, "figure_stem": stem,
                    "generator": f"duckrabbit.publication.{builder.__name__}",
                    "seed": 0, "parameters": {"seed": 0, "figure_stem": stem}, "data": data})
                if _canonical(sources[stem]["payload"]) != _canonical(expected):
                    raise ValueError(f"readable-panel source disagrees with live derivation: {stem}")
        expected = _build(destination, sources)
        if _canonical(report) != _canonical(expected):
            raise ValueError("readable-panel report disagrees with exact source/raster replay")
        expected_paths = set()
        for figure in expected["figures"]:
            for panel in figure["panels"]:
                relative = panel["path"].removeprefix("output/")
                expected_paths.add(relative)
                actual = _safe_path(root, relative)
                if _digest(actual) != panel["sha256"]:
                    raise ValueError(f"readable-panel raster disagrees with live derivation: {relative}")
        actual_paths = {f"figures/{path.name}" for path in (root / "figures").glob("*-detail-*")}
        if actual_paths != expected_paths:
            raise ValueError("readable-panel delivery contains missing/extra/unrelated detail files")
    return report


__all__ = ["generate_readable_figure_panels", "validate_readable_figure_panels"]
