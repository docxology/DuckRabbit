"""Boundary tests for DuckRabbit's strongly typed parameter objects."""

from __future__ import annotations

import pytest

from duckrabbit.errors import ParameterValidationError
from duckrabbit.generators import DuckRabbitParams, ShepardToneParams
from duckrabbit.parameters import (
    Amplitude,
    AngleDegrees,
    AudioConfig,
    AudiovisualConfig,
    ChannelCount,
    ColorMode,
    DurationSeconds,
    Envelope,
    FrameRate,
    FrameCount,
    FrequencyHz,
    GrayscaleLevels,
    ImageConfig,
    Luminance,
    LuminanceRange,
    MediaFormat,
    Normalized,
    OutputSpec,
    PcmBitDepth,
    PixelDimension,
    Seed,
    QuantizationLevels,
    PhaseRadians,
    RationalFrameRate,
    SampleRate,
    SpatialOffset,
    SyncOffsetMs,
    VideoConfig,
    replace_from_mapping,
)


@pytest.mark.parametrize(
    ("factory", "value"),
    [
        (Normalized, -0.1),
        (Luminance, 1.1),
        (Amplitude, float("nan")),
        (AngleDegrees, 91),
        (PhaseRadians, 2 * 3.141592653589793 + 0.1),
        (DurationSeconds, 0),
        (FrequencyHz, -1),
        (FrameRate, 241),
        (SampleRate, 999),
        (GrayscaleLevels, 1),
        (QuantizationLevels, 257),
        (SyncOffsetMs, 10001),
        (SpatialOffset, 2),
        (Normalized, True),
        (SampleRate, 1000.5),
        (DurationSeconds, "short"),
    ],
)
def test_scalar_types_reject_invalid_values(factory, value):
    with pytest.raises(ParameterValidationError):
        factory(value)


def test_luminance_range_and_image_config_validation():
    with pytest.raises(ParameterValidationError, match="minimum"):
        LuminanceRange(Luminance(0.9), Luminance(0.1))
    with pytest.raises(ParameterValidationError, match="width"):
        ImageConfig(width=7)
    with pytest.raises(ParameterValidationError, match="mode"):
        ImageConfig(mode="RGBA")
    with pytest.raises(ParameterValidationError, match="height"):
        ImageConfig(height=5000)


def test_audio_video_config_validation():
    with pytest.raises(ParameterValidationError, match="channels"):
        AudioConfig(channels=3)
    with pytest.raises(ParameterValidationError, match="frame count"):
        VideoConfig(frame_count=0)
    with pytest.raises(ParameterValidationError, match="video width"):
        VideoConfig(width=7)
    with pytest.raises(ParameterValidationError, match="durations"):
        AudiovisualConfig(audio=AudioConfig(duration=DurationSeconds(1.0)))
    with pytest.raises(ParameterValidationError, match="phase"):
        AudioConfig(phase=object())  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="envelope"):
        AudioConfig(envelope="unknown")  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="grayscale_levels"):
        ImageConfig(grayscale_levels=4)  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="quantization_levels"):
        ImageConfig(quantization_levels=4)  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="luminance_range"):
        ImageConfig(luminance_range=object())  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="sample_rate"):
        AudioConfig(sample_rate=4000)  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="duration"):
        AudioConfig(duration=0.5)  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="amplitude"):
        AudioConfig(amplitude=0.5)  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="frame_rate"):
        VideoConfig(frame_rate=12)  # type: ignore[arg-type]


def test_nested_json_overrides_are_revalidated():
    parameters = replace_from_mapping(
        DuckRabbitParams(),
        {"duck_weight": 0.75, "config": {"width": 64, "quantization_levels": 4}},
    )
    assert parameters.duck_weight.value == 0.75
    assert parameters.config.width == 64
    assert parameters.config.quantization_levels.value == 4
    audio = replace_from_mapping(
        ShepardToneParams(),
        {"config": {"phase": 1.0, "envelope": "linear"}},
    )
    assert audio.config.phase.value == 1.0
    assert audio.config.envelope is Envelope.LINEAR
    with pytest.raises(ParameterValidationError):
        replace_from_mapping(ShepardToneParams(), {"config": {"sample_rate": 500}})
    with pytest.raises(ParameterValidationError, match="unknown parameter"):
        replace_from_mapping(DuckRabbitParams(), {"duck_wieght": 0.75})
    with pytest.raises(ParameterValidationError, match="unknown configuration"):
        replace_from_mapping(DuckRabbitParams(), {"config": {"quantizaton_levels": 4}})
    from duckrabbit.generators import MissingFundamentalParams

    with pytest.raises(ParameterValidationError, match="JSON arrays"):
        replace_from_mapping(MissingFundamentalParams(), {"harmonics": 8})


def test_mapping_requires_dataclass_instance():
    with pytest.raises(ParameterValidationError, match="dataclass"):
        replace_from_mapping(object(), {})


def test_scalar_conversions_and_valid_boundaries():
    assert float(Normalized(0.25)) == 0.25
    assert float(Luminance(0.25)) == 0.25
    assert float(Amplitude(0.25)) == 0.25
    assert float(AngleDegrees(30)) == 30
    assert float(DurationSeconds(0.25)) == 0.25
    assert float(FrequencyHz(220)) == 220
    assert float(FrameRate(12)) == 12
    assert SampleRate(1000).value == 1000
    assert GrayscaleLevels(2).value == 2
    assert QuantizationLevels(256).value == 256
    assert SyncOffsetMs(-10).value == -10
    assert SpatialOffset(1).value == 1


def test_expanded_integer_enums_and_output_spec_are_typed_and_json_friendly():
    assert PixelDimension(32) == 32
    assert PixelDimension(32).value == 32
    assert ChannelCount(2).value == 2
    assert FrameCount(12).value == 12
    assert PcmBitDepth(24).value == 24
    assert (RationalFrameRate(30000, 1001).numerator, RationalFrameRate(30000, 1001).denominator) == (30000, 1001)
    assert (RationalFrameRate(60, 2).numerator, RationalFrameRate(60, 2).denominator) == (30, 1)
    assert Seed(-1).value == -1
    assert int(SampleRate(4000)) == 4000
    assert ImageConfig(width=32, mode="RGB").mode is ColorMode.RGB
    assert isinstance(AudioConfig(channels=2).channels, ChannelCount)
    output = replace_from_mapping(
        OutputSpec(),
        {"format": "wav", "audio_encoding": {"bit_depth": 24}, "include_manifest": False},
    )
    assert output.format is MediaFormat.WAV
    assert output.audio_encoding.bit_depth == 24
    assert output.include_manifest is False
    with pytest.raises(ParameterValidationError, match="PCM bit depth"):
        PcmBitDepth(12)
    with pytest.raises(ParameterValidationError, match="output format"):
        OutputSpec(format="flac")  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="bools"):
        OutputSpec(include_manifest=1)  # type: ignore[arg-type]
