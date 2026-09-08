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
import textwrap
from collections.abc import Mapping
from typing import Iterable
from urllib.parse import urlsplit

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .artifacts import AudioBuffer, AudiovisualTimeline, CanonicalArtifact, VideoSequence
from .canonical import canonical_digest
from .claims import default_claim_registry
from .cover import install_cover
from .evidence import load_evidence_matrix
from .formalism import formalism_registry, validate_formalism_registry
from .generators import DuckRabbitParams, default_parameters, default_registry
from .io import atomic_write_text
from .metrics import measure_artifact
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


def _wrapped(value: object, width: int) -> str:
    """Wrap publication text without silently dropping scholarly content."""
    return "\n".join(
        textwrap.wrap(
            str(value),
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    ) or ""


def _text_block(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: object,
    width: int,
    size: int = 16,
    fill: tuple[int, int, int] = INK,
) -> None:
    """Draw wrapped text for figures whose claims need more than one line."""
    draw.multiline_text(xy, _wrapped(value, width), font=_font(size), fill=fill, spacing=4)


def _cell_text(value: object) -> str:
    """Fit a catalog cell into its fixed column, keeping whole tokens.

    Composite values are cut at a comma boundary with an explicit ellipsis;
    the complete value stays available in the source-data sidecar.
    """
    text = str(value)
    if len(text) <= 34:
        return text
    head, separator, _ = text.partition(",")
    if separator:
        return head[:31].rstrip(",") + ",…"
    return text[:33] + "…"


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
    _text(draw, (left + (right - left) // 2 - 55, bottom + 43), x_label, 16, MUTED)
    _text(draw, (max(0, left - 70), top - 30), y_label, 16, MUTED)


def _panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, accent: tuple[int, int, int] = ACCENT) -> None:
    """Add a thin publication panel rule without heavy dashboard chrome."""
    draw.rounded_rectangle(box, radius=14, outline=(215, 221, 228), width=2)
    draw.line((box[0], box[1] + 46, box[2], box[1] + 46), fill=accent, width=4)


def _footer(draw: ImageDraw.ImageDraw, text: str, *, y: int, color: tuple[int, int, int] = MUTED, right: int = 1850) -> None:
    """Place a compact epistemic note in the figure's lower margin."""
    draw.line((50, y - 18, right, y - 18), fill=(225, 229, 234), width=1)
    _text(draw, (55, y), text, 16, color)


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
    image = Image.new("RGB", (1800, 760), CANVAS)
    draw = ImageDraw.Draw(image)
    boxes = [(60, 260, 300, 430), (390, 260, 630, 430), (720, 260, 960, 430), (1050, 260, 1290, 430), (1380, 260, 1740, 430)]
    labels = [
        ("Typed request", "i, θ, seed, encoding"),
        ("Generator", "Gᵢ(θ; s)"),
        ("Canonical artifact", "LE float32 + clock"),
        ("Encode / inspect", "Eₑ, D, decoded facts"),
        ("Manifest + verify", "hashes + claims"),
    ]
    claim_levels = ("request", "canonical", "delivery", "delivery", "provenance")
    for index, (box, (title, detail), level) in enumerate(zip(boxes, labels, claim_levels)):
        accent = ACCENT if index < 2 else GREEN if index == 2 else AMBER if index < 4 else RED
        draw.rounded_rectangle(box, radius=20, outline=accent, width=5, fill=(247, 249, 251))
        _text(draw, (box[0] + 20, box[1] + 22), f"{index + 1:02d}", 22, accent)
        _text(draw, (box[0] + 20, box[1] + 64), title, 23)
        _text_block(draw, (box[0] + 20, box[1] + 112), detail, 20, 17, MUTED)
        _text(draw, (box[0] + 20, box[3] - 30), level, 15, accent)
    for first, second in zip(boxes, boxes[1:]):
        draw.line((first[2] + 10, 345, second[0] - 10, 345), fill=INK, width=4)
        draw.polygon(((second[0] - 10, 345), (second[0] - 28, 334), (second[0] - 28, 356)), fill=INK)
    _text(draw, (60, 65), "DuckRabbit reproducibility contract", 38)
    _text(draw, (60, 125), "Canonical identity is established before delivery; decoded inspection tests what was actually written.", 22, MUTED)
    _footer(draw, "Engineering trace only: deterministic media facts and verification are not observer evidence.", y=690)
    digest = _save(image, path)
    return digest, {"stages": [title for title, _ in labels], "equations": ["A = Gᵢ(θ; s)", "h₍c₎ = H(c(A))", "V(F, M) ∈ {pass, fail}"]}


def _catalog(path: Path) -> tuple[str, dict[str, object]]:
    entries = taxonomy_entries()
    image = Image.new("RGB", (1900, 1700), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 35), "Catalog status and evidence matrix", 36)
    _text(draw, (50, 82), "Taxonomy facets are orthogonal; status and evidence are separate dimensions.", 20, MUTED)
    headers = ("ID", "modality", "mechanism", "signature", "input", "status")
    x = (45, 355, 590, 850, 1230, 1630)
    for pos, header in zip(x, headers):
        _text(draw, (pos, 105), header, 19, MUTED)
    y = 150
    for entry in entries:
        status_color = GREEN if entry.implementation_status is ImplementationStatus.IMPLEMENTED else AMBER if entry.implementation_status is ImplementationStatus.PLANNED else RED
        values = (
            entry.illusion_id,
            ",".join(item.value for item in entry.modalities),
            ",".join(item.value for item in entry.mechanisms),
            ",".join(item.value for item in entry.signatures),
            entry.input_requirement.value,
            entry.implementation_status.value,
        )
        for pos, value in zip(x, values):
            _text(draw, (pos, y), _cell_text(value), 15, status_color if pos == x[-1] else INK)
        draw.line((45, y + 31, 1840, y + 31), fill=(224, 228, 233), width=1)
        y += 72
    data = {"entries": [jsonable(entry) for entry in entries]}
    digest = _save(image, path)
    return digest, data


def _visual_panel(path: Path) -> tuple[str, dict[str, object]]:
    ids = tuple(entry.illusion_id for entry in taxonomy_entries() if Modality.VISUAL in entry.modalities and entry.implementation_status is ImplementationStatus.IMPLEMENTED)
    # Reserve a separate lower margin for the epistemic footer; the third row
    # of cards reaches y=1595, so the canvas must extend beyond that boundary.
    image = Image.new("RGB", (1900, 1770), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 25), "Complete panel of implemented visual constructions", 42)
    _text(draw, (50, 75), "One typed default per implemented entry. Static families show canonical rasters; apparent motion shows frame 1, with sequence facts retained in source data.", 24, MUTED)
    _text(draw, (50, 108), "Reading guide: luminance and raster levels describe pixels; frame rate and frame delta describe temporal media; neither is an observer report.", 18, MUTED)
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
        x, y = 40 + column * 620, 140 + row * 500
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
        _text(draw, (x + 20, y + 347), kind, 16, ACCENT if "first frame" in kind else MUTED)
        _text(draw, (x + 20, y + 378), summary, 17, MUTED)
        _text(draw, (x + 20, y + 409), detail, 17, MUTED)
        records.append({"illusion_id": illusion_id, "canonical_digest": digest_text, "metrics": metrics, "seed": 0, "parameter_boundary": "typed default parameters"})
    _footer(draw, "Physical image metrics: relative luminance (Rec. 709 for RGB), normalized raster levels, and canonical digest. The panel is complete for currently implemented visual entries, not exhaustive of visual illusions in the literature.", y=1665)
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
            draw.rectangle((x - 3, y - 3, x + 253, y + 143), outline=(218, 224, 230), width=1)
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
    _text(draw, (50, 68), f"frame rate = {artifact.frame_rate.value:g} frames/s · frame count = {artifact.frame_count} · rational timebase = {rate_fraction.numerator}/{rate_fraction.denominator}", 20, MUTED)
    for index in range(len(shown_frames)):
        _text(draw, (65 + index * 235, 275), f"f{index}  t={index / artifact.frame_rate.value:.3f}s", 15, INK)
    _text(draw, (50, 335), "Adjacent-frame mean absolute difference", 20, MUTED)
    plot_box = (125, 390, 1760, 650)
    _axes(draw, plot_box, x_label="frame transition k", y_label="normalized pixel difference", x_ticks=tuple((index, str(index)) for index in range(max(1, len(artifact.temporal_deltas)))), y_ticks=((0.0, "0"), (0.5, "0.5"), (1.0, "1.0")), x_range=(0.0, max(1.0, len(artifact.temporal_deltas) - 1)), y_range=(0.0, 1.0))
    _line_plot(draw, artifact.temporal_deltas, plot_box, ACCENT, value_range=(0.0, 1.0))
    _footer(draw, "Frame timestamps and deltas are decoded/canonical timing facts; apparent motion remains an observer-level hypothesis.", y=755)
    digest = _save(image, path)
    return digest, {"frame_rate": artifact.frame_rate.value, "frame_rate_rational": {"numerator": rate_fraction.numerator, "denominator": rate_fraction.denominator}, "frame_count": artifact.frame_count, "timestamps_seconds": [index / artifact.frame_rate.value for index in range(artifact.frame_count)], "temporal_deltas": artifact.temporal_deltas}


def _audio(path: Path) -> tuple[str, dict[str, object]]:
    ids = ("audio.shepard_tone", "audio.missing_fundamental", "audio.tritone_paradox", "audio.octave_illusion", "audio.auditory_continuity")
    image = Image.new("RGB", (1900, 1650), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 25), "Auditory canonical signals", 36)
    _text(draw, (50, 72), "Canonical waveforms, one-sided spectral summaries, and typed playback facts; no pitch report is inferred.", 20, MUTED)
    records = []
    for row, illusion_id in enumerate(ids):
        artifact = _generate(illusion_id)
        if not isinstance(artifact, AudioBuffer):
            raise TypeError(f"{illusion_id} must generate AudioBuffer")
        samples = artifact.samples[:, 0]
        stride = max(1, len(samples) // 350)
        values = samples[::stride]
        x, y = 50, 115 + row * 290
        _panel(draw, (x - 8, y - 8, 1840, y + 235), accent=ACCENT if row % 2 == 0 else GREEN)
        _text(draw, (x, y), illusion_id, 22)
        # Reserve a true left margin for the vertical label; this keeps the
        # word "amplitude" intact at full and publication-column scales.
        plot_box = (x + 105, y + 42, 1120, y + 190)
        _axes(draw, plot_box, x_label="normalized sample index", y_label="", x_ticks=((0.0, "0"), (0.5, "0.5"), (1.0, "1.0")), y_ticks=((-1.0, "−1"), (0.0, "0"), (1.0, "1")), x_range=(0.0, 1.0), y_range=(-1.0, 1.0))
        _text(draw, (x + 35, y + 82), "amplitude", 16, MUTED)
        _line_plot(draw, values, plot_box, ACCENT, value_range=(-1.0, 1.0))
        metrics = measure_artifact(artifact).to_dict()
        _text(draw, (1180, y + 52), f"RMS {metrics['values']['rms']:.4f} normalized amplitude", 17, MUTED)
        _text(draw, (1180, y + 85), f"peak {metrics['values']['peak']:.4f} normalized amplitude", 17, MUTED)
        _text(draw, (1180, y + 118), f"centroid {metrics['values']['spectral_centroid_hz']:.1f} Hz", 17, MUTED)
        _text(draw, (1180, y + 151), f"bandwidth {metrics['values']['spectral_bandwidth_hz']:.1f} Hz · crest {metrics['values']['crest_factor']:.2f}", 17, MUTED)
        spectrum = np.abs(np.fft.rfft(samples))
        bins = spectrum[1 : max(2, len(spectrum) // 2)]
        bins = bins[np.linspace(0, len(bins) - 1, 48).astype(int)]
        scale = max(float(np.max(bins)), 1e-12)
        _text(draw, (1500, y + 42), "spectral magnitude (relative)", 16, MUTED)
        for bin_index, magnitude in enumerate(bins):
            bar_height = int(135 * float(magnitude) / scale)
            x0 = 1500 + bin_index * 7
            draw.rectangle((x0, y + 205 - bar_height, x0 + 5, y + 205), fill=GREEN)
        records.append({"illusion_id": illusion_id, "metrics": metrics, "canonical_digest": canonical_digest(artifact)})
    _footer(draw, "Audio metrics are canonical-buffer properties; playback level, transducers, and listener organization remain external.", y=1580)
    digest = _save(image, path)
    return digest, {"signals": records, "spectral_definition": "one-sided FFT magnitude sampled into 48 display bins", "seed": 0}


def _audiovisual(path: Path) -> tuple[str, dict[str, object]]:
    artifact = _generate("audiovisual.sound_induced_flash")
    if not isinstance(artifact, AudiovisualTimeline):
        raise TypeError("audiovisual.sound_induced_flash must generate AudiovisualTimeline")
    image = Image.new("RGB", (1900, 1020), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 25), "Audiovisual shared-clock timeline", 36)
    _text(draw, (50, 72), "Video and audio are plotted against normalized shared time; offsets are declared, not inferred from perception.", 20, MUTED)
    video_values = [float(np.mean(frame.pixels)) for frame in artifact.video.frames]
    audio_values = np.abs(artifact.audio.samples[:, 0])
    stride = max(1, len(audio_values) // 600)
    video_box = (140, 145, 1760, 350)
    audio_box = (140, 470, 1760, 675)
    _axes(draw, video_box, x_label="shared time (normalized)", y_label="video mean luminance", x_ticks=((0.0, "0"), (0.5, "0.5"), (1.0, "1.0")), y_ticks=((0.0, "0"), (0.5, "0.5"), (1.0, "1")), x_range=(0.0, 1.0), y_range=(0.0, 1.0))
    _line_plot(draw, video_values, video_box, RED, value_range=(0.0, 1.0))
    _axes(draw, audio_box, x_label="shared time (normalized)", y_label="audio absolute amplitude", x_ticks=((0.0, "0"), (0.5, "0.5"), (1.0, "1.0")), y_ticks=((0.0, "0"), (0.5, "0.5"), (1.0, "1")), x_range=(0.0, 1.0), y_range=(0.0, 1.0))
    _line_plot(draw, audio_values[::stride], audio_box, ACCENT, value_range=(0.0, 1.0))
    _text(draw, (50, 745), f"declared sync offset ΔAV = {artifact.sync_offset.value:g} ms", 22, INK)
    _text(draw, (780, 745), f"declared spatial discrepancy = {artifact.spatial_offset.value:g} normalized", 22, INK)
    _text(draw, (50, 800), f"video frames = {artifact.video.frame_count} · frame rate = {artifact.video.frame_rate.value:g} frames/s · audio samples = {artifact.audio.sample_count} · sample rate = {artifact.audio.sample_rate.value:g} Hz", 18, MUTED)
    _footer(draw, "The aligned traces verify physical timing metadata; audiovisual capture or temporal recalibration requires a controlled observer task.", y=935)
    digest = _save(image, path)
    return digest, {"sync_offset_ms": artifact.sync_offset.value, "spatial_offset": artifact.spatial_offset.value, "video_luminance": video_values, "audio_envelope": audio_values[::stride], "timebase": {"video_frames": artifact.video.frame_count, "frame_rate": artifact.video.frame_rate.value, "audio_samples": artifact.audio.sample_count, "sample_rate": artifact.audio.sample_rate.value}}


def _encoding(path: Path) -> tuple[str, dict[str, object]]:
    image = Image.new("RGB", (1900, 900), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 30), "Encoding and verification surface", 36)
    headers = ("format", "backend", "canonical fact preserved", "verification")
    xs = (60, 430, 800, 1450)
    for x, header in zip(xs, headers):
        _text(draw, (x, 115), header, 20, MUTED)
    rows = (("PNG", "Pillow", "image shape + float32 digest", "decoded dimensions"), ("WAV", "wave", "sample count + clock", "rate/channels/samples"), ("GIF", "Pillow", "frame count + timing", "decoded frames"), ("NPZ", "NumPy", "exact arrays + digest", "exact canonical round trip"), ("MP4", "ffmpeg", "canonical artifact + stream facts", "optional capability"))
    for row, values in enumerate(rows):
        y = 175 + row * 115
        for x, value in zip(xs, values):
            _text(draw, (x, y), value, 19, INK)
        draw.line((50, y + 42, 1840, y + 42), fill=(224, 228, 233), width=1)
    digest = _save(image, path)
    return digest, {"profiles": [dict(zip(headers, row)) for row in rows]}


def _observer(path: Path) -> tuple[str, dict[str, object]]:
    diagnostic = default_duck_rabbit_diagnostic()
    model = diagnostic.model
    points = diagnostic.points
    summary = diagnostic.summary
    image = Image.new("RGB", (1900, 1050), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 25), "Synthetic psychophysics: transparent feature observer", 36)
    _text(draw, (50, 72), "A deterministic model diagnostic varies duck_weight against a fixed reference; it is not a human or pretrained vision-model result.", 20, MUTED)
    plot_box = (145, 180, 1250, 670)
    # The model output occupies a narrow, analytic range.  Showing that range
    # explicitly makes the diagnostic legible without visually imitating a
    # human psychometric plot on a 0--1 probability axis.
    model_low, model_high = 0.48, 0.58
    _axes(draw, plot_box, x_label="duck_weight of comparison stimulus", y_label="model P(comparison)", x_ticks=((0.0, "0.00"), (0.5, "0.50"), (1.0, "1.00")), y_ticks=((model_low, "0.48"), (0.50, "0.50 reference"), (model_high, "0.58")), x_range=(0.0, 1.0), y_range=(model_low, model_high))
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
    for line_index, line in enumerate(contract_lines):
        _text(draw, (1360, 265 + line_index * 38), line, 16, INK)
    _text(draw, (1360, 510), f"reference = {diagnostic.reference_label}", 16, MUTED)
    _text(draw, (1360, 550), f"points = {summary['point_count']}", 16, MUTED)
    _text(draw, (1360, 590), f"P range = {summary['probability_min']:.3f}–{summary['probability_max']:.3f}", 16, MUTED)
    _text(draw, (50, 745), "Model-output scale: 0.48–0.58 · reference = 0.50 · human_data: false · training_data: none", 20, RED)
    _footer(draw, "This curve diagnoses sensitivity of a specified feature observer. It does not estimate a psychometric function or establish a perceptual effect.", y=940)
    digest = _save(image, path)
    return digest, diagnostic.to_dict()


def _claim_boundary(path: Path) -> tuple[str, dict[str, object]]:
    image = Image.new("RGB", (1900, 1050), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (55, 35), "Claim-level boundary", 38)
    _text(draw, (55, 95), "Each stage exposes a different kind of evidence; later stages do not retroactively validate perception.", 21, MUTED)
    stages = (
        ("canonical_stimulus", "typed request → deterministic buffer", ACCENT),
        ("physical_metric", "shape, clock, luminance, spectrum", GREEN),
        ("encoded_media", "container + decoded inspection", AMBER),
        ("observer_hypothesis", "future protocol and estimand", RED),
    )
    boxes = []
    for index, (level, detail, color) in enumerate(stages):
        x = 85 + index * 455
        box = (x, 300, x + 360, 610)
        boxes.append(box)
        draw.rounded_rectangle(box, radius=25, fill=(247, 249, 251), outline=color, width=8)
        _text(draw, (x + 25, 350), str(index + 1), 32, color)
        _text(draw, (x + 25, 415), level, 25)
        _text(draw, (x + 25, 480), detail, 18, MUTED)
    for first, second in zip(boxes, boxes[1:]):
        draw.line((first[2] + 12, 455, second[0] - 12, 455), fill=INK, width=5)
        draw.polygon(((second[0] - 12, 455), (second[0] - 28, 444), (second[0] - 28, 466)), fill=INK)
    draw.rounded_rectangle((265, 760, 1635, 900), radius=18, fill=(253, 246, 238), outline=AMBER, width=4)
    _text(draw, (315, 805), "Boundary rule: deterministic media facts are package claims; observer effects require a separate validated study.", 23, INK)
    digest = _save(image, path)
    return digest, {"stages": [{"claim_level": level, "detail": detail} for level, detail, _ in stages], "observer_data": "none"}


def _scholarship_map(path: Path) -> tuple[str, dict[str, object]]:
    sources, evidence = load_evidence_matrix()
    entries = taxonomy_entries()
    columns = (55, 480, 820, 1120, 1410, 1810)
    headers = ("catalog entry", "primary", "review", "theory", "supported claim", "status")

    row_heights = []
    for entry in entries:
        record = evidence[entry.illusion_id]
        claim_lines = max(1, _wrapped(record.supported_claim, 42).count("\n") + 1)
        limitation_lines = max(1, _wrapped(f"limitation recorded: {record.evidence_limitations[0]}", 42).count("\n") + 1)
        content_height = claim_lines * 21 + 6 + limitation_lines * 16
        row_heights.append(max(92, content_height + 20))

    top_offset = 205
    image = Image.new("RGB", (2050, top_offset + sum(row_heights) + 60), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (45, 30), "Source-tiered scholarship map", 36)
    _text(draw, (45, 88), f"{len(evidence)} catalog entries; {len(sources)} source records; exact claims, engineering bases, and limitations are retained in source data.", 20, MUTED)
    for x, header in zip(columns, headers):
        _text(draw, (x, 155), header, 18, MUTED)
    rows = []
    y = top_offset
    for entry, row_height in zip(entries, row_heights):
        record = evidence[entry.illusion_id]
        values = (entry.illusion_id, len(record.primary_sources), len(record.review_sources), len(record.theory_sources), record.supported_claim, entry.implementation_status.value)
        color = GREEN if entry.implementation_status is ImplementationStatus.IMPLEMENTED else AMBER if entry.implementation_status.value == "planned" else RED
        for x, value in zip(columns[:4], values[:4]):
            _text(draw, (x, y), str(value), 15, INK)
        _text_block(draw, (columns[4], y - 4), values[4], 42, 14, INK)
        _text(draw, (columns[5], y), values[5], 15, color)
        claim_lines = max(1, _wrapped(values[4], 42).count("\n") + 1)
        limitation_y = y - 4 + claim_lines * 21 + 6
        _text_block(draw, (columns[4], limitation_y), f"limitation recorded: {record.evidence_limitations[0]}", 42, 10, MUTED)
        draw.line((45, y + row_height - 20, 1995, y + row_height - 20), fill=(229, 232, 236), width=1)
        rows.append({"illusion_id": entry.illusion_id, "primary": record.primary_sources, "review": record.review_sources, "theory": record.theory_sources, "supported_claim": record.supported_claim, "engineering_basis": record.engineering_basis, "limitations": record.evidence_limitations, "gap": entry.implementation_status.value != "implemented"})
        y += row_height
    digest = _save(image, path)
    return digest, {"source_count": len(sources), "entry_count": len(evidence), "rows": rows}


def _formalism_traceability(path: Path) -> tuple[str, dict[str, object]]:
    definitions = formalism_registry()
    image = Image.new("RGB", (2050, 205 + len(definitions) * 175 + 60), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 30), "Formalism traceability", 36)
    _text(draw, (50, 88), "Equation labels resolve to implementation modules, tests, figures, and claim levels.", 21, MUTED)
    columns = (55, 270, 900, 1260, 1640)
    headers = ("label", "equation", "implementation", "tests", "figures")
    for x, header in zip(columns, headers):
        _text(draw, (x, 150), header, 18, MUTED)
    records = []
    for row, definition in enumerate(definitions):
        y = 205 + row * 175
        values = (definition.label, definition.equation, ", ".join(definition.implementation), ", ".join(definition.tests), ", ".join(definition.figures))
        widths = (28, 58, 34, 34, 34)
        for x, value, width in zip(columns, values, widths):
            _text_block(draw, (x, y), value, width, 15, INK)
        _text(draw, (columns[0], y + 37), f"claim: {definition.claim_level.value}", 14, ACCENT)
        draw.line((50, y + 105, 2000, y + 105), fill=(229, 232, 236), width=1)
        records.append(definition.to_dict())
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
            _text(draw, (x + 35, y + 100 + metric_index * 58), f"{metric}: {rendered} {unit}", 18, INK)
        cards.append({"artifact": kind, "canonical_digest": canonical_digest(artifact), "metrics": metrics})
    digest = _save(image, path)
    return digest, {"cards": cards, "computation_version": "duckrabbit/metrics/v2"}


def _parameter_domains(path: Path) -> tuple[str, dict[str, object]]:
    records = (
        ("PixelDimension", PixelDimension.minimum, PixelDimension.maximum, "pixels"), ("Luminance", 0, 1, "normalized"), ("GrayscaleLevels", 2, 256, "levels"),
        ("QuantizationLevels", 2, 256, "levels"), ("FrequencyHz", 0.1, 24000, "Hz"), ("SampleRate", 1000, 384000, "samples/s"),
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
        _text(draw, (1570, y), f"{high:g} {unit}", 18, MUTED)
        draw.line((520, y + 15, 1530, y + 15), fill=(203, 211, 220), width=6)
        draw.ellipse((520 - 8, y + 7, 520 + 8, y + 23), fill=ACCENT)
        draw.ellipse((1530 - 8, y + 7, 1530 + 8, y + 23), fill=ACCENT)
        records_out.append({"type": name, "minimum": low, "maximum": high, "unit": unit})
    digest = _save(image, path)
    return digest, {"domains": records_out}


def _observer_protocol(path: Path) -> tuple[str, dict[str, object]]:
    design = default_study_design()
    image = Image.new("RGB", (2050, 1320), CANVAS)
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 30), "Observer protocol: orchestration boundary", 36)
    _text(draw, (50, 88), "The same stimulus manifest can feed a synthetic diagnostic now or a preregistered human study later; the data streams remain separate.", 21, MUTED)
    steps = (("trial identity", "pseudonym + condition + index"), ("randomization", f"seed={design.randomization_seed}; counterbalanced"), ("stimulus manifest", "canonical + encoded SHA-256"), ("response", "typed value + missingness"), ("estimand", "contrast + uncertainty interval"))
    boxes = []
    for index, (title, detail) in enumerate(steps):
        x = 60 + index * 395
        box = (x, 265, x + 320, 575)
        boxes.append(box)
        accent = ACCENT if index < 3 else GREEN
        draw.rounded_rectangle(box, radius=22, fill=(247, 249, 251), outline=accent, width=5)
        _text(draw, (x + 20, 305), f"{index + 1:02d}  {title}", 21, accent)
        _text_block(draw, (x + 20, 385), detail, 24, 17, MUTED)
        if index < len(steps) - 1:
            draw.line((x + 330, 420, x + 375, 420), fill=INK, width=4)
            draw.polygon(((x + 375, 420), (x + 360, 410), (x + 360, 430)), fill=INK)
    _text(draw, (60, 685), "Two explicitly different endpoints", 25, ACCENT)
    draw.rounded_rectangle((60, 735, 970, 1015), radius=20, fill=(241, 249, 244), outline=GREEN, width=5)
    _text(draw, (90, 775), "Synthetic psychophysics (included)", 23, GREEN)
    _text_block(draw, (90, 835), "duckrabbit.synthetic.feature_observer\nhand-specified features · analytic logistic rule\ntraining_data = none · human_data = false\noutput: model diagnostic, not a psychometric function", 48, 18, INK)
    draw.rounded_rectangle((1080, 735, 1990, 1015), radius=20, fill=(253, 246, 238), outline=AMBER, width=5)
    _text(draw, (1110, 775), "Human psychophysics (future contract)", 23, AMBER)
    _text_block(draw, (1110, 835), "display / playback calibration\nparticipant consent + pseudonymization\npreregistered response, exclusions, model\noutput: observer estimate with uncertainty", 48, 18, INK)
    _text(draw, (60, 1080), "Model templates for future human analysis", 25, ACCENT)
    for index, model in enumerate(default_model_specs()):
        _text(draw, (60 + (index % 2) * 970, 1130 + (index // 2) * 45), f"{model.model.value}: {model.family} / {model.link}", 16, INK)
    _footer(draw, "No participant records, fitted coefficients, or observer-level result is bundled; the included endpoint is model output only.", y=1280, color=RED, right=2000)
    digest = _save(image, path)
    return digest, {"study_id": design.study_id, "randomization_seed": design.randomization_seed, "steps": [{"name": name, "detail": detail} for name, detail in steps], "synthetic_model": {"model_id": "duckrabbit.synthetic.feature_observer", "training_data": "none", "human_data": False}, "human_study": {"status": "future", "participant_data": False}, "models": [model.to_dict() for model in default_model_specs()]}


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
        CaptionSpec("fig:visual_panel", "visual_panel", "Complete panel of implemented visual constructions", f"This complete gallery presents one deterministic representative from each of the {len(visual_entries)} currently implemented visual catalog entries: {visual_names}. The panel therefore covers the package's available visual families—ambiguous figure, contrast, apparent motion, geometric context, illusory contour, contextual size, and orientation-related constructions—using typed defaults at seed 0. For the temporally expressed apparent-motion entry, the displayed tile is its first frame and the source data preserve the full sequence. The source data sidecar output/data/visual_panel.json records the stable ID, generator parameters, canonical SHA-256 digest, Rec. 709 or grayscale luminance statistics, raster-level counts, and parameter boundary for every tile.", f"A {len(visual_entries)}-panel gallery shows every currently implemented visual catalog entry, with stable IDs and physical raster summaries: {visual_names}.", ClaimLevel.CANONICAL_STIMULUS, "output/data/visual_panel.json", ("gregory1997visual", "brugger1999duckrabbit", "howe2005muller", "morgan1999poggendorff", "fisher1967ponzo", "yildiz2022ponzo", "kanizsa1976contours", "mruczek2015ebbinghaus", "earle1995zollner", "wertheimer1912motion", "sekuler1996wertheimer"), ("The gallery is complete for implemented visual entries in this package, not a complete survey of visual illusions; literature families, historical displays, and DuckRabbit rasters are not pixel-identical by default.", "Viewing scale, display calibration, viewing distance, and observer conditions can change the relevance of a construction; the gallery does not measure an observer's perceptual report."), ("Each tile is labeled by stable illusion ID and accompanied by printed luminance, level-count, and digest fields; color only reinforces grouping and is not required to identify a stimulus.",), 0, "one default typed parameter object per implemented visual entry; seed s=0; dimensions, luminance bounds, grayscale, and quantization controls remain in each generator schema; temporal entries display their first frame but retain sequence metrics", "per tile: mean and standard-deviation relative luminance, unique raster levels, and canonical SHA-256 digest; temporal entries additionally retain frame count, frame rate, and frame deltas; definitions and units are in the source data JSON", "The figure establishes coverage of the package's implemented visual constructions and their deterministic raster facts. It does not establish that any viewer will perceive the named signature, nor that the set is exhaustive of the visual-illusion literature."),
        CaptionSpec("fig:visual_sweep", "visual_sweep", "Visual parameter sweep with physical readouts", "This 5×5 sweep varies duck–rabbit blend weight across rows and jointly varies grayscale and quantization levels across columns. Each cell is regenerated from an immutable typed parameter object at seed 0; source data output/data/visual_sweep.json records canonical digests, unique-level counts, normalized luminance, and effective dynamic range for every condition.", "A labeled grid crosses five duck–rabbit blend weights with five grayscale and quantization settings, with physical metrics recorded for each cell.", ClaimLevel.PHYSICAL_METRIC, "output/data/visual_sweep.json", ("brugger1999duckrabbit", "gregory1997visual"), ("The grid is a sensitivity of the construction parameters, not a psychophysical sensitivity curve or a validated observer effect.",), ("Row and column labels state the parameter values; numerical metrics and units are available in the sidecar.",), 0, "duck_weight ∈ {0,.25,.5,.75,1}; grayscale=quantization ∈ {2,4,8,16,32}; seed s=0", "25 canonical rasters; unique levels, normalized mean luminance, and effective dynamic range per cell", "The chosen grid is an engineering sampling of the parameter domain and does not imply an optimal or perceptually uniform spacing."),
        CaptionSpec("fig:temporal_sequence", "temporal_sequence", "Temporal sequence, clock, and frame deltas", "The frame strip exposes the order and timestamps of the apparent-motion construction, while the lower trace reports adjacent-frame mean absolute pixel differences. Source data output/data/temporal_sequence.json preserve frame count, frame rate, reduced rational timebase, timestamps in seconds, and the nonzero transition series; seed 0 identifies the generated sequence.", "Six ordered frames are labeled with timestamps and paired with a line plot of adjacent-frame normalized pixel differences.", ClaimLevel.PHYSICAL_METRIC, "output/data/temporal_sequence.json", ("wertheimer1912motion", "sekuler1996wertheimer"), ("Frame succession and frame deltas are physical file properties; playback timing, display persistence, and motion reports require a controlled observer task.",), ("Frame index, seconds, frames per second, and normalized-difference labels remain interpretable without color.",), 0, "visual.apparent_motion default typed parameters; frame rate and frame count from the canonical sequence; seed s=0", "timestamps in seconds, frame rate in frames/s, frame count, rational timebase, and adjacent-frame normalized pixel difference", "The figure documents temporal structure rather than the presence, direction, or strength of perceived motion."),
        CaptionSpec("fig:audio_signals", "audio_signals", "Auditory canonical signals and spectral summaries", "Five implemented auditory constructions—Shepard tone, missing fundamental, tritone paradox, octave illusion, and auditory continuity—are shown as canonical waveforms with compact one-sided FFT summaries. Source data output/data/audio_signals.json records sample rate, channel layout, RMS, peak, spectral centroid, bandwidth, crest factor, canonical digest, and the declared display-bin convention; no pitch or stream report is inferred.", "Five labeled rows show canonical audio waveforms, relative one-sided spectral bars, RMS and peak in normalized amplitude, and spectral summaries in hertz.", ClaimLevel.PHYSICAL_METRIC, "output/data/audio_signals.json", ("shepard1984scale", "zatorre2005missing", "deutsch1986tritone", "repp1997tritone", "deutsch1974octave", "warren1970continuity", "riecke2011continuity"), ("Playback level, transducer response, dichotic separation, masker design, and listener judgments are external to the canonical buffer.",), ("Waveform, spectral, amplitude, and frequency labels are printed; bar color is not the sole encoding.",), 0, "default typed audio parameters; per-generator channel layout and sample rate; seed s=0; one-sided FFT display with 48 sampled bins", "RMS and peak in normalized amplitude; spectral centroid and bandwidth in Hz; sample rate in samples/s; channel layout and canonical SHA-256 digest", "The figure compares generated signal properties and literature-linked families; it does not establish pitch, continuity, or stream organization for a listener."),
        CaptionSpec("fig:audiovisual_timeline", "audiovisual_timeline", "Audiovisual shared-clock timeline and declared offsets", "Video mean luminance and rectified audio amplitude are placed on a common normalized time axis for the sound-induced-flash construction. Source data output/data/audiovisual_timeline.json records the video frame clock, audio sampling clock, event traces, signed audio-minus-video synchronization offset in milliseconds, and normalized spatial discrepancy; alignment is declared by the generator, not estimated from perception.", "Two labeled traces share a normalized time axis: video mean luminance and audio absolute amplitude, with signed synchronization and spatial offsets printed below.", ClaimLevel.PHYSICAL_METRIC, "output/data/audiovisual_timeline.json", ("shams2000sifi", "hirst2020sound", "vroomen2004temporal", "hartcherobrien2011temporal"), ("Display refresh, audio hardware, event latency, and observer temporal binding are not measured by this figure.",), ("The two channels, time axis, signed offset convention, and normalized spatial discrepancy are labeled in text.",), 0, "audiovisual.sound_induced_flash default shared timeline; declared sync offset ΔAV and spatial offset; seed s=0", "video luminance and audio envelope on normalized shared time; ΔAV in ms; spatial discrepancy in normalized units; frame and sample clocks in the sidecar", "A shared-clock construction is not evidence that observers bind the events at the declared or any other perceptual time."),
        CaptionSpec("fig:encoding_verification", "encoding_verification", "Encoding profiles and verification scope", "The comparison separates the canonical artifact from delivery containers: PNG, WAV, GIF, NPZ, and optional MP4/muxed MP4. Source data output/data/encoding_verification.json records backend identity, preserved canonical facts, decoded inspection targets, and capability status as observed in the generation environment; the table therefore describes an adapter contract rather than a claim about codec quality.", "A five-row comparison lists format, backend, preserved canonical facts, and the corresponding decoded verification checks.", ClaimLevel.ENCODED_MEDIA, "output/data/encoding_verification.json", ("engineering:typed_media_adapters",), ("Backend availability, codec versions, container metadata, and lossy tolerances are environment-dependent; playback software can expose additional behavior.",), ("Format, backend, preserved fact, and verification columns are textual and remain usable without color.",), 0, "typed encoding profile selected per artifact; overwrite and backend capability checks; seed inherited from the stimulus request", "format availability and verification scope are environment observations; NPZ is exact while other formats are decoded and tolerance-checked", "A successful encode or decode does not validate an observer effect or guarantee cross-device perceptual equivalence."),
        CaptionSpec("fig:synthetic_psychophysics", "synthetic_psychophysics", "Synthetic observer diagnostic—model output, not human psychophysics", "The hand-specified feature observer compares duck_weight variants with a fixed canonical reference. Its probability trace is computed analytically from serialized features, weights, and temperature; source data output/data/synthetic_psychophysics.json records model ID/version, reference and comparison digests, seed, calibration, `training_data=none`, and `human_data=false`. The y-axis is deliberately a narrow model-output range rather than a human psychometric scale.", "A narrow-range line plot shows deterministic model probability across duck_weight values beside the model identity, temperature, no-training-data statement, and human-data boundary.", ClaimLevel.SYNTHETIC_MODEL_OUTPUT, "output/data/synthetic_psychophysics.json", ("observer:preregistered_estimands",), ("The model is hand-specified, has no training data, has not been calibrated against observers, and does not estimate a human threshold or effect size.", "Its probabilities are model outputs, not participant responses or a psychometric function."), ("Model scale, reference line, model identity, and `human_data=false` are printed; color is not needed to interpret the curve.",), 0, "duck_weight comparison against fixed reference; serialized feature weights and temperature; seed s=0", "model probability and score delta on the displayed model-output scale; canonical stimulus digests; human_data=false; training_data=none", "This diagnostic tests deterministic orchestration and metamorphic input-output behavior only; empirical psychophysics remains future work."),
        CaptionSpec("fig:claim_boundary", "claim_boundary", "Claim-level boundary from artifact to observer hypothesis", "The four-stage boundary distinguishes what DuckRabbit can establish directly—canonical stimulus identity, physical/media metrics, and decoded encoded-media facts—from a future observer hypothesis. Source data output/data/claim_boundary.json records the stage definitions and boundary rule; the arrows describe increasing evidential requirements, not an inference that one stage establishes the next.", "Four numbered boxes separate canonical stimulus, physical metric, encoded media, and observer hypothesis, with a boundary rule stating that observer effects require a separate study.", ClaimLevel.SOURCE_SUPPORTED, "output/data/claim_boundary.json", ("formalism:eq:observer_estimand", "formalism:eq:canonical_digest"), ("The diagram is a documentation contract and does not replace a preregistered observer study or empirical data.",), ("Each stage is named, numbered, and described in text; the boundary rule is readable without color.",), 0, "claim levels in the taxonomy and manifest; seed not applicable to the explanatory diagram", "no unit-bearing objective quantity is applicable; stage definitions and evidence boundaries are preserved in the sidecar", "A deterministic artifact can support a future hypothesis but cannot supply the observer data required to test it."),
        CaptionSpec("fig:scholarship_map", "scholarship_map", "Source-tiered scholarship map and evidence gaps", "The map links every catalog entry to its primary, review, and theory records, then preserves the exact source-supported claim, engineering departure, limitation, and implementation status. Source data output/data/scholarship_map.json are generated from the checked-in evidence matrix; a source record supports only the statement written in that record and does not certify pixel- or task-identical replication.", "Rows map catalog entries to source tiers, exact supported claims, engineering bases, limitations, and implementation status.", ClaimLevel.SOURCE_SUPPORTED, "output/data/scholarship_map.json", ("gregory1997visual", "brugger1999duckrabbit", "yildiz2022ponzo", "hirst2020sound", "bruns2019ventriloquist"), ("The offline snapshot validates citation and lineage structure; live resolver status is a separate audit, and classifications can remain contested.",), ("Source roles, claims, limitations, and statuses are printed or available in the sidecar; no category is encoded by color alone.",), 0, "checked-in evidence matrix; source roles and entry statuses; audit date recorded in data/evidence_matrix.json", f"one evidence row per catalog entry ({catalog_count} entries); source-tier counts, exact claim text, engineering basis, limitation, and gap status", "Scholarship coverage bounds the package’s evidence record and does not establish that any generated stimulus produces a universal percept."),
        CaptionSpec("fig:formalism_traceability", "formalism_traceability", "Formal definitions and implementation traceability", "The traceability registry connects the nine numbered equations to symbols, implementation modules, tests, and registered figures. Source data output/data/formalism_traceability.json is the machine-readable crosswalk used by the manuscript; it demonstrates contract coverage and test linkage without converting formal notation into empirical evidence.", "Rows connect equation labels to their mathematical definition, implementation paths, tests, figure labels, and claim levels.", ClaimLevel.PHYSICAL_METRIC, "output/data/formalism_traceability.json", ("formalism:eq:canonical_digest", "formalism:eq:clock_definition", "formalism:eq:objective_statistics"), ("Traceability records documentation and verification scope; it does not establish the truth of an observer-level theory.",), ("Equation labels, code paths, tests, and figure labels are written as text.",), 0, "formalism registry version; seed not applicable to the traceability diagram", "nine equation records with implementation, test, figure, and claim-level fields; no unit-bearing measurement is plotted", "A linked equation and test can show an implemented contract, not a validated perceptual law."),
        CaptionSpec("fig:metrics_dashboard", "metrics_dashboard", "Objective metrics dashboard with units and provenance", "The dashboard presents representative measurements from image, audio, video, and audiovisual canonical artifacts. Source data output/data/metrics_dashboard.json retains metric name, value, unit, computation version, tolerance, claim level, and canonical digest; luminance is normalized, amplitude is normalized, spectra are in hertz, frame differences are normalized pixel differences, and synchronization is in milliseconds.", "Four artifact cards list image, audio, video, and audiovisual metrics with units, computation provenance, and claim level.", ClaimLevel.PHYSICAL_METRIC, "output/data/metrics_dashboard.json", ("formalism:eq:objective_statistics", "formalism:eq:temporal_spectral_metrics"), ("Metrics are media properties and do not encode pitch, size, motion, localization, binding, or other observer interpretations.",), ("Every numerical value is paired with a printed unit or an explicit dimensionless definition.",), 0, "default canonical artifacts; metric computation version and tolerance recorded in the source-data sidecar; seed s=0", "finite objective values with units: normalized luminance/amplitude, Hz, normalized pixel difference, ms, counts, and durations", "Metric reproducibility is a package property; interpretation as perception requires a separate observer design and data."),
        CaptionSpec("fig:parameter_domains", "parameter_domains", "Typed parameter domains and units", "The domain map shows the validated ranges for dimensions, luminance, grayscale and quantization levels, frequency, sampling rate, frame rate, synchronization offset, and spatial discrepancy. Source data output/data/parameter_domains.json records the type name, unit, interval, and engineering role; intervals prevent malformed media and are not proposed as sensitivity thresholds.", "Horizontal interval markers show typed domains for dimensions, luminance, levels, frequency, sampling, frame rate, synchronization, and spatial discrepancy.", ClaimLevel.CANONICAL_STIMULUS, "output/data/parameter_domains.json", ("formalism:eq:typed_request",), ("The intervals are software validation bounds and do not encode safe listening levels, display limits, or psychophysical thresholds.",), ("Type names, endpoints, units, and roles are printed; interval color is redundant.",), 0, "parameter schema version and validated scalar domains; seed not applicable to the domain diagram", "dimensionless, pixel, level, Hz, samples/s, frames/s, ms, and normalized spatial units as listed per parameter", "A valid parameter is a reproducible construction request, not evidence that the requested value is perceptually effective."),
        CaptionSpec("fig:observer_protocol", "observer_protocol", "Observer protocol scaffold and estimand boundary", "The study-ready scaffold moves from pseudonymous trial identity and deterministic randomization to a stimulus manifest and encoded-file hash, typed response or missingness, and a preregistered estimand. Source data output/data/observer_protocol.json records the study design, randomization seed, model templates, and synthetic-only status; no participant record is included.", "A flow diagram connects trial identity, randomization, stimulus manifest, response, aggregate estimand, and analysis-model templates, with a synthetic-only boundary.", ClaimLevel.OBSERVER_HYPOTHESIS, "output/data/observer_protocol.json", ("observer:preregistered_estimands",), ("The scaffold specifies future data collection and analysis but supplies no participant responses, fitted coefficients, power claim, or validated observer effect.",), ("Every protocol step and the no-participant-data boundary is stated in text; arrows and labels remain legible without color.",), 0, "study design and deterministic randomization seed recorded in the sidecar; synthetic response generation is separate from human data", "trial counts, condition structure, estimand templates, response schemas, and model families; participant outcomes are not applicable", "The protocol is ready for ethical and preregistered extension, not evidence that the proposed effect exists."),
    )


_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


def validate_figure_registry(
    registry: Mapping[str, object] | Path,
    *,
    output_dir: Path | None = None,
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
        sources, _ = load_evidence_matrix()
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
        accessibility = record["accessibility"]
        if not isinstance(accessibility, Mapping) or accessibility.get("color_independent") is not True or accessibility.get("text_labels") is not True:
            raise ValueError(f"figure registry accessibility contract is incomplete for {label}")
        if not _SHA256_PATTERN.fullmatch(str(record["sha256"])) or not _SHA256_PATTERN.fullmatch(str(record["source_data_sha256"])):
            raise ValueError(f"figure registry hashes are invalid for {label}")
        if type(record["seed"]) is not int or not isinstance(record["parameters"], Mapping):
            raise ValueError(f"figure registry parameters are invalid for {label}")
        if record["parameters"].get("seed") != record["seed"]:
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
            if (
                source_payload.get("seed") != record["seed"]
                or not isinstance(source_payload.get("parameters"), Mapping)
                or source_payload["parameters"].get("seed") != record["seed"]
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
    """Make machine identifiers readable in the narrow printed tables."""
    return str(value).replace("entry:", "entry / ").replace("_", " ").replace("+", " / ")


def _display_url(value: object) -> str:
    """Use a breakable resolver label in printed tables; JSON keeps the URL."""
    raw = str(value)
    parsed = urlsplit(raw)
    return parsed.netloc or parsed.path or raw


def _display_doi_url(doi: object, url: object) -> str:
    """Summarize long DOI/URL values in print while retaining exact values in JSON."""
    doi_value = str(doi)
    if doi_value == "not_applicable":
        doi_label = "DOI: n/a"
    elif doi_value == "not_recorded":
        doi_label = "DOI: not recorded"
    else:
        doi_label = "DOI: recorded"
    return f"{doi_label}; URL host/path: {_display_url(url)}"


def _display_citation_keys(value: object) -> str:
    """Add print-only break opportunities to compact citation keys."""
    display = _display_identifier(value).replace(", ", "; ")
    display = re.sub(r"(?<=[a-z])(?=\d)", " ", display)
    return re.sub(r"(?<=\d)(?=[a-z])", " ", display)


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
            "sources_display": _display_citation_keys(record["sources"] or "none"),
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
        {"metric": "mean_luminance", "unit": "normalized_luminance", "definition": "mean Rec. 709 relative luminance (grayscale is identity)", "tolerance": "exact canonical", "claim_level": "physical_metric"},
        {"metric": "unique_values", "unit": "levels", "definition": "count of distinct canonical image values", "tolerance": "exact integer", "claim_level": "physical_metric"},
        {"metric": "rms", "unit": "normalized_amplitude", "definition": "root-mean-square audio amplitude", "tolerance": "finite scalar", "claim_level": "physical_metric"},
        {"metric": "peak", "unit": "normalized_amplitude", "definition": "maximum absolute audio amplitude", "tolerance": "finite scalar", "claim_level": "physical_metric"},
        {"metric": "spectral_centroid_hz", "unit": "Hz", "definition": "energy-weighted one-sided spectral centroid", "tolerance": "finite scalar", "claim_level": "physical_metric"},
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
            "key_display": _display_citation_keys(record["key"]),
            "record_display": f"{_display_identifier(record['source_type'])}; {_display_citation_keys(record['citation_key'] or 'none')}",
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
        {"claim_id": "publication:figure_count", "claim": f"The publication atlas contains {len(publication_caption_specs())} registered scientific figures.", "basis": "derived_from_code", "lineage": "publication_caption_specs()", "claim_level": "physical_metric", "limitation": "The count is a package-state fact, not evidence of empirical validity.", "manuscript_location": "manuscript/07_publication_audit.md"},
        {"claim_id": "publication:table_count", "claim": "The publication appendix contains the generated table set defined by the publication table payload registry.", "basis": "derived_from_code", "lineage": "publication_table_payloads()", "claim_level": "physical_metric", "limitation": "Generated tables summarize package state and do not replace source or observer evidence.", "manuscript_location": "manuscript/07_publication_audit.md"},
    ])
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


def _table_files(data_dir: Path) -> tuple[str, ...]:
    data_dir.mkdir(parents=True, exist_ok=True)
    payloads = publication_table_payloads()
    paths: list[str] = []
    for stem, payload in payloads.items():
        headers = payload["headers"]
        body = payload["body"]
        label = payload["label"]
        title = payload["title"]
        text = f"# {title}\n\n" + _markdown_row(headers) + "\n" + _markdown_row("---" for _ in headers) + "\n" + body + f"\n\n: {payload['caption']} {{#{label}}}\n"
        path = data_dir / f"{stem}.md"
        atomic_write_text(path, text)
        _write_json(data_dir / f"{stem}.json", {"schema_version": "duckrabbit/table/v1", **payload})
        paths.append(str(path))
    return tuple(paths)


def generate_publication_outputs(output_dir: Path = Path("output"), *, clean: bool = False) -> dict[str, object]:
    """Generate figures, source-data sidecars, registry, and tables.

    ``clean`` is explicit because callers may pass a shared output directory;
    generation itself never deletes files it did not create.
    """
    output_dir = Path(output_dir)
    validate_formalism_registry()
    figures_dir = output_dir / "figures"
    data_dir = output_dir / "data"
    figure_builders = (
        ("fig:architecture", "architecture", _architecture), ("fig:catalog_matrix", "catalog_matrix", _catalog),
        ("fig:visual_panel", "visual_panel", _visual_panel), ("fig:visual_sweep", "visual_sweep", _visual_sweep),
        ("fig:temporal_sequence", "temporal_sequence", _temporal), ("fig:audio_signals", "audio_signals", _audio),
        ("fig:audiovisual_timeline", "audiovisual_timeline", _audiovisual), ("fig:encoding_verification", "encoding_verification", _encoding),
        ("fig:synthetic_psychophysics", "synthetic_psychophysics", _observer), ("fig:claim_boundary", "claim_boundary", _claim_boundary),
        ("fig:scholarship_map", "scholarship_map", _scholarship_map), ("fig:formalism_traceability", "formalism_traceability", _formalism_traceability),
        ("fig:metrics_dashboard", "metrics_dashboard", _metrics_dashboard), ("fig:parameter_domains", "parameter_domains", _parameter_domains),
        ("fig:observer_protocol", "observer_protocol", _observer_protocol),
    )
    expected_figure_stems = {stem for _, stem, _ in figure_builders}
    expected_data_stems = expected_figure_stems | set(publication_table_payloads())
    if clean:
        for directory, expected_stems, suffixes in (
            (figures_dir, expected_figure_stems, (".png", ".webp")),
            (data_dir, expected_data_stems, (".json", ".md")),
        ):
            if directory.exists():
                for candidate in directory.iterdir():
                    if candidate.is_file() and candidate.suffix in suffixes and candidate.stem not in expected_stems and candidate.name not in {"figure_registry.json"}:
                        candidate.unlink()
    caption_specs = {spec.label: spec for spec in publication_caption_specs()}
    visual_qa_records: list[dict[str, object]] = []
    registry: dict[str, object] = {
        "schema_version": "duckrabbit/figures/v1",
        "figure_count": len(figure_builders),
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
    tables = _table_files(data_dir)
    cover = install_cover(output_dir)
    _write_json(output_dir / "reports" / "visual_qa.json", {
        "schema_version": "duckrabbit/visual-qa/v1",
        "figure_count": len(visual_qa_records),
        "scales": ["full", "publication_column", "thumbnail"],
        "figures": visual_qa_records,
    })
    report = {"figure_count": len(figure_builders), "table_count": len(tables), "table_files": tables, "registry": str(registry_path), "cover": cover, "sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest()}
    _write_json(output_dir / "reports" / "publication_report.json", report)
    return report


__all__ = ["generate_publication_outputs", "publication_caption_specs", "publication_table_payloads", "validate_figure_registry"]
