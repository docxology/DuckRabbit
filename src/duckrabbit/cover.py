"""Editorial cover installation and provenance manifest generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from collections.abc import Mapping

from PIL import Image

from .io import atomic_write_text


COVER_PROMPT = (
    "Use case: stylized-concept editorial cover illustration. "
    "Asset type: publication cover for a rigorous cognitive-science software methods paper. "
    "Primary request: a quiet, premium 4:5 charcoal-and-graphite illustration with one continuous "
    "ambiguous duck/rabbit contour, equally legible at thumbnail size, with one shared eye and "
    "shared face/neck geometry. Keep a clean dark upper third for later typesetting but embed no text. "
    "Use sparse burnt-sienna visual-channel traces and muted deep-purple technical/audio traces: "
    "waveforms, rational grid fragments, arcs, and provenance-like dots. "
    "Avoid a hard split-screen, duplicated animal, extra anatomy, photorealism, cartoon styling, "
    "neon color, heavy data-grid clutter, logos, watermarks, letters, numbers, or observer claims."
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COVER_SOURCE = PROJECT_ROOT / "assets" / "cover" / "duckrabbit-cover-v2.png"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install_cover(output_dir: Path = Path("output"), source_asset: Path | None = None) -> dict[str, object]:
    """Copy the previewed cover candidate and create portable delivery variants."""
    source = Path(source_asset) if source_asset is not None else DEFAULT_COVER_SOURCE
    if not source.is_file():
        raise FileNotFoundError(
            f"previewed cover source is unavailable: {source}. "
            "Pass an explicit source_asset, or place the project cover at "
            f"{DEFAULT_COVER_SOURCE}."
        )
    figures = Path(output_dir) / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    png = figures / "cover_visualization.png"
    webp = figures / "cover_visualization.webp"
    thumb = figures / "cover_visualization-thumb.png"
    image = Image.open(source).convert("RGB")
    if image.width <= 0 or image.height <= 0:
        raise ValueError("cover must have non-empty dimensions")
    image.save(png, format="PNG", optimize=True)
    image.save(webp, format="WEBP", quality=88, method=6)
    thumbnail = image.copy()
    thumbnail.thumbnail((320, 400), Image.Resampling.LANCZOS)
    thumbnail.save(thumb, format="PNG", optimize=True)
    try:
        source_asset_path = source.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
        source_scope = "project_asset"
    except ValueError:
        source_asset_path = source.as_posix()
        source_scope = "external_input"
    manifest = {
        "schema_version": "duckrabbit/cover/v1",
        "source_asset": source.name,
        "source_asset_path": source_asset_path,
        "source_scope": source_scope,
        "source_asset_sha256": _sha256(source),
        "source_asset_dimensions_px": {"width": image.width, "height": image.height},
        "source_kind": "editorial_charcoal_image_generation_v2",
        "model": "image_gen",
        "prompt_sha256": hashlib.sha256(COVER_PROMPT.encode()).hexdigest(),
        "selected_candidate": 4,
        "previewed": True,
        "dimensions_px": {"width": image.width, "height": image.height},
        "variants": {
            "png": {"path": "output/figures/cover_visualization.png", "sha256": _sha256(png)},
            "webp": {"path": "output/figures/cover_visualization.webp", "sha256": _sha256(webp)},
            "thumbnail": {"path": "output/figures/cover_visualization-thumb.png", "sha256": _sha256(thumb)},
        },
        "caption": "Editorial cover illustration combining an ambiguous duck/rabbit silhouette with waveform and construction motifs. It is a publication artifact, not an experimental stimulus or observer result. Source data are not applicable; generation provenance is recorded here.",
        "alt_text": "Charcoal duck-rabbit silhouette surrounded by burnt-sienna and deep-purple waveform traces, geometric guides, and provenance-like grid marks.",
        "claim_level": "publication_illustration",
        "provenance_boundary": "The image communicates the project's subject and methods aesthetic; it does not establish a perceptual effect, stimulus fidelity, or participant result.",
    }
    validate_cover_manifest(manifest, output_dir=Path(output_dir))
    report = Path(output_dir) / "reports" / "cover_visualization.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(report, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def validate_cover_manifest(manifest: Mapping[str, object] | Path, *, output_dir: Path | None = None) -> dict[str, object]:
    """Validate cover provenance and delivered variant hashes."""
    if isinstance(manifest, Path):
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read cover manifest {manifest}: {exc}") from exc
        if output_dir is None:
            output_dir = manifest.parent.parent
    else:
        payload = manifest
    if not isinstance(payload, Mapping) or payload.get("schema_version") != "duckrabbit/cover/v1":
        raise ValueError("unsupported cover manifest schema version")
    if payload.get("claim_level") != "publication_illustration":
        raise ValueError("cover claim level must be publication_illustration")
    for key in ("source_asset", "source_asset_path", "source_scope", "source_kind", "model", "caption", "alt_text", "provenance_boundary"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise ValueError(f"cover provenance field {key} is required")
    if payload["source_scope"] not in {"project_asset", "external_input"}:
        raise ValueError("cover source_scope must be project_asset or external_input")
    if payload["source_scope"] == "project_asset" and not payload["source_asset_path"].startswith("assets/cover/"):
        raise ValueError("project cover source must live under assets/cover")
    for key in ("source_asset_sha256", "prompt_sha256"):
        if not isinstance(payload.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", payload[key]):
            raise ValueError(f"cover provenance field {key} must be lowercase SHA-256")
    dimensions = payload.get("dimensions_px")
    if not isinstance(dimensions, Mapping) or type(dimensions.get("width")) is not int or type(dimensions.get("height")) is not int or dimensions["width"] <= 0 or dimensions["height"] <= 0:
        raise ValueError("cover dimensions_px must be positive integers")
    ratio = dimensions["width"] / dimensions["height"]
    if abs(ratio - 0.8) > 0.03:
        raise ValueError("cover dimensions must be a 4:5 portrait composition")
    source_dimensions = payload.get("source_asset_dimensions_px")
    if not isinstance(source_dimensions, Mapping) or source_dimensions.get("width") != dimensions["width"] or source_dimensions.get("height") != dimensions["height"]:
        raise ValueError("cover source_asset_dimensions_px must match dimensions_px")
    variants = payload.get("variants")
    if not isinstance(variants, Mapping) or set(variants) != {"png", "webp", "thumbnail"}:
        raise ValueError("cover variants must contain png, webp, and thumbnail")
    if output_dir is not None:
        output_dir = Path(output_dir)
        for name, variant in variants.items():
            if not isinstance(variant, Mapping) or not isinstance(variant.get("path"), str) or not isinstance(variant.get("sha256"), str):
                raise ValueError(f"cover variant {name} is malformed")
            if not variant["path"].startswith("output/figures/"):
                raise ValueError(f"cover variant {name} path must point to output/figures")
            if not re.fullmatch(r"[0-9a-f]{64}", variant["sha256"]):
                raise ValueError(f"cover variant {name} has an invalid hash")
            path = output_dir / variant["path"].removeprefix("output/")
            if not path.resolve().is_relative_to(output_dir.resolve()) or not path.is_file():
                raise ValueError(f"cover variant {name} is missing or escapes output")
            if _sha256(path) != variant["sha256"]:
                raise ValueError(f"cover variant {name} hash is stale")
    return dict(payload)


__all__ = ["COVER_PROMPT", "DEFAULT_COVER_SOURCE", "install_cover", "validate_cover_manifest"]
