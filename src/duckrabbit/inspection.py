"""Decode-level media inspection and manifest verification."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess  # nosec B404 -- ffprobe is invoked with a fixed argv and shell=False
import wave
from pathlib import Path
from typing import Mapping

import numpy as np

from .errors import BackendUnavailableError, DuckRabbitError, MediaInspectionError, VerificationError
from .canonical import canonical_digest
from .manifest import DecodedInspection, VerificationStatus, read_manifest
from .media import read_npz
from .parameters import BackendKind, MediaFormat


InspectionResult = DecodedInspection


def _format(path: Path, format_name: str | MediaFormat | None) -> MediaFormat:
    if isinstance(format_name, MediaFormat):
        return format_name
    candidate = format_name or path.suffix.lstrip(".")
    try:
        return MediaFormat(candidate.lower().lstrip("."))
    except ValueError as exc:
        raise MediaInspectionError(f"unsupported inspection format {candidate!r}") from exc


def inspect_media(path: Path, format_name: str | MediaFormat | None = None) -> InspectionResult:
    """Decode an encoded artifact and return normalized structural facts."""
    path = Path(path)
    if not path.is_file():
        raise MediaInspectionError(f"encoded artifact does not exist: {path}")
    selected = _format(path, format_name)
    if selected is MediaFormat.PNG or selected is MediaFormat.GIF:
        try:
            from PIL import Image
        except ModuleNotFoundError as exc:  # pragma: no cover - dependency gate
            raise BackendUnavailableError("image inspection requires Pillow") from exc
        try:
            with Image.open(path) as image:
                facts = {
                    "width": image.width,
                    "height": image.height,
                    "mode": image.mode,
                    "frames": getattr(image, "n_frames", 1),
                    "duration_ms": image.info.get("duration"),
                }
        except (OSError, ValueError) as exc:
            raise MediaInspectionError(f"cannot decode image artifact {path}: {exc}") from exc
        return InspectionResult(selected, BackendKind.PILLOW, "image" if selected is MediaFormat.PNG else "video", facts)
    if selected is MediaFormat.WAV:
        try:
            with wave.open(str(path), "rb") as handle:
                facts = {
                    "channels": handle.getnchannels(),
                    "sample_rate": handle.getframerate(),
                    "sample_width_bytes": handle.getsampwidth(),
                    "frames": handle.getnframes(),
                    "duration_seconds": handle.getnframes() / handle.getframerate(),
                }
        except (OSError, EOFError, wave.Error) as exc:
            raise MediaInspectionError(f"cannot decode WAV artifact {path}: {exc}") from exc
        return InspectionResult(selected, BackendKind.PYTHON_WAVE, "audio", facts)
    if selected is MediaFormat.NPZ:
        try:
            with np.load(path, allow_pickle=False) as archive:
                metadata = json.loads(str(archive["metadata_json"].item()))
                facts = {"arrays": sorted(key for key in archive.files if key != "metadata_json"), "metadata": metadata}
                for key in facts["arrays"]:
                    facts[f"{key}_shape"] = list(archive[key].shape)
                _add_npz_derived_facts(facts)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            raise MediaInspectionError(f"cannot decode NPZ artifact {path}: {exc}") from exc
        return InspectionResult(selected, BackendKind.NUMPY, str(facts["metadata"].get("kind", "unknown")), facts)
    if selected is MediaFormat.MP4:
        return _inspect_mp4(path)
    raise MediaInspectionError(f"no inspector registered for {selected.value}")


def _inspect_mp4(path: Path) -> InspectionResult:
    executable = shutil.which("ffprobe")
    if executable is None:
        raise BackendUnavailableError("MP4 inspection requires ffprobe")
    command = [
        executable,
        "-v",
        "error",
        "-show_entries",
        "stream=codec_type,codec_name,pix_fmt,width,height,channels,sample_rate,nb_frames,r_frame_rate,duration,start_time",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30.0)  # nosec B603 -- executable and arguments are fixed/validated
        payload = json.loads(result.stdout)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        raise MediaInspectionError(f"ffprobe could not inspect {path}: {exc}") from exc
    streams = payload.get("streams", [])
    if not isinstance(streams, list) or not streams:
        raise MediaInspectionError(f"ffprobe returned no streams for {path}")
    facts = {"streams": streams, "duration_seconds": float(payload.get("format", {}).get("duration", 0.0) or 0.0)}
    kind = "audiovisual" if {stream.get("codec_type") for stream in streams} == {"audio", "video"} else "video"
    return InspectionResult(MediaFormat.MP4, BackendKind.FFMPEG, kind, facts)


def verify_manifest(path: Path) -> dict[str, object]:
    """Verify an encoded artifact and its manifest as a negative-control oracle."""
    manifest_path = Path(path)
    payload = read_manifest(manifest_path)
    encoded = payload.get("encoding")
    output = payload.get("output")
    if not isinstance(encoded, Mapping):
        if not isinstance(output, str) or not output:
            raise VerificationError("manifest does not identify an encoded output")
        raise VerificationError("manifest encoding is missing or malformed")
    encoded_output = encoded.get("path")
    if isinstance(encoded_output, str):
        output = encoded_output
    if not isinstance(output, str) or not output:
        raise VerificationError("manifest does not identify an encoded output")
    output_path = Path(output)
    if not output_path.is_absolute():
        output_path = manifest_path.parent / output_path
    if not output_path.is_file():
        raise VerificationError(f"manifest output does not exist: {output_path}")
    try:
        output_is_local = output_path.resolve().is_relative_to(manifest_path.resolve().parent)
    except (OSError, RuntimeError) as exc:  # pragma: no cover - filesystem guard
        raise VerificationError("manifest output path cannot be resolved") from exc
    if not output_is_local:
        raise VerificationError("manifest output must remain within the manifest directory")
    checks: list[str] = []
    errors: list[str] = []
    if isinstance(payload.get("output"), str) and payload["output"]:
        declared_output_path = Path(payload["output"])
        if not declared_output_path.is_absolute():
            declared_output_path = manifest_path.parent / declared_output_path
        if declared_output_path.resolve() != output_path.resolve():
            errors.append("top-level output path conflicts with encoded artifact path")
    if not isinstance(encoded_output, str) or not encoded_output:
        errors.append("manifest encoding path is missing or malformed")
    declared_format = encoded.get("format")
    actual_format = _format(output_path, None)
    if not isinstance(declared_format, str) or not declared_format:
        errors.append("manifest encoding format is missing or malformed")
        format_name: str | MediaFormat = actual_format
    else:
        try:
            format_name = _format(output_path, declared_format)
        except MediaInspectionError:
            errors.append("manifest encoding format is unsupported")
            format_name = actual_format
        if format_name is not actual_format:
            errors.append("manifest encoding format does not match output suffix")
    expected_hash = encoded.get("sha256")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        errors.append("manifest encoded SHA-256 is missing or malformed")
    else:
        observed_hash = hashlib.sha256(output_path.read_bytes()).hexdigest()
        if observed_hash != expected_hash:
            errors.append("encoded SHA-256 does not match manifest")
        else:
            checks.append("encoded_sha256")
    # Decode according to the file suffix, while treating a conflicting
    # manifest format as an error. This keeps malformed metadata diagnosable
    # instead of allowing a wrong format request to crash the verifier.
    inspection = inspect_media(output_path, actual_format)
    checks.append("decoded_media")
    expected_artifact = payload.get("artifact")
    if not isinstance(expected_artifact, Mapping):
        errors.append("manifest artifact summary is missing or malformed")
    else:
        _compare_expected_facts(expected_artifact, inspection, errors, checks)
    if actual_format is MediaFormat.NPZ:
        try:
            observed_canonical_digest = canonical_digest(read_npz(output_path))
        except (DuckRabbitError, OSError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"canonical NPZ could not be reconstructed: {exc}")
        else:
            declared_canonical_digest = payload.get("canonical_digest")
            canonical_record = payload.get("canonical")
            if not isinstance(declared_canonical_digest, str) and isinstance(canonical_record, Mapping):
                declared_canonical_digest = canonical_record.get("digest")
            if not isinstance(declared_canonical_digest, str):
                errors.append("manifest canonical digest is missing")
            elif observed_canonical_digest != declared_canonical_digest:
                errors.append("canonical digest does not match decoded NPZ artifact")
            else:
                checks.append("canonical_digest")
    status = VerificationStatus.FAILED if errors else VerificationStatus.VERIFIED
    return {
        "status": status.value,
        "checks": checks,
        "errors": errors,
        "manifest": str(manifest_path),
        "output": str(output_path),
        "inspection": inspection.to_dict(),
    }


def _compare_value(label: str, expected_value: object, observed_value: object, errors: list[str], checks: list[str], *, tolerance: float = 0.0) -> None:
    try:
        matches = abs(float(expected_value) - float(observed_value)) <= tolerance
    except (TypeError, ValueError):
        matches = expected_value == observed_value
    if matches:
        checks.append(f"decoded_{label}")
    else:
        errors.append(f"decoded {label} does not match manifest")


def _npz_shape(facts: Mapping[str, object], name: str) -> list[int] | None:
    value = facts.get(f"{name}_shape")
    return list(value) if isinstance(value, (list, tuple)) and all(isinstance(item, int) for item in value) else None


def _require_fields(expected: Mapping[str, object], errors: list[str], *names: str) -> bool:
    missing = [name for name in names if name not in expected]
    if missing:
        errors.append(f"manifest artifact summary is missing: {', '.join(missing)}")
    return not missing


def _compare_image_facts(expected: Mapping[str, object], inspection: InspectionResult, errors: list[str], checks: list[str]) -> None:
    facts = inspection.facts
    if not _require_fields(expected, errors, "width", "height", "channels"):
        return
    for field in ("width", "height"):
        if field in facts:
            _compare_value(field, expected[field], facts[field], errors, checks)
    mode = facts.get("mode")
    observed_channels = 3 if mode in {"RGB", "RGBA"} else 1 if isinstance(mode, str) else None
    shape = _npz_shape(facts, "pixels")
    if shape is not None:
        _compare_value("height", expected["height"], shape[0], errors, checks)
        _compare_value("width", expected["width"], shape[1], errors, checks)
        if observed_channels is None:
            observed_channels = shape[-1] if len(shape) == 3 else 1
    if observed_channels is None:
        errors.append("decoded channels are unavailable")
    else:
        _compare_value("channels", expected["channels"], observed_channels, errors, checks)


def _compare_audio_facts(expected: Mapping[str, object], inspection: InspectionResult, errors: list[str], checks: list[str]) -> None:
    facts = inspection.facts
    if not _require_fields(expected, errors, "channels", "sample_rate", "samples", "duration_seconds"):
        return
    for field in ("channels", "sample_rate"):
        if field not in facts:
            errors.append(f"decoded {field} is unavailable")
        else:
            _compare_value(field, expected[field], facts[field], errors, checks)
    if "frames" not in facts:
        errors.append("decoded samples are unavailable")
    else:
        _compare_value("samples", expected["samples"], facts["frames"], errors, checks)
    shape = _npz_shape(facts, "samples")
    if shape is not None:
        _compare_value("samples", expected["samples"], shape[0], errors, checks)
        _compare_value("channels", expected["channels"], shape[1] if len(shape) > 1 else 1, errors, checks)
    if "duration_seconds" not in facts:
        errors.append("decoded duration_seconds is unavailable")
    else:
        tolerance = 1.0 / max(float(expected.get("sample_rate", 1)), 1.0)
        _compare_value("duration_seconds", expected["duration_seconds"], facts["duration_seconds"], errors, checks, tolerance=tolerance)


def _compare_video_facts(expected: Mapping[str, object], inspection: InspectionResult, errors: list[str], checks: list[str]) -> None:
    facts = _video_inspection(inspection.facts).facts if inspection.format is MediaFormat.MP4 else inspection.facts
    if not _require_fields(expected, errors, "width", "height", "frames", "frame_rate", "duration_seconds"):
        return
    for field in ("width", "height", "frames"):
        if field not in facts:
            errors.append(f"decoded {field} is unavailable")
        else:
            _compare_value(field, expected[field], facts[field], errors, checks)
    shape = _npz_shape(facts, "frames")
    if shape is not None:
        _compare_value("frames", expected["frames"], shape[0], errors, checks)
        _compare_value("height", expected["height"], shape[1], errors, checks)
        _compare_value("width", expected["width"], shape[2], errors, checks)
    observed_frame_rate = _frame_rate_from_inspection(facts)
    if observed_frame_rate is None:
        errors.append("decoded frame_rate is unavailable")
    else:
        _compare_value("frame_rate", expected["frame_rate"], observed_frame_rate, errors, checks, tolerance=1.0)
    observed_duration = _video_duration_from_inspection(facts)
    if observed_duration is None:
        errors.append("decoded duration_seconds is unavailable")
    else:
        tolerance = 1.0 / max(float(expected.get("frame_rate", 1)), 1.0)
        _compare_value("duration_seconds", expected["duration_seconds"], observed_duration, errors, checks, tolerance=tolerance)


def _compare_npz_audiovisual(expected: Mapping[str, object], facts: Mapping[str, object], errors: list[str], checks: list[str]) -> None:
    audio_facts = {"channels": facts.get("audio_channels"), "sample_rate": facts.get("sample_rate"), "frames": facts.get("audio_frames"), "duration_seconds": facts.get("audio_duration_seconds")}
    video_facts = {"width": facts.get("video_width"), "height": facts.get("video_height"), "frames": facts.get("video_frames"), "frame_rate": facts.get("frame_rate"), "duration_seconds": facts.get("video_duration_seconds")}
    _compare_audio_facts(expected["audio"], InspectionResult(MediaFormat.NPZ, BackendKind.NUMPY, "audio", audio_facts), errors, checks)
    _compare_video_facts(expected["video"], InspectionResult(MediaFormat.NPZ, BackendKind.NUMPY, "video", video_facts), errors, checks)
    declared_offset = float(expected.get("sync_offset_ms", 0.0))
    observed_offset = facts.get("sync_offset_ms")
    if observed_offset is None:
        errors.append("decoded sync_offset_ms is unavailable")
    else:
        _compare_value("sync_offset_ms", declared_offset, observed_offset, errors, checks, tolerance=0.001)
    audio_duration = facts.get("audio_duration_seconds")
    video_duration = facts.get("video_duration_seconds")
    if not isinstance(audio_duration, (int, float)) or not isinstance(video_duration, (int, float)):
        errors.append("decoded audiovisual durations are unavailable")
        return
    offset_seconds = declared_offset / 1000.0
    observed_end = max(max(0.0, offset_seconds) + float(audio_duration), max(0.0, -offset_seconds) + float(video_duration))
    expected_end = float(expected.get("presentation_duration_seconds", expected.get("duration_seconds", 0.0)))
    tolerance = 1.0 / max(float(expected["video"].get("frame_rate", 1)), 1.0)
    _compare_value("presentation_duration_seconds", expected_end, observed_end, errors, checks, tolerance=tolerance)


def _compare_encoded_audiovisual(expected: Mapping[str, object], inspection: InspectionResult, errors: list[str], checks: list[str]) -> None:
    facts = inspection.facts
    audio_inspection = _audio_inspection(facts)
    video_inspection = _video_inspection(facts)
    streams = facts.get("streams", [])
    declared_offset = float(expected.get("sync_offset_ms", 0.0)) / 1000.0
    audio_facts = dict(audio_inspection.facts)
    if declared_offset > 0 and isinstance(audio_facts.get("duration_seconds"), (int, float)):
        audio_facts["duration_seconds"] = float(audio_facts["duration_seconds"]) - declared_offset
        if isinstance(audio_facts.get("sample_rate"), int):
            audio_facts["frames"] = round(float(audio_facts["duration_seconds"]) * audio_facts["sample_rate"])
    _compare_audio_facts(expected["audio"], InspectionResult(audio_inspection.format, audio_inspection.backend, "audio", audio_facts), errors, checks)
    _compare_video_facts(expected["video"], video_inspection, errors, checks)
    if not isinstance(streams, (list, tuple)):
        errors.append("decoded audiovisual streams are unavailable")
        return
    audio = next((stream for stream in streams if isinstance(stream, Mapping) and stream.get("codec_type") == "audio"), None)
    video = next((stream for stream in streams if isinstance(stream, Mapping) and stream.get("codec_type") == "video"), None)
    if not isinstance(audio, Mapping) or not isinstance(video, Mapping):
        return
    audio_start = _stream_float(audio, "start_time", 0.0)
    video_start = _stream_float(video, "start_time", 0.0)
    audio_duration = _stream_float(audio, "duration", 0.0)
    video_duration = _stream_float(video, "duration", 0.0)
    observed_end = max(audio_start + audio_duration, video_start + video_duration)
    expected_end = float(expected.get("presentation_duration_seconds", expected.get("duration_seconds", 0.0)))
    _compare_value("presentation_duration_seconds", expected_end, observed_end, errors, checks, tolerance=0.03)
    observed_offset = (audio_duration - video_duration) if declared_offset >= 0 else -(video_start - audio_start)
    _compare_value("sync_offset_ms", declared_offset * 1000.0, observed_offset * 1000.0, errors, checks, tolerance=30.0)


def _compare_audiovisual_facts(expected: Mapping[str, object], inspection: InspectionResult, errors: list[str], checks: list[str]) -> None:
    if inspection.format is MediaFormat.NPZ:
        _compare_npz_audiovisual(expected, inspection.facts, errors, checks)
    else:
        _compare_encoded_audiovisual(expected, inspection, errors, checks)


def _compare_expected_facts(expected: Mapping[str, object], inspection: InspectionResult, errors: list[str], checks: list[str]) -> None:
    kind = expected.get("type")
    if kind == "image":
        _compare_image_facts(expected, inspection, errors, checks)
    elif kind == "audio":
        _compare_audio_facts(expected, inspection, errors, checks)
    elif kind == "video":
        _compare_video_facts(expected, inspection, errors, checks)
    elif kind == "audiovisual" and isinstance(expected.get("audio"), Mapping) and isinstance(expected.get("video"), Mapping):
        _compare_audiovisual_facts(expected, inspection, errors, checks)
    else:
        errors.append(f"manifest artifact type is unsupported: {kind!r}")


def _add_npz_derived_facts(facts: dict[str, object]) -> None:
    """Promote canonical archive metadata into stable decode-level facts."""
    metadata = facts.get("metadata")
    if not isinstance(metadata, Mapping):
        return
    kind = metadata.get("kind")
    for key in ("mode", "sample_rate", "frame_rate", "sync_offset_ms", "spatial_offset"):
        if key in metadata:
            facts[key] = metadata[key]
    if kind == "image":
        shape = facts.get("pixels_shape")
        if isinstance(shape, list) and len(shape) >= 2:
            facts.update({"height": shape[0], "width": shape[1], "channels": shape[2] if len(shape) == 3 else 1})
    elif kind == "audio":
        shape = facts.get("samples_shape")
        if isinstance(shape, list) and shape:
            facts.update({"frames": shape[0], "channels": shape[1] if len(shape) > 1 else 1})
            if isinstance(metadata.get("sample_rate"), (int, float)) and float(metadata["sample_rate"]) > 0:
                facts["duration_seconds"] = float(shape[0]) / float(metadata["sample_rate"])
    elif kind == "video":
        shape = facts.get("frames_shape")
        if isinstance(shape, list) and len(shape) >= 3:
            facts.update({"frames": shape[0], "height": shape[1], "width": shape[2]})
            if isinstance(metadata.get("frame_rate"), (int, float)) and float(metadata["frame_rate"]) > 0:
                facts["duration_seconds"] = float(shape[0]) / float(metadata["frame_rate"])
    elif kind == "audiovisual":
        audio_shape = facts.get("samples_shape")
        video_shape = facts.get("frames_shape")
        if isinstance(audio_shape, list) and audio_shape:
            facts.update({"audio_frames": audio_shape[0], "audio_channels": audio_shape[1] if len(audio_shape) > 1 else 1})
            if isinstance(metadata.get("sample_rate"), (int, float)) and float(metadata["sample_rate"]) > 0:
                facts["audio_duration_seconds"] = float(audio_shape[0]) / float(metadata["sample_rate"])
        if isinstance(video_shape, list) and len(video_shape) >= 3:
            facts.update({"video_frames": video_shape[0], "video_height": video_shape[1], "video_width": video_shape[2]})
            if isinstance(metadata.get("frame_rate"), (int, float)) and float(metadata["frame_rate"]) > 0:
                facts["video_duration_seconds"] = float(video_shape[0]) / float(metadata["frame_rate"])


def _stream_float(stream: Mapping[str, object], key: str, default: float) -> float:
    value = stream.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _frame_rate_from_inspection(facts: Mapping[str, object]) -> float | None:
    direct_rate = facts.get("frame_rate")
    if isinstance(direct_rate, (int, float)) and direct_rate > 0:
        return float(direct_rate)
    rate = facts.get("r_frame_rate")
    if isinstance(rate, str) and "/" in rate:
        numerator, denominator = rate.split("/", 1)
        try:
            return float(numerator) / float(denominator)
        except (ValueError, ZeroDivisionError):
            return None
    duration_ms = facts.get("duration_ms")
    if isinstance(duration_ms, (int, float)) and duration_ms > 0:
        return 1000.0 / float(duration_ms)
    return None


def _video_duration_from_inspection(facts: Mapping[str, object]) -> float | None:
    duration = facts.get("duration_seconds")
    if isinstance(duration, (int, float)):
        return float(duration)
    duration_ms = facts.get("duration_ms")
    frames = facts.get("frames")
    if isinstance(duration_ms, (int, float)) and isinstance(frames, int):
        return float(duration_ms) * frames / 1000.0
    return None


def _audio_inspection(facts: Mapping[str, object]) -> InspectionResult:
    stream = _stream_of_type(facts, "audio")
    if stream is None:
        return InspectionResult(MediaFormat.MP4, BackendKind.FFMPEG, "audio", facts)
    normalized = dict(stream)
    if "duration" in normalized:
        normalized["duration_seconds"] = _stream_float(stream, "duration", 0.0)
    if "sample_rate" in normalized:
        try:
            normalized["sample_rate"] = int(float(normalized["sample_rate"] or 0))
        except (TypeError, ValueError):
            normalized.pop("sample_rate", None)
    if "duration_seconds" in normalized and isinstance(normalized.get("sample_rate"), int):
        normalized["frames"] = round(float(normalized["duration_seconds"]) * normalized["sample_rate"])
    return InspectionResult(MediaFormat.MP4, BackendKind.FFMPEG, "audio", normalized)


def _video_inspection(facts: Mapping[str, object]) -> InspectionResult:
    stream = _stream_of_type(facts, "video")
    if stream is None:
        return InspectionResult(MediaFormat.MP4, BackendKind.FFMPEG, "video", facts)
    normalized = dict(stream)
    normalized["frames"] = int(float(stream["nb_frames"])) if stream.get("nb_frames") not in {None, "N/A"} else 0
    normalized["duration_seconds"] = _stream_float(stream, "duration", 0.0)
    return InspectionResult(MediaFormat.MP4, BackendKind.FFMPEG, "video", normalized)


def _stream_of_type(facts: Mapping[str, object], codec_type: str) -> Mapping[str, object] | None:
    streams = facts.get("streams", [])
    if not isinstance(streams, (list, tuple)):
        return None
    stream = next((item for item in streams if isinstance(item, Mapping) and item.get("codec_type") == codec_type), None)
    return stream if isinstance(stream, Mapping) else None
