"""Deterministic representative illusion generators and the default registry."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
import numpy as np

from .artifacts import AudioBuffer, AudiovisualTimeline, ImageFrame, VideoSequence
from .errors import ParameterValidationError
from .parameters import (
    AngleDegrees,
    Amplitude,
    AudioConfig,
    AudiovisualConfig,
    Envelope,
    FrequencyHz,
    ImageConfig,
    Luminance,
    MaskerKind,
    Normalized,
    SpatialOffset,
    VideoConfig,
)
from .registry import GeneratorSpec, IllusionRegistry
from .taxonomy import ImplementationStatus, get_taxonomy, validate_taxonomy_catalog


def _image_from_mask(mask: np.ndarray, config: ImageConfig) -> ImageFrame:
    return _image_from_values(1.0 - np.asarray(mask, dtype=np.float32), config)


def _image_from_values(values: np.ndarray, config: ImageConfig) -> ImageFrame:
    values = np.clip(np.asarray(values, dtype=np.float32), 0.0, 1.0)
    levels = min(config.grayscale_levels.value, config.quantization_levels.value)
    values = np.round(values * (levels - 1)) / (levels - 1)
    low = config.luminance_range.minimum.value
    high = config.luminance_range.maximum.value
    gray = low + values * (high - low)
    if config.mode == "RGB":
        return ImageFrame(np.repeat(gray[..., None], 3, axis=2), mode="RGB")
    return ImageFrame(gray, mode="L")


def _ellipse(x: np.ndarray, y: np.ndarray, cx: float, cy: float, rx: float, ry: float) -> np.ndarray:
    return (((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0).astype(np.float32)


def _duck_mask(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    body = _ellipse(x, y, 0.48, 0.58, 0.27, 0.19)
    head = _ellipse(x, y, 0.69, 0.40, 0.13, 0.13)
    beak = ((x >= 0.77) & (x <= 0.95) & (np.abs(y - 0.40) <= (0.95 - x) * 0.45)).astype(np.float32)
    return np.maximum.reduce((body, head, beak))


def _rabbit_mask(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    body = _ellipse(x, y, 0.52, 0.59, 0.25, 0.20)
    head = _ellipse(x, y, 0.32, 0.42, 0.13, 0.13)
    ear_one = _ellipse(x, y, 0.27, 0.19, 0.045, 0.17)
    ear_two = _ellipse(x, y, 0.37, 0.18, 0.045, 0.18)
    return np.maximum.reduce((body, head, ear_one, ear_two))


@dataclass(frozen=True)
class DuckRabbitParams:
    """Parameters for a continuous rabbit-to-duck ambiguous silhouette."""

    config: ImageConfig = ImageConfig()
    duck_weight: Normalized = Normalized(0.5)

    def __post_init__(self) -> None:
        if not isinstance(self.config, ImageConfig) or not isinstance(self.duck_weight, Normalized):
            raise TypeError("DuckRabbitParams requires ImageConfig and Normalized duck_weight")


def generate_duck_rabbit(parameters: DuckRabbitParams, *, seed: int = 0) -> ImageFrame:
    """Generate a deterministic ambiguous duck/rabbit silhouette."""
    del seed
    # Normalized float32 coordinate grids (broadcast row/column vectors)
    # avoid two full-size int64 mgrid allocations per request.
    x = np.arange(parameters.config.width, dtype=np.float32)[None, :] / max(parameters.config.width - 1, 1)
    y = np.arange(parameters.config.height, dtype=np.float32)[:, None] / max(parameters.config.height - 1, 1)
    rabbit = _rabbit_mask(x, y)
    duck = _duck_mask(x, y)
    weight = parameters.duck_weight.value
    return _image_from_mask((1.0 - weight) * rabbit + weight * duck, parameters.config)


def _segment_mask(
    x: np.ndarray,
    y: np.ndarray,
    start: tuple[float, float],
    end: tuple[float, float],
    width: float = 0.008,
) -> np.ndarray:
    """Return a binary mask for a line segment in normalized coordinates."""
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    denominator = dx * dx + dy * dy
    t = np.clip(((x - x1) * dx + (y - y1) * dy) / max(denominator, 1e-12), 0.0, 1.0)
    distance_squared = (x - (x1 + t * dx)) ** 2 + (y - (y1 + t * dy)) ** 2
    return (distance_squared <= width * width).astype(np.float32)


@dataclass(frozen=True)
class MullerLyerParams:
    """Parameters for two equal bars with inward or outward arrow wings."""

    config: ImageConfig = ImageConfig()
    line_length: Normalized = Normalized(0.48)
    arrow_length: Normalized = Normalized(0.10)
    arrow_angle: AngleDegrees = AngleDegrees(30.0)
    separation: Normalized = Normalized(0.25)
    tip_inward: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.config, ImageConfig):
            raise TypeError("MullerLyerParams.config must be ImageConfig")
        if not all(isinstance(value, Normalized) for value in (self.line_length, self.arrow_length, self.separation)):
            raise TypeError("MullerLyerParams lengths and separation must be Normalized")
        if not isinstance(self.arrow_angle, AngleDegrees):
            raise TypeError("MullerLyerParams.arrow_angle must be AngleDegrees")
        if type(self.tip_inward) is not bool:
            raise TypeError("MullerLyerParams.tip_inward must be bool")
        if self.line_length.value + 2.0 * self.arrow_length.value > 1.0:
            raise ParameterValidationError("line and arrow geometry must fit within normalized image width")


def generate_muller_lyer(parameters: MullerLyerParams, *, seed: int = 0) -> ImageFrame:
    """Generate equal-length bars with opposite arrow-wing configurations."""
    del seed
    height, width = parameters.config.height, parameters.config.width
    y, x = np.mgrid[0:height, 0:width]
    x = x / max(width - 1, 1)
    y = y / max(height - 1, 1)
    half_length = parameters.line_length.value / 2.0
    left, right = 0.5 - half_length, 0.5 + half_length
    y_values = (0.5 - parameters.separation.value / 2.0, 0.5 + parameters.separation.value / 2.0)
    angle = math.radians(parameters.arrow_angle.value)
    horizontal = parameters.arrow_length.value * math.cos(angle)
    vertical = parameters.arrow_length.value * math.sin(angle)
    values = np.zeros((height, width), dtype=np.float32)
    for y_value in y_values:
        values = np.maximum(values, _segment_mask(x, y, (left, y_value), (right, y_value)))
        for endpoint, side in ((left, 1.0), (right, -1.0)):
            direction = side if parameters.tip_inward else -side
            for wing_sign in (-1.0, 1.0):
                wing_end = (endpoint + direction * horizontal, y_value + wing_sign * vertical)
                values = np.maximum(values, _segment_mask(x, y, (endpoint, y_value), wing_end))
    return _image_from_values(values, parameters.config)


@dataclass(frozen=True)
class SimultaneousContrastParams:
    """Parameters for equal patches on unequal luminance surrounds."""

    config: ImageConfig = ImageConfig()
    center_luminance: Luminance = Luminance(0.5)
    left_surround: Luminance = Luminance(0.15)
    right_surround: Luminance = Luminance(0.85)
    patch_fraction: Normalized = Normalized(0.25)

    def __post_init__(self) -> None:
        if not isinstance(self.config, ImageConfig):
            raise TypeError("SimultaneousContrastParams.config must be ImageConfig")
        if not all(isinstance(value, Luminance) for value in (self.center_luminance, self.left_surround, self.right_surround)):
            raise TypeError("SimultaneousContrastParams luminances must be Luminance values")
        if not isinstance(self.patch_fraction, Normalized):
            raise TypeError("SimultaneousContrastParams.patch_fraction must be Normalized")


def generate_simultaneous_contrast(parameters: SimultaneousContrastParams, *, seed: int = 0) -> ImageFrame:
    """Generate two equal-luminance patches on contrasting surrounds."""
    del seed
    height, width = parameters.config.height, parameters.config.width
    image = np.empty((height, width), dtype=np.float32)
    midpoint = width // 2
    image[:, :midpoint] = parameters.left_surround.value
    image[:, midpoint:] = parameters.right_surround.value
    patch_height = max(2, int(height * parameters.patch_fraction.value))
    patch_width = max(2, int(width * parameters.patch_fraction.value))
    top = (height - patch_height) // 2
    left = (width // 4) - (patch_width // 2)
    right = (3 * width // 4) - (patch_width // 2)
    image[top : top + patch_height, left : left + patch_width] = parameters.center_luminance.value
    image[top : top + patch_height, right : right + patch_width] = parameters.center_luminance.value
    return _image_from_values(image, parameters.config)


@dataclass(frozen=True)
class ApparentMotionParams:
    """Parameters for an alternating bar-position video stimulus."""

    config: VideoConfig = VideoConfig()
    bar_width: Normalized = Normalized(0.12)
    displacement: Normalized = Normalized(0.55)

    def __post_init__(self) -> None:
        if not isinstance(self.config, VideoConfig):
            raise TypeError("ApparentMotionParams.config must be VideoConfig")
        if not isinstance(self.bar_width, Normalized) or not isinstance(self.displacement, Normalized):
            raise TypeError("ApparentMotionParams bar_width and displacement must be Normalized")


def generate_apparent_motion(parameters: ApparentMotionParams, *, seed: int = 0) -> VideoSequence:
    """Generate a deterministic sequence with alternating bar positions."""
    del seed
    # The bar only ever occupies two positions, so both masks are computed
    # once and reused; per-frame mgrid allocation would redo identical work.
    x = np.arange(parameters.config.width, dtype=np.float64)[None, :] / max(parameters.config.width - 1, 1)
    positions = (0.2, 0.2 + parameters.displacement.value)
    masks = tuple(
        np.broadcast_to((np.abs(x - position) <= parameters.bar_width.value / 2), (parameters.config.height, parameters.config.width)).astype(np.float32)
        for position in positions
    )
    frames = [
        _image_from_mask(masks[index % 2], ImageConfig(width=parameters.config.width, height=parameters.config.height))
        for index in range(parameters.config.frame_count)
    ]
    return VideoSequence(tuple(frames), parameters.config.frame_rate)


@dataclass(frozen=True)
class ShepardToneParams:
    """Parameters for an octave-spaced, continuously shifting tone."""

    config: AudioConfig = AudioConfig()
    base_frequency: FrequencyHz = FrequencyHz(220.0)
    sweep_octaves: float = 1.0
    partial_count: int = 8

    def __post_init__(self) -> None:
        if not isinstance(self.config, AudioConfig) or not isinstance(self.base_frequency, FrequencyHz):
            raise TypeError("ShepardToneParams requires AudioConfig and FrequencyHz")
        if not math.isfinite(self.sweep_octaves) or self.sweep_octaves < 0 or self.sweep_octaves > 4:
            raise ValueError("sweep_octaves must be in [0, 4]")
        if not isinstance(self.partial_count, int) or not 2 <= self.partial_count <= 16:
            raise ValueError("partial_count must be in [2, 16]")


def _envelope(time: np.ndarray, duration: float, config: AudioConfig) -> np.ndarray:
    """Return the configured deterministic amplitude envelope."""
    if config.envelope is Envelope.RECTANGULAR:
        return np.ones_like(time)
    if config.envelope is Envelope.LINEAR:
        return np.minimum(time / duration, (duration - time) / duration).clip(0.0, 1.0)
    return np.sin(np.pi * time / duration) ** 2


def _audio_from_mono(mono: np.ndarray, config: AudioConfig) -> AudioBuffer:
    mono = np.clip(np.asarray(mono, dtype=np.float32), -1.0, 1.0)
    if config.channels == 2:
        samples = np.repeat(mono[:, None], 2, axis=1)
    else:
        samples = mono[:, None]
    return AudioBuffer(samples, config.sample_rate)


def generate_shepard_tone(parameters: ShepardToneParams, *, seed: int = 0) -> AudioBuffer:
    """Generate overlapping octave partials with a smooth spectral envelope."""
    del seed
    sample_rate = parameters.config.sample_rate.value
    duration = parameters.config.duration.value
    time = np.arange(int(round(sample_rate * duration)), dtype=np.float64) / sample_rate
    signal = np.zeros_like(time)
    center = (parameters.partial_count - 1) / 2
    spread = max(parameters.partial_count / 3, 1.0)
    used_weights = 0.0
    nyquist = sample_rate / 2.0
    for index in range(parameters.partial_count):
        start_frequency = parameters.base_frequency.value * (2.0**index)
        end_frequency = start_frequency * (2.0**parameters.sweep_octaves)
        if end_frequency >= nyquist:
            continue
        weight = np.exp(-0.5 * ((index - center) / spread) ** 2)
        if parameters.sweep_octaves == 0.0:
            cycles = start_frequency * time
        else:
            cycles = (
                start_frequency
                * duration
                / (parameters.sweep_octaves * math.log(2.0))
                * (2.0 ** (parameters.sweep_octaves * time / duration) - 1.0)
            )
        signal += weight * np.sin(2.0 * np.pi * cycles + parameters.config.phase.value)
        used_weights += weight
    if used_weights == 0.0:
        raise ParameterValidationError("Shepard tone has no partial below the configured Nyquist frequency")
    envelope = _envelope(time, duration, parameters.config)
    signal = signal * envelope * parameters.config.amplitude.value / max(used_weights, 1.0)
    return _audio_from_mono(signal, parameters.config)


@dataclass(frozen=True)
class MissingFundamentalParams:
    """Parameters for a harmonic complex with its fundamental omitted."""

    config: AudioConfig = AudioConfig()
    fundamental: FrequencyHz = FrequencyHz(220.0)
    harmonics: tuple[int, ...] = (2, 3, 4, 5)

    def __post_init__(self) -> None:
        if not isinstance(self.config, AudioConfig) or not isinstance(self.fundamental, FrequencyHz):
            raise TypeError("MissingFundamentalParams requires AudioConfig and FrequencyHz")
        if not isinstance(self.harmonics, tuple) or not self.harmonics or any(
            type(harmonic) is not int or harmonic < 2 for harmonic in self.harmonics
        ):
            raise ValueError("harmonics must contain integers >= 2")


def generate_missing_fundamental(parameters: MissingFundamentalParams, *, seed: int = 0) -> AudioBuffer:
    """Generate harmonic partials without the fundamental component."""
    del seed
    sample_rate = parameters.config.sample_rate.value
    if parameters.fundamental.value * max(parameters.harmonics) >= sample_rate / 2.0:
        raise ParameterValidationError("harmonic complex exceeds the configured Nyquist frequency")
    duration = parameters.config.duration.value
    time = np.arange(int(round(sample_rate * duration)), dtype=np.float64) / sample_rate
    signal = sum(
        np.sin(2.0 * np.pi * parameters.fundamental.value * harmonic * time + parameters.config.phase.value) / harmonic
        for harmonic in parameters.harmonics
    )
    envelope = _envelope(time, duration, parameters.config)
    signal = signal * envelope * parameters.config.amplitude.value
    return _audio_from_mono(signal, parameters.config)


def _circle_mask(width: int, height: int, cx: float, cy: float, radius: float) -> np.ndarray:
    y, x = np.mgrid[0:height, 0:width]
    x = x / max(width - 1, 1)
    y = y / max(height - 1, 1)
    return (((x - cx) ** 2 + (y - cy) ** 2) <= radius**2).astype(np.float32)


def _make_beeps(config: AudioConfig, beep_count: int, *, frequency: float = 880.0) -> AudioBuffer:
    sample_rate = config.sample_rate.value
    duration = config.duration.value
    time = np.arange(int(round(sample_rate * duration)), dtype=np.float64) / sample_rate
    centers = (duration * 0.5,) if beep_count == 1 else (duration * 0.4, duration * 0.6)
    width = min(0.025, duration / 10.0)
    signal = np.zeros_like(time)
    for center in centers:
        window = np.maximum(0.0, 1.0 - np.abs(time - center) / width)
        signal += np.sin(2.0 * np.pi * frequency * time + config.phase.value) * window
    return _audio_from_mono(signal * _envelope(time, duration, config) * config.amplitude.value, config)


def _make_flash_video(config: VideoConfig, flash_count: int, *, x: float = 0.5) -> VideoSequence:
    frames: list[ImageFrame] = []
    flash_indices = {int(round((index + 1) * config.frame_count / (flash_count + 1))) for index in range(flash_count)}
    for index in range(config.frame_count):
        background = np.full((config.height, config.width), 0.08, dtype=np.float32)
        if index in flash_indices:
            background = np.full_like(background, 1.0)
        else:
            background = np.maximum(background, _circle_mask(config.width, config.height, x, 0.5, 0.04) * 0.25)
        frames.append(ImageFrame(background, mode="L"))
    return VideoSequence(tuple(frames), config.frame_rate)


@dataclass(frozen=True)
class SoundInducedFlashParams:
    """Parameters for a shared-clock flash and beep-count contrast."""

    config: AudiovisualConfig = AudiovisualConfig()
    beep_count: int = 2
    flash_count: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.config, AudiovisualConfig):
            raise TypeError("SoundInducedFlashParams.config must be AudiovisualConfig")
        if self.beep_count not in {1, 2}:
            raise ValueError("beep_count must be 1 or 2")
        if self.flash_count != 1:
            raise ValueError("the representative sound-induced-flash generator uses one flash")


def generate_sound_induced_flash(parameters: SoundInducedFlashParams, *, seed: int = 0) -> AudiovisualTimeline:
    """Generate a one-flash, one- or two-beep shared-clock stimulus."""
    del seed
    audio = _make_beeps(parameters.config.audio, parameters.beep_count)
    video = _make_flash_video(parameters.config.video, parameters.flash_count)
    return AudiovisualTimeline(
        audio,
        video,
        sync_offset=parameters.config.sync_offset,
        spatial_offset=parameters.config.spatial_offset,
        metadata={"beep_count": str(parameters.beep_count), "flash_count": str(parameters.flash_count)},
    )


@dataclass(frozen=True)
class VentriloquistParams:
    """Parameters for a visual marker paired with stereo-panned audio."""

    config: AudiovisualConfig = field(
        default_factory=lambda: AudiovisualConfig(audio=AudioConfig(channels=2), spatial_offset=SpatialOffset(0.35))
    )
    visual_offset: SpatialOffset | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.config, AudiovisualConfig):
            raise TypeError("VentriloquistParams.config must be AudiovisualConfig")
        if self.visual_offset is not None and not isinstance(self.visual_offset, SpatialOffset):
            raise TypeError("VentriloquistParams.visual_offset must be SpatialOffset")
        if self.config.audio.channels != 2:
            raise ParameterValidationError("ventriloquist stimuli require stereo audio (channels=2)")


def generate_ventriloquist(parameters: VentriloquistParams, *, seed: int = 0) -> AudiovisualTimeline:
    """Generate a visual-location and audio-location discrepancy."""
    del seed
    config = parameters.config
    audio_config = config.audio
    sample_rate = audio_config.sample_rate.value
    duration = audio_config.duration.value
    time = np.arange(int(round(sample_rate * duration)), dtype=np.float64) / sample_rate
    tone = np.sin(2.0 * np.pi * 440.0 * time + audio_config.phase.value) * _envelope(time, duration, audio_config) * audio_config.amplitude.value
    effective_offset = parameters.visual_offset if parameters.visual_offset is not None else config.spatial_offset
    pan = (effective_offset.value + 1.0) / 2.0
    left = tone * np.sqrt(1.0 - pan)
    right = tone * np.sqrt(pan)
    audio = AudioBuffer(np.column_stack((left, right)), audio_config.sample_rate)
    frames = []
    x = 0.5 + effective_offset.value * 0.25
    for index in range(config.video.frame_count):
        drift = 0.02 * np.sin(2.0 * np.pi * index / config.video.frame_count)
        frames.append(ImageFrame(_circle_mask(config.video.width, config.video.height, x + drift, 0.5, 0.06)))
    video = VideoSequence(tuple(frames), config.video.frame_rate)
    return AudiovisualTimeline(
        audio,
        video,
        sync_offset=config.sync_offset,
        spatial_offset=effective_offset,
        metadata={"audio_pan": f"{pan:.6f}", "visual_offset": f"{effective_offset.value:.6f}"},
    )


@dataclass(frozen=True)
class PoggendorffParams:
    """Parameters for an occluded-line alignment stimulus."""

    config: ImageConfig = ImageConfig()
    line_angle: AngleDegrees = AngleDegrees(28.0)
    occluder_fraction: Normalized = Normalized(0.18)

    def __post_init__(self) -> None:
        if not isinstance(self.config, ImageConfig) or not isinstance(self.line_angle, AngleDegrees):
            raise TypeError("PoggendorffParams requires ImageConfig and AngleDegrees")
        if not isinstance(self.occluder_fraction, Normalized) or self.occluder_fraction.value <= 0:
            raise ParameterValidationError("occluder_fraction must be > 0")


def generate_poggendorff(parameters: PoggendorffParams, *, seed: int = 0) -> ImageFrame:
    """Generate two diagonal segments separated by a central occluder."""
    del seed
    height, width = parameters.config.height, parameters.config.width
    y, x = np.mgrid[0:height, 0:width]
    x = x / max(width - 1, 1)
    y = y / max(height - 1, 1)
    values = np.ones((height, width), dtype=np.float32)
    angle = math.radians(parameters.line_angle.value)
    slope = math.tan(angle)
    center_y = 0.52
    left_end = (0.43, center_y - slope * (0.43 - 0.12))
    right_start = (0.57, center_y + slope * (0.57 - 0.43))
    line_width = 0.008
    values = np.minimum(values, 1.0 - _segment_mask(x, y, (0.08, left_end[1] + slope * 0.08), left_end, line_width))
    values = np.minimum(values, 1.0 - _segment_mask(x, y, right_start, (0.92, right_start[1] + slope * (0.92 - 0.57)), line_width))
    occluder_left = 0.5 - parameters.occluder_fraction.value / 2.0
    occluder_right = 0.5 + parameters.occluder_fraction.value / 2.0
    values[(x >= occluder_left) & (x <= occluder_right)] = 1.0
    return _image_from_values(values, parameters.config)


@dataclass(frozen=True)
class PonzoParams:
    """Parameters for converging rails and equal target bars."""

    config: ImageConfig = ImageConfig()
    convergence: Normalized = Normalized(0.18)
    target_separation: Normalized = Normalized(0.28)

    def __post_init__(self) -> None:
        if not isinstance(self.config, ImageConfig):
            raise TypeError("PonzoParams.config must be ImageConfig")
        if not isinstance(self.convergence, Normalized) or not isinstance(self.target_separation, Normalized):
            raise TypeError("PonzoParams geometry must be Normalized")
        if self.target_separation.value <= 0:
            raise ParameterValidationError("target_separation must be > 0")


def generate_ponzo(parameters: PonzoParams, *, seed: int = 0) -> ImageFrame:
    """Generate perspective rails with two equal-length horizontal targets."""
    del seed
    height, width = parameters.config.height, parameters.config.width
    y, x = np.mgrid[0:height, 0:width]
    x = x / max(width - 1, 1)
    y = y / max(height - 1, 1)
    values = np.ones((height, width), dtype=np.float32)
    rail_width = 0.008
    values = np.minimum(values, 1.0 - _segment_mask(x, y, (0.12, 0.95), (0.5 - parameters.convergence.value, 0.12), rail_width))
    values = np.minimum(values, 1.0 - _segment_mask(x, y, (0.88, 0.95), (0.5 + parameters.convergence.value, 0.12), rail_width))
    for y_value in (0.5 - parameters.target_separation.value / 2.0, 0.5 + parameters.target_separation.value / 2.0):
        values = np.minimum(values, 1.0 - _segment_mask(x, y, (0.32, y_value), (0.68, y_value), 0.01))
    return _image_from_values(values, parameters.config)


@dataclass(frozen=True)
class KanizsaParams:
    """Parameters for four inducers supporting an illusory triangle."""

    config: ImageConfig = ImageConfig()
    inducer_radius: Normalized = Normalized(0.10)
    gap_fraction: Normalized = Normalized(0.30)

    def __post_init__(self) -> None:
        if not isinstance(self.config, ImageConfig):
            raise TypeError("KanizsaParams.config must be ImageConfig")
        if not isinstance(self.inducer_radius, Normalized) or not isinstance(self.gap_fraction, Normalized):
            raise TypeError("KanizsaParams geometry must be Normalized")
        if self.inducer_radius.value <= 0:
            raise ParameterValidationError("inducer_radius must be > 0")


def generate_kanizsa_triangle(parameters: KanizsaParams, *, seed: int = 0) -> ImageFrame:
    """Generate three gap-oriented circular inducers around a blank triangle."""
    del seed
    height, width = parameters.config.height, parameters.config.width
    y, x = np.mgrid[0:height, 0:width]
    x = x / max(width - 1, 1)
    y = y / max(height - 1, 1)
    values = np.ones((height, width), dtype=np.float32)
    centers = ((0.5, 0.20, -math.pi / 2), (0.25, 0.72, math.pi / 6), (0.75, 0.72, 5 * math.pi / 6))
    for cx, cy, gap_angle in centers:
        disk = ((x - cx) ** 2 + (y - cy) ** 2 <= parameters.inducer_radius.value**2)
        orientation = np.arctan2(y - cy, x - cx)
        delta = np.abs(np.angle(np.exp(1j * (orientation - gap_angle))))
        inducer = disk & (delta > math.pi * parameters.gap_fraction.value / 2.0)
        values[inducer] = 0.0
    return _image_from_values(values, parameters.config)


@dataclass(frozen=True)
class EbbinghausParams:
    """Parameters for equal centers surrounded by unequal context circles."""

    config: ImageConfig = ImageConfig()
    center_radius: Normalized = Normalized(0.08)
    left_context_radius: Normalized = Normalized(0.045)
    right_context_radius: Normalized = Normalized(0.15)
    context_count: int = 8

    def __post_init__(self) -> None:
        if not isinstance(self.config, ImageConfig):
            raise TypeError("EbbinghausParams.config must be ImageConfig")
        if not all(isinstance(value, Normalized) for value in (self.center_radius, self.left_context_radius, self.right_context_radius)):
            raise TypeError("EbbinghausParams radii must be Normalized")
        if type(self.context_count) is not int or not 4 <= self.context_count <= 16:
            raise ValueError("context_count must be in [4, 16]")


def generate_ebbinghaus(parameters: EbbinghausParams, *, seed: int = 0) -> ImageFrame:
    """Generate two equal centers with small and large contextual rings."""
    del seed
    height, width = parameters.config.height, parameters.config.width
    y, x = np.mgrid[0:height, 0:width]
    x = x / max(width - 1, 1)
    y = y / max(height - 1, 1)
    values = np.full((height, width), 0.45, dtype=np.float32)
    for center_x, context_radius in ((0.30, parameters.left_context_radius.value), (0.70, parameters.right_context_radius.value)):
        center = _ellipse(x, y, center_x, 0.5, parameters.center_radius.value, parameters.center_radius.value)
        values[center > 0] = 0.65
        for index in range(parameters.context_count):
            angle = 2.0 * math.pi * index / parameters.context_count
            cx = center_x + 0.19 * math.cos(angle)
            cy = 0.5 + 0.19 * math.sin(angle)
            context = _ellipse(x, y, cx, cy, context_radius, context_radius)
            values[context > 0] = 0.15
    return _image_from_values(values, parameters.config)


@dataclass(frozen=True)
class ZollnerParams:
    """Parameters for a crossing-line orientation construction.

    The generator fixes the long lines to vertical and varies the short
    inducer angle.  This is an engineering parameterization of the classic
    family; the raster does not assert an observer's orientation judgment.
    """

    config: ImageConfig = ImageConfig()
    line_count: int = 4
    inducer_count: int = 5
    line_spacing: Normalized = Normalized(0.16)
    inducer_spacing: Normalized = Normalized(0.14)
    inducer_angle: AngleDegrees = AngleDegrees(30.0)
    inducer_length: Normalized = Normalized(0.10)

    def __post_init__(self) -> None:
        if not isinstance(self.config, ImageConfig):
            raise TypeError("ZollnerParams.config must be ImageConfig")
        if type(self.line_count) is not int or not 2 <= self.line_count <= 8:
            raise ParameterValidationError("line_count must be in [2, 8]")
        if type(self.inducer_count) is not int or not 2 <= self.inducer_count <= 16:
            raise ParameterValidationError("inducer_count must be in [2, 16]")
        if not all(isinstance(value, Normalized) for value in (self.line_spacing, self.inducer_spacing, self.inducer_length)):
            raise TypeError("Zollner spacing and length fields must be Normalized")
        if not isinstance(self.inducer_angle, AngleDegrees) or not 0.0 < self.inducer_angle.value < 90.0:
            raise ParameterValidationError("inducer_angle must be strictly between 0 and 90 degrees")
        if self.line_spacing.value <= 0 or self.inducer_spacing.value <= 0 or self.inducer_length.value <= 0:
            raise ParameterValidationError("Zollner spacing and length must be > 0")
        if 0.5 + (self.line_count - 1) * self.line_spacing.value / 2.0 > 0.92:
            raise ParameterValidationError("Zollner line field must fit within normalized width")
        if 0.14 + (self.inducer_count - 1) * self.inducer_spacing.value > 0.86:
            raise ParameterValidationError("Zollner inducer field must fit within normalized height")


def generate_zollner(parameters: ZollnerParams, *, seed: int = 0) -> ImageFrame:
    """Generate vertical long lines crossed by short oblique inducers."""
    del seed
    height, width = parameters.config.height, parameters.config.width
    y, x = np.mgrid[0:height, 0:width]
    x = x / max(width - 1, 1)
    y = y / max(height - 1, 1)
    values = np.ones((height, width), dtype=np.float32)
    center = 0.5
    line_positions = center + (np.arange(parameters.line_count) - (parameters.line_count - 1) / 2.0) * parameters.line_spacing.value
    for line_x in line_positions:
        values = np.minimum(values, 1.0 - _segment_mask(x, y, (line_x, 0.08), (line_x, 0.92), 0.006))
        for index in range(parameters.inducer_count):
            y_center = 0.14 + index * parameters.inducer_spacing.value
            half = parameters.inducer_length.value / 2.0
            angle = math.radians(parameters.inducer_angle.value)
            dx, dy = half * math.cos(angle), half * math.sin(angle)
            values = np.minimum(values, 1.0 - _segment_mask(x, y, (line_x - dx, y_center - dy), (line_x + dx, y_center + dy), 0.006))
    return _image_from_values(values, parameters.config)


@dataclass(frozen=True)
class AuditoryContinuityParams:
    """Parameters for an interrupted tone with a deterministic masker."""

    config: AudioConfig = AudioConfig()
    carrier_frequency: FrequencyHz = FrequencyHz(440.0)
    masker_frequency: FrequencyHz = FrequencyHz(660.0)
    interruption_fraction: Normalized = Normalized(0.25)
    masker_amplitude: Amplitude = Amplitude(0.35)
    masker_kind: MaskerKind = MaskerKind.WHITE_NOISE

    def __post_init__(self) -> None:
        if not isinstance(self.config, AudioConfig):
            raise TypeError("AuditoryContinuityParams.config must be AudioConfig")
        if not isinstance(self.carrier_frequency, FrequencyHz) or not isinstance(self.masker_frequency, FrequencyHz):
            raise TypeError("auditory continuity frequencies must be FrequencyHz")
        if not isinstance(self.interruption_fraction, Normalized) or not 0.0 < self.interruption_fraction.value < 1.0:
            raise ParameterValidationError("interruption_fraction must be strictly between 0 and 1")
        if not isinstance(self.masker_amplitude, Amplitude) or self.masker_amplitude.value <= 0:
            raise ParameterValidationError("masker_amplitude must be > 0")
        if not isinstance(self.masker_kind, MaskerKind):
            try:
                object.__setattr__(self, "masker_kind", MaskerKind(self.masker_kind))
            except ValueError as exc:
                raise ParameterValidationError("masker_kind must be white_noise or tone") from exc
        nyquist = self.config.sample_rate.value / 2.0
        if self.carrier_frequency.value >= nyquist or self.masker_frequency.value >= nyquist:
            raise ParameterValidationError("carrier and masker frequencies must be below Nyquist")


def generate_auditory_continuity(parameters: AuditoryContinuityParams, *, seed: int = 0) -> AudioBuffer:
    """Generate an interrupted carrier and calibrated deterministic masker.

    The output encodes a physical interruption/masking relation only; it does
    not establish that a listener hears a continuous signal.
    """
    config = parameters.config
    sample_rate = config.sample_rate.value
    total_samples = int(round(sample_rate * config.duration.value))
    time = np.arange(total_samples, dtype=np.float64) / sample_rate
    signal = np.sin(2.0 * np.pi * parameters.carrier_frequency.value * time + config.phase.value)
    gap_width = max(1, int(round(total_samples * parameters.interruption_fraction.value)))
    gap_start = max(0, (total_samples - gap_width) // 2)
    gap_stop = min(total_samples, gap_start + gap_width)
    rng = np.random.default_rng(int(seed) % (2**64))
    if parameters.masker_kind is MaskerKind.WHITE_NOISE:
        masker = rng.standard_normal(total_samples)
        peak = float(np.max(np.abs(masker))) or 1.0
        masker = masker / peak
    else:
        masker = np.sin(2.0 * np.pi * parameters.masker_frequency.value * time + config.phase.value)
    signal[gap_start:gap_stop] = masker[gap_start:gap_stop] * parameters.masker_amplitude.value
    envelope = _envelope(time, config.duration.value, config)
    signal *= envelope * config.amplitude.value
    return _audio_from_mono(signal, config)


@dataclass(frozen=True)
class TritoneParadoxParams:
    """Parameters for a pair of octave-complex tones separated by a tritone."""

    config: AudioConfig = AudioConfig()
    base_frequency: FrequencyHz = FrequencyHz(220.0)
    partial_count: int = 4
    interval_semitones: int = 6

    def __post_init__(self) -> None:
        if not isinstance(self.config, AudioConfig) or not isinstance(self.base_frequency, FrequencyHz):
            raise TypeError("TritoneParadoxParams requires AudioConfig and FrequencyHz")
        if type(self.partial_count) is not int or not 2 <= self.partial_count <= 10:
            raise ValueError("partial_count must be in [2, 10]")
        if self.interval_semitones != 6:
            raise ValueError("the representative tritone interval is six semitones")
        if self.base_frequency.value * (2.0 ** (self.interval_semitones / 12.0)) * (2 ** (self.partial_count - 1)) >= self.config.sample_rate.value / 2.0:
            raise ParameterValidationError("tritone complex exceeds the configured Nyquist frequency")


def generate_tritone_paradox(parameters: TritoneParadoxParams, *, seed: int = 0) -> AudioBuffer:
    """Generate two temporally adjacent Shepard-like tritone complexes."""
    del seed
    sample_rate = parameters.config.sample_rate.value
    half_duration = parameters.config.duration.value / 2.0
    time = np.arange(int(round(sample_rate * parameters.config.duration.value)), dtype=np.float64) / sample_rate
    signal = np.zeros_like(time)
    semitone_ratio = 2.0 ** (parameters.interval_semitones / 12.0)
    for index in range(parameters.partial_count):
        frequency = parameters.base_frequency.value * (2.0**index)
        weight = math.exp(-0.5 * ((index - (parameters.partial_count - 1) / 2.0) / max(parameters.partial_count / 3.0, 1.0)) ** 2)
        first = time < half_duration
        local_time = np.where(first, time, time - half_duration)
        local_frequency = np.where(first, frequency, frequency * semitone_ratio)
        signal += weight * np.sin(2.0 * np.pi * local_frequency * local_time + parameters.config.phase.value)
    signal *= _envelope(time, parameters.config.duration.value, parameters.config)
    signal *= parameters.config.amplitude.value / max(parameters.partial_count, 1)
    return _audio_from_mono(signal, parameters.config)


@dataclass(frozen=True)
class OctaveIllusionParams:
    """Parameters for alternating dichotic high and low tones."""

    config: AudioConfig = field(default_factory=lambda: AudioConfig(channels=2))
    low_frequency: FrequencyHz = FrequencyHz(220.0)
    high_frequency: FrequencyHz = FrequencyHz(440.0)
    cycles: int = 4

    def __post_init__(self) -> None:
        if not isinstance(self.config, AudioConfig) or not isinstance(self.low_frequency, FrequencyHz) or not isinstance(self.high_frequency, FrequencyHz):
            raise TypeError("OctaveIllusionParams requires AudioConfig and frequencies")
        if self.config.channels != 2:
            raise ParameterValidationError("octave illusion requires stereo audio")
        if self.high_frequency.value != 2.0 * self.low_frequency.value:
            raise ParameterValidationError("high_frequency must be one octave above low_frequency")
        if type(self.cycles) is not int or not 1 <= self.cycles <= 16:
            raise ValueError("cycles must be in [1, 16]")


def generate_octave_illusion(parameters: OctaveIllusionParams, *, seed: int = 0) -> AudioBuffer:
    """Generate alternating high/low tones in opposite stereo channels."""
    del seed
    sample_rate = parameters.config.sample_rate.value
    total_samples = int(round(sample_rate * parameters.config.duration.value))
    segment_count = parameters.cycles * 2
    boundaries = np.linspace(0, total_samples, segment_count + 1, dtype=int)
    samples = np.zeros((total_samples, 2), dtype=np.float32)
    for index in range(segment_count):
        start, stop = int(boundaries[index]), int(boundaries[index + 1])
        local = np.arange(stop - start, dtype=np.float64) / sample_rate
        high = index % 2 == 0
        left_frequency = parameters.high_frequency.value if high else parameters.low_frequency.value
        right_frequency = parameters.low_frequency.value if high else parameters.high_frequency.value
        samples[start:stop, 0] = np.sin(2.0 * np.pi * left_frequency * local + parameters.config.phase.value)
        samples[start:stop, 1] = np.sin(2.0 * np.pi * right_frequency * local + parameters.config.phase.value)
    samples *= (_envelope(np.arange(total_samples, dtype=np.float64) / sample_rate, parameters.config.duration.value, parameters.config) * parameters.config.amplitude.value)[:, None]
    return AudioBuffer(samples, parameters.config.sample_rate)


@dataclass(frozen=True)
class TemporalVentriloquismParams:
    """Parameters for a visual event paired with a timed audio click."""

    config: AudiovisualConfig = AudiovisualConfig()
    click_frequency: FrequencyHz = FrequencyHz(1200.0)

    def __post_init__(self) -> None:
        if not isinstance(self.config, AudiovisualConfig) or not isinstance(self.click_frequency, FrequencyHz):
            raise TypeError("TemporalVentriloquismParams requires AudiovisualConfig and FrequencyHz")
        if self.click_frequency.value >= self.config.audio.sample_rate.value / 2.0:
            raise ParameterValidationError("click_frequency must be below the audio Nyquist frequency")


def generate_temporal_ventriloquism(parameters: TemporalVentriloquismParams, *, seed: int = 0) -> AudiovisualTimeline:
    """Generate one visual event and one audio click on a shared clock."""
    del seed
    config = parameters.config
    sample_rate = config.audio.sample_rate.value
    duration = config.audio.duration.value
    time = np.arange(int(round(sample_rate * duration)), dtype=np.float64) / sample_rate
    center = duration / 2.0
    click_width = min(0.01, duration / 20.0)
    window = np.maximum(0.0, 1.0 - np.abs(time - center) / click_width)
    audio = _audio_from_mono(np.sin(2.0 * np.pi * parameters.click_frequency.value * time) * window * config.audio.amplitude.value, config.audio)
    video = _make_flash_video(config.video, flash_count=1)
    return AudiovisualTimeline(
        audio,
        video,
        sync_offset=config.sync_offset,
        spatial_offset=config.spatial_offset,
        metadata={"click_frequency_hz": f"{parameters.click_frequency.value:.6f}", "event": "single_visual_flash_single_audio_click"},
    )


_IMPLEMENTED_GENERATORS = {
        "visual.duck_rabbit": DuckRabbitParams,
        "visual.muller_lyer": MullerLyerParams,
        "visual.simultaneous_contrast": SimultaneousContrastParams,
        "visual.apparent_motion": ApparentMotionParams,
        "visual.poggendorff": PoggendorffParams,
        "visual.ponzo": PonzoParams,
        "visual.kanizsa_triangle": KanizsaParams,
        "visual.ebbinghaus": EbbinghausParams,
        "visual.zollner": ZollnerParams,
        "audio.shepard_tone": ShepardToneParams,
        "audio.missing_fundamental": MissingFundamentalParams,
        "audio.tritone_paradox": TritoneParadoxParams,
        "audio.octave_illusion": OctaveIllusionParams,
        "audio.auditory_continuity": AuditoryContinuityParams,
        "audiovisual.sound_induced_flash": SoundInducedFlashParams,
        "audiovisual.ventriloquist": VentriloquistParams,
        "audiovisual.temporal_ventriloquism": TemporalVentriloquismParams,
    }

_GENERATOR_FUNCTIONS = {
        "visual.duck_rabbit": generate_duck_rabbit,
        "visual.muller_lyer": generate_muller_lyer,
        "visual.simultaneous_contrast": generate_simultaneous_contrast,
        "visual.apparent_motion": generate_apparent_motion,
        "visual.poggendorff": generate_poggendorff,
        "visual.ponzo": generate_ponzo,
        "visual.kanizsa_triangle": generate_kanizsa_triangle,
        "visual.ebbinghaus": generate_ebbinghaus,
        "visual.zollner": generate_zollner,
        "audio.shepard_tone": generate_shepard_tone,
        "audio.missing_fundamental": generate_missing_fundamental,
        "audio.tritone_paradox": generate_tritone_paradox,
        "audio.octave_illusion": generate_octave_illusion,
        "audio.auditory_continuity": generate_auditory_continuity,
        "audiovisual.sound_induced_flash": generate_sound_induced_flash,
        "audiovisual.ventriloquist": generate_ventriloquist,
        "audiovisual.temporal_ventriloquism": generate_temporal_ventriloquism,
    }


def default_parameters(illusion_id: str) -> object:
    """Return defaults for one implemented generator."""
    try:
        return _IMPLEMENTED_GENERATORS[illusion_id]()
    except KeyError as exc:
        raise KeyError(f"no implemented defaults for {illusion_id}") from exc


def build_default_registry() -> IllusionRegistry:
    """Build a fresh registry containing all implemented v1 generators."""
    registry = IllusionRegistry()
    validate_taxonomy_catalog()
    for illusion_id, parameter_type in _IMPLEMENTED_GENERATORS.items():
        taxonomy = get_taxonomy(illusion_id)
        if taxonomy.implementation_status is not ImplementationStatus.IMPLEMENTED:
            raise ValueError(f"registry generator {illusion_id} is not marked implemented")
        registry.register(GeneratorSpec(illusion_id, parameter_type, _GENERATOR_FUNCTIONS[illusion_id], taxonomy))
    registry.freeze()
    return registry


default_registry = build_default_registry()
