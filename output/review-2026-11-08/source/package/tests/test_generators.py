"""No-mock tests for generators, artifacts, registry, and taxonomy."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import duckrabbit
from duckrabbit.artifacts import AudioBuffer, AudiovisualTimeline, ImageFrame, VideoSequence
from duckrabbit.errors import ParameterValidationError, UnknownIllusionError
from duckrabbit.generators import (
    ApparentMotionParams,
    DuckRabbitParams,
    MissingFundamentalParams,
    MullerLyerParams,
    ShepardToneParams,
    SoundInducedFlashParams,
    VentriloquistParams,
    AuditoryContinuityParams,
    OctaveIllusionParams,
    ZollnerParams,
    default_parameters,
)
from duckrabbit.parameters import (
    AudioConfig,
    AudiovisualConfig,
    DurationSeconds,
    ImageConfig,
    Normalized,
    Envelope,
    PhaseRadians,
    SampleRate,
    SpatialOffset,
    VideoConfig,
)
from duckrabbit.registry import generate as registry_generate
from duckrabbit.taxonomy import EvidenceStatus, ImplementationStatus, taxonomy_entries


def test_all_implemented_catalog_entries_have_specs():
    entries = taxonomy_entries(include_unimplemented=False)
    specs = duckrabbit.default_registry.list()
    assert {entry.illusion_id for entry in entries} == {spec.illusion_id for spec in specs}
    assert all(spec.taxonomy.implementation_status is ImplementationStatus.IMPLEMENTED for spec in specs)
    assert {entry.implementation_status for entry in taxonomy_entries()} == {
        ImplementationStatus.IMPLEMENTED,
        ImplementationStatus.INPUT_REQUIRED,
    }
    assert all(isinstance(entry.evidence_status, EvidenceStatus) for entry in taxonomy_entries())
    assert all(entry.evidence_references for entry in taxonomy_entries())
    bibliography = (Path(__file__).parents[1] / "docs" / "manuscript" / "references.bib").read_text(encoding="utf-8")
    assert all(f"{{{reference}," in bibliography for entry in taxonomy_entries() for reference in entry.evidence_references)
    assert duckrabbit.default_registry.status_counts() == {
        status: sum(entry.implementation_status is status for entry in taxonomy_entries())
        for status in ImplementationStatus
    }


@pytest.mark.parametrize("illusion_id", [spec.illusion_id for spec in duckrabbit.default_registry.list()])
def test_default_generators_are_deterministic_and_well_formed(illusion_id):
    first = duckrabbit.generate(illusion_id)
    second = duckrabbit.generate(illusion_id)
    assert type(first) is type(second)
    if isinstance(first, ImageFrame):
        np.testing.assert_array_equal(first.pixels, second.pixels)
        assert first.pixels.min() >= 0 and first.pixels.max() <= 1
    elif isinstance(first, AudioBuffer):
        np.testing.assert_array_equal(first.samples, second.samples)
        assert first.samples.shape[1] in {1, 2}
    elif isinstance(first, VideoSequence):
        assert len(first.frames) == len(second.frames)
        for frame_a, frame_b in zip(first.frames, second.frames):
            np.testing.assert_array_equal(frame_a.pixels, frame_b.pixels)
    else:
        assert isinstance(first, AudiovisualTimeline)
        np.testing.assert_array_equal(first.audio.samples, second.audio.samples)
        assert first.video.duration_seconds == second.video.duration_seconds


def test_visual_parameters_expose_grayscale_and_quantization_controls():
    frame = duckrabbit.generate(
        "visual.duck_rabbit",
        DuckRabbitParams(config=ImageConfig(width=32, height=24, grayscale_levels=duckrabbit.GrayscaleLevels(8), quantization_levels=duckrabbit.QuantizationLevels(4))),
    )
    assert isinstance(frame, ImageFrame)
    assert np.unique(frame.pixels).size <= 4
    rgb = duckrabbit.generate(
        "visual.duck_rabbit",
        DuckRabbitParams(config=ImageConfig(width=32, height=24, mode="RGB")),
    )
    assert isinstance(rgb, ImageFrame)
    assert rgb.mode.value == "RGB"
    assert rgb.pixels.shape == (24, 32, 3)


def test_audio_generators_honor_signed_seeds_controls_and_remainders():
    continuity = duckrabbit.generate("audio.auditory_continuity", seed=-1)
    assert isinstance(continuity, AudioBuffer)
    assert np.array_equal(
        continuity.samples,
        duckrabbit.generate("audio.auditory_continuity", seed=-1).samples,
    )
    config = AudioConfig(
        duration=DurationSeconds(0.5001),
        amplitude=duckrabbit.Amplitude(0.5),
        phase=PhaseRadians(0.5),
        envelope=Envelope.RECTANGULAR,
        channels=2,
    )
    octave = duckrabbit.generate("audio.octave_illusion", OctaveIllusionParams(config=config))
    assert isinstance(octave, AudioBuffer)
    assert np.any(np.abs(octave.samples[-1]) > 0)
    assert octave.samples[0, 0] == pytest.approx(np.sin(0.5) * 0.5, abs=1e-6)


def test_ventriloquist_accepts_an_explicit_zero_spatial_offset():
    config = AudiovisualConfig(
        audio=AudioConfig(channels=2),
        spatial_offset=SpatialOffset(0.0),
    )
    artifact = duckrabbit.generate("audiovisual.ventriloquist", VentriloquistParams(config=config))
    assert isinstance(artifact, AudiovisualTimeline)
    assert artifact.spatial_offset.value == 0.0


def test_muller_lyer_is_a_real_registered_visual_generator():
    inward = duckrabbit.generate("visual.muller_lyer", MullerLyerParams(tip_inward=True))
    outward = duckrabbit.generate("visual.muller_lyer", MullerLyerParams(tip_inward=False))
    assert isinstance(inward, ImageFrame)
    assert inward.pixels.shape == outward.pixels.shape
    assert np.count_nonzero(inward.pixels != outward.pixels) > 0
    with pytest.raises(ParameterValidationError, match="geometry"):
        MullerLyerParams(line_length=Normalized(0.9), arrow_length=Normalized(0.1))


def test_audio_generators_respect_sample_rate_and_channels():
    config = AudioConfig(sample_rate=SampleRate(4000), channels=2)
    shepard = duckrabbit.generate("audio.shepard_tone", ShepardToneParams(config=config))
    missing = duckrabbit.generate("audio.missing_fundamental", MissingFundamentalParams(config=config))
    assert shepard.samples.shape == missing.samples.shape == (2000, 2)
    assert np.max(np.abs(shepard.samples)) <= 1


def test_audio_frequency_contracts_reject_aliasing_and_short_beeps_are_not_silent():
    with pytest.raises(ParameterValidationError, match="Nyquist"):
        duckrabbit.generate(
            "audio.missing_fundamental",
            MissingFundamentalParams(fundamental=duckrabbit.FrequencyHz(1000), harmonics=(2, 3, 4)),
        )
    with pytest.raises(ParameterValidationError, match="no partial"):
        duckrabbit.generate(
            "audio.shepard_tone",
            ShepardToneParams(base_frequency=duckrabbit.FrequencyHz(3000), partial_count=2),
        )
    short_config = AudioConfig(sample_rate=SampleRate(4000), duration=DurationSeconds(0.05))
    short_av = AudiovisualConfig(audio=short_config, video=VideoConfig(frame_rate=duckrabbit.FrameRate(20), frame_count=1))
    flash = duckrabbit.generate("audiovisual.sound_induced_flash", SoundInducedFlashParams(config=short_av, beep_count=1))
    assert np.count_nonzero(flash.audio.samples) > 0


def test_audio_visual_timeline_has_shared_clock_and_metadata():
    flash = duckrabbit.generate("audiovisual.sound_induced_flash", SoundInducedFlashParams(beep_count=1))
    ventriloquist = duckrabbit.generate("audiovisual.ventriloquist", VentriloquistParams())
    assert isinstance(flash, AudiovisualTimeline)
    assert flash.metadata["beep_count"] == "1"
    assert abs(flash.audio.duration_seconds - flash.video.duration_seconds) <= 1 / flash.video.frame_rate.value
    assert ventriloquist.audio.channels == 2
    assert ventriloquist.video.has_temporal_change
    with pytest.raises(ParameterValidationError, match="stereo"):
        duckrabbit.generate(
            "audiovisual.ventriloquist",
            VentriloquistParams(config=AudiovisualConfig(audio=AudioConfig(channels=1))),
        )


def test_invalid_generator_parameters_and_unknown_ids_fail_closed():
    with pytest.raises(ValueError, match="partial_count"):
        duckrabbit.generate("audio.shepard_tone", ShepardToneParams(partial_count=1))
    with pytest.raises(UnknownIllusionError):
        duckrabbit.default_registry.get("not.real")
    with pytest.raises(ParameterValidationError, match="expects"):
        duckrabbit.default_registry.generate("visual.duck_rabbit", object())
    with pytest.raises(ParameterValidationError, match="seed"):
        duckrabbit.generate("visual.duck_rabbit", seed=True)
    with pytest.raises(ParameterValidationError, match="seed"):
        duckrabbit.generate("visual.duck_rabbit", seed=2**63)


def test_registry_rejects_duplicate_ids_and_defaults_reject_future_entries():
    registry = duckrabbit.IllusionRegistry()
    spec = duckrabbit.default_registry.get("visual.duck_rabbit")
    registry.register(spec)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(spec)
    with pytest.raises(KeyError):
        default_parameters("audiovisual.mcgurk")


def test_registry_function_and_parameter_type_guards():
    parameters = DuckRabbitParams()
    assert isinstance(registry_generate(duckrabbit.default_registry, "visual.duck_rabbit", parameters), ImageFrame)
    with pytest.raises(TypeError):
        DuckRabbitParams(config="not-a-config")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ApparentMotionParams(config="not-a-config")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        SoundInducedFlashParams(config="not-a-config")  # type: ignore[arg-type]


def test_additional_generator_parameter_boundaries():
    with pytest.raises(ValueError, match="harmonics"):
        MissingFundamentalParams(harmonics=(1,))
    with pytest.raises(ValueError, match="beep_count"):
        SoundInducedFlashParams(beep_count=3)
    with pytest.raises(ValueError, match="flash"):
        SoundInducedFlashParams(flash_count=2)
    with pytest.raises(ValueError, match="sweep_octaves"):
        ShepardToneParams(sweep_octaves=5)
    with pytest.raises(ParameterValidationError, match="line field"):
        ZollnerParams(line_count=8, line_spacing=Normalized(0.2))
    with pytest.raises(ParameterValidationError, match="inducer field"):
        ZollnerParams(inducer_count=16, inducer_spacing=Normalized(0.06))
    with pytest.raises(ParameterValidationError, match="interruption_fraction"):
        AuditoryContinuityParams(interruption_fraction=Normalized(0.0))
    with pytest.raises(ParameterValidationError, match="Nyquist"):
        AuditoryContinuityParams(carrier_frequency=duckrabbit.FrequencyHz(5000), config=AudioConfig(sample_rate=SampleRate(8000)))
