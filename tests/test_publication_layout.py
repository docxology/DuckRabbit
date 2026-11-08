"""Real-sample extrema and measured-pixel publication layout regressions."""

import numpy as np
from PIL import Image, ImageChops, ImageDraw
import pytest

from duckrabbit.artifacts import AudioBuffer
from duckrabbit.canonical import canonical_digest
from duckrabbit.parameters import SampleRate
from duckrabbit.publication import (
    ACCENT,
    CANVAS,
    RED,
    _audio_waveform,
    _draw_waveform,
    _font,
    _text_block,
    _wrapped,
)


def test_skipped_impulse_survives_aggregation_and_reaches_the_raster() -> None:
    samples = np.zeros((700, 1), dtype=np.float32)
    samples[1, 0] = 1.0  # The former stride-2 display omitted this sample.
    artifact = AudioBuffer(samples, SampleRate(8000))
    digest = canonical_digest(artifact)
    waveform = _audio_waveform(artifact)
    assert np.max(waveform["maximum"]) == 1.0
    assert np.min(waveform["minimum"]) == 0.0
    image = Image.new("RGB", (1401, 201), CANVAS)
    _draw_waveform(
        ImageDraw.Draw(image), waveform, (0, 0, 1400, 200),
        channel=0, color=ACCENT, x_range=(0.0, artifact.duration_seconds),
    )
    # The exact extremum time is not claimed: its containing bin is visible.
    assert ACCENT in [image.getpixel((x, 0)) for x in range(image.width)]
    assert canonical_digest(artifact) == digest
    assert not artifact.samples.flags.writeable


@pytest.mark.parametrize("sample_count", [1, 349, 350, 351, 700, 1001])
def test_extrema_bins_cover_every_stereo_sample_exactly_once(sample_count: int) -> None:
    index = np.arange(sample_count)
    left = np.where(index % 2, -0.75, 0.5).astype(np.float32)
    right = -left
    samples = np.column_stack((left, right))
    samples[-1] = (1.0, -1.0)
    artifact = AudioBuffer(samples, SampleRate(1000))
    waveform = _audio_waveform(artifact)
    starts = waveform["bin_start_samples"]
    stops = waveform["bin_stop_samples_exclusive"]
    assert starts[0] == 0 and stops[-1] == sample_count
    np.testing.assert_array_equal(stops[:-1], starts[1:])
    assert np.all(stops > starts)
    assert len(starts) <= 350
    assert waveform["channel_indices"] == [0, 1]
    for row, (start, stop) in enumerate(zip(starts, stops, strict=True)):
        np.testing.assert_array_equal(waveform["minimum"][row], np.min(samples[start:stop], axis=0))
        np.testing.assert_array_equal(waveform["maximum"][row], np.max(samples[start:stop], axis=0))
    np.testing.assert_array_equal(np.min(waveform["minimum"], axis=0), np.min(samples, axis=0))
    np.testing.assert_array_equal(np.max(waveform["maximum"], axis=0), np.max(samples, axis=0))


def test_final_partial_bin_keeps_opposite_channel_extrema_inside_the_clock() -> None:
    samples = np.zeros((1001, 2), dtype=np.float32)
    samples[-1] = (1.0, -1.0)
    artifact = AudioBuffer(samples, SampleRate(1000))
    waveform = _audio_waveform(artifact)
    assert waveform["bin_start_samples"][-1] == 999
    assert waveform["bin_stop_samples_exclusive"][-1] == 1001
    np.testing.assert_array_equal(waveform["minimum"][-1], (0.0, -1.0))
    np.testing.assert_array_equal(waveform["maximum"][-1], (1.0, 0.0))
    for channel, color, extreme_y in ((0, ACCENT, 0), (1, RED, 200)):
        image = Image.new("RGB", (4005, 201), CANVAS)
        _draw_waveform(
            ImageDraw.Draw(image), waveform, (0, 0, 4004, 200),
            channel=channel, color=color, x_range=(0.0, artifact.duration_seconds),
        )
        # The last bin is centered on samples 999..1000, not stretched to 1.001 s.
        assert image.getpixel((3998, extreme_y)) == color
        assert image.getpixel((4004, extreme_y)) == CANVAS


def test_short_audio_retains_each_sample_without_inventing_a_partial_bin() -> None:
    artifact = AudioBuffer(np.array([0.25, -0.5, 1.0], dtype=np.float32), SampleRate(1000))
    waveform = _audio_waveform(artifact)
    np.testing.assert_array_equal(waveform["bin_start_samples"], (0, 1, 2))
    np.testing.assert_array_equal(waveform["bin_stop_samples_exclusive"], (1, 2, 3))
    np.testing.assert_array_equal(waveform["minimum"], artifact.samples)
    np.testing.assert_array_equal(waveform["maximum"], artifact.samples)
    with pytest.raises(ValueError, match="positive"):
        _audio_waveform(artifact, max_bins=0)


@pytest.mark.parametrize("value", [
    "WWWWWWWWWWWW WWWWWWWWWWWW narrow iiiiiiiiiiiiiiiiii",
    "canonical_identity_with_a_very_long_unbroken_identifier_" * 3,
    "First paragraph with measured proportional glyph widths.\n\nSecond paragraph retains its source boundary.",
])
def test_measured_wrap_retains_content_and_contains_actual_ink(value: str) -> None:
    width, size = 180, 18
    wrapped = _wrapped(value, width, size)
    assert "".join(wrapped.split()) == "".join(value.split())
    assert all(_font(size).getlength(line) <= width for line in wrapped.split("\n"))
    if "\n\n" in value:
        assert "\n\n" in wrapped
    image = Image.new("RGB", (500, 1800), CANVAS)
    height = _text_block(ImageDraw.Draw(image), (40, 30), value, width, size)
    ink_bounds = ImageChops.difference(image, Image.new("RGB", image.size, CANVAS)).getbbox()
    assert ink_bounds is not None
    assert ink_bounds[0] >= 40
    assert ink_bounds[2] <= 40 + width + 2  # TrueType glyph side bearings.
    assert ink_bounds[3] <= 30 + height
