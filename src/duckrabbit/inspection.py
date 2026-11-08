"""Decode-level media inspection and manifest verification."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess  # nosec B404 -- ffprobe is invoked with a fixed argv and shell=False
import wave
import zipfile
import zlib
from collections.abc import Mapping
from pathlib import Path

import numpy as np

from .canonical import canonical_digest_and_size
from .errors import (
    BackendUnavailableError,
    DuckRabbitError,
    ManifestValidationError,
    MediaInspectionError,
    VerificationError,
)
from .manifest import (
    DecodedInspection,
    VerificationStatus,
    _read_manifest_document,
    upconvert_v1_manifest,
    validate_manifest_payload,
)
from .media import _canonical_npz_array, read_npz
from .parameters import BackendKind, FrameRate, MediaFormat, SampleRate
from .serialization import jsonable

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
                    "container_format": image.format,
                    "bands": list(image.getbands()),
                    "has_transparency": "A" in image.getbands() or "transparency" in image.info,
                    "width": image.width,
                    "height": image.height,
                    "mode": image.mode,
                    "frames": getattr(image, "n_frames", 1),
                    "duration_ms": image.info.get("duration"),
                }
                frame_durations = []
                for frame_index in range(facts["frames"]):
                    image.seek(frame_index)
                    image.load()
                    frame_durations.append(image.info.get("duration", 0))
                if selected is MediaFormat.GIF:
                    facts["frame_durations_ms"] = frame_durations
                    facts["duration_seconds"] = sum(frame_durations) / 1000.0
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
                remaining = handle.getnframes() * handle.getnchannels() * handle.getsampwidth()
                while remaining:
                    chunk = handle.readframes(min(65536, handle.getnframes()))
                    if not chunk:
                        raise EOFError("WAV payload is shorter than the declared frame count")
                    remaining -= len(chunk)
        except (OSError, EOFError, wave.Error) as exc:
            raise MediaInspectionError(f"cannot decode WAV artifact {path}: {exc}") from exc
        return InspectionResult(selected, BackendKind.PYTHON_WAVE, "audio", facts)
    if selected is MediaFormat.NPZ:
        try:
            with np.load(path, allow_pickle=False) as archive:
                metadata = json.loads(str(archive["metadata_json"].item()))
                if not isinstance(metadata, dict):
                    raise TypeError("NPZ metadata must contain an object")
                facts = {"arrays": sorted(key for key in archive.files if key != "metadata_json"), "metadata": metadata}
                for key in facts["arrays"]:
                    values = _canonical_npz_array(archive, key)
                    facts[f"{key}_shape"] = list(values.shape)
                    facts[f"{key}_dtype"] = values.dtype.str
                _add_npz_derived_facts(facts)
        except (OSError, ValueError, KeyError, TypeError, OverflowError, RecursionError, EOFError, zipfile.BadZipFile, zlib.error) as exc:
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
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    if audio is not None and audio.get("codec_name") == "aac":
        packet_command = [
            executable, "-v", "error", "-select_streams", "a:0", "-read_intervals", "%+#1",
            "-show_packets", "-show_entries", "packet=pts_time", "-of", "json", str(path),
        ]
        try:
            packet_result = subprocess.run(packet_command, check=True, capture_output=True, text=True, timeout=30.0)
            packets = json.loads(packet_result.stdout)["packets"]
            facts["audio_onset_seconds"] = float(packets[0]["pts_time"]) + 1024.0 / float(audio["sample_rate"])
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, KeyError, IndexError, TypeError) as exc:
            raise MediaInspectionError(f"ffprobe could not inspect AAC onset in {path}: {exc}") from exc
    stream_kinds = {stream.get("codec_type") for stream in streams}
    kind = "audiovisual" if stream_kinds == {"audio", "video"} else next(iter(stream_kinds)) if len(stream_kinds) == 1 else "unknown"
    return InspectionResult(MediaFormat.MP4, BackendKind.FFMPEG, kind, facts)


def verify_manifest(path: Path) -> dict[str, object]:
    """Verify an encoded artifact and its manifest as a negative-control oracle."""
    manifest_path = Path(path)
    payload = _read_manifest_document(manifest_path)
    legacy = payload["schema_version"] == "duckrabbit/artifact/v1"
    if legacy:
        payload = upconvert_v1_manifest(payload)
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
    unavailable: list[str] = []
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
    if encoded.get("size_bytes") != output_path.stat().st_size:
        errors.append("encoded size_bytes does not match manifest")
    else:
        checks.append("encoded_size_bytes")
    # Decode according to the file suffix, while treating a conflicting
    # manifest format as an error. This keeps malformed metadata diagnosable
    # instead of allowing a wrong format request to crash the verifier.
    inspection = inspect_media(output_path, actual_format)
    checks.append("decoded_media")
    expected_artifact = payload.get("artifact")
    if not isinstance(expected_artifact, Mapping):
        errors.append("manifest artifact summary is missing or malformed")
    else:
        try:
            _compare_expected_facts(expected_artifact, inspection, errors, checks)
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            errors.append(f"manifest artifact facts cannot be compared: {exc}")
    if actual_format is MediaFormat.NPZ:
        _compare_npz_canonical(output_path, payload, errors, checks, unavailable, legacy=legacy)
    try:
        validate_manifest_payload(payload)
    except ManifestValidationError as exc:
        errors.append(f"manifest validation failed: {exc}")
    status = VerificationStatus.FAILED if errors else VerificationStatus.UNVERIFIED if unavailable else VerificationStatus.VERIFIED
    return {
        "status": status.value,
        "checks": checks,
        "errors": errors,
        "unavailable": unavailable,
        "manifest": str(manifest_path),
        "output": str(output_path),
        "inspection": inspection.to_dict(),
    }


def _compare_npz_canonical(path: Path, payload: Mapping[str, object], errors: list[str], checks: list[str], unavailable: list[str], *, legacy: bool = False) -> None:
    """Bind an exact archive to its full summary and framed canonical bytes."""
    from .render import artifact_summary

    try:
        artifact = read_npz(path)
        digest, byte_count = canonical_digest_and_size(artifact)
    except (DuckRabbitError, OSError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"canonical NPZ could not be reconstructed: {exc}")
        return
    record = payload.get("canonical")
    declared_digest = payload.get("canonical_digest")
    if not isinstance(declared_digest, str) and isinstance(record, Mapping):
        declared_digest = record.get("digest")
    if not isinstance(declared_digest, str):
        errors.append("manifest canonical digest is missing")
    elif digest != declared_digest:
        errors.append("canonical digest does not match decoded NPZ artifact")
    else:
        checks.append("canonical_digest")
    # v1 has no framed byte-count field; do not certify its synthesized value.
    if not legacy:
        if not isinstance(record, Mapping) or record.get("byte_count") != byte_count:
            errors.append("canonical byte_count does not match decoded NPZ artifact")
        else:
            checks.append("canonical_byte_count")
    if jsonable(artifact_summary(artifact)) != jsonable(payload.get("artifact")):
        errors.append("canonical full summary does not match decoded NPZ artifact")
    else:
        checks.append("canonical_full_summary")
    _compare_npz_metrics(artifact, payload.get("metrics"), errors, checks, unavailable)


def _compare_npz_metrics(artifact, declared: object, errors: list[str], checks: list[str], unavailable: list[str]) -> None:
    """Replay supported declarations; never relabel historical computations."""
    from .metrics import COMPUTATION_VERSION, measure_artifact

    if declared is None:
        return
    if not isinstance(declared, Mapping):
        errors.append("canonical metrics must contain an object or null")
        return
    if declared.get("computation_version") != COMPUTATION_VERSION:
        unavailable.append("canonical_metrics: unsupported computation_version")
        return
    expected = jsonable(measure_artifact(artifact).to_dict())
    records = declared.get("records")
    if not isinstance(records, (list, tuple)) or not all(isinstance(record, Mapping) and isinstance(record.get("name"), str) for record in records):
        errors.append("canonical metric records are malformed")
        return
    names = [record["name"] for record in records]
    expected_records = {record["name"]: record for record in expected["records"]}
    if len(names) != len(set(names)) or set(names) != set(expected_records):
        errors.append("canonical metric records are missing, duplicated, or unknown")
        return
    for record in records:
        provenance = record.get("provenance")
        if not isinstance(provenance, Mapping) or not all(isinstance(provenance.get(key), str) for key in ("source_sha256", "numpy_version")):
            errors.append("canonical metric computation identity is malformed")
            return
        supported = expected_records[record["name"]]["provenance"]
        if any(provenance[key] != supported[key] for key in ("source_sha256", "numpy_version")):
            unavailable.append("canonical_metrics: implementation or NumPy identity is unsupported")
            return
    actual = jsonable(declared)
    actual["records"] = sorted(actual["records"], key=lambda record: record["name"])
    expected["records"] = sorted(expected["records"], key=lambda record: record["name"])
    try:
        agrees = json.dumps(actual, sort_keys=True, allow_nan=False) == json.dumps(expected, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as exc:
        errors.append(f"canonical metrics cannot be compared: {exc}")
        return
    if agrees:
        checks.append("canonical_metrics")
    else:
        errors.append("canonical metrics do not match decoded NPZ artifact and trusted definitions")


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
    observed_channels = {"L": 1, "RGB": 3}.get(mode) if isinstance(mode, str) else None
    if inspection.format is MediaFormat.PNG:
        _compare_value("mode", expected.get("mode", mode), mode, errors, checks)
        if facts.get("has_transparency"):
            errors.append("decoded PNG transparency is incompatible with canonical L/RGB images")
        _compare_value("image_frame_count", 1, facts.get("frames"), errors, checks)
    shape = _npz_shape(facts, "pixels")
    if shape is not None and len(shape) in (2, 3):
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
    if shape is not None and len(shape) in (1, 2):
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
    if shape is not None and len(shape) in (3, 4):
        _compare_value("frames", expected["frames"], shape[0], errors, checks)
        _compare_value("height", expected["height"], shape[1], errors, checks)
        _compare_value("width", expected["width"], shape[2], errors, checks)
    if inspection.format is MediaFormat.GIF:
        ticks = 100.0 / float(expected["frame_rate"])
        durations = [
            10 * (round((index + 1) * ticks) - round(index * ticks))
            for index in range(int(expected["frames"]))
        ]
        _compare_value("gif_frame_durations_ms", durations, list(facts.get("frame_durations_ms", ())), errors, checks)
        if "decoded_gif_frame_durations_ms" in checks:
            checks.extend(("decoded_frame_rate", "decoded_duration_seconds"))
        return
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
    """Compare expected audiovisual facts against ffprobe stream inspection.

    The sync offset is encoded as an itsoffset delay on the later stream,
    so the observed presentation end-time must account for the delayed
    stream's start.  The observed sync offset is derived from the
    difference in stream start times, allowing for retained AAC priming.
    """
    facts = inspection.facts
    audio_inspection = _audio_inspection(facts)
    video_inspection = _video_inspection(facts)
    streams = facts.get("streams", [])
    declared_offset = float(expected.get("sync_offset_ms", 0.0)) / 1000.0
    audio_facts = dict(audio_inspection.facts)
    if not isinstance(streams, (list, tuple)):
        errors.append("decoded audiovisual streams are unavailable")
        return
    audio = next((stream for stream in streams if isinstance(stream, Mapping) and stream.get("codec_type") == "audio"), None)
    video = next((stream for stream in streams if isinstance(stream, Mapping) and stream.get("codec_type") == "video"), None)
    if not isinstance(audio, Mapping) or not isinstance(video, Mapping):
        errors.append("decoded audiovisual artifact requires one audio and one video stream")
        return
    audio_start = _stream_float(audio, "start_time", 0.0)
    video_start = _stream_float(video, "start_time", 0.0)
    audio_duration = _stream_float(audio, "duration", 0.0)
    video_duration = _stream_float(video, "duration", 0.0)
    sample_rate = _stream_float(audio, "sample_rate", 1.0)
    audio_onset = float(facts.get("audio_onset_seconds", audio_start))
    padding = audio_onset - audio_start
    audio_facts["duration_seconds"] = audio_duration - padding
    audio_facts["frames"] = round((audio_duration - padding) * sample_rate)
    _compare_audio_facts(expected["audio"], InspectionResult(audio_inspection.format, audio_inspection.backend, "audio", audio_facts), errors, checks)
    _compare_video_facts(expected["video"], video_inspection, errors, checks)
    observed_end = max(audio_start + audio_duration, video_start + video_duration)
    expected_end = float(expected.get("presentation_duration_seconds", expected.get("duration_seconds", 0.0)))
    tolerance = 1.0 / max(float(expected["video"].get("frame_rate", 1)), 1.0)
    _compare_value("presentation_duration_seconds", expected_end, observed_end, errors, checks, tolerance=tolerance)
    observed_offset = audio_onset - video_start
    _compare_value("sync_offset_ms", declared_offset * 1000.0, observed_offset * 1000.0, errors, checks, tolerance=30.0)


def _compare_audiovisual_facts(expected: Mapping[str, object], inspection: InspectionResult, errors: list[str], checks: list[str]) -> None:
    if inspection.format is MediaFormat.NPZ:
        _compare_npz_audiovisual(expected, inspection.facts, errors, checks)
    else:
        _compare_encoded_audiovisual(expected, inspection, errors, checks)


def _compare_expected_facts(expected: Mapping[str, object], inspection: InspectionResult, errors: list[str], checks: list[str]) -> None:
    kind = expected.get("type")
    if inspection.kind != kind:
        errors.append("decoded artifact kind does not match manifest")
    allowed = {
        MediaFormat.PNG: {"image"}, MediaFormat.GIF: {"video"},
        MediaFormat.WAV: {"audio"}, MediaFormat.MP4: {"video", "audiovisual"},
        MediaFormat.NPZ: {"image", "audio", "video", "audiovisual"},
    }
    if kind not in allowed[inspection.format]:
        errors.append("decoded container format is incompatible with manifest artifact kind")
        return
    if inspection.format in (MediaFormat.PNG, MediaFormat.GIF):
        if inspection.facts.get("container_format") != inspection.format.value.upper():
            errors.append("decoded Pillow container format does not match declared format")
    if inspection.format is MediaFormat.MP4:
        streams = inspection.facts.get("streams", ())
        observed = sorted(stream.get("codec_type", "unknown") for stream in streams if isinstance(stream, Mapping))
        required = ["audio", "video"] if kind == "audiovisual" else ["video"]
        if observed != required or len(streams) != len(required):
            errors.append("decoded MP4 stream kind/count does not match manifest")
            return
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
    required_arrays = {
        "image": {"pixels": (2, 3)}, "audio": {"samples": (1, 2)},
        "video": {"frames": (3, 4)}, "audiovisual": {"samples": (1, 2), "frames": (3, 4)},
    }
    if kind not in required_arrays:
        raise ValueError("NPZ metadata kind is unsupported")
    required = required_arrays[kind]
    if set(facts["arrays"]) != set(required):
        raise ValueError("NPZ arrays do not match the declared artifact kind")
    for name, ranks in required.items():
        shape = facts[f"{name}_shape"]
        if len(shape) not in ranks or any(size <= 0 for size in shape):
            raise ValueError(f"NPZ {name} rank/shape is invalid for {kind}")
    if kind in {"audio", "audiovisual"}:
        facts["sample_rate"] = SampleRate(metadata["sample_rate"]).value
    if kind in {"video", "audiovisual"}:
        facts["frame_rate"] = FrameRate(metadata["frame_rate"]).value
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
            facts["duration_seconds"] = shape[0] / facts["sample_rate"]
    elif kind == "video":
        shape = facts.get("frames_shape")
        if isinstance(shape, list) and len(shape) >= 3:
            facts.update({"frames": shape[0], "height": shape[1], "width": shape[2]})
            facts["duration_seconds"] = shape[0] / facts["frame_rate"]
    elif kind == "audiovisual":
        audio_shape = facts.get("samples_shape")
        video_shape = facts.get("frames_shape")
        if isinstance(audio_shape, list) and audio_shape:
            facts.update({"audio_frames": audio_shape[0], "audio_channels": audio_shape[1] if len(audio_shape) > 1 else 1})
            facts["audio_duration_seconds"] = audio_shape[0] / facts["sample_rate"]
        if isinstance(video_shape, list) and len(video_shape) >= 3:
            facts.update({"video_frames": video_shape[0], "video_height": video_shape[1], "video_width": video_shape[2]})
            facts["video_duration_seconds"] = video_shape[0] / facts["frame_rate"]


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
    duration = facts.get("duration_seconds")
    frames = facts.get("frames")
    if isinstance(duration, (int, float)) and duration > 0 and isinstance(frames, int):
        return frames / duration
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
