"""Deterministic publication figures, tables, and source-data registries."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import functools
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
from tempfile import TemporaryDirectory
from collections.abc import Mapping
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont, __version__ as PILLOW_VERSION

from .artifacts import AudioBuffer, AudiovisualTimeline, CanonicalArtifact, VideoSequence
from .canonical import canonical_digest
from .claims import default_claim_registry
from .cover import install_cover
from .evidence import load_evidence_matrix
from .formalism import formalism_registry, validate_formalism_registry
from .generators import DuckRabbitParams, default_parameters, default_registry
from .io import atomic_write_text
from .metrics import COMPUTATION_VERSION, _relative_luminance, measure_artifact
from .observer_analysis import default_model_specs, default_study_design
from .parameters import (
    GrayscaleLevels,
    PixelDimension,
    QuantizationLevels,
)
from .render import jsonable
from .publication_specs import CaptionSpec
from .synthetic_psychophysics import default_duck_rabbit_diagnostic
from .taxonomy import ClaimLevel, ImplementationStatus, Modality, taxonomy_entries


CANVAS = (255, 255, 255)
INK = (24, 31, 42)
MUTED = (86, 96, 112)
ACCENT = (25, 119, 181)
GREEN = (34, 139, 94)
AMBER = (211, 139, 37)
RED = (177, 61, 61)


_FONT_CANDIDATES = (
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:/Windows/Fonts/arial.ttf",
)


@functools.lru_cache(maxsize=64)
def _font(size: int) -> ImageFont.FreeTypeFont:
    """Resolve the figure font deterministically for the running platform.

    ``DUCKRABBIT_FONT_PATH`` wins when set; otherwise the first available
    candidate is used. The renderer never falls back to a bitmap default:
    every layout coordinate assumes TrueType metrics, so a silent downgrade
    would corrupt figures instead of failing loudly.
    """
    size = max(1, int(round(size * 1.10)))
    env_path = os.environ.get("DUCKRABBIT_FONT_PATH")
    for font_path in ((env_path,) if env_path else ()) + _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue
    raise RuntimeError(
        "no TrueType font found for publication figures; "
        "set DUCKRABBIT_FONT_PATH to an absolute .ttf path"
    )


def _image(artifact: object) -> Image.Image:
    pixels = np.asarray(getattr(artifact, "pixels"), dtype=np.float32)
    values = np.clip(np.round(pixels * 255), 0, 255).astype(np.uint8)
    mode = getattr(artifact, "mode", "L")
    if mode == "RGB" and values.ndim == 3:
        return Image.fromarray(values, mode="RGB")
    return Image.fromarray(values.squeeze(), mode="L")


def _text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int = 20, fill: tuple[int, int, int] = INK) -> None:
    draw.text(xy, value, font=_font(size), fill=fill)


def _wrapped(value: object, width: int, size: int = 16) -> str:
    """Wrap to measured pixels, retaining paragraphs and complete content."""
    font = _font(size)
    lines = []
    for paragraph in str(value).split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}" if line else word
            if font.getlength(candidate) <= width:
                line = candidate
                continue
            if line:
                lines.append(line)
            line = ""
            # Long identifiers/paths have no whitespace; split only when needed.
            for character in word:
                if line and font.getlength(line + character) > width:
                    lines.append(line)
                    line = ""
                line += character
        lines.append(line)
    return "\n".join(lines)


def _text_height(value: object, width: int, size: int = 16) -> int:
    """Use the same Pillow bounds as the corresponding text block."""
    bounds = ImageDraw.Draw(Image.new("RGB", (1, 1))).multiline_textbbox(
        (0, 0), _wrapped(value, width, size), font=_font(size), spacing=4,
    )
    return bounds[3] - bounds[1]


def _text_block(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: object,
    width: int,
    size: int = 16,
    fill: tuple[int, int, int] = INK,
) -> int:
    """Draw pixel-wrapped text with its actual ink anchored at ``xy``."""
    font = _font(size)
    wrapped = _wrapped(value, width, size)
    bounds = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=4)
    origin = (xy[0] - bounds[0], xy[1] - bounds[1])
    draw.multiline_text(origin, wrapped, font=font, fill=fill, spacing=4)
    return bounds[3] - bounds[1]




def _save(image: Image.Image, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    # A fixed 300 dpi pHYs chunk keeps print/layout sizing deterministic.
    image.save(path, format="PNG", optimize=False, dpi=(300, 300))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _visual_qa(path: Path) -> dict[str, object]:
    """Record dimensions and a deterministic thumbnail digest for QA."""
    with Image.open(path) as image:
        thumbnail = image.convert("RGB").copy()
        thumbnail.thumbnail((320, 320), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        thumbnail.save(buffer, format="PNG", optimize=True)
        return {
            "width_px": image.width,
            "height_px": image.height,
            "mode": image.mode,
            "thumbnail_width_px": thumbnail.width,
            "thumbnail_height_px": thumbnail.height,
            "thumbnail_sha256": hashlib.sha256(buffer.getvalue()).hexdigest(),
            "scales": ["full", "thumbnail"],
        }


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(path, json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n")


def _line_plot(
    draw: ImageDraw.ImageDraw,
    values: Iterable[float],
    box: tuple[int, int, int, int],
    color: tuple[int, int, int] = ACCENT,
    value_range: tuple[float, float] | None = None,
) -> None:
    values = tuple(float(value) for value in values)
    if not values:
        return
    left, top, right, bottom = box
    low, high = value_range if value_range is not None else (min(values), max(values))
    span = high - low or 1.0
    points = []
    for index, value in enumerate(values):
        x = left if len(values) == 1 else int(left + (right - left) * index / (len(values) - 1))
        y = int(bottom - (value - low) / span * (bottom - top))
        points.append((x, y))
    if len(points) > 1:
        draw.line(points, fill=color, width=4)
    for x, y in points[:: max(1, len(points) // 12)]:
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color)


def _coordinate_plot(
    draw: ImageDraw.ImageDraw,
    timestamps: Iterable[float],
    values: Iterable[float],
    box: tuple[int, int, int, int],
    color: tuple[int, int, int],
    *,
    x_range: tuple[float, float],
    value_range: tuple[float, float],
) -> None:
    left, top, right, bottom = box
    start, end = x_range
    low, high = value_range
    points = [
        (int(left + (float(timestamp) - start) / (end - start) * (right - left)),
         int(bottom - (float(value) - low) / (high - low) * (bottom - top)))
        for timestamp, value in zip(timestamps, values, strict=True)
    ]
    if len(points) > 1:
        draw.line(points, fill=color, width=4)
    elif points:
        draw.point(points[0], fill=color)


def _audio_waveform(artifact: AudioBuffer, *, max_bins: int = 350) -> dict[str, object]:
    """Aggregate every sample into disjoint, channel-preserving extrema bins."""
    if max_bins < 1:
        raise ValueError("waveform max_bins must be positive")
    bin_width = max(1, (artifact.sample_count + max_bins - 1) // max_bins)
    starts = np.arange(0, artifact.sample_count, bin_width)
    stops = np.minimum(starts + bin_width, artifact.sample_count)
    return {
        "bin_start_samples": starts,
        "bin_stop_samples_exclusive": stops,
        "minimum": np.minimum.reduceat(artifact.samples, starts, axis=0),
        "maximum": np.maximum.reduceat(artifact.samples, starts, axis=0),
        "channel_indices": list(range(artifact.channels)),
        "aggregation": "per-channel minimum and maximum of all samples in each half-open bin; no downmix or point decimation",
        "display": "vertical min/max range at the midpoint of first/last sample timestamps in each bin; not an exact waveform or within-bin event time",
        "display_timestamp_rule": "(bin_start_samples + bin_stop_samples_exclusive - 1) / (2 * sample_rate_hz); not the extremum timestamp",
        "sample_rate_hz": artifact.sample_rate.value,
        "sample_count": artifact.sample_count,
        "duration_seconds": artifact.duration_seconds,
    }


def _draw_waveform(
    draw: ImageDraw.ImageDraw,
    waveform: Mapping[str, object],
    box: tuple[int, int, int, int],
    *,
    channel: int,
    color: tuple[int, int, int],
    x_range: tuple[float, float],
) -> None:
    """Draw extrema without connecting bins into fictitious sample traces."""
    left, top, right, bottom = box
    rate = float(waveform["sample_rate_hz"])
    for start, stop, low, high in zip(
        waveform["bin_start_samples"], waveform["bin_stop_samples_exclusive"],
        np.asarray(waveform["minimum"])[:, channel], np.asarray(waveform["maximum"])[:, channel], strict=True,
    ):
        timestamp = (float(start) + float(stop) - 1) / (2 * rate)
        x = round(left + (timestamp - x_range[0]) / (x_range[1] - x_range[0]) * (right - left))
        y_high = round(bottom - (float(high) + 1) / 2 * (bottom - top))
        y_low = round(bottom - (float(low) + 1) / 2 * (bottom - top))
        draw.line((x, y_high, x, y_low), fill=color, width=2)


def _audio_spectrum(artifact: AudioBuffer) -> dict[str, object]:
    frequencies = np.fft.rfftfreq(artifact.sample_count, d=1.0 / artifact.sample_rate.value)
    magnitudes = np.mean(np.abs(np.fft.rfft(artifact.samples, axis=0)), axis=1) / artifact.sample_count
    edges = np.linspace(0.0, artifact.sample_rate.value / 2.0, 49)
    band_indices = np.clip(np.searchsorted(edges, frequencies, side="right") - 1, 0, 47)
    band_values = np.zeros(48)
    np.maximum.at(band_values, band_indices, magnitudes)
    scale = max(float(np.max(band_values)), 1e-12)
    return {
        "band_edges_hz": edges,
        "band_values": band_values,
        "plotted_values": band_values / scale,
        "aggregation": "maximum magnitude in each band; left-inclusive, right-exclusive; final band includes Nyquist",
        "channel_rule": "arithmetic mean of per-channel rFFT magnitudes (no waveform downmix)",
        "channel_indices": list(range(artifact.channels)),
        "window": "rectangular (unwindowed)",
        "fft_normalization": "abs(rfft) / sample_count; no one-sided doubling",
        "display_normalization": "band_values / max(max(band_values), 1e-12)",
        "normalization_scale": scale,
        "sample_count": artifact.sample_count,
        "sample_rate_hz": artifact.sample_rate.value,
        "fft_bin_spacing_hz": artifact.sample_rate.value / artifact.sample_count,
    }


def _draw_spectrum(
    draw: ImageDraw.ImageDraw,
    spectrum: Mapping[str, object],
    box: tuple[int, int, int, int],
) -> None:
    edges = np.asarray(spectrum["band_edges_hz"])
    values = np.asarray(spectrum["plotted_values"])
    left, top, right, bottom = box
    for index, value in enumerate(values):
        x0 = int(left + (right - left) * edges[index] / edges[-1])
        x1 = int(left + (right - left) * edges[index + 1] / edges[-1])
        bar_top = int(bottom - (bottom - top) * value)
        draw.rectangle((x0, bar_top, max(x0, x1 - 1), bottom), fill=GREEN)


def _draw_audiovisual_traces(
    draw: ImageDraw.ImageDraw,
    artifact: AudiovisualTimeline,
    video_box: tuple[int, int, int, int],
    audio_box: tuple[int, int, int, int],
) -> dict[str, object]:
    luminance = np.array([float(np.mean(_relative_luminance(frame.pixels))) for frame in artifact.video.frames])
    frame_edges = artifact.video_start_seconds + np.arange(artifact.video.frame_count + 1) / artifact.video.frame_rate.value
    video_times = np.repeat(frame_edges, 2)[1:-1]
    video_values = np.repeat(luminance, 2)
    audio_times = artifact.audio_start_seconds + np.arange(artifact.audio.sample_count) / artifact.audio.sample_rate.value
    audio_values = np.mean(np.abs(artifact.audio.samples), axis=1)
    duration = artifact.presentation_duration_seconds
    for timestamps, values, box, color in (
        (video_times, video_values, video_box, RED),
        (audio_times, audio_values, audio_box, ACCENT),
    ):
        _coordinate_plot(draw, timestamps, values, box, color, x_range=(0.0, duration), value_range=(0.0, 1.0))
    return {
        "duration_seconds": duration,
        "video": {"timestamps_seconds": video_times, "values": video_values, "interpolation": "frame hold; vertical transitions at frame boundaries", "color_space": "uncalibrated_normalized_channel_values", "transfer_function": "none_applied; not_display_calibrated", "channel_rule": "Rec.709_coefficients_on_RGB_values; grayscale_identity"},
        "audio": {"timestamps_seconds": audio_times, "values": audio_values, "channel_rule": "mean absolute amplitude across channels", "interpolation": "linear between actual sample timestamps; no decimation"},
    }


def _axes(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    x_label: str,
    y_label: str,
    x_ticks: tuple[tuple[float, str], ...] = (),
    y_ticks: tuple[tuple[float, str], ...] = (),
    x_range: tuple[float, float] = (0.0, 1.0),
    y_range: tuple[float, float] = (0.0, 1.0),
) -> None:
    """Draw a restrained, unit-bearing axis frame for code-generated plots."""
    left, top, right, bottom = box
    draw.line((left, bottom, right, bottom), fill=MUTED, width=2)
    draw.line((left, top, left, bottom), fill=MUTED, width=2)
    x_low, x_high = x_range
    y_low, y_high = y_range
    tick_font = _font(15)
    for value, label in x_ticks:
        fraction = (value - x_low) / (x_high - x_low or 1.0)
        x = int(left + fraction * (right - left))
        draw.line((x, bottom, x, bottom + 8), fill=MUTED, width=2)
        width = draw.textlength(label, font=tick_font)
        draw.text((x - width / 2, bottom + 13), label, font=tick_font, fill=MUTED)
    for value, label in y_ticks:
        fraction = (value - y_low) / (y_high - y_low or 1.0)
        y = int(bottom - fraction * (bottom - top))
        draw.line((left - 8, y, left, y), fill=MUTED, width=2)
        width = draw.textlength(label, font=tick_font)
        draw.text((max(0, int(left - 12 - width)), y - 10), label, font=tick_font, fill=MUTED)
        if value not in {y_low, y_high}:
            draw.line((left, y, right, y), fill=(232, 236, 240), width=1)
    label_width = draw.textlength(x_label, font=_font(16))
    _text(draw, (round((left + right - label_width) / 2), bottom + 43), x_label, 16, MUTED)
    _text(draw, (max(0, left - 70), top - 30), y_label, 16, MUTED)


def _panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, accent: tuple[int, int, int] = ACCENT) -> None:
    """Add a thin publication panel rule without heavy dashboard chrome."""
    draw.rounded_rectangle(box, radius=14, outline=(215, 221, 228), width=2)
    draw.line((box[0], box[1] + 46, box[2], box[1] + 46), fill=accent, width=4)


def _footer(draw: ImageDraw.ImageDraw, text: str, *, y: int, color: tuple[int, int, int] = MUTED, right: int = 1850) -> None:
    """Place a compact epistemic note in the figure's lower margin."""
    draw.line((50, y - 18, right, y - 18), fill=(225, 229, 234), width=1)
    _text_block(draw, (55, y), text, right - 70, 16, color)


def _frame_strip(frames: tuple[object, ...], width: int = 180, height: int = 130) -> Image.Image:
    strip = Image.new("RGB", (width * len(frames), height), CANVAS)
    for index, frame in enumerate(frames):
        image = _image(frame).convert("RGB")
        image.thumbnail((width - 10, height - 10), Image.Resampling.NEAREST)
        strip.paste(image, (index * width + (width - image.width) // 2, (height - image.height) // 2))
    return strip


def _generate(illusion_id: str, parameters: object | None = None) -> CanonicalArtifact:
    return default_registry.generate(illusion_id, parameters or default_parameters(illusion_id))


def _architecture(path: Path) -> tuple[str, dict[str, object]]:
    image = Image.new("RGB", (1900, 740), CANVAS)
    draw = ImageDraw.Draw(image)
    boxes = [(50 + index * 365, 235, 360 + index * 365, 535) for index in range(5)]
    labels = [
        ("Typed request", "generator ID, parameters, seed; separate output specification"),
        ("Generator", "Gᵢ(θ; s)"),
        ("Canonical artifact", "immutable float32 buffers + clocks; canonical digest"),
        ("Encode / inspect", "delivery bytes → decoded dimensions, samples, timing"),
        ("Manifest + verify", "file hashes + canonical identity + decoded facts"),
    ]
    claim_levels = ("request", "construction", "canonical", "delivery", "provenance")
    for index, (box, (title, detail), level) in enumerate(zip(boxes, labels, claim_levels)):
        accent = ACCENT if index < 2 else GREEN if index == 2 else AMBER if index < 4 else RED
        draw.rounded_rectangle(box, radius=20, outline=accent, width=5, fill=(247, 249, 251))
        _text(draw, (box[0] + 20, box[1] + 22), f"{index + 1:02d}", 22, accent)
        _text_block(draw, (box[0] + 20, box[1] + 64), title, 270, 23)
        _text_block(draw, (box[0] + 20, box[1] + 155), detail, 270, 17, MUTED)
        _text(draw, (box[0] + 20, box[3] - 35), level, 15, accent)
    for first, second in zip(boxes, boxes[1:]):
        draw.line((first[2] + 8, 365, second[0] - 8, 365), fill=INK, width=4)
        draw.polygon(((second[0] - 8, 365), (second[0] - 24, 354), (second[0] - 24, 376)), fill=INK)
    _text(draw, (60, 65), "DuckRabbit reproducibility contract", 38)
    _text_block(draw, (60, 125), "Canonical identity precedes delivery. Decoded inspection checks written media; only NPZ retains exact canonical arrays.", 1760, 22, MUTED)
    _footer(draw, "Engineering trace only: deterministic media facts and verification are not observer evidence.", y=650)
    digest = _save(image, path)
    return digest, {"stages": [title for title, _ in labels], "equations": ["A = Gᵢ(θ; s)", "h₍c₎ = H(c(A))", "V(F, M) ∈ {pass, fail}"]}


def _catalog(path: Path) -> tuple[str, dict[str, object]]:
    entries = taxonomy_entries()
    headers = ("catalog ID", "modality", "mechanism", "signature", "input", "status")
    columns = (45, 380, 610, 885, 1250, 1620)
    widths = (310, 205, 250, 340, 345, 235)
    rows = []
    for entry in entries:
        values = (entry.illusion_id, ", ".join(item.value for item in entry.modalities), ", ".join(item.value for item in entry.mechanisms), ", ".join(item.value for item in entry.signatures), entry.input_requirement.value, entry.implementation_status.value)
        height = max(_text_height(value, width, 16) for value, width in zip(values, widths)) + 32
        rows.append((entry, values, height))
    image = Image.new("RGB", (1900, 200 + sum(height for _, _, height in rows) + 100), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 35), "Catalog facets and implementation status", 36)
    _text(draw, (50, 92), "All facets are retained without ellipsis; implementation status is not evidence of perception.", 20, MUTED)
    for pos, header in zip(columns, headers):
        _text(draw, (pos, 150), header, 18, MUTED)
    y = 200
    for entry, values, height in rows:
        status_color = GREEN if entry.implementation_status is ImplementationStatus.IMPLEMENTED else AMBER if entry.implementation_status is ImplementationStatus.PLANNED else RED
        for pos, width, value in zip(columns, widths, values):
            _text_block(draw, (pos, y), value, width, 16, status_color if pos == columns[-1] else INK)
        draw.line((45, y + height - 14, 1855, y + height - 14), fill=(224, 228, 233), width=1)
        y += height
    _footer(draw, "Source-supported claims and limitations are mapped separately in the scholarship figure and complete source data.", y=y + 35)
    data = {"entries": [jsonable(entry) for entry in entries]}
    digest = _save(image, path)
    return digest, data


def _visual_panel(path: Path) -> tuple[str, dict[str, object]]:
    ids = tuple(entry.illusion_id for entry in taxonomy_entries() if Modality.VISUAL in entry.modalities and entry.implementation_status is ImplementationStatus.IMPLEMENTED)
    image = Image.new("RGB", (1900, 1840), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 25), "Complete panel of implemented visual constructions", 42)
    _text_block(draw, (50, 85), "One typed default per implemented entry. Static families show canonical rasters; apparent motion shows frame 0 of its sequence.", 1800, 21, MUTED)
    _text_block(draw, (50, 143), "Reading guide: normalized pixel values and temporal metrics describe constructed media, not observer reports.", 1800, 18, MUTED)
    records = []
    for index, illusion_id in enumerate(ids):
        artifact = _generate(illusion_id)
        digest_text = canonical_digest(artifact)
        metrics = measure_artifact(artifact).to_dict()
        # A visual-family entry may be temporally expressed.  Show its first
        # frame as the representative raster while retaining the sequence
        # digest and frame metrics in the source-data record.
        representative = artifact.frames[0] if hasattr(artifact, "frames") else artifact
        thumbnail = _image(representative).convert("RGB")
        thumbnail.thumbnail((500, 280), Image.Resampling.NEAREST)
        row, column = divmod(index, 3)
        x, y = 40 + column * 620, 200 + row * 500
        _panel(draw, (x, y, x + 580, y + 455), accent=ACCENT if row == 0 else GREEN)
        _text(draw, (x + 20, y + 12), illusion_id, 22)
        image.paste(thumbnail, (x + (580 - thumbnail.width) // 2, y + 68))
        values = metrics["values"]
        if "mean_luminance" in values:
            kind = "canonical raster"
            summary = f"Luminance mean: {float(values['mean_luminance']):.3f} · SD: {float(values['std_luminance']):.3f}"
            detail = f"Levels: {int(values['unique_values'])} · digest: {digest_text[:10]}…"
        else:
            kind = "representative first frame; sequence in source data"
            summary = f"Frames: {int(values['frames'])} · rate: {float(values['frame_rate']):.1f} frames/s"
            detail = f"Frame delta: {float(values['mean_temporal_delta']):.3f} normalized · digest: {digest_text[:10]}…"
        _text_block(draw, (x + 20, y + 347), kind, 540, 16, ACCENT if "first frame" in kind else MUTED)
        _text_block(draw, (x + 20, y + 383), summary, 540, 17, MUTED)
        _text_block(draw, (x + 20, y + 418), detail, 540, 15, MUTED)
        records.append({"illusion_id": illusion_id, "canonical_digest": digest_text, "metrics": metrics, "seed": 0, "parameters": jsonable(default_parameters(illusion_id))})
    _footer(draw, "Normalized code-value metrics, not display calibration: grayscale identity or Rec. 709-weighted RGB proxy. Complete for implemented visual entries, not all visual illusions.", y=1740)
    digest = _save(image, path)
    return digest, {"stimuli": records}


def _visual_sweep(path: Path) -> tuple[str, dict[str, object]]:
    base = default_parameters("visual.duck_rabbit")
    if not isinstance(base, DuckRabbitParams):
        raise TypeError("visual.duck_rabbit defaults must be DuckRabbitParams")
    weights = (0.0, 0.25, 0.5, 0.75, 1.0)
    levels = (2, 4, 8, 16, 32)
    image = Image.new("RGB", (1800, 1050), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 25), "Duck-rabbit parameter sweep", 36)
    _text(draw, (50, 68), "Rows vary blend weight; columns vary grayscale and quantization levels. Each cell is a physical construction.", 20, MUTED)
    records = []
    for row, weight in enumerate(weights):
        for column, level in enumerate(levels):
            config = replace(base.config, grayscale_levels=GrayscaleLevels(level), quantization_levels=QuantizationLevels(level))
            artifact = _generate("visual.duck_rabbit", replace(base, config=config, duck_weight=type(base.duck_weight)(weight)))
            thumbnail = _image(artifact).convert("RGB")
            thumbnail.thumbnail((250, 170), Image.Resampling.NEAREST)
            x, y = 130 + column * 340, 140 + row * 170
            draw.rectangle((x - 3, y - 3, x + thumbnail.width + 3, y + thumbnail.height + 3), outline=(218, 224, 230), width=1)
            image.paste(thumbnail, (x, y))
            values = measure_artifact(artifact).values
            records.append({"duck_weight": weight, "grayscale_levels": level, "quantization_levels": level, "digest": canonical_digest(artifact), "unique_values": int(np.unique(artifact.pixels).size), "mean_luminance": float(values["mean_luminance"]), "effective_dynamic_range": float(values["effective_dynamic_range"])})
    # Header band: axis notes stacked above the gutter/labels so no text
    # overprints the first tile column.
    _text(draw, (50, 96), "grayscale / quantization →", 16, MUTED)
    _text(draw, (50, 118), "duck_weight ↓", 16, MUTED)
    for column, level in enumerate(levels):
        _text(draw, (200 + column * 340, 118), f"{level} levels", 16, INK)
    for row, weight in enumerate(weights):
        _text(draw, (50, 140 + row * 170), f"{weight:.2f}", 15, INK)
    _footer(draw, "The sweep reports canonical digests, unique levels, luminance, and dynamic range; it does not estimate perceptual sensitivity.", y=1010)
    digest = _save(image, path)
    return digest, {"sweep": records}


def _temporal(path: Path) -> tuple[str, dict[str, object]]:
    artifact = _generate("visual.apparent_motion")
    if not isinstance(artifact, VideoSequence):
        raise TypeError("visual.apparent_motion must generate VideoSequence")
    shown_frames = artifact.frames[:6]
    strip = _frame_strip(shown_frames, 235, 170)
    image = Image.new("RGB", (1900, 820), CANVAS)
    image.paste(strip, (50, 95))
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 25), "Temporal sequence and frame deltas", 36)
    rate_fraction = Fraction(artifact.frame_rate.value).limit_denominator(1000)
    _text(draw, (50, 68), f"rational frame rate = {rate_fraction.numerator}/{rate_fraction.denominator} frames/s · frame interval = {rate_fraction.denominator}/{rate_fraction.numerator} s/frame · frame count = {artifact.frame_count}", 20, MUTED)
    for index in range(len(shown_frames)):
        _text(draw, (65 + index * 235, 275), f"f{index}  t={index / artifact.frame_rate.value:.3f}s", 15, INK)
    _text(draw, (50, 335), "Canonical adjacent-frame mean absolute difference; k denotes frame k → k+1", 20, MUTED)
    plot_box = (150, 420, 1760, 650)
    delta_high = min(1.0, max(0.01, max(artifact.temporal_deltas, default=0.0) * 1.25))
    _axes(draw, plot_box, x_label="transition k → k+1 (zero-based)", y_label="normalized pixel difference", x_ticks=tuple((index, str(index)) for index in range(max(1, len(artifact.temporal_deltas)))), y_ticks=((0.0, "0"), (delta_high / 2, f"{delta_high / 2:.3f}"), (delta_high, f"{delta_high:.3f}")), x_range=(0.0, max(1.0, len(artifact.temporal_deltas) - 1)), y_range=(0.0, delta_high))
    _line_plot(draw, artifact.temporal_deltas, plot_box, ACCENT, value_range=(0.0, delta_high))
    _footer(draw, "Canonical timestamps and deltas describe construction, not decoded delivery or an observed apparent-motion effect.", y=755)
    digest = _save(image, path)
    return digest, {"canonical_digest": canonical_digest(artifact), "frame_rate": artifact.frame_rate.value, "frame_rate_rational": {"numerator": rate_fraction.numerator, "denominator": rate_fraction.denominator}, "frame_count": artifact.frame_count, "timestamps_seconds": [index / artifact.frame_rate.value for index in range(artifact.frame_count)], "temporal_deltas": artifact.temporal_deltas, "transition_definition": "delta[k] = mean(abs(frame[k+1] - frame[k])); canonical pixels, zero-based frames", "plotted_delta_range": [0.0, delta_high]}


def _audio(path: Path) -> tuple[str, dict[str, object]]:
    ids = ("audio.shepard_tone", "audio.missing_fundamental", "audio.tritone_paradox", "audio.octave_illusion", "audio.auditory_continuity")
    image = Image.new("RGB", (1900, 1650), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 25), "Auditory canonical signals", 36)
    _text(draw, (50, 72), "All-sample min/max envelopes and one-sided spectral summaries; bin ranges are not exact waveforms or pitch reports.", 20, MUTED)
    records = []
    for row, illusion_id in enumerate(ids):
        artifact = _generate(illusion_id)
        if not isinstance(artifact, AudioBuffer):
            raise TypeError(f"{illusion_id} must generate AudioBuffer")
        waveform = _audio_waveform(artifact)
        x, y = 50, 115 + row * 290
        _panel(draw, (x - 8, y - 8, 1840, y + 260), accent=ACCENT if row % 2 == 0 else GREEN)
        _text(draw, (x, y), illusion_id, 22)
        # Separate channel lanes prevent one stereo envelope hiding the other.
        duration = artifact.duration_seconds
        _text(draw, (620, y + 8), f"{artifact.channels} channel(s) · {artifact.sample_rate.value:g} samples/s", 15, MUTED)
        lane_height = (118 - 22 * (artifact.channels - 1)) / artifact.channels
        for channel in range(artifact.channels):
            top = round(y + 62 + channel * (lane_height + 22))
            bottom = round(top + lane_height)
            plot_box = (x + 105, top, 1000, bottom)
            last_channel = channel == artifact.channels - 1
            _axes(draw, plot_box, x_label="time (s); extrema bins" if last_channel else "", y_label="", x_ticks=tuple((time, f"{time:g}") for time in (0.0, duration / 2, duration)) if last_channel else (), y_ticks=((-1.0, "−1"), (0.0, "0"), (1.0, "1")), x_range=(0.0, duration), y_range=(-1.0, 1.0))
            _text(draw, (x + 8, top + 12), f"ch{channel}", 15, MUTED)
            _draw_waveform(draw, waveform, plot_box, channel=channel, color=(ACCENT, RED)[channel], x_range=(0.0, duration))
        metrics = measure_artifact(artifact).to_dict()
        _text_block(draw, (1060, y + 52), f"RMS {metrics['values']['rms']:.4f} norm.", 380, 17, MUTED)
        _text_block(draw, (1060, y + 85), f"peak {metrics['values']['peak']:.4f} norm.", 380, 17, MUTED)
        _text_block(draw, (1060, y + 118), f"centroid {metrics['values']['spectral_centroid_hz']:.1f} Hz", 380, 17, MUTED)
        _text_block(draw, (1060, y + 151), f"bandwidth {metrics['values']['spectral_bandwidth_hz']:.1f} Hz", 380, 17, MUTED)
        _text(draw, (1060, y + 184), f"crest {metrics['values']['crest_factor']:.2f} (ratio)", 17, MUTED)
        spectrum = _audio_spectrum(artifact)
        _text(draw, (1500, y + 43), "48 bands; relative peak", 15, MUTED)
        spectrum_box = (1500, y + 75, 1800, y + 190)
        nyquist = artifact.sample_rate.value / 2
        _axes(draw, spectrum_box, x_label="frequency (Hz)", y_label="", x_ticks=tuple((frequency, f"{frequency:g}") for frequency in (0.0, nyquist / 2, nyquist)), y_ticks=((0.0, "0"), (1.0, "1")), x_range=(0.0, nyquist), y_range=(0.0, 1.0))
        _draw_spectrum(draw, spectrum, spectrum_box)
        records.append({"illusion_id": illusion_id, "metrics": metrics, "canonical_digest": canonical_digest(artifact), "waveform": waveform, "spectrum": spectrum})
    _footer(draw, "Norm. = normalized amplitude; stereo channels occupy separate labeled lanes. Each vertical bin retains all sample extrema, not within-bin timing. Spectra are relative to the largest band. No listener data.", y=1580)
    digest = _save(image, path)
    return digest, {"signals": records, "spectral_definition": "48 peak-aggregated mean-channel magnitude bands covering DC through Nyquist; relative to the largest band", "seed": 0}


def _audiovisual(path: Path) -> tuple[str, dict[str, object]]:
    artifact = _generate("audiovisual.sound_induced_flash")
    if not isinstance(artifact, AudiovisualTimeline):
        raise TypeError("audiovisual.sound_induced_flash must generate AudiovisualTimeline")
    image = Image.new("RGB", (1900, 1020), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 25), "Audiovisual shared-clock timeline", 36)
    _text(draw, (50, 72), "Video frame holds and audio samples share seconds and declared offsets; no perceptual timing is inferred.", 20, MUTED)
    video_box = (140, 145, 1760, 350)
    audio_box = (140, 470, 1760, 675)
    duration = artifact.presentation_duration_seconds
    ticks = tuple((time, f"{time:g}") for time in (0.0, duration / 2, duration))
    _axes(draw, video_box, x_label="shared time (s)", y_label="video mean code-value proxy (normalized)", x_ticks=ticks, y_ticks=((0.0, "0"), (0.5, "0.5"), (1.0, "1")), x_range=(0.0, duration), y_range=(0.0, 1.0))
    _axes(draw, audio_box, x_label="shared time (s)", y_label="mean-channel absolute amplitude (normalized)", x_ticks=ticks, y_ticks=((0.0, "0"), (0.5, "0.5"), (1.0, "1")), x_range=(0.0, duration), y_range=(0.0, 1.0))
    traces = _draw_audiovisual_traces(draw, artifact, video_box, audio_box)
    _text(draw, (50, 745), f"declared sync offset ΔAV = {artifact.sync_offset.value:g} ms", 22, INK)
    _text(draw, (780, 745), f"declared spatial discrepancy = {artifact.spatial_offset.value:g} normalized", 22, INK)
    _text(draw, (50, 800), f"video frames = {artifact.video.frame_count} · frame rate = {artifact.video.frame_rate.value:g} frames/s · audio samples = {artifact.audio.sample_count} · sample rate = {artifact.audio.sample_rate.value:g} Hz", 18, MUTED)
    _footer(draw, "The aligned traces verify physical timing metadata; audiovisual capture or temporal recalibration requires a controlled observer task.", y=935)
    digest = _save(image, path)
    return digest, {"sync_offset_ms": artifact.sync_offset.value, "spatial_offset": artifact.spatial_offset.value, "video_luminance": traces["video"]["values"][::2], "audio_envelope": traces["audio"]["values"], "plotted_traces": traces, "canonical_digest": canonical_digest(artifact), "timebase": {"video_frames": artifact.video.frame_count, "frame_rate": artifact.video.frame_rate.value, "audio_samples": artifact.audio.sample_count, "sample_rate": artifact.audio.sample_rate.value, "audio_start_seconds": artifact.audio_start_seconds, "video_start_seconds": artifact.video_start_seconds}}


def _encoding(path: Path) -> tuple[str, dict[str, object]]:
    image = Image.new("RGB", (1900, 900), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 30), "Encoding and verification surface", 36)
    headers = ("format", "backend", "delivery fact", "verification")
    xs = (60, 430, 800, 1450)
    for x, header in zip(xs, headers):
        _text(draw, (x, 115), header, 20, MUTED)
    rows = (("PNG", "Pillow", "raster dimensions; uint8 quantization", "dimensions / uint8 pixels"), ("WAV", "wave", "sample count + clock", "rate/channels/samples"), ("GIF", "Pillow", "frame count + timing", "decoded frames"), ("NPZ", "NumPy", "exact arrays + digest", "exact canonical round trip"), ("MP4", "ffmpeg", "canonical artifact + stream facts", "optional capability"))
    for row, values in enumerate(rows):
        y = 175 + row * 115
        for x, value in zip(xs, values):
            width = (330, 330, 600, 380)[xs.index(x)]
            _text_block(draw, (x, y), value, width, 19, INK)
        draw.line((50, y + 82, 1840, y + 82), fill=(224, 228, 233), width=1)
    _text_block(draw, (50, 800), "Provenance retains the canonical digest; only NPZ preserves exact canonical arrays. PNG quantizes float32 to uint8. These are adapter contracts, not a delivery run.", 1800, 20, MUTED)
    digest = _save(image, path)
    return digest, {"profiles": [dict(zip(headers, row)) for row in rows], "canonical_identity": "Canonical digest retained in provenance; exact canonical arrays only in NPZ; PNG stores uint8-quantized raster pixels."}


def _observer(path: Path) -> tuple[str, dict[str, object]]:
    diagnostic = default_duck_rabbit_diagnostic()
    model = diagnostic.model
    points = diagnostic.points
    summary = diagnostic.summary
    payload = diagnostic.to_dict()
    bounds = payload["uncertainty"]["points"]
    image = Image.new("RGB", (1900, 1050), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 25), "Synthetic psychophysics: transparent feature observer", 36)
    _text(draw, (50, 72), "A deterministic model diagnostic varies duck_weight against a fixed reference; it is not a human or pretrained vision-model result.", 20, MUTED)
    plot_box = (145, 180, 1250, 670)
    model_low, model_high = 0.0, 1.0
    _axes(draw, plot_box, x_label="duck_weight of comparison stimulus", y_label="model P(comparison), unitless", x_ticks=((0.0, "0.00"), (0.5, "0.50"), (1.0, "1.00")), y_ticks=((0.0, "0"), (0.5, "0.50"), (1.0, "1")), x_range=(0.0, 1.0), y_range=(model_low, model_high))
    def coordinate(point, value):
        return (int(plot_box[0] + point["x_value"] * (plot_box[2] - plot_box[0])),
                int(plot_box[3] - (value - model_low) / (model_high - model_low) * (plot_box[3] - plot_box[1])))
    polygon = [coordinate(point, point["probability_min"]) for point in bounds]
    polygon += [coordinate(point, point["probability_max"]) for point in reversed(bounds)]
    draw.polygon(polygon, fill=(224, 240, 230))
    null_y = (plot_box[1] + plot_box[3]) // 2
    for x in range(plot_box[0], plot_box[2], 24):
        draw.line((x, null_y, min(x + 12, plot_box[2]), null_y), fill=MUTED, width=2)
    _line_plot(draw, [point.prediction.probability_comparison for point in points], plot_box, GREEN, value_range=(model_low, model_high))
    for point in points:
        x = int(plot_box[0] + point.x_value * (plot_box[2] - plot_box[0]))
        y = int(plot_box[3] - (point.prediction.probability_comparison - model_low) / (model_high - model_low) * (plot_box[3] - plot_box[1]))
        _text(draw, (x - 25, y - 28), f"{point.prediction.probability_comparison:.2f}", 15, INK)
    _panel(draw, (1330, 175, 1840, 675), accent=GREEN)
    _text(draw, (1360, 187), "Model contract", 24, GREEN)
    contract_lines = (
        f"model = {model.model_id}",
        f"version = {model.version}",
        f"temperature = {model.temperature:g}",
        f"training data = {model.training_data}",
        "calibration = analytic logistic",
        f"human validation = {model.human_validation}",
    )
    contract_y = 250
    for line in contract_lines:
        contract_y += _text_block(draw, (1360, contract_y), line, 450, 16, INK) + 12
    contract_y += _text_block(draw, (1360, contract_y), f"reference = {diagnostic.reference_label}", 450, 16, MUTED) + 12
    _text_block(draw, (1360, contract_y), f"points = {summary['point_count']} · P = {summary['probability_min']:.3f}–{summary['probability_max']:.3f}", 450, 16, MUTED)
    draw.line((60, 752, 125, 752), fill=GREEN, width=4)
    _text(draw, (145, 737), "solid: default model", 19, GREEN)
    draw.rectangle((500, 742, 555, 765), fill=(224, 240, 230), outline=GREEN)
    _text(draw, (575, 737), "shading: declared configuration range", 19, INK)
    draw.line((1290, 752, 1310, 752), fill=MUTED, width=2)
    draw.line((1320, 752, 1340, 752), fill=MUTED, width=2)
    _text(draw, (1360, 737), "dashed: zero-weight null", 19, MUTED)
    _text_block(draw, (50, 800), "Range includes weight ablations, inactive-feature controls, the zero-weight null, and temperatures 0.5× / 1× / 2×. Not a confidence interval; human_data = false.", 1800, 19, RED)
    _footer(draw, "This curve diagnoses sensitivity of a specified feature observer. It does not estimate a psychometric function or establish a perceptual effect.", y=940)
    digest = _save(image, path)
    payload["plot"] = {"probability_axis": [model_low, model_high], "range_kind": "model_sensitivity_not_confidence_interval", "null_probability": 0.5, "null_style": "dashed", "default_model_style": "solid"}
    return digest, payload


def _claim_boundary(path: Path) -> tuple[str, dict[str, object]]:
    image = Image.new("RGB", (1900, 970), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (55, 35), "Construction evidence is not observer evidence", 38)
    _text_block(draw, (55, 100), "Canonical arrays support measurements and delivery checks. Neither branch is a bridge to a perceptual result.", 1790, 21, MUTED)
    stages = (
        ("canonical_stimulus", "Canonical stimulus", "Typed request → immutable buffer + clock", ACCENT, (60, 270, 540, 560)),
        ("physical_metric", "Physical metric", "Measurements of canonical pixels, samples, and timing", GREEN, (650, 200, 1170, 450)),
        ("encoded_media", "Encoded media", "Delivery container + decoded inspection; canonical digest retained", AMBER, (650, 510, 1170, 760)),
        ("observer_hypothesis", "Observer hypothesis", "Separate calibrated study, consent, responses, estimand", RED, (1320, 270, 1840, 650)),
    )
    for level, title, detail, color, box in stages:
        draw.rounded_rectangle(box, radius=20, fill=(247, 249, 251), outline=color, width=5)
        _text_block(draw, (box[0] + 25, box[1] + 25), title, box[2] - box[0] - 50, 27, color)
        _text_block(draw, (box[0] + 25, box[1] + 100), detail, box[2] - box[0] - 50, 20, INK)
        _text_block(draw, (box[0] + 25, box[3] - 50), level, box[2] - box[0] - 50, 15, MUTED)
    for endpoint in ((640, 325), (640, 635)):
        draw.line(((550, 415), (590, 415), (590, endpoint[1]), endpoint), fill=INK, width=3)
        draw.polygon((endpoint, (endpoint[0] - 14, endpoint[1] - 8), (endpoint[0] - 14, endpoint[1] + 8)), fill=INK)
    draw.line((1250, 200, 1250, 760), fill=RED, width=5)
    _text_block(draw, (1335, 700), "No inference arrow crosses this boundary", 480, 18, RED)
    _footer(draw, "Package evidence: canonical identity, objective metrics, and inspected delivery. Observer effects require independent empirical evidence. No participant data.", y=850, color=RED)
    digest = _save(image, path)
    return digest, {"stages": [{"claim_level": level, "detail": detail} for level, _, detail, _, _ in stages], "dependencies": [["canonical_stimulus", "physical_metric"], ["canonical_stimulus", "encoded_media"]], "observer_inference": "not established by either branch", "observer_data": "none"}


def _scholarship_map(path: Path) -> tuple[str, dict[str, object]]:
    sources, evidence = load_evidence_matrix()
    entries = taxonomy_entries()
    columns = (55, 480, 610, 740, 880, 1780)
    headers = ("catalog entry", "primary", "review", "theory", "supported claim + first limitation", "status")

    row_heights = []
    for entry in entries:
        record = evidence[entry.illusion_id]
        content_height = _text_height(record.supported_claim, 850, 16) + 12
        content_height += _text_height(f"Limitation: {record.evidence_limitations[0]}", 850, 14)
        row_heights.append(max(100, content_height + 38))

    top_offset = 205
    image = Image.new("RGB", (2050, top_offset + sum(row_heights) + 60), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (45, 30), "Source-tiered scholarship map", 36)
    _text_block(draw, (45, 88), f"{len(evidence)} catalog entries; {len(sources)} source records. Counts are source roles, not evidence strength. Full claims, engineering bases and limitations are retained in source data.", 1950, 20, MUTED)
    for x, header in zip(columns, headers):
        _text(draw, (x, 155), header, 18, MUTED)
    rows = []
    y = top_offset
    for entry, row_height in zip(entries, row_heights):
        record = evidence[entry.illusion_id]
        values = (entry.illusion_id, len(record.primary_sources), len(record.review_sources), len(record.theory_sources), record.supported_claim, entry.implementation_status.value)
        color = GREEN if entry.implementation_status is ImplementationStatus.IMPLEMENTED else AMBER if entry.implementation_status.value == "planned" else RED
        for x, value, width in zip(columns[:4], values[:4], (400, 100, 100, 100)):
            _text_block(draw, (x, y), value, width, 16, INK)
        claim_height = _text_block(draw, (columns[4], y), values[4], 850, 16, INK)
        _text_block(draw, (columns[5], y), values[5], 220, 16, color)
        _text_block(draw, (columns[4], y + claim_height + 12), f"Limitation: {record.evidence_limitations[0]}", 850, 14, MUTED)
        draw.line((45, y + row_height - 20, 1995, y + row_height - 20), fill=(229, 232, 236), width=1)
        rows.append({"illusion_id": entry.illusion_id, "primary": record.primary_sources, "review": record.review_sources, "theory": record.theory_sources, "supported_claim": record.supported_claim, "engineering_basis": record.engineering_basis, "limitations": record.evidence_limitations, "gap": entry.implementation_status.value != "implemented"})
        rows[-1]["implementation_status"] = entry.implementation_status.value
        y += row_height
    digest = _save(image, path)
    return digest, {"source_count": len(sources), "entry_count": len(evidence), "rows": rows}


def _formalism_traceability(path: Path) -> tuple[str, dict[str, object]]:
    definitions = formalism_registry()
    columns = (55, 340, 950, 1320, 1690)
    widths = (260, 585, 345, 345, 310)
    rows = []
    for definition in definitions:
        values = (definition.label, definition.equation, ", ".join(definition.implementation), ", ".join(definition.tests), ", ".join(definition.figures))
        heights = [_text_height(value, width, 16) for value, width in zip(values, widths)]
        claim = f"claim: {definition.claim_level.value}"
        heights[0] += 14 + _text_height(claim, widths[0], 14)
        rows.append((definition, values, max(heights) + 40))
    image = Image.new("RGB", (2050, 205 + sum(height for _, _, height in rows) + 60), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 30), "Formalism traceability", 36)
    _text(draw, (50, 88), "Equation labels resolve to implementation modules, tests, figures, and claim levels.", 21, MUTED)
    headers = ("label + claim level", "equation", "implementation", "tests", "figures")
    for x, header in zip(columns, headers):
        _text(draw, (x, 150), header, 18, MUTED)
    records = []
    y = 205
    for definition, values, height in rows:
        for x, value, width in zip(columns, values, widths):
            _text_block(draw, (x, y), value, width, 16, INK)
        claim_y = y + _text_height(values[0], widths[0], 16) + 14
        _text_block(draw, (columns[0], claim_y), f"claim: {definition.claim_level.value}", widths[0], 14, ACCENT)
        draw.line((50, y + height - 16, 2000, y + height - 16), fill=(229, 232, 236), width=1)
        records.append(definition.to_dict())
        y += height
    digest = _save(image, path)
    return digest, {"definitions": records}


def _metrics_dashboard(path: Path) -> tuple[str, dict[str, object]]:
    artifacts = {
        "image": _generate("visual.duck_rabbit"),
        "audio": _generate("audio.shepard_tone"),
        "video": _generate("visual.apparent_motion"),
        "audiovisual": _generate("audiovisual.sound_induced_flash"),
    }
    image = Image.new("RGB", (1950, 1250), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 30), "Objective metrics dashboard", 36)
    _text(draw, (50, 88), "Values are deterministic properties of canonical artifacts; units and computation provenance are explicit.", 21, MUTED)
    cards = []
    for index, (kind, artifact) in enumerate(artifacts.items()):
        x = 55 + (index % 2) * 950
        y = 170 + (index // 2) * 500
        draw.rounded_rectangle((x, y, x + 850, y + 400), radius=22, fill=(248, 250, 252), outline=ACCENT, width=4)
        metrics = measure_artifact(artifact).to_dict()
        _text(draw, (x + 30, y + 28), kind, 28, ACCENT)
        selected = ("mean_luminance", "unique_values", "effective_dynamic_range") if kind == "image" else ("rms", "peak", "spectral_centroid_hz", "dominant_frequency_hz") if kind == "audio" else ("frames", "frame_rate", "duration_seconds", "mean_temporal_delta") if kind == "video" else ("duration_seconds", "sync_offset_ms", "spatial_offset", "audio_rms")
        for metric_index, metric in enumerate(selected):
            value = metrics["values"].get(metric, "n/a")
            unit = next((record["unit"] for record in metrics["records"] if record["name"] == metric), "")
            rendered = str(value) if isinstance(value, int) and not isinstance(value, bool) else f"{float(value):.4f}" if isinstance(value, (int, float)) and not isinstance(value, bool) else str(value)
            _text_block(draw, (x + 35, y + 100 + metric_index * 58), f"{metric}: {rendered} {unit}", 780, 18, INK)
        cards.append({"artifact": kind, "canonical_digest": canonical_digest(artifact), "metrics": metrics})
    digest = _save(image, path)
    return digest, {"cards": cards, "computation_version": COMPUTATION_VERSION}


def _parameter_domains(path: Path) -> tuple[str, dict[str, object]]:
    records = (
        ("PixelDimension", PixelDimension.minimum, PixelDimension.maximum, "pixels"), ("Luminance", 0, 1, "normalized"), ("GrayscaleLevels", 2, 256, "levels"),
        ("QuantizationLevels", 2, 256, "levels"), ("FrequencyHz", 0, None, "Hz"), ("SampleRate", 1000, 384000, "samples/s"),
        ("FrameRate", 1, 240, "frames/s"), ("SyncOffsetMs", -10000, 10000, "ms"), ("SpatialOffset", -1, 1, "normalized"),
    )
    image = Image.new("RGB", (1950, 1300), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 30), "Typed parameter domains", 36)
    _text(draw, (50, 88), "Intervals are validation domains, not claims about perceptual thresholds or sensitivity.", 21, MUTED)
    records_out = []
    for row, (name, low, high, unit) in enumerate(records):
        y = 165 + row * 115
        _text(draw, (60, y), name, 20, INK)
        _text(draw, (400, y), f"{low:g}", 18, MUTED)
        _text_block(draw, (1570, y), f"{high:g} {unit}" if high is not None else f"unbounded; finite {unit}", 325, 18, MUTED)
        draw.line((520, y + 15, 1530, y + 15), fill=(203, 211, 220), width=6)
        draw.ellipse((512, y + 7, 528, y + 23), outline=ACCENT, fill=ACCENT if high is not None else CANVAS, width=3)
        if high is None:
            draw.polygon(((1530, y + 15), (1510, y + 3), (1510, y + 27)), fill=ACCENT)
        else:
            draw.ellipse((1522, y + 7, 1538, y + 23), fill=ACCENT)
        records_out.append({"type": name, "minimum": low, "maximum": high, "minimum_inclusive": high is not None, "maximum_inclusive": high is not None, "finite": True, "unit": unit})
    _footer(draw, "Frequency is finite and strictly positive; each audio generator separately enforces its sample-rate-dependent Nyquist constraint.", y=1230)
    digest = _save(image, path)
    return digest, {"domains": records_out}


def _observer_protocol(path: Path) -> tuple[str, dict[str, object]]:
    design = default_study_design()
    image = Image.new("RGB", (2050, 1320), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 30), "Observer protocol: orchestration boundary", 36)
    _text(draw, (50, 88), "The same stimulus manifest can feed a synthetic diagnostic now or a preregistered human study later; the data streams remain separate.", 21, MUTED)
    steps = (("trial identity", "pseudonym + condition + index"), ("randomization", f"seed={design.randomization_seed}; seeded shuffle"), ("stimulus manifest", "canonical + encoded SHA-256"), ("response", "typed value + missingness"), ("estimand", "contrast + uncertainty interval"))
    boxes = []
    for index, (title, detail) in enumerate(steps):
        x = 60 + index * 395
        box = (x, 265, x + 320, 575)
        boxes.append(box)
        accent = ACCENT if index < 3 else GREEN
        draw.rounded_rectangle(box, radius=22, fill=(247, 249, 251), outline=accent, width=5)
        _text_block(draw, (x + 20, 295), f"{index + 1:02d}  {title}", 280, 21, accent)
        _text_block(draw, (x + 20, 390), detail, 280, 17, MUTED)
        if index < len(steps) - 1:
            draw.line((x + 330, 420, x + 375, 420), fill=INK, width=4)
            draw.polygon(((x + 375, 420), (x + 360, 410), (x + 360, 430)), fill=INK)
    _text(draw, (60, 685), "Two explicitly different endpoints", 25, ACCENT)
    draw.rounded_rectangle((60, 735, 970, 1015), radius=20, fill=(241, 249, 244), outline=GREEN, width=5)
    _text(draw, (90, 775), "Synthetic psychophysics (included)", 23, GREEN)
    _text_block(draw, (90, 835), "duckrabbit.synthetic.feature_observer\nhand-specified features · analytic logistic rule\ntraining_data = none · human_data = false\noutput: model diagnostic, not a psychometric function", 850, 18, INK)
    draw.rounded_rectangle((1080, 735, 1990, 1015), radius=20, fill=(253, 246, 238), outline=AMBER, width=5)
    _text(draw, (1110, 775), "Human psychophysics (future contract)", 23, AMBER)
    _text_block(draw, (1110, 835), "display / playback calibration\nparticipant consent + pseudonymization\npreregistered response, exclusions, model\noutput: observer estimate with uncertainty", 850, 18, INK)
    _text(draw, (60, 1080), "Model templates for future human analysis", 25, ACCENT)
    for index, model in enumerate(default_model_specs()):
        _text(draw, (60 + (index % 2) * 970, 1130 + (index // 2) * 45), f"{model.model.value}: {model.family} / {model.link}", 16, INK)
    _footer(draw, "No participant records, fitted coefficients, or observer-level result is bundled; the included endpoint is model output only.", y=1280, color=RED, right=2000)
    digest = _save(image, path)
    return digest, {"study_id": design.study_id, "study_design": design.to_dict(), "randomization_seed": design.randomization_seed, "steps": [{"name": name, "detail": detail} for name, detail in steps], "synthetic_model": {"model_id": "duckrabbit.synthetic.feature_observer", "training_data": "none", "human_data": False}, "human_study": {"status": "future", "participant_data": False}, "models": [model.to_dict() for model in default_model_specs()]}


def _graphical_abstract(path: Path) -> tuple[str, dict[str, object]]:
    """Show real default constructions, never illustrative substitute traces."""
    ids = ("visual.duck_rabbit", "audio.missing_fundamental", "visual.apparent_motion", "audiovisual.sound_induced_flash")
    visual, audio, temporal, audiovisual = (_generate(illusion_id) for illusion_id in ids)
    if not isinstance(audio, AudioBuffer) or not isinstance(temporal, VideoSequence) or not isinstance(audiovisual, AudiovisualTimeline):
        raise TypeError("graphical abstract requires canonical audio, video, and audiovisual defaults")
    artifacts = (visual, audio, temporal, audiovisual)
    records = [{"illusion_id": illusion_id, "parameters": jsonable(default_parameters(illusion_id)), "seed": 0, "canonical_digest": canonical_digest(artifact), "metrics": measure_artifact(artifact).to_dict()} for illusion_id, artifact in zip(ids, artifacts)]
    image = Image.new("RGB", (1900, 1460), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 30), "Deterministic multimodal stimulus construction", 38)
    _text(draw, (50, 88), "Source-derived examples · canonical buffers and clocks · synthetic constructions only · human_data = false", 21, RED)
    story = (
        ("1  Typed request", "Registry ID + validated immutable parameters + seed; output format is separate.", ACCENT),
        ("2  Canonical artifact", "Deterministic float32 arrays + explicit clocks → canonical SHA-256 identity.", GREEN),
        ("3  Delivery / verification", "Adapter contract: encode → decode / inspect → manifest checks. NPZ alone retains exact arrays.", AMBER),
    )
    for index, (title, detail, color) in enumerate(story):
        x = 50 + index * 615
        _panel(draw, (x, 150, x + 570, 325), accent=color)
        _text(draw, (x + 18, 162), title, 23, color)
        _text_block(draw, (x + 18, 217), detail, 534, 19, INK)
        if index < 2:
            draw.line((x + 578, 235, x + 605, 235), fill=INK, width=3)
            draw.polygon(((x + 605, 235), (x + 593, 227), (x + 593, 243)), fill=INK)
    for box, title, color in (
        ((50, 365, 920, 795), "A  Visual · canonical raster", ACCENT),
        ((970, 365, 1840, 795), "B  Audio · all-sample extrema", GREEN),
        ((50, 835, 920, 1265), "C  Temporal · ordered canonical frames", ACCENT),
        ((970, 835, 1840, 1265), "D  Audiovisual · shared-clock events", GREEN),
    ):
        _panel(draw, box, accent=color)
        _text(draw, (box[0] + 20, box[1] + 12), title, 23, color)
    thumbnail = _image(visual).convert("RGB")
    thumbnail.thumbnail((390, 270), Image.Resampling.NEAREST)
    image.paste(thumbnail, (75 + (390 - thumbnail.width) // 2, 445))
    _text_block(draw, (490, 450), ids[0], 390, 20)
    _text_block(draw, (490, 500), "Uncalibrated normalized pixel values. A construction, not a perceptual report.", 390, 19, MUTED)
    _text_block(draw, (490, 615), f"canonical SHA-256\n{records[0]['canonical_digest'][:16]}…", 390, 17, MUTED)
    waveform = _audio_waveform(audio)
    records[1]["waveform"] = waveform
    audio_box = (1080, 495, 1770, 665)
    duration = audio.duration_seconds
    _text(draw, (995, 430), ids[1], 20)
    _axes(draw, audio_box, x_label="time (s); min/max bins, not exact samples", y_label="normalized amplitude", x_ticks=((0.0, "0"), (duration / 2, f"{duration / 2:g}"), (duration, f"{duration:g}")), y_ticks=((-1.0, "−1"), (0.0, "0"), (1.0, "1")), x_range=(0.0, duration), y_range=(-1.0, 1.0))
    for channel in range(audio.channels):
        _draw_waveform(draw, waveform, audio_box, channel=channel, color=(ACCENT, RED)[channel], x_range=(0.0, duration))
    _text(draw, (995, 752), f"{audio.sample_rate.value:g} samples/s · {audio.channels} channel(s) · SHA-256 {records[1]['canonical_digest'][:12]}…", 17, MUTED)
    shown_indices = tuple(range(min(4, temporal.frame_count)))
    strip = _frame_strip(tuple(temporal.frames[index] for index in shown_indices), 195, 160)
    image.paste(strip, (85, 935))
    _text(draw, (75, 900), ids[2], 20)
    for column, index in enumerate(shown_indices):
        _text(draw, (85 + column * 195, 1110), f"f{index} · {index / temporal.frame_rate.value:.3f} s", 17)
    _text_block(draw, (75, 1160), f"{temporal.frame_count} frames · {temporal.frame_rate.value:g} frames/s · first four shown in order\ncanonical SHA-256 {records[2]['canonical_digest'][:16]}…", 815, 18, MUTED)
    records[2]["displayed_frame_indices"] = shown_indices
    records[2]["timestamps_seconds"] = [index / temporal.frame_rate.value for index in range(temporal.frame_count)]
    records[2]["temporal_deltas"] = temporal.temporal_deltas
    _text(draw, (995, 900), ids[3], 20)
    av_duration = audiovisual.presentation_duration_seconds
    ticks = ((0.0, "0"), (av_duration / 2, f"{av_duration / 2:g}"), (av_duration, f"{av_duration:g}"))
    video_box, av_audio_box = (1080, 970, 1770, 1040), (1080, 1140, 1770, 1190)
    _axes(draw, video_box, x_label="shared time (s)", y_label="video code-value proxy (norm.)", x_ticks=ticks, y_ticks=((0.0, "0"), (1.0, "1")), x_range=(0.0, av_duration))
    _axes(draw, av_audio_box, x_label="shared time (s)", y_label="audio absolute amplitude (norm.)", x_ticks=ticks, y_ticks=((0.0, "0"), (1.0, "1")), x_range=(0.0, av_duration))
    records[3]["plotted_traces"] = _draw_audiovisual_traces(draw, audiovisual, video_box, av_audio_box)
    records[3]["sync_offset_ms"] = audiovisual.sync_offset.value
    records[3]["spatial_offset"] = audiovisual.spatial_offset.value
    _text_block(draw, (55, 1310), "Claim boundary: reproducible media + objective measurements ≠ observer evidence. No participant responses, fitted human model, or validated perceptual effect.", 1790, 23, RED)
    _footer(draw, "Four real typed defaults at seed 0. Full parameters, metrics, canonical digests and plotted data: graphical_abstract.json. Delivery boxes describe contracts, not codec execution.", y=1400)
    digest = _save(image, path)
    return digest, {"stimuli": records, "story": [{"stage": title, "detail": detail} for title, detail, _ in story], "human_data": False, "delivery_status": "adapter contract only; no encoding executed for this figure", "visual_display": "nearest-neighbor uint8 thumbnail of canonical normalized pixels; canonical float32 identity retained by digest", "claim_boundary": "synthetic stimulus constructions and canonical measurements; not observer evidence"}


def publication_caption_specs() -> tuple[CaptionSpec, ...]:
    """Return publication captions with controls, evidence, metrics, and limits.

    Caption text is deliberately generated beside each figure specification so
    the manuscript, registry, alt text, source-data sidecar, and accessibility
    audit cannot drift into separate descriptions.
    """
    catalog_count = len(taxonomy_entries())
    visual_entries = tuple(entry for entry in taxonomy_entries() if Modality.VISUAL in entry.modalities and entry.implementation_status is ImplementationStatus.IMPLEMENTED)
    visual_names = ", ".join(entry.name for entry in visual_entries)
    return (
        CaptionSpec("fig:architecture", "architecture", "Architecture and provenance pipeline", "This schematic separates a typed request from the canonical artifact it generates, the optional delivery encoder, decoded inspection, and the manifest-level verification decision. Arrows indicate data and provenance dependencies rather than a causal model of perception; the seed is 0 and the complete stage record is in source data output/data/architecture.json.", "Five labeled stages connect a typed request to a deterministic canonical artifact, encoded media, decoded inspection, and a verification manifest.", ClaimLevel.CANONICAL_STIMULUS, "output/data/architecture.json", ("formalism:eq:typed_request", "formalism:eq:canonical_generation", "formalism:eq:encoding_verification"), ("The schematic abstracts implementation boundaries and does not represent an observer study or a causal theory of perception.",), ("Stage names, mathematical symbols, and arrow direction are printed directly; color is redundant.",), 0, "typed request q=(i,θ,s,e) with seed s=0; default generator and delivery-independent canonicalization", "no unit-bearing objective quantity is applicable to this architecture diagram; stage identities and provenance fields are recorded in the sidecar", "The pipeline verifies reproducible media facts, not what a person experiences."),
        CaptionSpec("fig:catalog_matrix", "catalog_matrix", "Catalog taxonomy and scholarship", f"The live catalog matrix contains {catalog_count} entries and keeps modality, mechanism, perceptual signature, input requirement, evidence status, and implementation status as separate facets. Source data output/data/catalog_matrix.json preserve the exact taxonomy snapshot and its source-reference namespace; status is not a proxy for perceptual validation.", "A matrix lists all catalog entries with modality, mechanism, signature, input requirement, and implementation status.", ClaimLevel.SOURCE_SUPPORTED, "output/data/catalog_matrix.json", ("gregory1997visual", "hirst2020sound", "bruns2019ventriloquist"), ("Taxonomy facets are engineering classifications and remain provisional where the literature supports competing accounts.",), ("Every status and facet is written as text; color only reinforces the printed status.",), 0, "live taxonomy registry; evidence matrix snapshot; seed not applicable to the catalog diagram", f"{catalog_count} catalog rows; categorical facets and statuses; no observer-level quantity is applicable", "Catalog coverage is bounded to this registered package and does not enumerate all known illusions."),
        CaptionSpec("fig:visual_panel", "visual_panel", "Complete panel of implemented visual constructions", f"This complete gallery presents one deterministic representative from each of the {len(visual_entries)} currently implemented visual catalog entries: {visual_names}. The panel therefore covers the package's available visual families—ambiguous figure, contrast, apparent motion, geometric context, illusory contour, contextual size, and orientation-related constructions—using typed defaults at seed 0. For the temporally expressed apparent-motion entry, the displayed tile is its first frame and the source data preserve the full sequence. The source data sidecar output/data/visual_panel.json records the stable ID, generator parameters, canonical SHA-256 digest, grayscale code-value or Rec. 709-weighted RGB proxy statistics (no transfer conversion or display calibration), raster-level counts, and parameter boundary for every tile.", f"A {len(visual_entries)}-panel gallery shows every currently implemented visual catalog entry, with stable IDs and physical raster summaries: {visual_names}.", ClaimLevel.CANONICAL_STIMULUS, "output/data/visual_panel.json", ("gregory1997visual", "brugger1999duckrabbit", "howe2005muller", "morgan1999poggendorff", "fisher1967ponzo", "yildiz2022ponzo", "kanizsa1976contours", "mruczek2015ebbinghaus", "earle1995zollner", "wertheimer1912motion", "sekuler1996wertheimer"), ("The gallery is complete for implemented visual entries in this package, not a complete survey of visual illusions; literature families, historical displays, and DuckRabbit rasters are not pixel-identical by default.", "Viewing scale, display calibration, viewing distance, and observer conditions can change the relevance of a construction; the gallery does not measure an observer's perceptual report."), ("Each tile is labeled by stable illusion ID and accompanied by printed luminance, level-count, and digest fields; color only reinforces grouping and is not required to identify a stimulus.",), 0, "one default typed parameter object per implemented visual entry; seed s=0; dimensions, luminance bounds, grayscale, and quantization controls remain in each generator schema; temporal entries display their first frame but retain sequence metrics", "per tile: mean and standard deviation of the declared uncalibrated channel-value proxy, unique raster levels, and canonical SHA-256 digest; temporal entries additionally retain frame count, frame rate, and frame deltas; definitions and units are in the source data JSON", "The figure establishes coverage of the package's implemented visual constructions and their deterministic raster facts. It does not establish that any viewer will perceive the named signature, nor that the set is exhaustive of the visual-illusion literature."),
        CaptionSpec("fig:visual_sweep", "visual_sweep", "Visual parameter sweep with physical readouts", "This 5×5 sweep varies duck–rabbit blend weight across rows and jointly varies grayscale and quantization levels across columns. Each cell is regenerated from an immutable typed parameter object at seed 0; source data output/data/visual_sweep.json records canonical digests, unique-level counts, normalized luminance, and effective dynamic range for every condition.", "A labeled grid crosses five duck–rabbit blend weights with five grayscale and quantization settings, with physical metrics recorded for each cell.", ClaimLevel.PHYSICAL_METRIC, "output/data/visual_sweep.json", ("brugger1999duckrabbit", "gregory1997visual"), ("The grid is a sensitivity of the construction parameters, not a psychophysical sensitivity curve or a validated observer effect.",), ("Row and column labels state the parameter values; numerical metrics and units are available in the sidecar.",), 0, "duck_weight ∈ {0,.25,.5,.75,1}; grayscale=quantization ∈ {2,4,8,16,32}; seed s=0", "25 canonical rasters; unique levels, normalized mean luminance, and effective dynamic range per cell", "The chosen grid is an engineering sampling of the parameter domain and does not imply an optimal or perceptually uniform spacing."),
        CaptionSpec("fig:temporal_sequence", "temporal_sequence", "Temporal sequence, clock, and frame deltas", "The frame strip exposes zero-based frame order and canonical timestamps of the apparent-motion construction. The lower trace reports mean absolute pixel difference for each transition k → k+1 on an explicitly labeled data-scaled axis. Source data output/data/temporal_sequence.json preserve canonical digest, frame count and rate, reduced rational frame rate in frames/s, timestamps in seconds, transition definition, complete delta series and plotted range; seed 0 identifies the generated sequence.", "Six ordered canonical frames have timestamps in seconds and a plot of adjacent-frame normalized pixel differences labeled by transition index.", ClaimLevel.PHYSICAL_METRIC, "output/data/temporal_sequence.json", ("wertheimer1912motion", "sekuler1996wertheimer"), ("Frame succession and deltas are canonical construction properties, not decoded timing measurements; playback timing, display persistence, and motion reports require a controlled observer task.",), ("Zero-based frame index, seconds, frames per second, and normalized-difference axes are explicit without color.",), 0, "visual.apparent_motion default typed parameters; frame rate and frame count from the canonical sequence; seed s=0", "timestamps in seconds, frame rate in frames/s, frame count, rational frame rate in frames/s, and adjacent-frame normalized pixel difference", "The figure documents temporal structure rather than the presence, direction, or strength of perceived motion."),
        CaptionSpec("fig:audio_signals", "audio_signals", "Auditory canonical extrema and spectral summaries", "Five implemented auditory constructions—Shepard tone, missing fundamental, tritone paradox, octave illusion, and auditory continuity—are displayed as per-channel all-sample min/max envelopes with one-sided FFT summaries. Every sample contributes to one contiguous half-open bin, including the final partial bin; the vertical range is drawn at the bin midpoint and does not recover within-bin waveform or extremum timing. Source data output/data/audio_signals.json records bin sample boundaries, minima and maxima, sample rate, channel indices, RMS, peak, spectral centroid, bandwidth, crest factor, canonical digest, and spectral normalization; no pitch or stream report is inferred.", "Five labeled rows show channel-preserving audio extrema bins, relative one-sided spectral bars, normalized RMS and peak, and spectral summaries in hertz.", ClaimLevel.PHYSICAL_METRIC, "output/data/audio_signals.json", ("shepard1984scale", "zatorre2005missing", "deutsch1986tritone", "repp1997tritone", "deutsch1974octave", "warren1970continuity", "riecke2011continuity"), ("Extrema aggregation preserves amplitude bounds, not within-bin sample order or event time. Playback level, transducer response, dichotic separation, masker design, and listener judgments remain external.",), ("Channel indices, extrema convention, spectral normalization, amplitude and frequency units are explicit; complete per-channel extrema arrays are retained in source data, not the original sample-by-sample signals.",), 0, "default typed audio parameters and sample rates at seed 0; disjoint all-sample per-channel extrema bins; one-sided FFT display with 48 frequency-labelled peak-magnitude bands", "RMS and peak in normalized amplitude; centroid and bandwidth in Hz; crest as a ratio; sample rate in samples/s; exact bin sample boundaries and canonical SHA-256 digest", "The figure compares generated signal properties and literature-linked families; it does not establish pitch, continuity, or stream organization for a listener."),
        CaptionSpec("fig:audiovisual_timeline", "audiovisual_timeline", "Audiovisual shared-clock timeline and declared offsets", "Video mean channel-value proxy and rectified audio amplitude are placed on a common time axis in seconds with video frame holds and actual audio sample timestamps for the sound-induced-flash construction. Source data output/data/audiovisual_timeline.json records the video frame clock, audio sampling clock, event traces, signed audio-minus-video synchronization offset in milliseconds, and normalized spatial discrepancy; alignment is declared by the generator, not estimated from perception.", "Two labeled traces share a time axis in seconds: video mean channel-value proxy and audio absolute amplitude, with signed synchronization and spatial offsets printed below.", ClaimLevel.PHYSICAL_METRIC, "output/data/audiovisual_timeline.json", ("shams2000sifi", "hirst2020sound", "vroomen2004temporal", "hartcherobrien2011temporal"), ("Display refresh, audio hardware, event latency, and observer temporal binding are not measured by this figure.",), ("The two channels, time axis, signed offset convention, and normalized spatial discrepancy are labeled in text.",), 0, "audiovisual.sound_induced_flash default shared timeline; declared sync offset ΔAV and spatial offset; seed s=0", "video frame-hold grayscale/weighted-RGB proxy and mean-channel absolute audio amplitude on shared time in seconds; ΔAV in ms; spatial discrepancy in normalized units; frame and sample clocks in the sidecar", "A shared-clock construction is not evidence that observers bind the events at the declared or any other perceptual time."),
        CaptionSpec("fig:encoding_verification", "encoding_verification", "Encoding profiles and verification scope", "The comparison separates canonical artifacts from delivery containers: PNG, WAV, GIF, NPZ, and optional MP4/muxed MP4. Source data output/data/encoding_verification.json records the declared backend, delivery facts and decoded inspection targets. This is an adapter contract, not an observation of backend availability, an executed delivery receipt, or a codec-quality comparison.", "A five-row adapter-contract comparison lists format, backend, delivery facts and corresponding decoded verification checks.", ClaimLevel.ENCODED_MEDIA, "output/data/encoding_verification.json", ("engineering:typed_media_adapters",), ("Actual backend availability, codec versions, metadata, and lossy tolerances require a separate delivery run; playback software can expose additional behavior.",), ("Format, backend, delivery fact and verification columns are textual and remain usable without color.",), 0, "declared typed adapter contracts; no encoding or capability probe executed for this diagram", "categorical adapter and verification scope; no unit-bearing measurement is plotted; NPZ retains exact canonical arrays while other formats require decoded/tolerance-aware checks", "An adapter contract or successful encode/decode does not validate an observer effect or establish cross-device perceptual equivalence."),
        CaptionSpec("fig:synthetic_psychophysics", "synthetic_psychophysics", "Synthetic observer diagnostic—model output, not human psychophysics", "The hand-specified feature observer compares duck_weight variants with a fixed canonical reference. Its probability trace is computed analytically from serialized features, weights, and temperature; source data output/data/synthetic_psychophysics.json records model ID/version, reference and comparison digests, seed, calibration, `training_data=none`, and `human_data=false`. The shaded range covers the declared zero-weight control, one-at-a-time weight ablations, and temperature multipliers 0.5, 1, and 2; it is model sensitivity, not a confidence interval.", "A line plot and model-sensitivity range show deterministic model probability across duck_weight values beside the model identity, temperature, no-training-data statement, and human-data boundary.", ClaimLevel.SYNTHETIC_MODEL_OUTPUT, "output/data/synthetic_psychophysics.json", ("observer:preregistered_estimands",), ("The model is hand-specified, has no training data, has not been calibrated against observers, and does not estimate a human threshold or effect size.", "Its probabilities and the finite configuration range are model outputs, not participant responses, confidence intervals, or a psychometric function."), ("Model scale, reference line, model identity, and `human_data=false` are printed; color is not needed to interpret the curve.",), 0, "duck_weight comparison against fixed reference; serialized feature weights and temperature; seed s=0", "model probability, null baseline, ablations, temperature sensitivity and exact-self control; full feature values, specifications and canonical stimulus digests; human_data=false; training_data=none", "This diagnostic tests deterministic orchestration and metamorphic input-output behavior only; empirical psychophysics remains future work."),
        CaptionSpec("fig:claim_boundary", "claim_boundary", "Claim-level boundary between construction and observer evidence", "The diagram branches from canonical stimulus identity to physical measurements and encoded-media inspection, while isolating the future observer hypothesis behind an explicit evidence boundary. No arrow connects those engineering branches to an observer result. Source data output/data/claim_boundary.json records stage definitions, the two canonical dependencies, and the absence of observer data; delivery is not a higher level of perceptual evidence than a canonical measurement.", "Canonical stimulus branches to physical metric and encoded media; a separate observer-hypothesis box lies beyond a boundary that no inference arrow crosses.", ClaimLevel.SOURCE_SUPPORTED, "output/data/claim_boundary.json", ("formalism:eq:observer_estimand", "formalism:eq:canonical_digest"), ("The diagram documents a claim contract and does not replace a preregistered observer study or empirical data.",), ("Each branch is named and described in text; the isolated observer boundary is stated without relying on color.",), 0, "claim levels in the taxonomy and manifest; seed not applicable to the explanatory diagram", "no unit-bearing objective quantity is applicable; dependencies and evidence boundaries are preserved in source data", "A deterministic artifact can support a future hypothesis but cannot supply the observer data required to test it."),
        CaptionSpec("fig:scholarship_map", "scholarship_map", "Source-tiered scholarship map and evidence gaps", "The map shows each catalog entry's primary, review and theory source-role counts, exact supported claim, first recorded limitation, and implementation status. Source data output/data/scholarship_map.json retain complete source identifiers, engineering bases and all limitations from the checked-in evidence matrix. Counts are not evidence-strength scores, and a source record does not certify pixel- or task-identical replication.", "Rows map catalog entries to source-role counts, supported claims, first limitations and printed implementation status; full lineage and engineering bases remain in source data.", ClaimLevel.SOURCE_SUPPORTED, "output/data/scholarship_map.json", ("gregory1997visual", "brugger1999duckrabbit", "yildiz2022ponzo", "hirst2020sound", "bruns2019ventriloquist"), ("The offline snapshot validates citation and lineage structure; live resolver status is a separate audit, and classifications can remain contested.",), ("Source roles, claims, limitations, and statuses are printed or available in source data; no category is encoded by color alone.",), 0, "checked-in evidence matrix; source roles and entry statuses; audit date recorded in data/evidence_matrix.json", f"one evidence row per catalog entry ({catalog_count} entries); source-tier counts, exact claim text, engineering basis, limitations, and gap status", "Scholarship coverage bounds the package’s evidence record and does not establish an observer-level effect."),
        CaptionSpec("fig:formalism_traceability", "formalism_traceability", "Formal definitions and implementation traceability", "The traceability registry connects the nine numbered equations to symbols, implementation modules, tests, and registered figures. Source data output/data/formalism_traceability.json is the machine-readable crosswalk used by the manuscript; it demonstrates contract coverage and test linkage without converting formal notation into empirical evidence.", "Rows connect equation labels to their mathematical definition, implementation paths, tests, figure labels, and claim levels.", ClaimLevel.PHYSICAL_METRIC, "output/data/formalism_traceability.json", ("formalism:eq:canonical_digest", "formalism:eq:clock_definition", "formalism:eq:objective_statistics"), ("Traceability records documentation and verification scope; it does not establish the truth of an observer-level theory.",), ("Equation labels, code paths, tests, and figure labels are written as text.",), 0, "formalism registry version; seed not applicable to the traceability diagram", "nine equation records with implementation, test, figure, and claim-level fields; no unit-bearing measurement is plotted", "A linked equation and test can show an implemented contract, not a validated perceptual law."),
        CaptionSpec("fig:metrics_dashboard", "metrics_dashboard", "Objective metrics dashboard with units and provenance", "The dashboard presents representative measurements from image, audio, video, and audiovisual canonical artifacts. Source data output/data/metrics_dashboard.json retains metric name, value, unit, computation version, tolerance, claim level, and canonical digest; image values are an uncalibrated grayscale/weighted-RGB proxy with explicit transfer/window definitions and definition hashes, amplitude is normalized, spectra are in hertz, frame differences are normalized pixel differences, and synchronization is in milliseconds.", "Four artifact cards list image, audio, video, and audiovisual metrics with units, computation provenance, and claim level.", ClaimLevel.PHYSICAL_METRIC, "output/data/metrics_dashboard.json", ("formalism:eq:objective_statistics", "formalism:eq:temporal_spectral_metrics"), ("Metrics are media properties and do not encode pitch, size, motion, localization, binding, or other observer interpretations.",), ("Every numerical value is paired with a printed unit or an explicit dimensionless definition.",), 0, "default canonical artifacts; metric computation version and tolerance recorded in the source-data sidecar; seed s=0", "finite objective values with units: normalized luminance/amplitude, Hz, normalized pixel difference, ms, counts, and durations", "Metric reproducibility is a package property; interpretation as perception requires a separate observer design and data."),
        CaptionSpec("fig:parameter_domains", "parameter_domains", "Typed parameter domains and units", "The domain map shows the validated ranges for dimensions, luminance, grayscale and quantization levels, frequency, sampling rate, frame rate, synchronization offset, and spatial discrepancy. Source data output/data/parameter_domains.json records the type name, unit, interval, and engineering role; intervals prevent malformed media and are not proposed as sensitivity thresholds.", "Horizontal interval markers show typed domains for dimensions, luminance, levels, frequency, sampling, frame rate, synchronization, and spatial discrepancy.", ClaimLevel.CANONICAL_STIMULUS, "output/data/parameter_domains.json", ("formalism:eq:typed_request",), ("The intervals are software validation bounds and do not encode safe listening levels, display limits, or psychophysical thresholds.",), ("Type names, endpoints, units, and roles are printed; interval color is redundant.",), 0, "parameter schema version and validated scalar domains; seed not applicable to the domain diagram", "dimensionless, pixel, level, Hz, samples/s, frames/s, ms, and normalized spatial units as listed per parameter", "A valid parameter is a reproducible construction request, not evidence that the requested value is perceptually effective."),
        CaptionSpec("fig:observer_protocol", "observer_protocol", "Observer protocol scaffold and estimand boundary", "The data-free protocol template moves from pseudonymous trial identity and deterministic randomization to a stimulus manifest and encoded-file hash, typed response or missingness, and a preregistered estimand. Source data output/data/observer_protocol.json records the study design, randomization seed, model templates, and synthetic-only status; no participant record is included.", "A flow diagram connects trial identity, randomization, stimulus manifest, response, aggregate estimand, and analysis-model templates, with a synthetic-only boundary.", ClaimLevel.OBSERVER_HYPOTHESIS, "output/data/observer_protocol.json", ("observer:preregistered_estimands",), ("The scaffold specifies future data collection and analysis but supplies no participant responses, fitted coefficients, power claim, or validated observer effect.",), ("Every protocol step and the no-participant-data boundary is stated in text; arrows and labels remain legible without color.",), 0, "study design and deterministic randomization seed recorded in the sidecar; synthetic response generation is separate from human data", "trial counts, condition structure, estimand templates, response schemas, and model families; participant outcomes are not applicable", "The protocol requires ethical review, task and calibration specifications, and preregistration before human use, not evidence that the proposed effect exists."),
        CaptionSpec(
            "fig:graphical_abstract", "graphical_abstract", "Deterministic multimodal stimulus construction and verification",
            "Four actual default generators supply the visual raster, missing-fundamental audio extrema, apparent-motion frame strip, and sound-induced-flash shared-clock traces. The compact typed-request → canonical-artifact → delivery/verification story separates immutable float32 identity from adapter contracts. Source data output/data/graphical_abstract.json retain each typed parameter object, seed, canonical SHA-256 digest, unit-bearing metrics, displayed temporal indices, audio bin extrema, and audiovisual traces. The delivery stage is a contract diagram, not a codec execution receipt; all constructions are synthetic and human_data=false.",
            "Four labeled panels show a generated duck–rabbit raster, all-sample audio min/max bins, four ordered apparent-motion frames with seconds, and audiovisual event traces on shared seconds, beneath a three-stage construction and verification diagram.",
            ClaimLevel.CANONICAL_STIMULUS, "output/data/graphical_abstract.json",
            ("formalism:eq:typed_request", "formalism:eq:canonical_generation", "formalism:eq:canonical_digest", "engineering:typed_media_adapters", "brugger1999duckrabbit", "zatorre2005missing", "wertheimer1912motion", "shams2000sifi"),
            ("Raster thumbnails quantize normalized pixels to uint8; extrema bins preserve amplitude bounds but not within-bin event time. Canonical digests identify complete original artifacts.", "No delivery encode is executed for this diagram, and no observer responses or perceptual validation are included."),
            ("Panel letters, generator IDs, time units, and epistemic boundaries are explicit; full plotted arrays and digests are in the source-data sidecar.",),
            0, "four live default typed requests at seed 0; no substituted or decorative signals",
            "normalized pixel/amplitude values, sample rate in samples/s, frame rate in frames/s, timestamps in seconds, audiovisual offsets in ms and normalized spatial units; complete canonical SHA-256 digests in source data",
            "Synthetic stimulus construction and deterministic verification contracts do not establish an observer-level effect.",
        ),
    )


_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


def validate_figure_registry(
    registry: Mapping[str, object] | Path,
    *,
    output_dir: Path | None = None,
    project_root: Path | None = None,
) -> dict[str, object]:
    """Validate a generated figure registry as an independent trust boundary.

    The renderer is allowed to create a registry, but the registry itself is
    not trusted merely because it came from the renderer.  This validator
    checks code-owned caption equality, source-data lineage, evidence
    namespaces, stable paths, and (when ``output_dir`` is supplied) actual
    file hashes.
    """
    if isinstance(registry, Path):
        try:
            payload = json.loads(registry.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read figure registry {registry}: {exc}") from exc
        if output_dir is None:
            output_dir = registry.parent.parent
    else:
        payload = registry
    if not isinstance(payload, Mapping):
        raise ValueError("figure registry must be an object")
    if payload.get("schema_version") != "duckrabbit/figures/v1":
        raise ValueError("unsupported figure registry schema version")
    records = payload.get("figures")
    if not isinstance(records, list):
        raise ValueError("figure registry figures must be a list")
    expected_specs = {spec.label: spec for spec in publication_caption_specs()}
    count = payload.get("figure_count")
    if type(count) is not int or count != len(records) or count != len(expected_specs):
        raise ValueError(f"figure registry count must equal {len(expected_specs)}")
    try:
        if project_root is None:
            sources, _ = load_evidence_matrix()
        else:
            manuscript_dir = project_root / "docs" / "manuscript"
            if not manuscript_dir.is_dir():
                manuscript_dir = project_root / "manuscript"
            sources, _ = load_evidence_matrix(
                project_root / "data" / "evidence_matrix.json",
                bibliography_path=manuscript_dir / "references.bib",
                manuscript_dir=manuscript_dir,
            )
    except Exception as exc:
        raise ValueError(f"figure registry cannot load evidence namespace: {exc}") from exc
    known_references = set(sources)
    known_references.update(f"formalism:{record.label}" for record in formalism_registry())
    known_references.update({"engineering:typed_media_adapters", "observer:preregistered_estimands"})
    required = {
        "label", "filename", "path", "source_data", "title", "caption", "alt_text",
        "accessibility", "parameters", "claim_level", "evidence_references", "limitations",
        "caption_core", "controls", "objective_facts", "boundary_statement",
        "sha256", "source_data_sha256", "generator", "generated_by", "seed", "visual_qa",
    }
    seen: set[str] = set()

    def resolve_reference(reference: object, prefix: str) -> Path:
        if not isinstance(reference, str) or not reference.startswith(prefix):
            raise ValueError(f"figure registry path must start with {prefix}")
        if output_dir is None:
            raise ValueError("figure registry path validation requires output_dir")
        candidate = output_dir / reference.removeprefix("output/")
        try:
            if not candidate.resolve().is_relative_to(output_dir.resolve()):
                raise ValueError("figure registry path escapes output directory")
        except ValueError as exc:
            if "escapes" in str(exc):
                raise
            raise ValueError("figure registry path cannot be resolved") from exc
        return candidate

    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("figure registry records must be objects")
        missing = required - set(record)
        if missing:
            raise ValueError(f"figure registry record is missing: {sorted(missing)}")
        label = record["label"]
        if not isinstance(label, str) or label in seen or label not in expected_specs:
            raise ValueError(f"figure registry label is duplicate or unknown: {label!r}")
        seen.add(label)
        spec = expected_specs[label]
        stem = label.removeprefix("fig:")
        if record["filename"] != f"{stem}.png" or record["path"] != f"output/figures/{stem}.png" or record["source_data"] != f"output/data/{stem}.json":
            raise ValueError(f"figure registry paths do not match {label}")
        if (
            record["title"] != spec.title
            or record["caption"] != spec.rendered_caption
            or record["caption_core"] != spec.caption
            or record["alt_text"] != spec.alt_text
            or record["controls"] != spec.controls
            or record["objective_facts"] != spec.objective_facts
            or record["boundary_statement"] != spec.boundary_statement
        ):
            raise ValueError(f"figure registry caption contract disagrees with code for {label}")
        if record["seed"] != spec.seed:
            raise ValueError(f"figure registry seed disagrees with code for {label}")
        caption_text = str(record["caption"])
        for required_phrase in ("Source data:", "Claim level:", "Limitations:", "Boundary:", "Evidence lineage:"):
            if required_phrase not in caption_text:
                raise ValueError(f"figure registry caption contract is missing {required_phrase} for {label}")
        try:
            claim_level = ClaimLevel(record["claim_level"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"figure registry claim level is invalid for {label}") from exc
        if claim_level is not spec.claim_level:
            raise ValueError(f"figure registry claim level disagrees with code for {label}")
        evidence_references = record["evidence_references"]
        limitations = record["limitations"]
        if not isinstance(evidence_references, list) or not evidence_references or not all(isinstance(item, str) and item in known_references for item in evidence_references):
            raise ValueError(f"figure registry evidence references are unresolved for {label}")
        if not isinstance(limitations, list) or not limitations or not all(isinstance(item, str) and item.strip() for item in limitations):
            raise ValueError(f"figure registry limitations are invalid for {label}")
        if evidence_references != list(spec.evidence_references):
            raise ValueError(f"figure registry evidence lineage disagrees with code for {label}")
        if limitations != list(spec.limitations):
            raise ValueError(f"figure registry limitations disagree with code for {label}")
        producer = "duckrabbit.publication.generate_publication_outputs"
        if record["generator"] != producer or record["generated_by"] != producer:
            raise ValueError(f"figure registry producer disagrees with code for {label}")
        accessibility = record["accessibility"]
        if not isinstance(accessibility, Mapping) or accessibility.get("color_independent") is not True or accessibility.get("text_labels") is not True:
            raise ValueError(f"figure registry accessibility contract is incomplete for {label}")
        if not _SHA256_PATTERN.fullmatch(str(record["sha256"])) or not _SHA256_PATTERN.fullmatch(str(record["source_data_sha256"])):
            raise ValueError(f"figure registry hashes are invalid for {label}")
        if type(record["seed"]) is not int or not isinstance(record["parameters"], Mapping):
            raise ValueError(f"figure registry parameters are invalid for {label}")
        if record["parameters"] != {"seed": spec.seed, "figure_stem": spec.stem} or type(record["parameters"].get("seed")) is not int:
            raise ValueError(f"figure registry parameter seed disagrees for {label}")
        visual_qa = record["visual_qa"]
        if not isinstance(visual_qa, Mapping) or type(visual_qa.get("width_px")) is not int or type(visual_qa.get("height_px")) is not int or visual_qa["width_px"] <= 0 or visual_qa["height_px"] <= 0:
            raise ValueError(f"figure registry visual QA dimensions are invalid for {label}")
        if output_dir is not None:
            figure_path = resolve_reference(record["path"], "output/figures/")
            source_data_path = resolve_reference(record["source_data"], "output/data/")
            if not figure_path.is_file() or not source_data_path.is_file():
                raise ValueError(f"figure registry references missing output for {label}")
            if hashlib.sha256(figure_path.read_bytes()).hexdigest() != record["sha256"]:
                raise ValueError(f"figure registry figure hash is stale for {label}")
            with Image.open(figure_path) as inspected:
                if inspected.size != (visual_qa["width_px"], visual_qa["height_px"]):
                    raise ValueError(f"figure registry visual QA dimensions disagree for {label}")
                if inspected.mode != visual_qa.get("mode"):
                    raise ValueError(f"figure registry visual QA mode disagrees for {label}")
            if dict(visual_qa) != _visual_qa(figure_path):
                raise ValueError(f"figure registry visual QA disagrees with inspected image for {label}")
            if hashlib.sha256(source_data_path.read_bytes()).hexdigest() != record["source_data_sha256"]:
                raise ValueError(f"figure registry source-data hash is stale for {label}")
            try:
                source_payload = json.loads(source_data_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(f"figure registry source-data JSON is unreadable for {label}: {exc}") from exc
            if not isinstance(source_payload, Mapping) or source_payload.get("schema_version") != "duckrabbit/figure-source/v1":
                raise ValueError(f"figure registry source-data schema is invalid for {label}")
            if source_payload.get("figure_label") != label or source_payload.get("figure_stem") != stem:
                raise ValueError(f"figure registry source-data identity disagrees for {label}")
            builder_names = {
                "catalog_matrix": "_catalog", "temporal_sequence": "_temporal",
                "audio_signals": "_audio", "audiovisual_timeline": "_audiovisual",
                "encoding_verification": "_encoding", "synthetic_psychophysics": "_observer",
            }
            expected_generator = f"duckrabbit.publication.{builder_names.get(stem, '_' + stem)}"
            if source_payload.get("generator") != expected_generator:
                raise ValueError(f"figure registry source-data producer disagrees with code for {label}")
            if (
                type(source_payload.get("seed")) is not int
                or source_payload.get("seed") != record["seed"]
                or not isinstance(source_payload.get("parameters"), Mapping)
                or source_payload["parameters"] != record["parameters"]
                or type(source_payload["parameters"].get("seed")) is not int
                or not isinstance(source_payload.get("data"), Mapping)
            ):
                raise ValueError(f"figure registry source-data provenance is invalid for {label}")
    if seen != set(expected_specs):
        raise ValueError("figure registry does not contain every code-owned figure")
    return dict(payload)


def _markdown_cell(value: object) -> str:
    # A literal pipe is a Markdown delimiter; spelling it out also avoids the
    # template's LaTeX preflight interpreting an escaped pipe as ``\mid``.
    return str(value).replace("|", " given ").replace("\n", " ")


def _markdown_row(values: Iterable[object]) -> str:
    return "| " + " | ".join(_markdown_cell(value) for value in values) + " |"


def _display_identifier(value: object) -> str:
    """Preserve exact identifiers while escaping Markdown underscores."""
    return str(value).replace("_", r"\_")


def _display_doi_url(doi: object, url: object) -> str:
    """Retain complete source locators in printed and digital tables."""
    raw_url = str(url)
    url_label = f"<{raw_url}>" if raw_url.startswith(("https://", "http://")) else _display_identifier(raw_url)
    return f"DOI: {_display_identifier(doi)}; URL: {url_label}"


def publication_table_payloads() -> dict[str, dict[str, object]]:
    """Return the code-owned table definitions used by output and prose."""
    sources, evidence = load_evidence_matrix()
    catalog_records = []
    for entry in taxonomy_entries():
        record = evidence[entry.illusion_id]
        catalog_records.append(
            {
                "id": entry.illusion_id,
                "modality": ", ".join(item.value for item in entry.modalities),
                "mechanism": ", ".join(item.value for item in entry.mechanisms),
                "signature": ", ".join(item.value for item in entry.signatures),
                "evidence": entry.evidence_status.value,
                "status": entry.implementation_status.value,
                "sources": ", ".join(record.primary_sources + record.review_sources + record.theory_sources),
                "supported_claim": record.supported_claim,
                "claim_level": record.supported_claim_level.value,
            }
        )
    catalog_display_records = [
        {
            **record,
            "id_display": _display_identifier(record["id"]),
            "construction": f"{record['modality']}; {_display_identifier(record['mechanism'])}; {_display_identifier(record['signature'])}",
            "evidence_status": f"{_display_identifier(record['evidence'])}; {_display_identifier(record['status'])}",
            "sources_display": _display_identifier(record["sources"] or "none"),
        }
        for record in catalog_records
    ]
    parameter_records = [
        {"type": "PixelDimension", "unit": "pixels", "domain": f"{PixelDimension.minimum}–{PixelDimension.maximum}", "role": "image/video width and height"},
        {"type": "GrayscaleLevels", "unit": "levels", "domain": "2–256", "role": "representable grayscale levels"},
        {"type": "QuantizationLevels", "unit": "levels", "domain": "2–256", "role": "output quantization buckets"},
        {"type": "FrequencyHz", "unit": "Hz", "domain": "> 0 and finite", "role": "oscillator and harmonic frequencies"},
        {"type": "SampleRate", "unit": "samples/s", "domain": "1,000–384,000", "role": "audio sampling clock"},
        {"type": "FrameRate", "unit": "frames/s", "domain": "1–240", "role": "video presentation clock"},
        {"type": "SyncOffsetMs", "unit": "ms", "domain": "−10,000–10,000", "role": "audio relative to video"},
        {"type": "SpatialOffset", "unit": "normalized", "domain": "−1–1", "role": "declared crossmodal spatial discrepancy"},
    ]
    ffmpeg_status = "available" if shutil.which("ffmpeg") else "unavailable"
    encoding_records = [
        {"format": "PNG", "backend": "Pillow", "artifact": "image", "profile": "lossless uint8 raster", "status": "available"},
        {"format": "WAV", "backend": "python wave", "artifact": "audio", "profile": "PCM 8/16/24/32-bit", "status": "available"},
        {"format": "GIF", "backend": "Pillow", "artifact": "video", "profile": "palette animation with declared duration", "status": "available"},
        {"format": "NPZ", "backend": "NumPy", "artifact": "canonical artifact", "profile": "exact little-endian float32 archive", "status": "available"},
        {"format": "MP4", "backend": "ffmpeg", "artifact": "video/audiovisual", "profile": "H.264 or muxed MP4; decode inspected", "status": ffmpeg_status},
    ]
    metric_records = [
        {"metric": "mean_luminance", "unit": "normalized_luminance", "definition": "mean grayscale value or Rec.709-weighted RGB code-value proxy; no transfer conversion or display calibration", "tolerance": "exact canonical", "claim_level": "physical_metric"},
        {"metric": "unique_values", "unit": "levels", "definition": "count of distinct canonical image values", "tolerance": "exact integer", "claim_level": "physical_metric"},
        {"metric": "rms", "unit": "normalized_amplitude", "definition": "root-mean-square audio amplitude", "tolerance": "finite scalar", "claim_level": "physical_metric"},
        {"metric": "peak", "unit": "normalized_amplitude", "definition": "maximum absolute audio amplitude", "tolerance": "finite scalar", "claim_level": "physical_metric"},
        {"metric": "spectral_centroid_hz", "unit": "Hz", "definition": "one-sided frequency mean weighted by mean-channel abs(unwindowed rFFT) magnitude, not energy", "tolerance": "finite scalar", "claim_level": "physical_metric"},
        {"metric": "spectral_bandwidth_hz", "unit": "Hz", "definition": "spectral standard deviation around the one-sided centroid", "tolerance": "finite scalar", "claim_level": "physical_metric"},
        {"metric": "crest_factor", "unit": "ratio", "definition": "audio peak divided by RMS with zero-RMS guard", "tolerance": "finite scalar", "claim_level": "physical_metric"},
        {"metric": "mean_temporal_delta", "unit": "normalized_pixel_difference", "definition": "mean adjacent-frame absolute difference", "tolerance": "finite scalar", "claim_level": "physical_metric"},
        {"metric": "sync_offset", "unit": "ms", "definition": "declared audio-minus-video offset", "tolerance": "typed value", "claim_level": "physical_metric"},
    ]
    observer_records = [
        {
            "estimand": estimand.name,
            "response": estimand.response_kind.value,
            "model": estimand.model.value,
            "reference": estimand.reference_condition,
            "contrast": estimand.primary_contrast,
            "uncertainty": estimand.uncertainty,
        }
        for estimand in default_study_design().estimands
    ]
    observer_display_records = [
        {
            **record,
            "estimand_display": _display_identifier(record["estimand"]),
            "response_model": f"{_display_identifier(record['response'])}; {_display_identifier(record['model'])}",
            "reference_contrast": f"{_display_identifier(record['reference'])}; {record['contrast']}",
        }
        for record in observer_records
    ]
    verification_records = [
        {"failure_mode": "altered encoded file", "control": "recompute encoded SHA-256", "result": "fail"},
        {"failure_mode": "stale canonical digest", "control": "recompute canonical little-endian float32 digest", "result": "fail"},
        {"failure_mode": "incorrect decoded dimensions", "control": "compare inspection facts with manifest summary", "result": "fail"},
        {"failure_mode": "stream timing mismatch", "control": "compare duration/timebase and declared sync offset", "result": "fail"},
        {"failure_mode": "unsupported backend", "control": "capability probe before encoding", "result": "explicit capability error"},
        {"failure_mode": "conflicting format requests", "control": "reject format_name/output_spec disagreement", "result": "parameter error"},
    ]
    caption_records = [
        {
            "label": spec.label,
            "claim_level": spec.claim_level.value,
            "source_data": spec.source_data,
            "evidence_references": ", ".join(spec.evidence_references),
            "limitations": " ".join(spec.limitations),
            "accessibility": " ".join(spec.accessibility_notes),
            "controls": spec.controls or "default typed controls",
            "objective_facts": spec.objective_facts or "sidecar metrics",
            "boundary": spec.boundary_statement or "no observer-level effect established",
        }
        for spec in publication_caption_specs()
    ]
    caption_display_records = [
        {
            **record,
            "label_claim": f"{_display_identifier(record['label'])}; {_display_identifier(record['claim_level'])}",
            "source_evidence": f"{_display_identifier(record['source_data'])}; {_display_identifier(record['evidence_references'])}",
            "controls_objective": _display_identifier(f"Controls: {record['controls']} Objective: {record['objective_facts']}"),
            "limitations_boundary_accessibility": _display_identifier(
                f"Limitations: {record['limitations']} Boundary: {record['boundary']} "
                f"Accessibility: {record['accessibility']}"
            ),
        }
        for record in caption_records
    ]
    source_audit_records = [
        {"key": source.key, "citation_key": source.citation_key, "source_type": source.source_type, "doi": source.doi or "not_recorded", "url": source.url, "verified": source.verification_status.value in {"snapshot_validated", "doi_metadata_match", "doi_less_archival"}, "verification_status": source.verification_status.value, "resolver": source.resolver, "supported_claim": source.supports}
        for source in sources.values()
    ]
    lineage_records = [
        {
            "key": f"entry:{entry.illusion_id}",
            "citation_key": ", ".join(record.primary_sources + record.review_sources + record.theory_sources),
            "source_type": "engineering+limitation+gap",
            "doi": "not_applicable",
            "url": "data/evidence_matrix.json",
            "verified": True,
            "verification_status": "snapshot_validated",
            "resolver": "offline_snapshot",
            "supported_claim": f"{record.supported_claim} Engineering basis: {record.engineering_basis} Limitation: {' '.join(record.evidence_limitations)} Missing contract: {record.missing_contract or 'none'}",
        }
        for entry in taxonomy_entries()
        for record in (evidence[entry.illusion_id],)
    ]
    source_audit_records.extend(lineage_records)
    source_audit_display_records = [
        {
            **record,
            "key_display": _display_identifier(record["key"]),
            "record_display": f"{_display_identifier(record['source_type'])}; {_display_identifier(record['citation_key'] or 'none')}",
            "doi_url": _display_doi_url(record["doi"], record["url"]),
            "verification_display": f"{_display_identifier(record['verification_status'])}; {_display_identifier(record['resolver'])}",
        }
        for record in source_audit_records
    ]
    formalism_records = [definition.to_dict() for definition in formalism_registry()]
    formalism_display_records = [
        {
            **record,
            "label_display": _display_identifier(record["label"]),
            "definition_symbols": f"{record['equation']} Symbols: {', '.join(record['symbols'])}",
            "implementation_tests": (
                f"Code: {_display_identifier(', '.join(record['implementation']))}; "
                f"Tests: {_display_identifier(', '.join(record['tests']))}"
            ),
            "figures_level": f"Figures: {_display_identifier(', '.join(record['figures']))}; Level: {_display_identifier(record['claim_level'])}",
        }
        for record in formalism_records
    ]
    claim_records = []
    for claim in default_claim_registry():
        lineage = "; ".join(claim.source_or_artifact_lineage)
        if claim.claim_id.startswith("evidence:") and claim.claim_id.removeprefix("evidence:") in evidence:
            record = evidence[claim.claim_id.removeprefix("evidence:")]
            lineage = f"sources={lineage}; engineering={record.engineering_basis}; limitation={claim.limitation}; missing_contract={record.missing_contract or 'none'}"
        claim_records.append({
            "claim_id": claim.claim_id,
            "claim": claim.text,
            "basis": claim.basis.value,
            "lineage": lineage,
            "claim_level": claim.claim_level.value,
            "limitation": claim.limitation,
            "manuscript_location": claim.manuscript_location,
        })
    claim_records.extend([
        {"claim_id": "publication:figure_count", "claim": f"The publication atlas contains {len(publication_caption_specs())} registered scientific figures.", "basis": "derived_from_code", "lineage": "publication_caption_specs()", "claim_level": "physical_metric", "limitation": "The count is a package-state fact, not evidence of empirical validity.", "manuscript_location": "docs/manuscript/07_publication_audit.md"},
        {"claim_id": "publication:table_count", "claim": "The publication appendix contains the generated table set defined by the publication table payload registry.", "basis": "derived_from_code", "lineage": "publication_table_payloads()", "claim_level": "physical_metric", "limitation": "Generated tables summarize package state and do not replace source or observer evidence.", "manuscript_location": "docs/manuscript/07_publication_audit.md"},
    ])
    project_root = Path(__file__).resolve().parents[2]
    for claim in claim_records:
        location = project_root / claim["manuscript_location"]
        if not location.resolve().is_relative_to((project_root / "docs" / "manuscript").resolve()) or not location.is_file():
            raise ValueError(f"publication claim manuscript location is invalid: {claim['claim_id']}")
    claim_display_records = [
        {
            **record,
            "claim_id_display": _display_identifier(record["claim_id"]),
            "claim_level_display": f"{record['claim']} Level: {record['claim_level']}",
            "lineage_limit": (
                f"Lineage: {_display_identifier(record['lineage'])} Limitation: {record['limitation']} "
                f"Manuscript: {_display_identifier(record['manuscript_location'])}"
            ),
        }
        for record in claim_records
    ]
    definitions = (
        ("catalog_table", "tbl:catalog", "Catalog and source-tiered evidence matrix", ("ID", "Construction", "Evidence / status", "Sources", "Supported claim"), catalog_records, catalog_display_records, ("id_display", "construction", "evidence_status", "sources_display", "supported_claim"), "Catalog entries and source-supported physical claims; implementation status does not imply observer validation. Full source roles and URLs remain in the machine-readable evidence matrix."),
        ("parameter_domains_table", "tbl:parameters", "Typed parameter domains and units", ("Type", "Unit", "Validated domain", "Role"), parameter_records, parameter_records, ("type", "unit", "domain", "role"), "Typed domains are validation contracts, not estimates of perceptual sensitivity."),
        ("encoding_profiles_table", "tbl:encodings", "Encoding profiles and backend capabilities", ("Format", "Backend", "Artifact", "Profile", "Status"), encoding_records, encoding_records, ("format", "backend", "artifact", "profile", "status"), "Backend status is environment-dependent; encoded files are inspected after delivery."),
        ("metrics_table", "tbl:metrics", "Objective metric definitions", ("Metric", "Unit", "Definition", "Tolerance", "Claim level"), metric_records, metric_records, ("metric", "unit", "definition", "tolerance", "claim_level"), "Metrics are deterministic artifact properties and do not report observer outcomes."),
        ("observer_estimands_table", "tbl:observer_estimands", "Observer outcomes and preregistered estimands", ("Estimand", "Response and model", "Reference and contrast", "Uncertainty"), observer_records, observer_display_records, ("estimand_display", "response_model", "reference_contrast", "uncertainty"), "This is a data-free analysis design; no participant result is included."),
        ("verification_failure_modes_table", "tbl:verification", "Verification failure modes and negative controls", ("Failure mode", "Control", "Expected result"), verification_records, verification_records, ("failure_mode", "control", "result"), "Negative controls define package failure behavior, not scientific null results."),
        ("caption_audit_table", "tbl:caption_audit", "Figure caption, provenance, and accessibility audit", ("Figure / claim level", "Source and evidence", "Controls and objective facts", "Limitations, boundary, and accessibility"), caption_records, caption_display_records, ("label_claim", "source_evidence", "controls_objective", "limitations_boundary_accessibility"), "Every caption is code-owned, source-linked, explicit about controls and objective facts, bounded by limitations, and accompanied by accessibility notes."),
        ("evidence_source_audit_table", "tbl:evidence_audit", "Evidence source, claim, engineering, and limitation audit", ("Key", "Record and citations", "DOI and URL", "Verification", "Supported claim / engineering / limitation"), source_audit_records, source_audit_display_records, ("key_display", "record_display", "doi_url", "verification_display", "supported_claim"), "Source rows distinguish the checked-in snapshot from live DOI metadata verification; entry rows expose engineering bases, limitations, and planned/input-required gaps. Network verification is a separate command."),
        ("formalism_traceability_table", "tbl:formalism", "Formalism traceability registry", ("Label", "Definition and symbols", "Implementation and tests", "Figures and claim level"), formalism_records, formalism_display_records, ("label_display", "definition_symbols", "implementation_tests", "figures_level"), "Formal definitions connect implementation and tests without converting engineering traceability into empirical evidence."),
        ("claim_ledger_table", "tbl:claim_ledger", "Claim ledger and source-to-limitation lineage", ("Claim ID", "Claim and level", "Basis", "Lineage and limitation"), claim_records, claim_display_records, ("claim_id_display", "claim_level_display", "basis", "lineage_limit"), "The ledger distinguishes code-derived facts, checked-in scholarship, engineering departures, limitations, package scope, and future observer hypotheses."),
    )
    result: dict[str, dict[str, object]] = {}
    for stem, label, title, headers, records, display_records, keys, caption in definitions:
        result[stem] = {
            "label": label,
            "title": title,
            "headers": list(headers),
            "records": records,
            "body": "\n".join(_markdown_row(record[key] for key in keys) for record in display_records),
            "caption": caption,
        }
    return result


def _table_markdown(payload: Mapping[str, object]) -> str:
    headers = payload["headers"]
    return (
        f"# {payload['title']}\n\n" + _markdown_row(headers) + "\n"
        + _markdown_row("---" for _ in headers) + "\n" + payload["body"]
        + f"\n\n: {payload['caption']} {{#{payload['label']}}}\n"
    )


def validate_publication_tables(output_dir: Path) -> None:
    """Compare every publication table with its code-owned data and Markdown."""
    for stem, payload in publication_table_payloads().items():
        path = output_dir / "data" / f"{stem}.json"
        expected = jsonable({"schema_version": "duckrabbit/table/v1", **payload})
        actual = json.loads(path.read_text(encoding="utf-8"))
        if json.dumps(actual, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
            raise ValueError(f"publication table JSON disagrees with code: {stem}")
        markdown = output_dir / "data" / f"{stem}.md"
        if markdown.read_text(encoding="utf-8") != _table_markdown(payload):
            raise ValueError(f"publication table Markdown disagrees with code: {stem}")


def validate_publication_visual_qa(output_dir: Path) -> None:
    """Recompute the independent visual-QA report from actual image files."""
    expected = {
        "schema_version": "duckrabbit/visual-qa/v1",
        "figure_count": len(publication_caption_specs()),
        "scales": ["full", "publication_column", "thumbnail"],
        "figures": [
            {"label": spec.label, "path": f"output/figures/{spec.stem}.png",
             **_visual_qa(output_dir / "figures" / f"{spec.stem}.png")}
            for spec in publication_caption_specs()
        ],
    }
    path = output_dir / "reports" / "visual_qa.json"
    if json.loads(path.read_text(encoding="utf-8")) != expected:
        raise ValueError("independent visual QA report disagrees with inspected figures")


def validate_publication_report(output_dir: Path) -> None:
    """Validate publication totals, bundle references, cover, and registry digest."""
    path = output_dir / "reports" / "publication_report.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(report, dict) or not isinstance(report.get("registry"), str):
        raise ValueError("publication report must contain its registry reference")
    registry_reference = Path(report["registry"])
    if report["registry"] != "output/figures/figure_registry.json":
        raise ValueError("publication report registry reference is invalid")
    report_root = registry_reference.parent.parent
    expected = {
        "figure_count": len(publication_caption_specs()),
        "table_count": len(publication_table_payloads()),
        "table_files": [str(report_root / "data" / f"{stem}.md") for stem in publication_table_payloads()],
        "registry": str(registry_reference),
        "cover": json.loads((output_dir / "reports" / "cover_visualization.json").read_text(encoding="utf-8")),
        "sha256": hashlib.sha256((output_dir / "figures" / "figure_registry.json").read_bytes()).hexdigest(),
    }
    if report != expected:
        raise ValueError("publication report disagrees with the publication bundle")


def _table_files(data_dir: Path) -> tuple[str, ...]:
    data_dir.mkdir(parents=True, exist_ok=True)
    payloads = publication_table_payloads()
    paths: list[str] = []
    for stem, payload in payloads.items():
        text = _table_markdown(payload)
        path = data_dir / f"{stem}.md"
        atomic_write_text(path, text)
        _write_json(data_dir / f"{stem}.json", {"schema_version": "duckrabbit/table/v1", **payload})
        paths.append(str(path))
    return tuple(paths)


def _figure_builders():
    return (
        ("fig:architecture", "architecture", _architecture), ("fig:catalog_matrix", "catalog_matrix", _catalog),
        ("fig:visual_panel", "visual_panel", _visual_panel), ("fig:visual_sweep", "visual_sweep", _visual_sweep),
        ("fig:temporal_sequence", "temporal_sequence", _temporal), ("fig:audio_signals", "audio_signals", _audio),
        ("fig:audiovisual_timeline", "audiovisual_timeline", _audiovisual), ("fig:encoding_verification", "encoding_verification", _encoding),
        ("fig:synthetic_psychophysics", "synthetic_psychophysics", _observer), ("fig:claim_boundary", "claim_boundary", _claim_boundary),
        ("fig:scholarship_map", "scholarship_map", _scholarship_map), ("fig:formalism_traceability", "formalism_traceability", _formalism_traceability),
        ("fig:metrics_dashboard", "metrics_dashboard", _metrics_dashboard), ("fig:parameter_domains", "parameter_domains", _parameter_domains),
        ("fig:observer_protocol", "observer_protocol", _observer_protocol),
        ("fig:graphical_abstract", "graphical_abstract", _graphical_abstract),
    )


def _render_environment() -> dict[str, str]:
    font = Path(_font(20).path)
    return {"pillow": PILLOW_VERSION, "numpy": np.__version__, "font_file": font.name,
            "font_sha256": hashlib.sha256(font.read_bytes()).hexdigest(),
            "renderer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def validate_publication_derivation(output_dir: Path) -> None:
    """Replay every scientific panel and compare actual data and raster bytes.

    This is a deterministic current-renderer consistency oracle, not an
    independent implementation of the scientific model or human visual QA.
    """
    output_dir = Path(output_dir)
    registry = json.loads((output_dir / "figures" / "figure_registry.json").read_text())
    if registry.get("render_environment") != _render_environment():
        raise ValueError("publication renderer/font/dependency provenance is stale; regenerate outputs")
    with TemporaryDirectory(prefix=".duckrabbit-replay-", dir=output_dir.parent) as temporary:
        for label, stem, builder in _figure_builders():
            replay = Path(temporary) / f"{stem}.png"
            digest, data = builder(replay)
            expected = jsonable({"schema_version": "duckrabbit/figure-source/v1", "figure_label": label,
                "figure_stem": stem, "generator": f"duckrabbit.publication.{builder.__name__}",
                "seed": 0, "parameters": {"seed": 0, "figure_stem": stem}, "data": data})
            actual = json.loads((output_dir / "data" / f"{stem}.json").read_text())
            if json.dumps(actual, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
                raise ValueError(f"publication source data disagree with live derivation: {stem}")
            if hashlib.sha256((output_dir / "figures" / f"{stem}.png").read_bytes()).hexdigest() != digest:
                raise ValueError(f"publication raster disagrees with live derivation: {stem}")
    from .publication_panels import validate_readable_figure_panels

    validate_readable_figure_panels(output_dir, replay_sources=False)


def generate_publication_outputs(output_dir: Path = Path("output"), *, clean: bool = False) -> dict[str, object]:
    """Generate figures, source-data sidecars, registry, and tables.

    ``clean`` is explicit because callers may pass a shared output directory;
    generation itself never deletes files it did not create.
    """
    output_dir = Path(output_dir)
    validate_formalism_registry()
    figures_dir = output_dir / "figures"
    data_dir = output_dir / "data"
    figure_builders = _figure_builders()
    expected_figure_stems = {stem for _, stem, _ in figure_builders}
    expected_data_stems = expected_figure_stems | set(publication_table_payloads())
    protected_names = {"AGENTS.md", "README.md", "manuscript_variables.json", "figure_registry.json"}
    expected_figure_stems |= {"cover_visualization", "cover_visualization-thumb"}
    if clean:
        for directory, expected_stems, suffixes in (
            (figures_dir, expected_figure_stems, (".png", ".webp")),
            (data_dir, expected_data_stems, (".json", ".md")),
        ):
            if directory.exists():
                for candidate in directory.iterdir():
                    if candidate.is_file() and candidate.suffix in suffixes and candidate.stem not in expected_stems and candidate.name not in protected_names:
                        candidate.unlink()
    caption_specs = {spec.label: spec for spec in publication_caption_specs()}
    visual_qa_records: list[dict[str, object]] = []
    registry: dict[str, object] = {
        "schema_version": "duckrabbit/figures/v1",
        "figure_count": len(figure_builders),
        "render_environment": _render_environment(),
        "figures": [],
    }
    for label, stem, builder in figure_builders:
        figure_path = figures_dir / f"{stem}.png"
        digest, data = builder(figure_path)
        visual_qa = _visual_qa(figure_path)
        data_path = data_dir / f"{stem}.json"
        _write_json(data_path, {
            "schema_version": "duckrabbit/figure-source/v1",
            "figure_label": label,
            "figure_stem": stem,
            "generator": f"duckrabbit.publication.{builder.__name__}",
            "seed": 0,
            "parameters": {"seed": 0, "figure_stem": stem},
            "data": data,
        })
        source_data_digest = hashlib.sha256(data_path.read_bytes()).hexdigest()
        spec = caption_specs[label]
        registry["figures"].append({
            "label": label,
            "filename": f"{stem}.png",
            "path": f"output/figures/{stem}.png",
            "source_data": f"output/data/{stem}.json",
            "title": spec.title,
            "caption": spec.rendered_caption,
            "caption_core": spec.caption,
            "alt_text": spec.alt_text,
            "accessibility": {
                "color_independent": True,
                "text_labels": True,
                "notes": "Interpret plotted values from the labels and source-data sidecar; color is not the sole encoding.",
            },
            "parameters": {"seed": 0, "figure_stem": stem},
            "claim_level": spec.claim_level.value,
            "evidence_references": list(spec.evidence_references),
            "limitations": list(spec.limitations),
            "controls": spec.controls,
            "objective_facts": spec.objective_facts,
            "boundary_statement": spec.boundary_statement,
            "sha256": digest,
            "source_data_sha256": source_data_digest,
            "generator": "duckrabbit.publication.generate_publication_outputs",
            "generated_by": "duckrabbit.publication.generate_publication_outputs",
            "seed": 0,
            "visual_qa": visual_qa,
        })
        visual_qa_records.append({"label": label, "path": f"output/figures/{stem}.png", **visual_qa})
    registry_path = figures_dir / "figure_registry.json"
    _write_json(registry_path, registry)
    validate_figure_registry(registry_path, output_dir=output_dir)
    from .publication_panels import generate_readable_figure_panels

    generate_readable_figure_panels(output_dir)
    tables = _table_files(data_dir)
    cover = install_cover(output_dir)
    _write_json(output_dir / "reports" / "visual_qa.json", {
        "schema_version": "duckrabbit/visual-qa/v1",
        "figure_count": len(visual_qa_records),
        "scales": ["full", "publication_column", "thumbnail"],
        "figures": visual_qa_records,
    })
    report = {"figure_count": len(figure_builders), "table_count": len(tables), "table_files": [f"output/data/{Path(path).name}" for path in tables], "registry": "output/figures/figure_registry.json", "cover": cover, "sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest()}
    _write_json(output_dir / "reports" / "publication_report.json", report)
    return report


__all__ = ["generate_publication_outputs", "publication_caption_specs", "publication_table_payloads", "validate_figure_registry", "validate_publication_tables", "validate_publication_visual_qa", "validate_publication_report"]
