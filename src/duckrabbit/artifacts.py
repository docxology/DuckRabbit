"""Canonical in-memory media artifacts shared by generators and encoders."""

from __future__ import annotations

from dataclasses import dataclass, field, is_dataclass
import math
from types import MappingProxyType
from collections.abc import Mapping
from enum import Enum
from typing import Iterator, Literal, TypedDict


import numpy as np

from .errors import ParameterValidationError
from .parameters import BackendKind, ColorMode, FrameRate, MediaFormat, SampleRate, Seed, SpatialOffset, SyncOffsetMs
from .taxonomy import ImplementationStatus, Modality, TaxonomyEntry


def _freeze_profile(value: object) -> object:
    """Recursively freeze JSON-like encoding-profile values."""
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze_profile(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_profile(item) for item in value)
    return value


def _readonly_float32(array: np.ndarray, *, name: str) -> np.ndarray:
    values = np.asarray(array, dtype=np.float32)
    if not np.isfinite(values).all():
        raise ParameterValidationError(f"{name} contains non-finite values")
    if values.size and (values.min() < 0.0 or values.max() > 1.0):
        raise ParameterValidationError(f"{name} values must be in [0, 1]")
    values = np.array(values, dtype=np.float32, copy=True)
    values.setflags(write=False)
    return values


@dataclass(frozen=True)
class ImageFrame:
    """A canonical grayscale or RGB image with float32 pixels in [0, 1]."""

    pixels: np.ndarray
    mode: ColorMode = ColorMode.GRAYSCALE

    def __post_init__(self) -> None:
        values = _readonly_float32(self.pixels, name="image")
        if not isinstance(self.mode, ColorMode):
            try:
                object.__setattr__(self, "mode", ColorMode(self.mode))
            except ValueError as exc:
                raise ParameterValidationError(f"unsupported image mode {self.mode!r}") from exc
        if self.mode is ColorMode.GRAYSCALE and (values.ndim != 2 or min(values.shape) < 1):
            raise ParameterValidationError("grayscale images must have shape (height, width)")
        if self.mode is ColorMode.RGB and (values.ndim != 3 or values.shape[-1] != 3 or min(values.shape[:2]) < 1):
            raise ParameterValidationError("RGB images must have shape (height, width, 3)")
        object.__setattr__(self, "pixels", values)

    @property
    def width(self) -> int:
        return int(self.pixels.shape[1])

    @property
    def height(self) -> int:
        return int(self.pixels.shape[0])

    @property
    def channels(self) -> int:
        """Number of encoded color channels."""
        return 1 if self.mode is ColorMode.GRAYSCALE else 3

    @property
    def nbytes(self) -> int:
        """Canonical pixel storage size in bytes."""
        return int(self.pixels.nbytes)

    @property
    def value_range(self) -> tuple[float, float]:
        """Minimum and maximum canonical pixel values."""
        return float(self.pixels.min()), float(self.pixels.max())


@dataclass(frozen=True)
class AudioBuffer:
    """A canonical float32 audio signal with shape (samples, channels)."""

    samples: np.ndarray
    sample_rate: SampleRate

    def __post_init__(self) -> None:
        if not isinstance(self.sample_rate, SampleRate):
            raise ParameterValidationError("audio sample_rate must be SampleRate")
        values = np.asarray(self.samples, dtype=np.float32)
        if values.ndim == 1:
            values = values[:, None]
        if values.ndim != 2 or values.shape[0] < 1 or values.shape[1] not in {1, 2}:
            raise ParameterValidationError("audio samples must have shape (samples, 1) or (samples, 2)")
        if not np.isfinite(values).all():
            raise ParameterValidationError("audio contains non-finite values")
        if values.size and (values.min() < -1.0 or values.max() > 1.0):
            raise ParameterValidationError("audio samples must be in [-1, 1]")
        values = np.array(values, dtype=np.float32, copy=True)
        values.setflags(write=False)
        object.__setattr__(self, "samples", values)

    @property
    def channels(self) -> int:
        return int(self.samples.shape[1])

    @property
    def duration_seconds(self) -> float:
        return self.samples.shape[0] / self.sample_rate.value

    @property
    def sample_count(self) -> int:
        return int(self.samples.shape[0])

    @property
    def nbytes(self) -> int:
        return int(self.samples.nbytes)

    @property
    def peak(self) -> float:
        return float(np.max(np.abs(self.samples)))

    @property
    def rms(self) -> float:
        return float(np.sqrt(np.mean(np.square(self.samples))))


@dataclass(frozen=True)
class VideoSequence:
    """A sequence of canonical image frames on a fixed clock."""

    frames: tuple[ImageFrame, ...]
    frame_rate: FrameRate

    def __post_init__(self) -> None:
        if not isinstance(self.frame_rate, FrameRate):
            raise ParameterValidationError("video frame_rate must be FrameRate")
        frames = tuple(self.frames)
        if not frames:
            raise ParameterValidationError("video must contain at least one frame")
        if not all(isinstance(frame, ImageFrame) for frame in frames):
            raise ParameterValidationError("video frames must be ImageFrame objects")
        first_shape = frames[0].pixels.shape[:2]
        if any(frame.pixels.shape[:2] != first_shape for frame in frames):
            raise ParameterValidationError("all video frames must have identical shapes")
        if any(frame.mode is not frames[0].mode for frame in frames):
            raise ParameterValidationError("all video frames must have identical color modes")
        object.__setattr__(self, "frames", frames)

    def __iter__(self) -> Iterator[ImageFrame]:
        return iter(self.frames)

    @property
    def duration_seconds(self) -> float:
        return len(self.frames) / self.frame_rate.value

    @property
    def temporal_deltas(self) -> tuple[float, ...]:
        """Mean absolute pixel change between each adjacent frame."""
        return tuple(
            float(np.mean(np.abs(current.pixels - previous.pixels)))
            for previous, current in zip(self.frames, self.frames[1:])
        )

    @property
    def has_temporal_change(self) -> bool:
        """Whether at least one adjacent frame differs."""
        return any(delta > 0.0 for delta in self.temporal_deltas)

    @property
    def width(self) -> int:
        return self.frames[0].width

    @property
    def height(self) -> int:
        return self.frames[0].height

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def nbytes(self) -> int:
        return int(sum(frame.nbytes for frame in self.frames))

    @property
    def pixel_mode(self) -> ColorMode:
        return self.frames[0].mode

    @property
    def mean_temporal_delta(self) -> float:
        deltas = self.temporal_deltas
        return float(np.mean(deltas)) if deltas else 0.0


@dataclass(frozen=True)
class AudiovisualTimeline:
    """Audio and video sharing an explicit timeline and discrepancy metadata."""

    audio: AudioBuffer
    video: VideoSequence
    sync_offset: SyncOffsetMs = SyncOffsetMs(0.0)
    spatial_offset: SpatialOffset = SpatialOffset(0.0)
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.audio, AudioBuffer) or not isinstance(self.video, VideoSequence):
            raise ParameterValidationError("timeline audio/video must be AudioBuffer and VideoSequence")
        if not isinstance(self.sync_offset, SyncOffsetMs) or not isinstance(self.spatial_offset, SpatialOffset):
            raise ParameterValidationError("timeline offsets must use typed offset values")
        if not isinstance(self.metadata, Mapping) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in self.metadata.items()
        ):
            raise ParameterValidationError("timeline metadata must be a string mapping")
        if abs(self.audio.duration_seconds - self.video.duration_seconds) > 1.0 / self.video.frame_rate.value:
            raise ParameterValidationError(
                "audio/video duration mismatch exceeds one video frame: "
                f"{self.audio.duration_seconds:.6f}s vs {self.video.duration_seconds:.6f}s"
            )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def duration_seconds(self) -> float:
        return max(self.audio.duration_seconds, self.video.duration_seconds)

    @property
    def audio_start_seconds(self) -> float:
        """Presentation start of audio relative to the shared zero clock."""
        return max(0.0, self.sync_offset.value / 1000.0)

    @property
    def video_start_seconds(self) -> float:
        """Presentation start of video relative to the shared zero clock."""
        return max(0.0, -self.sync_offset.value / 1000.0)

    @property
    def presentation_duration_seconds(self) -> float:
        """Duration after applying the declared synchronization offset."""
        return max(
            self.audio_start_seconds + self.audio.duration_seconds,
            self.video_start_seconds + self.video.duration_seconds,
        )

    @property
    def nbytes(self) -> int:
        return self.audio.nbytes + self.video.nbytes


CanonicalArtifact = ImageFrame | AudioBuffer | VideoSequence | AudiovisualTimeline


class ImageSummary(TypedDict):
    type: Literal["image"]
    mode: ColorMode
    width: int
    height: int
    channels: int
    dtype: str
    nbytes: int
    min_value: float
    max_value: float


class AudioSummary(TypedDict):
    type: Literal["audio"]
    samples: int
    channels: int
    sample_rate: int
    duration_seconds: float
    dtype: str
    nbytes: int
    peak: float
    rms: float


class VideoSummary(TypedDict):
    type: Literal["video"]
    width: int
    height: int
    frames: int
    frame_rate: float
    duration_seconds: float
    mode: ColorMode
    dtype: str
    nbytes: int
    temporal_deltas: list[float]
    mean_temporal_delta: float


class AudiovisualSummary(TypedDict):
    type: Literal["audiovisual"]
    audio: AudioSummary
    video: VideoSummary
    sync_offset_ms: float
    spatial_offset: float
    duration_seconds: float
    audio_start_seconds: float
    video_start_seconds: float
    presentation_duration_seconds: float
    nbytes: int


ArtifactSummary = ImageSummary | AudioSummary | VideoSummary | AudiovisualSummary



class ArtifactKind(str, Enum):
    """Stable artifact kind labels used by summaries and manifests."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    AUDIOVISUAL = "audiovisual"


@dataclass(frozen=True)
class EncodedArtifact:
    """Immutable record of one encoded artifact written to disk."""

    path: str
    format: MediaFormat
    media_type: str
    size_bytes: int
    sha256: str
    backend: BackendKind = BackendKind.PILLOW
    profile: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.path or not self.media_type or not self.sha256:
            raise ParameterValidationError("encoded artifact path, media_type, and sha256 are required")
        if not isinstance(self.format, MediaFormat):
            raise ParameterValidationError("encoded artifact format must be MediaFormat")
        if type(self.size_bytes) is not int or self.size_bytes <= 0:
            raise ParameterValidationError("encoded artifact size_bytes must be a positive integer")
        if len(self.sha256) != 64 or any(character not in "0123456789abcdef" for character in self.sha256):
            raise ParameterValidationError("encoded artifact sha256 must be lowercase hex")
        if not isinstance(self.backend, BackendKind):
            raise ParameterValidationError("encoded artifact backend must be BackendKind")
        if not isinstance(self.profile, Mapping) or not all(isinstance(key, str) for key in self.profile):
            raise ParameterValidationError("encoded artifact profile must be a string-keyed mapping")
        object.__setattr__(self, "profile", _freeze_profile(self.profile))


@dataclass(frozen=True)
class ArtifactManifest:
    """Typed provenance record for one canonical artifact and optional encoding."""

    schema_version: str
    illusion_id: str
    implementation_status: ImplementationStatus
    modality: tuple[Modality, ...]
    taxonomy: TaxonomyEntry
    parameters: object
    seed: Seed
    canonical_digest: str
    duration_seconds: float | None
    output: str | None = None
    manifest: str | None = None
    artifact: ArtifactSummary | None = None
    encoding: EncodedArtifact | None = None

    def __post_init__(self) -> None:
        if self.schema_version != "duckrabbit/artifact/v1" or not self.illusion_id:
            raise ParameterValidationError("manifest schema_version and illusion_id are required")
        if not isinstance(self.seed, Seed):
            try:
                object.__setattr__(self, "seed", Seed(self.seed))
            except ParameterValidationError as exc:
                raise ParameterValidationError("manifest seed must be a signed 64-bit integer") from exc
        if not isinstance(self.implementation_status, ImplementationStatus):
            raise ParameterValidationError("manifest implementation_status must be ImplementationStatus")
        if not isinstance(self.modality, tuple) or not self.modality or not all(isinstance(item, Modality) for item in self.modality):
            raise ParameterValidationError("manifest modality must be a non-empty tuple of Modality")
        if not isinstance(self.taxonomy, TaxonomyEntry):
            raise ParameterValidationError("manifest taxonomy must be TaxonomyEntry")
        if self.taxonomy.illusion_id != self.illusion_id:
            raise ParameterValidationError("manifest taxonomy illusion_id does not match manifest illusion_id")
        if self.taxonomy.implementation_status is not self.implementation_status:
            raise ParameterValidationError("manifest implementation_status disagrees with taxonomy")
        if self.taxonomy.modalities != self.modality:
            raise ParameterValidationError("manifest modality disagrees with taxonomy")
        if not is_dataclass(self.parameters):
            raise ParameterValidationError("manifest parameters must be a dataclass instance")
        if len(self.canonical_digest) != 64 or any(character not in "0123456789abcdef" for character in self.canonical_digest):
            raise ParameterValidationError("manifest canonical_digest must be lowercase SHA-256 hex")
        if self.artifact is not None:
            _validate_artifact_summary(self.artifact)
        if self.encoding is not None and not isinstance(self.encoding, EncodedArtifact):
            raise ParameterValidationError("manifest encoding must be EncodedArtifact")
        if self.duration_seconds is not None and (
            not isinstance(self.duration_seconds, (int, float))
            or isinstance(self.duration_seconds, bool)
            or not math.isfinite(float(self.duration_seconds))
            or self.duration_seconds < 0
        ):
            raise ParameterValidationError("manifest duration must not be negative")
        for name, value in (("output", self.output), ("manifest", self.manifest)):
            if value is not None and not isinstance(value, str):
                raise ParameterValidationError(f"manifest {name} must be a string or null")


def _validate_artifact_summary(summary: ArtifactSummary) -> None:
    """Validate the discriminated summary union instead of accepting any mapping."""
    if not isinstance(summary, Mapping):
        raise ParameterValidationError("manifest artifact summary must be a mapping")
    kind = summary.get("type")
    required: dict[str, tuple[str, ...]] = {
        "image": ("mode", "width", "height", "channels", "dtype", "nbytes", "min_value", "max_value"),
        "audio": ("samples", "channels", "sample_rate", "duration_seconds", "dtype", "nbytes", "peak", "rms"),
        "video": ("width", "height", "frames", "frame_rate", "duration_seconds", "mode", "dtype", "nbytes", "temporal_deltas", "mean_temporal_delta"),
        "audiovisual": ("audio", "video", "sync_offset_ms", "spatial_offset", "duration_seconds", "audio_start_seconds", "video_start_seconds", "presentation_duration_seconds", "nbytes"),
    }
    if not isinstance(kind, str) or kind not in required:
        raise ParameterValidationError("manifest artifact summary has an unsupported type")
    missing = [field for field in required[kind] if field not in summary]
    if missing:
        raise ParameterValidationError(f"manifest artifact summary missing fields: {', '.join(missing)}")
    if kind == "audiovisual":
        _validate_artifact_summary(summary["audio"])  # type: ignore[arg-type]
        _validate_artifact_summary(summary["video"])  # type: ignore[arg-type]
    for field_name in ("width", "height", "channels", "samples", "frames", "nbytes"):
        if field_name in summary and (type(summary[field_name]) is not int or summary[field_name] <= 0):
            raise ParameterValidationError(f"manifest artifact {field_name} must be a positive integer")

    def finite_number(field_name: str) -> float:
        value = summary[field_name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise ParameterValidationError(f"manifest artifact {field_name} must be finite")
        return float(value)

    def mode_value(value: object) -> str:
        if isinstance(value, ColorMode):
            return value.value
        if not isinstance(value, str) or value not in {ColorMode.GRAYSCALE.value, ColorMode.RGB.value}:
            raise ParameterValidationError("manifest artifact mode must be 'L' or 'RGB'")
        return value

    if kind == "image":
        mode = mode_value(summary["mode"])
        channels = int(summary["channels"])
        expected_channels = 1 if mode == ColorMode.GRAYSCALE.value else 3
        if channels != expected_channels:
            raise ParameterValidationError("manifest image channels disagree with mode")
        if summary["dtype"] != "<f4":
            raise ParameterValidationError("manifest image dtype must be <f4")
        minimum = finite_number("min_value")
        maximum = finite_number("max_value")
        if not 0.0 <= minimum <= maximum <= 1.0:
            raise ParameterValidationError("manifest image values must satisfy 0 <= min <= max <= 1")
        expected_nbytes = int(summary["width"]) * int(summary["height"]) * channels * 4
        if int(summary["nbytes"]) != expected_nbytes:
            raise ParameterValidationError("manifest image nbytes disagree with shape and dtype")
        return

    if kind == "audio":
        if summary["dtype"] != "<f4":
            raise ParameterValidationError("manifest audio dtype must be <f4")
        sample_rate = summary["sample_rate"]
        if type(sample_rate) is not int or not 1000 <= sample_rate <= 384000:
            raise ParameterValidationError("manifest audio sample_rate must be an integer in [1000, 384000]")
        channels = int(summary["channels"])
        if channels not in {1, 2}:
            raise ParameterValidationError("manifest audio channels must be 1 or 2")
        duration = finite_number("duration_seconds")
        peak = finite_number("peak")
        rms = finite_number("rms")
        if not 0.0 < duration or not 0.0 <= rms <= peak <= 1.0:
            raise ParameterValidationError("manifest audio duration, RMS, and peak are out of range")
        if not math.isclose(duration, int(summary["samples"]) / sample_rate, rel_tol=0.0, abs_tol=1e-9):
            raise ParameterValidationError("manifest audio duration disagrees with samples and sample_rate")
        expected_nbytes = int(summary["samples"]) * channels * 4
        if int(summary["nbytes"]) != expected_nbytes:
            raise ParameterValidationError("manifest audio nbytes disagree with shape and dtype")
        return

    if kind == "video":
        mode = mode_value(summary["mode"])
        if summary["dtype"] != "<f4":
            raise ParameterValidationError("manifest video dtype must be <f4")
        frame_rate = finite_number("frame_rate")
        if not 1.0 <= frame_rate <= 240.0:
            raise ParameterValidationError("manifest video frame_rate must be in [1, 240]")
        duration = finite_number("duration_seconds")
        if not math.isclose(duration, int(summary["frames"]) / frame_rate, rel_tol=0.0, abs_tol=1e-9):
            raise ParameterValidationError("manifest video duration disagrees with frames and frame_rate")
        deltas = summary["temporal_deltas"]
        if not isinstance(deltas, (list, tuple)) or len(deltas) != int(summary["frames"]) - 1:
            raise ParameterValidationError("manifest video temporal_deltas must have frames - 1 values")
        numeric_deltas = []
        for delta in deltas:
            if isinstance(delta, bool) or not isinstance(delta, (int, float)) or not math.isfinite(float(delta)) or not 0.0 <= float(delta) <= 1.0:
                raise ParameterValidationError("manifest video temporal_deltas must be finite values in [0, 1]")
            numeric_deltas.append(float(delta))
        expected_mean = sum(numeric_deltas) / len(numeric_deltas) if numeric_deltas else 0.0
        if not math.isclose(finite_number("mean_temporal_delta"), expected_mean, rel_tol=0.0, abs_tol=1e-9):
            raise ParameterValidationError("manifest video mean_temporal_delta disagrees with temporal_deltas")
        channels = 1 if mode == ColorMode.GRAYSCALE.value else 3
        expected_nbytes = int(summary["width"]) * int(summary["height"]) * int(summary["frames"]) * channels * 4
        if int(summary["nbytes"]) != expected_nbytes:
            raise ParameterValidationError("manifest video nbytes disagree with shape and dtype")
        return

    # Audiovisual summaries have already validated their child summaries.
    sync_ms = finite_number("sync_offset_ms")
    spatial_offset = finite_number("spatial_offset")
    if not -10000.0 <= sync_ms <= 10000.0 or not -1.0 <= spatial_offset <= 1.0:
        raise ParameterValidationError("manifest audiovisual offsets are out of range")
    audio = summary["audio"]
    video = summary["video"]
    audio_duration = float(audio["duration_seconds"])
    video_duration = float(video["duration_seconds"])
    sync_seconds = sync_ms / 1000.0
    audio_start = max(0.0, sync_seconds)
    video_start = max(0.0, -sync_seconds)
    presentation = max(audio_start + audio_duration, video_start + video_duration)
    if not math.isclose(finite_number("duration_seconds"), max(audio_duration, video_duration), rel_tol=0.0, abs_tol=1e-9):
        raise ParameterValidationError("manifest audiovisual duration disagrees with child durations")
    if not math.isclose(finite_number("audio_start_seconds"), audio_start, rel_tol=0.0, abs_tol=1e-9):
        raise ParameterValidationError("manifest audiovisual audio_start_seconds disagrees with sync offset")
    if not math.isclose(finite_number("video_start_seconds"), video_start, rel_tol=0.0, abs_tol=1e-9):
        raise ParameterValidationError("manifest audiovisual video_start_seconds disagrees with sync offset")
    if not math.isclose(finite_number("presentation_duration_seconds"), presentation, rel_tol=0.0, abs_tol=1e-9):
        raise ParameterValidationError("manifest audiovisual presentation duration disagrees with timing")
    if int(summary["nbytes"]) != int(audio["nbytes"]) + int(video["nbytes"]):
        raise ParameterValidationError("manifest audiovisual nbytes disagree with child summaries")
