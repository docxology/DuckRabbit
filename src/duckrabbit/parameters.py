"""Strongly typed, validated parameter objects for multimodal stimuli."""

from __future__ import annotations

import math
from dataclasses import dataclass, fields, replace
from enum import Enum
from numbers import Integral, Real
from fractions import Fraction
from typing import Any, TypeVar

from .errors import ParameterValidationError


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ParameterValidationError(f"{name} must be a real number, got {value!r}")
    value = float(value)
    if not math.isfinite(value):
        raise ParameterValidationError(f"{name} must be finite, got {value!r}")
    return value


def _integer(value: int, name: str, low: int, high: int) -> int:
    """Validate an integer-valued control without accepting bools or floats."""
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ParameterValidationError(f"{name} must be an integer in [{low}, {high}], got {value!r}")
    value = int(value)
    if not low <= value <= high:
        raise ParameterValidationError(f"{name} must be an integer in [{low}, {high}], got {value}")
    return value


def _range(value: float, name: str, low: float, high: float) -> float:
    value = _finite(value, name)
    if not low <= value <= high:
        raise ParameterValidationError(f"{name} must be in [{low}, {high}], got {value}")
    return value


class _BoundedInt(int):
    """Immutable integer value object that remains arithmetic-compatible."""

    minimum: int = 0
    maximum: int = 2**63 - 1
    label: str = "value"

    def __new__(cls, value: int) -> "_BoundedInt":
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise ParameterValidationError(
                f"{cls.label} must be an integer in [{cls.minimum}, {cls.maximum}], got {value!r}"
            )
        value = int(value)
        if not cls.minimum <= value <= cls.maximum:
            raise ParameterValidationError(
                f"{cls.label} must be in [{cls.minimum}, {cls.maximum}], got {value}"
            )
        return int.__new__(cls, value)

    @property
    def value(self) -> int:
        return int(self)


class PixelDimension(_BoundedInt):
    """A validated image/video dimension in pixels."""

    minimum = 8
    maximum = 4096
    label = "pixel dimension"


class ChannelCount(_BoundedInt):
    """A supported canonical channel count."""

    minimum = 1
    maximum = 2
    label = "channel count"


class FrameCount(_BoundedInt):
    """A validated number of video frames."""

    minimum = 1
    maximum = 2400
    label = "frame count"


class SampleCount(_BoundedInt):
    """A validated number of audio samples."""

    minimum = 1
    maximum = 384000 * 3600
    label = "sample count"


class FrameIndex(_BoundedInt):
    """A non-negative video frame index."""

    minimum = 0
    maximum = 2400 * 3600
    label = "frame index"


class Seed(_BoundedInt):
    """Portable signed 64-bit deterministic generation seed."""

    minimum = -(2**63)
    maximum = 2**63 - 1
    label = "seed"


class PcmBitDepth(_BoundedInt):
    """PCM bit depth supported by the WAV adapter."""

    minimum = 8
    maximum = 32
    label = "PCM bit depth"

    def __new__(cls, value: int) -> "PcmBitDepth":
        result = super().__new__(cls, value)
        if result not in {8, 16, 24, 32}:
            raise ParameterValidationError("PCM bit depth must be one of 8, 16, 24, or 32")
        return result


class ColorMode(str, Enum):
    """Canonical image color modes."""

    GRAYSCALE = "L"
    RGB = "RGB"


class ChannelLayout(str, Enum):
    """Canonical audio channel layouts."""

    MONO = "mono"
    STEREO = "stereo"

    @property
    def channels(self) -> int:
        return 1 if self is ChannelLayout.MONO else 2


class MediaFormat(str, Enum):
    """Encodings exposed by the lazy media adapters."""

    PNG = "png"
    WAV = "wav"
    GIF = "gif"
    MP4 = "mp4"
    NPZ = "npz"


class PixelFormat(str, Enum):
    """Canonical pixel storage labels independent of container format."""

    FLOAT32_L = "float32_l"
    FLOAT32_RGB = "float32_rgb"


class BackendKind(str, Enum):
    """Backend class recorded in encoded-media provenance."""

    PILLOW = "pillow"
    PYTHON_WAVE = "python_wave"
    FFMPEG = "ffmpeg"
    NUMPY = "numpy"


@dataclass(frozen=True)
class AudioEncoding:
    """WAV encoding controls independent of canonical float audio."""

    bit_depth: PcmBitDepth = PcmBitDepth(16)

    def __post_init__(self) -> None:
        if not isinstance(self.bit_depth, PcmBitDepth):
            object.__setattr__(self, "bit_depth", PcmBitDepth(self.bit_depth))


@dataclass(frozen=True)
class GifEncoding:
    """GIF timing and palette controls."""

    loop: int = 0
    optimize: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "loop", _integer(self.loop, "GIF loop count", 0, 65535))
        if type(self.optimize) is not bool:
            raise ParameterValidationError("GIF optimize must be bool")


@dataclass(frozen=True)
class VideoEncoding:
    """ffmpeg video profile controls."""

    codec: str = "libx264"
    pixel_format: str = "yuv420p"
    crf: int = 18

    def __post_init__(self) -> None:
        if not self.codec or not self.pixel_format:
            raise ParameterValidationError("video codec and pixel_format are required")
        object.__setattr__(self, "crf", _integer(self.crf, "video CRF", 0, 51))


@dataclass(frozen=True)
class MuxEncoding:
    """Audio/video mux profile controls."""

    audio_codec: str = "aac"
    video: VideoEncoding = VideoEncoding()

    def __post_init__(self) -> None:
        if not self.audio_codec:
            raise ParameterValidationError("audio codec is required")
        if not isinstance(self.video, VideoEncoding):
            raise ParameterValidationError("mux video profile must be VideoEncoding")


@dataclass(frozen=True)
class CanonicalArchiveEncoding:
    """Exact NumPy archive profile for canonical artifacts."""

    compressed: bool = True

    def __post_init__(self) -> None:
        if type(self.compressed) is not bool:
            raise ParameterValidationError("canonical archive compressed must be bool")


@dataclass(frozen=True)
class RationalFrameRate:
    """An exact positive frame rate represented as a reduced fraction."""

    numerator: int
    denominator: int = 1

    def __post_init__(self) -> None:
        numerator = _integer(self.numerator, "frame-rate numerator", 1, 1000000)
        denominator = _integer(self.denominator, "frame-rate denominator", 1, 1000000)
        reduced = Fraction(numerator, denominator)
        object.__setattr__(self, "numerator", reduced.numerator)
        object.__setattr__(self, "denominator", reduced.denominator)

    @property
    def fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    @property
    def value(self) -> float:
        return float(self.fraction)

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class TimestampSeconds:
    """A finite timestamp relative to a canonical presentation clock."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _finite(self.value, "timestamp"))

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class OutputSpec:
    """Typed request for an optional encoded output and its manifest."""

    format: MediaFormat | None = None
    include_manifest: bool = True
    overwrite: bool = True
    audio_encoding: AudioEncoding = AudioEncoding()
    gif_encoding: GifEncoding = GifEncoding()
    video_encoding: VideoEncoding = VideoEncoding()
    mux_encoding: MuxEncoding = MuxEncoding()
    archive_encoding: CanonicalArchiveEncoding = CanonicalArchiveEncoding()

    def __post_init__(self) -> None:
        if self.format is not None and not isinstance(self.format, MediaFormat):
            try:
                object.__setattr__(self, "format", MediaFormat(self.format))
            except ValueError as exc:
                raise ParameterValidationError(f"unsupported output format {self.format!r}") from exc
        if type(self.include_manifest) is not bool or type(self.overwrite) is not bool:
            raise ParameterValidationError("output include_manifest and overwrite must be bools")
        if not isinstance(self.audio_encoding, AudioEncoding):
            raise ParameterValidationError("audio_encoding must be AudioEncoding")
        for name, value, expected in (
            ("gif_encoding", self.gif_encoding, GifEncoding),
            ("video_encoding", self.video_encoding, VideoEncoding),
            ("mux_encoding", self.mux_encoding, MuxEncoding),
            ("archive_encoding", self.archive_encoding, CanonicalArchiveEncoding),
        ):
            if not isinstance(value, expected):
                raise ParameterValidationError(f"{name} must be {expected.__name__}")


@dataclass(frozen=True)
class Normalized:
    """A finite scalar in the closed interval [0, 1]."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _range(self.value, "normalized value", 0.0, 1.0))

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class Luminance:
    """A normalized display luminance."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _range(self.value, "luminance", 0.0, 1.0))

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class Amplitude:
    """A normalized audio amplitude."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _range(self.value, "amplitude", 0.0, 1.0))

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class PhaseRadians:
    """A finite oscillator phase in the inclusive interval [-2π, 2π]."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _range(self.value, "phase", -2.0 * math.pi, 2.0 * math.pi))

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class AngleDegrees:
    """A geometric angle in degrees for visual construction parameters."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _range(self.value, "angle", 0.0, 90.0))

    def __float__(self) -> float:
        return self.value


class Envelope(str, Enum):
    """Amplitude envelope applied to generated audio."""

    SINE_SQUARED = "sine_squared"
    LINEAR = "linear"
    RECTANGULAR = "rectangular"


class MaskerKind(str, Enum):
    """Deterministic masker family for auditory-continuity constructions."""

    WHITE_NOISE = "white_noise"
    TONE = "tone"


@dataclass(frozen=True)
class DurationSeconds:
    """A strictly positive duration in seconds."""

    value: float

    def __post_init__(self) -> None:
        value = _finite(self.value, "duration")
        if value <= 0:
            raise ParameterValidationError(f"duration must be > 0, got {value}")
        object.__setattr__(self, "value", value)

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class FrequencyHz:
    """A strictly positive frequency in hertz."""

    value: float

    def __post_init__(self) -> None:
        value = _finite(self.value, "frequency")
        if value <= 0:
            raise ParameterValidationError(f"frequency must be > 0, got {value}")
        object.__setattr__(self, "value", value)

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class FrameRate:
    """A video frame rate in frames per second."""

    value: float

    def __post_init__(self) -> None:
        value = _finite(self.value, "frame rate")
        if not 1 <= value <= 240:
            raise ParameterValidationError(f"frame rate must be in [1, 240], got {value}")
        object.__setattr__(self, "value", value)

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class SampleRate:
    """An audio sample rate in samples per second."""

    value: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _integer(self.value, "sample rate", 1000, 384000))

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value


@dataclass(frozen=True)
class GrayscaleLevels:
    """The number of representable grayscale levels."""

    value: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _integer(self.value, "grayscale levels", 2, 256))


@dataclass(frozen=True)
class QuantizationLevels:
    """The number of output quantization buckets."""

    value: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _integer(self.value, "quantization levels", 2, 256))


@dataclass(frozen=True)
class SyncOffsetMs:
    """Audio/video timing offset in milliseconds."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _range(self.value, "sync offset", -10000.0, 10000.0))

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class SpatialOffset:
    """Normalized left/right spatial discrepancy."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _range(self.value, "spatial offset", -1.0, 1.0))

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True)
class LuminanceRange:
    """Inclusive lower and upper luminance bounds."""

    minimum: Luminance
    maximum: Luminance

    def __post_init__(self) -> None:
        if not isinstance(self.minimum, Luminance) or not isinstance(self.maximum, Luminance):
            raise ParameterValidationError("luminance range bounds must be Luminance values")
        if self.minimum.value > self.maximum.value:
            raise ParameterValidationError("luminance range minimum must not exceed maximum")


@dataclass(frozen=True)
class ImageConfig:
    """Canonical image-generation controls."""

    width: PixelDimension = PixelDimension(256)
    height: PixelDimension = PixelDimension(256)
    grayscale_levels: GrayscaleLevels = GrayscaleLevels(256)
    quantization_levels: QuantizationLevels = QuantizationLevels(256)
    luminance_range: LuminanceRange = LuminanceRange(Luminance(0.0), Luminance(1.0))
    mode: ColorMode = ColorMode.GRAYSCALE

    def __post_init__(self) -> None:
        try:
            if not isinstance(self.width, PixelDimension):
                object.__setattr__(self, "width", PixelDimension(self.width))
            if not isinstance(self.height, PixelDimension):
                object.__setattr__(self, "height", PixelDimension(self.height))
        except ParameterValidationError as exc:
            raise ParameterValidationError(f"image width/height: {exc}") from exc
        if not isinstance(self.grayscale_levels, GrayscaleLevels):
            raise ParameterValidationError("grayscale_levels must be GrayscaleLevels")
        if not isinstance(self.quantization_levels, QuantizationLevels):
            raise ParameterValidationError("quantization_levels must be QuantizationLevels")
        if not isinstance(self.luminance_range, LuminanceRange):
            raise ParameterValidationError("luminance_range must be LuminanceRange")
        if not isinstance(self.mode, ColorMode):
            try:
                object.__setattr__(self, "mode", ColorMode(self.mode))
            except ValueError as exc:
                raise ParameterValidationError(f"image mode must be 'L' or 'RGB', got {self.mode!r}") from exc


@dataclass(frozen=True)
class AudioConfig:
    """Canonical audio-generation controls."""

    sample_rate: SampleRate = SampleRate(8000)
    channels: ChannelCount = ChannelCount(1)
    duration: DurationSeconds = DurationSeconds(0.5)
    amplitude: Amplitude = Amplitude(0.5)
    phase: PhaseRadians = PhaseRadians(0.0)
    envelope: Envelope = Envelope.SINE_SQUARED

    def __post_init__(self) -> None:
        try:
            if not isinstance(self.channels, ChannelCount):
                object.__setattr__(self, "channels", ChannelCount(self.channels))
        except ParameterValidationError as exc:
            raise ParameterValidationError(f"audio channels: {exc}") from exc
        if not isinstance(self.sample_rate, SampleRate):
            raise ParameterValidationError("sample_rate must be SampleRate")
        if not isinstance(self.duration, DurationSeconds):
            raise ParameterValidationError("duration must be DurationSeconds")
        if not isinstance(self.amplitude, Amplitude):
            raise ParameterValidationError("amplitude must be Amplitude")
        if not isinstance(self.phase, PhaseRadians):
            raise ParameterValidationError("audio phase must be PhaseRadians")
        if not isinstance(self.envelope, Envelope):
            raise ParameterValidationError("audio envelope must be an Envelope")


@dataclass(frozen=True)
class VideoConfig:
    """Canonical video-generation controls."""

    width: PixelDimension = PixelDimension(256)
    height: PixelDimension = PixelDimension(256)
    frame_rate: FrameRate = FrameRate(12.0)
    frame_count: FrameCount = FrameCount(6)

    def __post_init__(self) -> None:
        try:
            if not isinstance(self.width, PixelDimension):
                object.__setattr__(self, "width", PixelDimension(self.width))
            if not isinstance(self.height, PixelDimension):
                object.__setattr__(self, "height", PixelDimension(self.height))
        except ParameterValidationError as exc:
            raise ParameterValidationError(f"video width/height: {exc}") from exc
        if not isinstance(self.frame_rate, FrameRate):
            raise ParameterValidationError("frame_rate must be FrameRate")
        try:
            if not isinstance(self.frame_count, FrameCount):
                object.__setattr__(self, "frame_count", FrameCount(self.frame_count))
        except ParameterValidationError as exc:
            raise ParameterValidationError(f"frame count: {exc}") from exc


@dataclass(frozen=True)
class AudiovisualConfig:
    """Shared timing controls for audio-visual stimuli."""

    audio: AudioConfig = AudioConfig()
    video: VideoConfig = VideoConfig()
    sync_offset: SyncOffsetMs = SyncOffsetMs(0.0)
    spatial_offset: SpatialOffset = SpatialOffset(0.0)

    def __post_init__(self) -> None:
        if not isinstance(self.audio, AudioConfig) or not isinstance(self.video, VideoConfig):
            raise ParameterValidationError("audio/video must be AudioConfig and VideoConfig")
        if not isinstance(self.sync_offset, SyncOffsetMs):
            raise ParameterValidationError("sync_offset must be SyncOffsetMs")
        if not isinstance(self.spatial_offset, SpatialOffset):
            raise ParameterValidationError("spatial_offset must be SpatialOffset")
        video_duration = self.video.frame_count / self.video.frame_rate.value
        if abs(video_duration - self.audio.duration.value) > 1.0 / self.video.frame_rate.value:
            raise ParameterValidationError(
                "audio and video durations must agree within one video frame; "
                f"got audio={self.audio.duration.value} and video={video_duration:.6f}"
            )


ConfigT = TypeVar("ConfigT", ImageConfig, AudioConfig, VideoConfig, AudiovisualConfig)


def _coerce(current: Any, value: Any) -> Any:
    """Coerce JSON-friendly scalar overrides using an existing typed default."""
    if isinstance(
        current,
        (
            ImageConfig,
            AudioConfig,
            VideoConfig,
            AudiovisualConfig,
            AudioEncoding,
            GifEncoding,
            VideoEncoding,
            MuxEncoding,
            CanonicalArchiveEncoding,
            OutputSpec,
        ),
    ):
        if not isinstance(value, dict):
            raise ParameterValidationError("nested configuration must be a JSON object")
        allowed = {field.name for field in fields(current)}
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise ParameterValidationError(f"unknown configuration field(s): {', '.join(unknown)}")
        updates = {
            field.name: _coerce(getattr(current, field.name), value[field.name])
            for field in fields(current)
            if field.name in value
        }
        return replace(current, **updates)
    if isinstance(current, (Envelope, MaskerKind, ColorMode, ChannelLayout, MediaFormat, PixelFormat, BackendKind)):
        try:
            return type(current)(value)
        except ValueError as exc:
            raise ParameterValidationError(f"unsupported enum value {value!r}") from exc
    if isinstance(
        current,
        (
            Normalized,
            Luminance,
            Amplitude,
            PhaseRadians,
            AngleDegrees,
            DurationSeconds,
            FrequencyHz,
            FrameRate,
            RationalFrameRate,
            TimestampSeconds,
            SampleRate,
            SampleCount,
            FrameIndex,
            GrayscaleLevels,
            QuantizationLevels,
            SyncOffsetMs,
            SpatialOffset,
        ),
    ):
        return type(current)(value)
    if isinstance(current, LuminanceRange):
        if not isinstance(value, dict):
            raise ParameterValidationError("luminance_range must be a JSON object")
        unknown = sorted(set(value) - {"minimum", "maximum"})
        if unknown:
            raise ParameterValidationError(f"unknown luminance_range field(s): {', '.join(unknown)}")
        return LuminanceRange(
            Luminance(value.get("minimum", current.minimum.value)),
            Luminance(value.get("maximum", current.maximum.value)),
        )
    if isinstance(current, tuple):
        if not isinstance(value, (list, tuple)):
            raise ParameterValidationError("tuple parameters must be JSON arrays")
        return tuple(value)
    return value


def replace_from_mapping(parameters: Any, mapping: dict[str, Any]) -> Any:
    """Return a validated parameter dataclass with JSON-friendly overrides."""
    if not hasattr(parameters, "__dataclass_fields__"):
        raise ParameterValidationError("parameters must be a dataclass instance")
    if not isinstance(mapping, dict):
        raise ParameterValidationError("parameter overrides must be a JSON object")
    allowed = {field.name for field in fields(parameters)}
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ParameterValidationError(f"unknown parameter field(s): {', '.join(unknown)}")
    updates = {
        field.name: _coerce(getattr(parameters, field.name), mapping[field.name])
        for field in fields(parameters)
        if field.name in mapping
    }
    return replace(parameters, **updates)
