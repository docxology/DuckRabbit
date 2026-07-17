"""Typed generation, encoding, inspection, and manifest orchestration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from collections.abc import Mapping

from .version import __version__
from .artifacts import (
    ArtifactKind,
    ArtifactManifest,
    ArtifactSummary,
    AudioBuffer,
    AudiovisualTimeline,
    CanonicalArtifact,
    EncodedArtifact,
    ImageFrame,
    VideoSequence,
)
from .canonical import canonical_bytes, canonical_digest
from .errors import UnsupportedFormatError
from .io import atomic_write_text
from .generators import default_parameters, default_registry
from .inspection import inspect_media
from .manifest import CanonicalRecord, DecodedInspection, Manifest, RenderResult, VerificationReport, VerificationStatus
from .media import write_audiovisual, write_gif, write_mp4, write_npz, write_png, write_wav
from .metrics import measure_artifact
from .parameters import (
    AudioEncoding,
    BackendKind,
    CanonicalArchiveEncoding,
    GifEncoding,
    MediaFormat,
    MuxEncoding,
    OutputSpec,
    VideoEncoding,
    replace_from_mapping,
)
from .schema import parameter_payload, parameter_schema
from .serialization import jsonable
from .taxonomy import ClaimLevel


def artifact_digest(artifact: CanonicalArtifact) -> str:
    """Return the versioned canonical digest."""
    return canonical_digest(artifact)


def artifact_summary(artifact: CanonicalArtifact) -> ArtifactSummary:
    """Return typed dimensions, signal statistics, and clock facts for a manifest."""
    if isinstance(artifact, ImageFrame):
        minimum, maximum = artifact.value_range
        return {
            "type": ArtifactKind.IMAGE.value,
            "mode": artifact.mode,
            "width": artifact.width,
            "height": artifact.height,
            "channels": artifact.channels,
            "dtype": "<f4",
            "nbytes": artifact.nbytes,
            "min_value": minimum,
            "max_value": maximum,
        }
    if isinstance(artifact, AudioBuffer):
        return {
            "type": ArtifactKind.AUDIO.value,
            "samples": artifact.sample_count,
            "channels": artifact.channels,
            "sample_rate": artifact.sample_rate.value,
            "duration_seconds": artifact.duration_seconds,
            "dtype": "<f4",
            "nbytes": artifact.nbytes,
            "peak": artifact.peak,
            "rms": artifact.rms,
        }
    if isinstance(artifact, VideoSequence):
        return {
            "type": ArtifactKind.VIDEO.value,
            "width": artifact.width,
            "height": artifact.height,
            "frames": artifact.frame_count,
            "frame_rate": artifact.frame_rate.value,
            "duration_seconds": artifact.duration_seconds,
            "mode": artifact.pixel_mode,
            "dtype": "<f4",
            "nbytes": artifact.nbytes,
            "temporal_deltas": list(artifact.temporal_deltas),
            "mean_temporal_delta": artifact.mean_temporal_delta,
        }
    if isinstance(artifact, AudiovisualTimeline):
        return {
            "type": ArtifactKind.AUDIOVISUAL.value,
            "audio": artifact_summary(artifact.audio),
            "video": artifact_summary(artifact.video),
            "sync_offset_ms": artifact.sync_offset.value,
            "spatial_offset": artifact.spatial_offset.value,
            "duration_seconds": artifact.duration_seconds,
            "audio_start_seconds": artifact.audio_start_seconds,
            "video_start_seconds": artifact.video_start_seconds,
            "presentation_duration_seconds": artifact.presentation_duration_seconds,
            "nbytes": artifact.nbytes,
        }
    raise TypeError(f"unsupported artifact type: {type(artifact).__name__}")


def _format_for_artifact(artifact: CanonicalArtifact, requested: str | MediaFormat | None) -> MediaFormat:
    if requested:
        try:
            return requested if isinstance(requested, MediaFormat) else MediaFormat(requested.lower().lstrip("."))
        except ValueError as exc:
            raise UnsupportedFormatError(f"unsupported output format {requested!r}") from exc
    if isinstance(artifact, ImageFrame):
        return MediaFormat.PNG
    if isinstance(artifact, AudioBuffer):
        return MediaFormat.WAV
    if isinstance(artifact, VideoSequence):
        return MediaFormat.GIF
    return MediaFormat.MP4


def _backend_for_format(format_value: MediaFormat) -> BackendKind:
    return {
        MediaFormat.PNG: BackendKind.PILLOW,
        MediaFormat.GIF: BackendKind.PILLOW,
        MediaFormat.WAV: BackendKind.PYTHON_WAVE,
        MediaFormat.MP4: BackendKind.FFMPEG,
        MediaFormat.NPZ: BackendKind.NUMPY,
    }[format_value]


def _media_type(format_value: MediaFormat) -> str:
    return {
        MediaFormat.PNG: "image/png",
        MediaFormat.WAV: "audio/wav",
        MediaFormat.GIF: "image/gif",
        MediaFormat.MP4: "video/mp4",
        MediaFormat.NPZ: "application/x-npz",
    }[format_value]


def encode_artifact(
    artifact: CanonicalArtifact,
    path: Path,
    format_name: str | MediaFormat,
    *,
    audio_encoding: AudioEncoding | None = None,
    gif_encoding: GifEncoding = GifEncoding(),
    video_encoding: VideoEncoding = VideoEncoding(),
    mux_encoding: MuxEncoding = MuxEncoding(),
    archive_encoding: CanonicalArchiveEncoding = CanonicalArchiveEncoding(),
    overwrite: bool = True,
) -> Path:
    """Encode one canonical artifact with a format-compatible adapter."""
    format_value = format_name.value if isinstance(format_name, MediaFormat) else format_name.lower().lstrip(".")
    if isinstance(artifact, ImageFrame) and format_value == MediaFormat.PNG.value:
        return write_png(artifact, path, overwrite=overwrite)
    if isinstance(artifact, AudioBuffer) and format_value == MediaFormat.WAV.value:
        return write_wav(artifact, path, encoding=audio_encoding or AudioEncoding(), overwrite=overwrite)
    if isinstance(artifact, VideoSequence) and format_value == MediaFormat.GIF.value:
        return write_gif(artifact, path, encoding=gif_encoding, overwrite=overwrite)
    if isinstance(artifact, VideoSequence) and format_value == MediaFormat.MP4.value:
        return write_mp4(artifact, path, encoding=video_encoding, overwrite=overwrite)
    if isinstance(artifact, AudiovisualTimeline) and format_value == MediaFormat.MP4.value:
        return write_audiovisual(artifact, path, encoding=mux_encoding, overwrite=overwrite)
    if format_value == MediaFormat.NPZ.value:
        return write_npz(artifact, path, encoding=archive_encoding, overwrite=overwrite)
    raise UnsupportedFormatError(f"format {format_value!r} is incompatible with {type(artifact).__name__}")


def build_manifest(illusion_id: str, parameters: object, artifact: CanonicalArtifact, *, seed: int = 0) -> ArtifactManifest:
    """Build the strict v1 compatibility manifest."""
    entry = default_registry.get(illusion_id).taxonomy
    return ArtifactManifest(
        schema_version="duckrabbit/artifact/v1",
        illusion_id=illusion_id,
        implementation_status=entry.implementation_status,
        modality=entry.modalities,
        taxonomy=entry,
        parameters=parameters,
        seed=seed,
        canonical_digest=artifact_digest(artifact),
        duration_seconds=getattr(artifact, "duration_seconds", None),
        artifact=artifact_summary(artifact),
    )


def build_manifest_v2(illusion_id: str, parameters: object, artifact: CanonicalArtifact, *, seed: int = 0) -> Manifest:
    """Build the fully typed v2 manifest before optional encoding."""
    entry = default_registry.get(illusion_id).taxonomy
    return Manifest(
        package_version=__version__,
        generator_version=f"duckrabbit/{__version__}",
        illusion_id=illusion_id,
        implementation_status=entry.implementation_status,
        evidence_status=entry.evidence_status,
        claim_level=ClaimLevel.CANONICAL_STIMULUS,
        modality=entry.modalities,
        taxonomy=entry,
        parameter_schema=parameter_schema(parameters),
        parameters=parameter_payload(parameters),
        seed=seed,
        artifact=artifact_summary(artifact),
        canonical=CanonicalRecord(
            schema_version="duckrabbit/canonical/v1",
            algorithm="sha256",
            digest=artifact_digest(artifact),
            byte_order="little",
            dtype="<f4",
            byte_count=len(canonical_bytes(artifact)),
        ),
        verification=VerificationReport(VerificationStatus.UNVERIFIED),
        metrics=measure_artifact(artifact).to_dict(),
    )


def _legacy_compatible_payload(manifest: Manifest, *, output: Path | None, manifest_path: Path | None) -> dict[str, object]:
    payload = manifest.to_dict()
    payload.update(
        {
            "canonical_digest": manifest.canonical.digest,
            "output": str(output) if output else None,
            "manifest": str(manifest_path) if manifest_path else None,
            "format": manifest.encoding.format.value if manifest.encoding else None,
            "encoded_size_bytes": manifest.encoding.size_bytes if manifest.encoding else None,
        }
    )
    return payload


def generate_artifact(
    illusion_id: str,
    parameters: object | None = None,
    *,
    seed: int = 0,
    output_dir: Path | None = None,
    format_name: str | MediaFormat | None = None,
    output_spec: OutputSpec | None = None,
) -> tuple[CanonicalArtifact, dict[str, object]]:
    """Generate canonical media, optionally encode it, inspect it, and write v2 provenance."""
    parameters = parameters if parameters is not None else default_parameters(illusion_id)
    artifact = default_registry.generate(illusion_id, parameters, seed=seed)
    spec = output_spec or OutputSpec()
    if format_name is not None and spec.format is not None:
        explicit = _format_for_artifact(artifact, format_name)
        if explicit is not spec.format:
            raise ValueError("format_name conflicts with output_spec.format")
    selected_format = _format_for_artifact(artifact, spec.format if format_name is None else format_name)
    manifest = build_manifest_v2(illusion_id, parameters, artifact, seed=seed)
    output_path: Path | None = None
    manifest_path: Path | None = None
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{illusion_id.replace('.', '_')}.{selected_format.value}"
        if output_path.exists() and not spec.overwrite:
            raise FileExistsError(f"output already exists and overwrite is disabled: {output_path}")
        encode_artifact(
            artifact,
            output_path,
            selected_format,
            audio_encoding=spec.audio_encoding,
            gif_encoding=spec.gif_encoding,
            video_encoding=spec.video_encoding,
            mux_encoding=spec.mux_encoding,
            archive_encoding=spec.archive_encoding,
            overwrite=spec.overwrite,
        )
        encoded = EncodedArtifact(
            path=str(output_path),
            format=selected_format,
            media_type=_media_type(selected_format),
            size_bytes=output_path.stat().st_size,
            sha256=hashlib.sha256(output_path.read_bytes()).hexdigest(),
            backend=_backend_for_format(selected_format),
            profile=jsonable(
                {
                    "audio": spec.audio_encoding,
                    "gif": spec.gif_encoding,
                    "video": spec.video_encoding,
                    "mux": spec.mux_encoding,
                    "archive": spec.archive_encoding,
                }
            ),
        )
        inspection = inspect_media(output_path, selected_format)
        manifest = Manifest(
            **{
                **manifest.__dict__,
                "encoding": encoded,
                "decoded_inspection": inspection,
                "verification": VerificationReport(
                    VerificationStatus.VERIFIED,
                    checks=("encoded_sha256", "decoded_media"),
                ),
            }
        )
        if spec.include_manifest:
            manifest_path = output_path.with_suffix(output_path.suffix + ".json")
    payload = _legacy_compatible_payload(manifest, output=output_path, manifest_path=manifest_path)
    if manifest_path is not None:
        atomic_write_text(manifest_path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return artifact, payload


def render_artifact(
    illusion_id: str,
    parameters: object | None = None,
    *,
    seed: int = 0,
    output_dir: Path | None = None,
    output_spec: OutputSpec | None = None,
) -> RenderResult:
    """Typed v0.3 facade over generation and optional encoding."""
    artifact, payload = generate_artifact(
        illusion_id,
        parameters,
        seed=seed,
        output_dir=output_dir,
        output_spec=output_spec,
    )
    manifest_payload = payload
    typed_manifest = _typed_manifest_from_payload(
        illusion_id,
        parameters or default_parameters(illusion_id),
        artifact,
        manifest_payload,
    )
    output = manifest_payload.get("output")
    manifest_path = manifest_payload.get("manifest")
    return RenderResult(
        artifact,
        typed_manifest,
        Path(output) if isinstance(output, str) else None,
        Path(manifest_path) if isinstance(manifest_path, str) else None,
    )


def _typed_manifest_from_payload(illusion_id: str, parameters: object, artifact: CanonicalArtifact, payload: Mapping[str, object]) -> Manifest:
    """Rehydrate the validated generation result into the typed facade."""
    base = build_manifest_v2(illusion_id, parameters, artifact, seed=int(payload.get("seed", 0)))
    encoded_payload = payload.get("encoding")
    encoded = None
    if isinstance(encoded_payload, Mapping):
        encoded = EncodedArtifact(
            path=str(encoded_payload["path"]),
            format=MediaFormat(str(encoded_payload["format"])),
            media_type=str(encoded_payload["media_type"]),
            size_bytes=int(encoded_payload["size_bytes"]),
            sha256=str(encoded_payload["sha256"]),
            backend=BackendKind(str(encoded_payload.get("backend", BackendKind.PILLOW.value))),
            profile=encoded_payload.get("profile", {}),  # type: ignore[arg-type]
        )
    verification_payload = payload.get("verification", {})
    verification = VerificationReport(
        VerificationStatus(str(verification_payload.get("status", VerificationStatus.UNVERIFIED.value))),
        tuple(str(item) for item in verification_payload.get("checks", [])),
        tuple(str(item) for item in verification_payload.get("errors", [])),
    )
    decoded_payload = payload.get("decoded_inspection")
    decoded = None
    if isinstance(decoded_payload, Mapping):
        facts = decoded_payload.get("facts", {})
        decoded = DecodedInspection(
            format=MediaFormat(str(decoded_payload.get("format", MediaFormat.PNG.value))),
            backend=BackendKind(str(decoded_payload.get("backend", BackendKind.PILLOW.value))),
            kind=str(decoded_payload.get("kind", "unknown")),
            facts=facts if isinstance(facts, Mapping) else {},
        )
    return Manifest(
        **{
            **base.__dict__,
            "encoding": encoded,
            "decoded_inspection": decoded,
            "verification": verification,
        }
    )


def parameters_from_json(illusion_id: str, payload: dict[str, object]) -> object:
    """Build validated typed parameters from JSON-friendly overrides."""
    return replace_from_mapping(default_parameters(illusion_id), payload)


__all__ = [
    "artifact_digest",
    "artifact_summary",
    "build_manifest",
    "build_manifest_v2",
    "encode_artifact",
    "generate_artifact",
    "jsonable",
    "parameters_from_json",
    "render_artifact",
]
