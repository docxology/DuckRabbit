"""Lazy media encoders for canonical DuckRabbit artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess  # nosec B404 -- argv is fixed and input paths are positional
import wave
import os
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory

import numpy as np

from .artifacts import AudioBuffer, AudiovisualTimeline, ImageFrame, VideoSequence
from .errors import BackendUnavailableError, MediaEncodingError
from .parameters import AudioEncoding, BackendKind, CanonicalArchiveEncoding, ColorMode, FrameRate, GifEncoding, MediaFormat, MuxEncoding, PcmBitDepth, SampleRate, SpatialOffset, SyncOffsetMs, VideoEncoding


@dataclass(frozen=True)
class BackendCapability:
    """Machine-readable availability of one encoding or inspection path."""

    format: MediaFormat
    operation: str
    backend: BackendKind
    available: bool
    dependency: str
    detail: str

    def __post_init__(self) -> None:
        if not isinstance(self.format, MediaFormat) or not isinstance(self.backend, BackendKind):
            raise ValueError("backend capability format and backend are typed enums")
        if self.operation not in {"encode", "inspect"} or not self.dependency or not self.detail:
            raise ValueError("backend capability operation, dependency, and detail are required")
        if type(self.available) is not bool:
            raise ValueError("backend capability available must be bool")

    def to_dict(self) -> dict[str, object]:
        return {
            "format": self.format.value,
            "operation": self.operation,
            "backend": self.backend.value,
            "available": self.available,
            "dependency": self.dependency,
            "detail": self.detail,
        }


def backend_capabilities() -> tuple[BackendCapability, ...]:
    """Probe declared codec dependencies without writing media."""
    pillow_available = find_spec("PIL") is not None
    numpy_available = find_spec("numpy") is not None
    ffmpeg_available = shutil.which("ffmpeg") is not None
    ffprobe_available = shutil.which("ffprobe") is not None
    return (
        BackendCapability(MediaFormat.PNG, "encode", BackendKind.PILLOW, pillow_available, "Pillow", "PNG raster encoder" if pillow_available else "Pillow is not importable"),
        BackendCapability(MediaFormat.PNG, "inspect", BackendKind.PILLOW, pillow_available, "Pillow", "PNG decoder" if pillow_available else "Pillow is not importable"),
        BackendCapability(MediaFormat.GIF, "encode", BackendKind.PILLOW, pillow_available, "Pillow", "GIF animation encoder" if pillow_available else "Pillow is not importable"),
        BackendCapability(MediaFormat.GIF, "inspect", BackendKind.PILLOW, pillow_available, "Pillow", "GIF decoder" if pillow_available else "Pillow is not importable"),
        BackendCapability(MediaFormat.WAV, "encode", BackendKind.PYTHON_WAVE, True, "Python standard library", "PCM WAV encoder"),
        BackendCapability(MediaFormat.WAV, "inspect", BackendKind.PYTHON_WAVE, True, "Python standard library", "PCM WAV decoder"),
        BackendCapability(MediaFormat.NPZ, "encode", BackendKind.NUMPY, numpy_available, "NumPy", "exact canonical archive encoder" if numpy_available else "NumPy is not importable"),
        BackendCapability(MediaFormat.NPZ, "inspect", BackendKind.NUMPY, numpy_available, "NumPy", "exact canonical archive decoder" if numpy_available else "NumPy is not importable"),
        BackendCapability(MediaFormat.MP4, "encode", BackendKind.FFMPEG, ffmpeg_available, "ffmpeg", "MP4 encoder" if ffmpeg_available else "ffmpeg executable is not discoverable"),
        BackendCapability(MediaFormat.MP4, "inspect", BackendKind.FFMPEG, ffprobe_available, "ffprobe", "MP4 stream inspector" if ffprobe_available else "ffprobe executable is not discoverable"),
    )


@contextmanager
def _atomic_destination(path: Path, *, overwrite: bool = True):
    """Yield a same-directory temporary path and atomically publish it on success."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if type(overwrite) is not bool:
        raise MediaEncodingError("overwrite must be bool")
    if path.exists() and not overwrite:
        raise FileExistsError(f"output already exists and overwrite is disabled: {path}")
    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(prefix=f".{path.name}.", suffix=path.suffix, dir=path.parent, delete=False) as handle:
            temporary_path = Path(handle.name)
        yield temporary_path
        os.replace(temporary_path, path)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def _uint8(image: ImageFrame) -> np.ndarray:
    return np.rint(np.clip(image.pixels, 0.0, 1.0) * 255.0).astype(np.uint8)


def write_png(image: ImageFrame, path: Path, *, overwrite: bool = True) -> Path:
    """Write one canonical frame as a PNG using Pillow lazily."""
    try:
        from PIL import Image
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency gate
        raise BackendUnavailableError("PNG encoding requires Pillow") from exc
    path = Path(path)
    with _atomic_destination(path, overwrite=overwrite) as temporary_path:
        Image.fromarray(_uint8(image), mode=image.mode.value).save(temporary_path, format="PNG")
    return path


def write_gif(video: VideoSequence, path: Path, *, encoding: GifEncoding = GifEncoding(), overwrite: bool = True) -> Path:
    """Write a canonical frame sequence as an animated GIF."""
    try:
        from PIL import Image
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency gate
        raise BackendUnavailableError("GIF encoding requires Pillow") from exc
    if not isinstance(encoding, GifEncoding):
        raise MediaEncodingError("GIF encoding must be GifEncoding")
    path = Path(path)
    frames = [Image.fromarray(_uint8(frame), mode=frame.mode.value) for frame in video.frames]
    with _atomic_destination(path, overwrite=overwrite) as temporary_path:
        frames[0].save(
            temporary_path,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=round(1000.0 / video.frame_rate.value),
            loop=encoding.loop,
            disposal=2,
            optimize=encoding.optimize,
        )
    return path


def _pcm_bytes(audio: AudioBuffer, bit_depth: PcmBitDepth) -> bytes:
    """Convert canonical float audio into little-endian PCM bytes."""
    samples = np.clip(audio.samples, -1.0, 1.0)
    if bit_depth == 8:
        return np.rint((samples + 1.0) * 127.5).astype("u1").tobytes()
    if bit_depth == 16:
        return np.rint(samples * 32767.0).astype("<i2").tobytes()
    if bit_depth == 24:
        values = np.rint(samples * 8388607.0).astype("<i4")
        return values.view("u1").reshape(-1, 4)[:, :3].tobytes()
    return np.rint(samples * 2147483647.0).astype("<i4").tobytes()


def write_wav(audio: AudioBuffer, path: Path, *, encoding: AudioEncoding = AudioEncoding(), overwrite: bool = True) -> Path:
    """Write canonical float audio as deterministic PCM WAV."""
    if not isinstance(encoding, AudioEncoding):
        raise MediaEncodingError("WAV encoding must be AudioEncoding")
    path = Path(path)
    bit_depth = encoding.bit_depth
    with _atomic_destination(path, overwrite=overwrite) as temporary_path:
        with wave.open(str(temporary_path), "wb") as handle:
            handle.setnchannels(audio.channels)
            handle.setsampwidth(bit_depth.value // 8)
            handle.setframerate(audio.sample_rate.value)
            handle.writeframes(_pcm_bytes(audio, bit_depth))
    return path


def _ffmpeg(ffmpeg_bin: str) -> str:
    resolved = shutil.which(ffmpeg_bin)
    if resolved is None:
        raise BackendUnavailableError(f"ffmpeg executable not found: {ffmpeg_bin}")
    return resolved


def _rgb_frames(video: VideoSequence) -> np.ndarray:
    arrays = []
    for frame in video.frames:
        values = _uint8(frame)
        if frame.mode is ColorMode.GRAYSCALE:
            values = np.repeat(values[..., None], 3, axis=2)
        arrays.append(values)
    return np.stack(arrays, axis=0)


def write_mp4(
    video: VideoSequence,
    path: Path,
    *,
    ffmpeg_bin: str = "ffmpeg",
    encoding: VideoEncoding = VideoEncoding(),
    overwrite: bool = True,
) -> Path:
    """Encode a silent MP4 from canonical RGB frames using ffmpeg."""
    executable = _ffmpeg(ffmpeg_bin)
    if not isinstance(encoding, VideoEncoding):
        raise MediaEncodingError("MP4 encoding must be VideoEncoding")
    if video.width % 2 or video.height % 2:
        raise MediaEncodingError("MP4 yuv420p encoding requires even video width and height")
    path = Path(path)
    frames = _rgb_frames(video)
    with _atomic_destination(path, overwrite=overwrite) as temporary_path:
        command = [
            executable,
            "-y",
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{video.width}x{video.height}",
            "-r",
            str(video.frame_rate.value),
            "-i",
            "-",
            "-an",
            "-c:v",
            encoding.codec,
            "-pix_fmt",
            encoding.pixel_format,
            "-crf",
            str(encoding.crf),
            str(temporary_path),
        ]
        try:
            subprocess.run(command, input=frames.tobytes(), check=True, capture_output=True, timeout=120.0)  # nosec B603 -- executable is resolved and argv has no shell
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            stderr = exc.stderr or b""
            detail = stderr.decode("utf-8", errors="replace")[-1000:] if isinstance(stderr, bytes) else str(stderr)[-1000:]
            raise MediaEncodingError(f"ffmpeg video encoding failed: {detail}") from exc
    return path


def write_audiovisual(
    timeline: AudiovisualTimeline,
    path: Path,
    *,
    ffmpeg_bin: str = "ffmpeg",
    encoding: MuxEncoding = MuxEncoding(),
    overwrite: bool = True,
) -> Path:
    """Encode a canonical timeline as an MP4 with declared sync offset applied.

    ``sync_offset`` is audio relative to video: positive values delay audio;
    negative values delay video. The output duration expands to retain the
    delayed stream instead of silently truncating it with ``-shortest``.
    """
    executable = _ffmpeg(ffmpeg_bin)
    if not isinstance(encoding, MuxEncoding):
        raise MediaEncodingError("audio-visual encoding must be MuxEncoding")
    path = Path(path)
    with _atomic_destination(path, overwrite=overwrite) as temporary_path:
        with TemporaryDirectory(prefix="duckrabbit-media-") as temporary:
            temporary_root = Path(temporary)
            silent_video = write_mp4(timeline.video, temporary_root / "video.mp4", ffmpeg_bin=ffmpeg_bin, encoding=encoding.video)
            audio_path = write_wav(timeline.audio, temporary_root / "audio.wav")
            offset_seconds = timeline.sync_offset.value / 1000.0
            video_delay = max(0.0, -offset_seconds)
            audio_delay = max(0.0, offset_seconds)
            output_duration = max(
                timeline.video.duration_seconds + video_delay,
                timeline.audio.duration_seconds + audio_delay,
            )
            video_input = ["-i", str(silent_video)]
            audio_input = ["-i", str(audio_path)]
            if video_delay:
                video_input = ["-itsoffset", f"{video_delay:.6f}", *video_input]
            if audio_delay:
                audio_input = ["-itsoffset", f"{audio_delay:.6f}", *audio_input]
            command = [
                executable,
                "-y",
                *video_input,
                *audio_input,
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                encoding.audio_codec,
                "-t",
                f"{output_duration:.6f}",
                str(temporary_path),
            ]
            try:
                subprocess.run(command, check=True, capture_output=True, timeout=120.0)  # nosec B603 -- executable is resolved and argv has no shell
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                stderr = exc.stderr or b""
                detail = stderr.decode("utf-8", errors="replace")[-1000:] if isinstance(stderr, bytes) else str(stderr)[-1000:]
                raise MediaEncodingError(f"ffmpeg audio/video mux failed: {detail}") from exc
    return path


def write_npz(
    artifact: ImageFrame | AudioBuffer | VideoSequence | AudiovisualTimeline,
    path: Path,
    *,
    encoding: CanonicalArchiveEncoding = CanonicalArchiveEncoding(),
    overwrite: bool = True,
) -> Path:
    """Write exact canonical arrays and clock metadata to a NumPy archive."""
    if not isinstance(encoding, CanonicalArchiveEncoding):
        raise MediaEncodingError("NPZ encoding must be CanonicalArchiveEncoding")
    path = Path(path)
    metadata: dict[str, object]
    arrays: dict[str, np.ndarray] = {}
    if isinstance(artifact, ImageFrame):
        metadata = {"kind": "image", "mode": artifact.mode.value}
        arrays["pixels"] = np.asarray(artifact.pixels, dtype="<f4")
    elif isinstance(artifact, AudioBuffer):
        metadata = {"kind": "audio", "sample_rate": artifact.sample_rate.value}
        arrays["samples"] = np.asarray(artifact.samples, dtype="<f4")
    elif isinstance(artifact, VideoSequence):
        metadata = {"kind": "video", "frame_rate": artifact.frame_rate.value, "mode": artifact.pixel_mode.value}
        arrays["frames"] = np.asarray([frame.pixels for frame in artifact.frames], dtype="<f4")
    elif isinstance(artifact, AudiovisualTimeline):
        metadata = {
            "kind": "audiovisual",
            "sample_rate": artifact.audio.sample_rate.value,
            "frame_rate": artifact.video.frame_rate.value,
            "mode": artifact.video.pixel_mode.value,
            "sync_offset_ms": artifact.sync_offset.value,
            "spatial_offset": artifact.spatial_offset.value,
            "timeline_metadata": dict(sorted(artifact.metadata.items())),
        }
        arrays["samples"] = np.asarray(artifact.audio.samples, dtype="<f4")
        arrays["frames"] = np.asarray([frame.pixels for frame in artifact.video.frames], dtype="<f4")
    else:  # pragma: no cover - union exhaustiveness
        raise MediaEncodingError(f"NPZ encoding does not support {type(artifact).__name__}")
    arrays["metadata_json"] = np.asarray(json.dumps(metadata, sort_keys=True))
    saver = np.savez_compressed if encoding.compressed else np.savez
    with _atomic_destination(path, overwrite=overwrite) as temporary_path:
        saver(temporary_path, **arrays)
    return path


def read_npz(path: Path) -> ImageFrame | AudioBuffer | VideoSequence | AudiovisualTimeline:
    """Read an exact canonical NPZ archive back into a validated artifact."""
    path = Path(path)
    try:
        with np.load(path, allow_pickle=False) as archive:
            metadata = json.loads(str(archive["metadata_json"].item()))
            kind = metadata["kind"]
            if kind == "image":
                return ImageFrame(archive["pixels"], mode=ColorMode(metadata["mode"]))
            if kind == "audio":
                return AudioBuffer(archive["samples"], SampleRate(metadata["sample_rate"]))
            if kind == "video":
                frames = tuple(ImageFrame(frame, mode=ColorMode(metadata["mode"])) for frame in archive["frames"])
                return VideoSequence(frames, FrameRate(metadata["frame_rate"]))
            if kind == "audiovisual":
                audio = AudioBuffer(archive["samples"], SampleRate(metadata["sample_rate"]))
                frames = tuple(ImageFrame(frame, mode=ColorMode(metadata["mode"])) for frame in archive["frames"])
                video = VideoSequence(frames, FrameRate(metadata["frame_rate"]))
                return AudiovisualTimeline(
                    audio,
                    video,
                    sync_offset=SyncOffsetMs(metadata["sync_offset_ms"]),
                    spatial_offset=SpatialOffset(metadata["spatial_offset"]),
                    metadata=metadata.get("timeline_metadata", {}),
                )
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise MediaEncodingError(f"cannot read canonical NPZ archive {path}: {exc}") from exc
    raise MediaEncodingError(f"unsupported canonical NPZ kind {kind!r}")
