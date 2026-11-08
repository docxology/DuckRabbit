"""Editorial cover delivery and explicitly bounded source provenance."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
import re

from PIL import Image

from .io import atomic_write_text, sha256_file


# A historical code-owned report, not authenticated image-generation evidence.
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
_HISTORICAL_SOURCE_SHA256 = "e42859f364316e1be4b23aba20de45fb7f578ffaa6fcb7b2c23bfb7a2d19d4d8"
_HISTORICAL_DIMENSIONS = {"width": 1122, "height": 1402}
_VARIANTS = {
    "png": ("cover_visualization.png", "PNG", "primary_image"),
    "webp": ("cover_visualization.webp", "WEBP", "web_delivery"),
    "thumbnail": ("cover_visualization-thumb.png", "PNG", "thumbnail"),
}
_PROVENANCE_BOUNDARY = (
    "Source bytes and image properties are checked when the source is available; "
    "delivered formats, dimensions, PNG pixels, and thumbnail derivation are checked when output is supplied. "
    "These checks do not authenticate image-generation history or establish preview quality, "
    "a perceptual effect, stimulus fidelity, or participant results."
)


def _generation_provenance(historical: bool) -> dict[str, object]:
    return {
        "status": "reported_unverified" if historical else "not_recorded",
        "reported_claims": {
            "source_kind": "editorial_charcoal_image_generation_v2",
            "model": "image_gen",
            "prompt_sha256": hashlib.sha256(COVER_PROMPT.encode()).hexdigest(),
            "selected_candidate": 4,
            "previewed": True,
        } if historical else None,
        "boundary": (
            "The historical code reports this prompt hash, model, candidate, and preview flag; "
            "the actual generation prompt, model, candidate selection, and preview were not independently authenticated. "
            "No preview-quality conclusion is verified."
        ) if historical else "No generation, prompt, model, candidate-selection, or preview history is recorded for this supplied image.",
    }


def _dimensions(image: Image.Image) -> dict[str, int]:
    return {"width": image.width, "height": image.height}


def _source_image(path: Path) -> tuple[str, str, Image.Image]:
    data = path.read_bytes()
    try:
        with Image.open(BytesIO(data)) as decoded:
            image_format = decoded.format
            image = decoded.convert("RGB")
    except (OSError, ValueError) as exc:
        raise ValueError(f"cannot read cover source image {path}: {exc}") from exc
    if image_format is None:
        raise ValueError("cover source image format is unavailable")
    return hashlib.sha256(data).hexdigest(), image_format, image


def _thumbnail_dimensions(dimensions: Mapping[str, int]) -> dict[str, int]:
    """Match Pillow thumbnail geometry, including rounding and no upscaling."""
    width, height = dimensions["width"], dimensions["height"]
    if width <= 320 and height <= 400:
        return {"width": width, "height": height}
    aspect = width / height
    if 320 / 400 >= aspect:
        width = max(min(math.floor(400 * aspect), math.ceil(400 * aspect), key=lambda n: abs(aspect - n / 400)), 1)
        height = 400
    else:
        height = max(min(math.floor(320 / aspect), math.ceil(320 / aspect), key=lambda n: 0 if n == 0 else abs(aspect - 320 / n)), 1)
        width = 320
    return {"width": width, "height": height}


def _contained_path(output_dir: Path, relative: str) -> Path:
    path = output_dir / relative
    if not path.resolve().is_relative_to(output_dir.resolve()):
        raise ValueError("cover path escapes output")
    return path


def _editorial_description(historical: bool) -> dict[str, str]:
    return {
        "caption": (
            "Editorial cover illustration combining an ambiguous duck/rabbit silhouette with waveform and construction motifs. "
            "It is a publication artifact, not an experimental stimulus or observer result. "
            "Historical generation claims are reported but unverified."
        ) if historical else "Supplied editorial cover image; not an experimental stimulus or observer result. Generation provenance is not recorded.",
        "alt_text": (
            "Charcoal duck-rabbit silhouette surrounded by burnt-sienna and deep-purple waveform traces, geometric guides, and provenance-like grid marks."
        ) if historical else "Supplied editorial cover image with no source-specific visual description recorded.",
    }


def install_cover(output_dir: Path = Path("output"), source_asset: Path | None = None) -> dict[str, object]:
    """Deliver an RGB cover without inferring generation history from image bytes."""
    source = (Path(source_asset) if source_asset is not None else DEFAULT_COVER_SOURCE).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"cover source is unavailable: {source}. Pass an explicit source_asset, or use {DEFAULT_COVER_SOURCE}.")
    source_digest, source_format, image = _source_image(source)
    dimensions = _dimensions(image)
    if abs(image.width / image.height - 0.8) > 0.03:
        raise ValueError("cover dimensions must be a 4:5 portrait composition")
    historical = source == DEFAULT_COVER_SOURCE.resolve()
    if historical and (source_digest != _HISTORICAL_SOURCE_SHA256 or dimensions != _HISTORICAL_DIMENSIONS or source_format != "PNG"):
        raise ValueError("historical cover source identity has changed")
    try:
        source_asset_path = source.relative_to(PROJECT_ROOT.resolve()).as_posix()
        source_scope = "project_asset" if source_asset_path.startswith("assets/cover/") else "external_input"
    except ValueError:
        source_scope = "external_input"
    if source_scope == "external_input":
        source_asset_path = source.as_posix()
    output_dir = Path(output_dir)
    paths = {name: _contained_path(output_dir, f"figures/{spec[0]}") for name, spec in _VARIANTS.items()}
    report = _contained_path(output_dir, "reports/cover_visualization.json")
    if any(path.resolve() == source or (path.exists() and path.samefile(source)) for path in (*paths.values(), report)):
        raise ValueError("cover delivery must not overwrite its source asset")
    paths["png"].parent.mkdir(parents=True, exist_ok=True)
    image.save(paths["png"], format="PNG", optimize=True)
    image.save(paths["webp"], format="WEBP", quality=88, method=6)
    thumbnail = image.copy()
    thumbnail.thumbnail((320, 400), Image.Resampling.LANCZOS)
    thumbnail.save(paths["thumbnail"], format="PNG", optimize=True)
    manifest = {
        "schema_version": "duckrabbit/cover/v2",
        "source_asset": source.name,
        "source_asset_path": source_asset_path,
        "source_scope": source_scope,
        "source_asset_sha256": source_digest,
        "source_asset_dimensions_px": dimensions,
        "source_asset_format": source_format,
        "source_kind": "historical_project_asset" if historical else "supplied_editorial_image",
        "generation_provenance": _generation_provenance(historical),
        "dimensions_px": dimensions,
        "variants": {
            name: {
                "path": f"output/figures/{filename}", "sha256": sha256_file(paths[name]),
                "format": image_format, "role": role,
                "dimensions_px": _dimensions(thumbnail if name == "thumbnail" else image),
            }
            for name, (filename, image_format, role) in _VARIANTS.items()
        },
        **_editorial_description(historical),
        "claim_level": "publication_illustration",
        "provenance_boundary": _PROVENANCE_BOUNDARY,
    }
    validate_cover_manifest(manifest, output_dir=output_dir)
    report.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(report, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def validate_cover_manifest(manifest: Mapping[str, object] | Path, *, output_dir: Path | None = None) -> dict[str, object]:
    """Check source facts and delivery relationships, not generation authenticity."""
    if isinstance(manifest, Path):
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read cover manifest {manifest}: {exc}") from exc
        if output_dir is None:
            output_dir = manifest.parent.parent
    else:
        payload = manifest
    if not isinstance(payload, Mapping) or payload.get("schema_version") != "duckrabbit/cover/v2":
        raise ValueError("unsupported cover manifest schema version")
    if payload.get("claim_level") != "publication_illustration":
        raise ValueError("cover claim level must be publication_illustration")
    for key in ("source_asset", "source_asset_path", "source_scope", "source_kind", "source_asset_format", "caption", "alt_text", "provenance_boundary"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise ValueError(f"cover provenance field {key} is required")
    if payload["provenance_boundary"] != _PROVENANCE_BOUNDARY:
        raise ValueError("cover provenance boundary contradicts verification scope")
    if any(key in payload for key in ("model", "prompt_sha256", "selected_candidate", "previewed")):
        raise ValueError("cover generation claims belong only in generation_provenance")
    source_path = Path(payload["source_asset_path"])
    if payload["source_scope"] == "project_asset":
        if source_path.is_absolute() or not source_path.as_posix().startswith("assets/cover/") or ".." in source_path.parts:
            raise ValueError("project cover source must live under assets/cover")
        source = PROJECT_ROOT / source_path
        if not source.resolve().is_relative_to((PROJECT_ROOT / "assets" / "cover").resolve()):
            raise ValueError("project cover source escapes assets/cover")
    elif payload["source_scope"] == "external_input":
        if not source_path.is_absolute():
            raise ValueError("external cover source must have an absolute path")
        source = source_path
        if source.resolve() == DEFAULT_COVER_SOURCE.resolve():
            raise ValueError("historical cover source must retain project_asset scope")
    else:
        raise ValueError("cover source_scope must be project_asset or external_input")
    if payload["source_asset"] != source.name:
        raise ValueError("cover source_asset must match source_asset_path")
    digest = payload.get("source_asset_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("cover provenance field source_asset_sha256 must be lowercase SHA-256")
    dimensions = payload.get("dimensions_px")
    if not isinstance(dimensions, Mapping) or set(dimensions) != {"width", "height"} or any(type(dimensions[key]) is not int or dimensions[key] <= 0 for key in ("width", "height")):
        raise ValueError("cover dimensions_px must be positive integers")
    if abs(dimensions["width"] / dimensions["height"] - 0.8) > 0.03:
        raise ValueError("cover dimensions must be a 4:5 portrait composition")
    source_dimensions = payload.get("source_asset_dimensions_px")
    if not isinstance(source_dimensions, Mapping) or any(type(source_dimensions.get(key)) is not int for key in ("width", "height")) or source_dimensions != dimensions:
        raise ValueError("cover source_asset_dimensions_px must match dimensions_px")
    historical = source.resolve() == DEFAULT_COVER_SOURCE.resolve()
    if historical and (digest != _HISTORICAL_SOURCE_SHA256 or dimensions != _HISTORICAL_DIMENSIONS or payload["source_asset_format"] != "PNG"):
        raise ValueError("historical cover source_asset_sha256, dimensions, or format contradict source identity")
    if payload["source_kind"] != ("historical_project_asset" if historical else "supplied_editorial_image"):
        raise ValueError("cover source_kind contradicts source identity")
    provenance = payload.get("generation_provenance")
    expected_provenance = _generation_provenance(historical)
    if provenance != expected_provenance or (historical and (
        not isinstance(provenance, Mapping) or not isinstance(provenance.get("reported_claims"), Mapping)
        or type(provenance["reported_claims"].get("selected_candidate")) is not int
        or type(provenance["reported_claims"].get("previewed")) is not bool
    )):
        raise ValueError("cover generation_provenance contradicts reported/unverified history (including prompt_sha256)")
    if any(payload[key] != text for key, text in _editorial_description(historical).items()):
        raise ValueError("cover editorial description contradicts recorded source provenance")
    source_image = None
    if source.exists():
        if not source.is_file():
            raise ValueError("cover source_asset_path is not a file")
        actual_digest, actual_format, source_image = _source_image(source)
        if actual_digest != digest:
            raise ValueError("cover source_asset_sha256 is stale")
        if _dimensions(source_image) != source_dimensions:
            raise ValueError("cover source_asset_dimensions_px disagree with actual source")
        if actual_format != payload["source_asset_format"]:
            raise ValueError("cover source_asset_format disagrees with actual source")
    variants = payload.get("variants")
    if not isinstance(variants, Mapping) or set(variants) != set(_VARIANTS):
        raise ValueError("cover variants must contain png, webp, and thumbnail")
    thumbnail_basis = None
    thumbnail_dimensions = _thumbnail_dimensions(dimensions)
    for name, (filename, image_format, role) in _VARIANTS.items():
        variant = variants[name]
        if not isinstance(variant, Mapping) or not isinstance(variant.get("path"), str) or not isinstance(variant.get("sha256"), str):
            raise ValueError(f"cover variant {name} is malformed")
        if variant["path"] != f"output/figures/{filename}":
            raise ValueError(f"cover variant {name} path must be output/figures/{filename}")
        if not re.fullmatch(r"[0-9a-f]{64}", variant["sha256"]):
            raise ValueError(f"cover variant {name} has an invalid hash")
        expected_dimensions = thumbnail_dimensions if name == "thumbnail" else dimensions
        if variant.get("format") != image_format or variant.get("role") != role or variant.get("dimensions_px") != expected_dimensions:
            raise ValueError(f"cover variant {name} format, role, or dimensions disagree")
        if output_dir is None:
            continue
        path = _contained_path(Path(output_dir), f"figures/{filename}")
        if not path.is_file():
            raise ValueError(f"cover variant {name} is missing or escapes output")
        if sha256_file(path) != variant["sha256"]:
            raise ValueError(f"cover variant {name} hash is stale")
        try:
            with Image.open(path) as decoded:
                if decoded.format != image_format or decoded.mode != "RGB" or _dimensions(decoded) != expected_dimensions:
                    raise ValueError(f"cover variant {name} actual format, mode, or dimensions disagree")
                decoded.load()
                if name == "png":
                    if source_image is not None and decoded.tobytes() != source_image.tobytes():
                        raise ValueError("cover variant png pixels disagree with RGB source")
                    thumbnail_basis = decoded.copy()
                elif name == "webp":
                    if thumbnail_basis is None:
                        raise ValueError("cover WebP requires its primary PNG")
                    buffer = BytesIO()
                    thumbnail_basis.save(buffer, format="WEBP", quality=88, method=6)
                    buffer.seek(0)
                    with Image.open(buffer) as expected:
                        expected.load()
                        if decoded.tobytes() != expected.tobytes():
                            raise ValueError("cover variant webp pixels disagree with current quality=88, method=6 derivation")
                elif name == "thumbnail":
                    if thumbnail_basis is None:
                        raise ValueError("cover thumbnail requires its primary PNG")
                    thumbnail_basis.thumbnail((320, 400), Image.Resampling.LANCZOS)
                    if decoded.tobytes() != thumbnail_basis.tobytes():
                        raise ValueError("cover variant thumbnail pixels disagree with expected resize")
        except OSError as exc:
            raise ValueError(f"cannot read cover variant {name}: {exc}") from exc
    return dict(payload)


__all__ = ["COVER_PROMPT", "DEFAULT_COVER_SOURCE", "install_cover", "validate_cover_manifest"]
