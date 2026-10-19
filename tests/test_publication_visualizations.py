"""Real-array and raster oracles for publication timing and spectral displays."""

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import pytest

from duckrabbit.artifacts import AudioBuffer, AudiovisualTimeline, ImageFrame, VideoSequence
from duckrabbit.canonical import canonical_digest
from duckrabbit.formalism import formalism_registry
from duckrabbit.metrics import measure_artifact
from duckrabbit.parameters import FrameRate, SampleRate, SyncOffsetMs
from duckrabbit.publication import (
    ACCENT,
    CANVAS,
    GREEN,
    RED,
    _audio,
    _audio_spectrum,
    _audio_waveform,
    _audiovisual,
    _coordinate_plot,
    _draw_audiovisual_traces,
    _draw_spectrum,
    _encoding,
    _generate,
    _write_json,
    publication_table_payloads,
)


@pytest.mark.parametrize("offset_ms", [0.0, 100.0, -100.0])
def test_frame_holds_and_stereo_audio_use_actual_shared_clock_pixels(offset_ms: float) -> None:
    frames = tuple(ImageFrame(np.full((2, 2), value, dtype=np.float32)) for value in (0, 0, 0, 1, 0, 0))
    samples = np.zeros((600, 2), dtype=np.float32)
    samples[300, 1] = 1.0
    artifact = AudiovisualTimeline(
        AudioBuffer(samples, SampleRate(1200)),
        VideoSequence(frames, FrameRate(12)),
        sync_offset=SyncOffsetMs(offset_ms),
    )
    image = Image.new("RGB", (1201, 301), CANVAS)
    traces = _draw_audiovisual_traces(ImageDraw.Draw(image), artifact, (0, 10, 1200, 110), (0, 180, 1200, 280))
    duration = 0.5 + abs(offset_ms) / 1000
    video_start = max(0.0, -offset_ms / 1000)
    audio_start = max(0.0, offset_ms / 1000)
    flash_x = int(1200 * (video_start + 0.25) / duration)
    flash_end_x = int(1200 * (video_start + 4 / 12) / duration)
    audio_x = int(1200 * (audio_start + 0.25) / duration)
    assert image.getpixel((flash_x, 60)) == RED
    assert image.getpixel(((flash_x + flash_end_x) // 2, 10)) == RED
    assert image.getpixel((flash_x - 5, 60)) == CANVAS
    assert image.getpixel((flash_end_x + 5, 10)) == CANVAS
    assert image.getpixel((audio_x, 230)) == ACCENT
    assert traces["duration_seconds"] == pytest.approx(duration)
    np.testing.assert_allclose(traces["video"]["timestamps_seconds"], video_start + np.repeat(np.arange(7) / 12, 2)[1:-1])
    np.testing.assert_array_equal(traces["video"]["values"], np.repeat((0, 0, 0, 1, 0, 0), 2))
    np.testing.assert_allclose(traces["audio"]["timestamps_seconds"], audio_start + np.arange(600) / 1200)
    np.testing.assert_array_equal(traces["audio"]["values"], np.mean(np.abs(samples), axis=1))


def test_waveform_last_sample_is_not_stretched_to_duration() -> None:
    samples = np.zeros((1000, 2), dtype=np.float32)
    samples[-1, 1] = 1.0
    waveform = _audio_waveform(AudioBuffer(samples, SampleRate(1000)))
    image = Image.new("RGB", (2001, 101), CANVAS)
    _coordinate_plot(
        ImageDraw.Draw(image), waveform["timestamps_seconds"], waveform["values"][:, 1],
        (0, 0, 2000, 100), RED, x_range=(0.0, 1.0), value_range=(0.0, 1.0),
    )
    assert waveform["timestamps_seconds"][-1] == pytest.approx(0.999)
    assert waveform["channel_indices"] == [0, 1]
    assert image.getpixel((1998, 0)) == RED
    assert image.getpixel((2000, 0)) == CANVAS
    np.testing.assert_array_equal(waveform["values"][-1], samples[-1])


def test_narrow_high_harmonic_survives_aggregation_and_is_drawn_at_its_frequency() -> None:
    sample_rate = 8192
    timestamps = np.arange(sample_rate) / sample_rate
    samples = 0.3 * np.sin(2 * np.pi * 257 * timestamps) + 0.6 * np.sin(2 * np.pi * 3001 * timestamps)
    artifact = AudioBuffer(samples, SampleRate(sample_rate))
    spectrum = _audio_spectrum(artifact)
    edges = spectrum["band_edges_hz"]
    frequencies = np.fft.rfftfreq(sample_rate, 1 / sample_rate)
    magnitudes = np.abs(np.fft.rfft(artifact.samples[:, 0])) / sample_rate
    expected = np.array([
        np.max(magnitudes[(frequencies >= low) & ((frequencies < high) if index < 47 else (frequencies <= high))], initial=0.0)
        for index, (low, high) in enumerate(zip(edges[:-1], edges[1:], strict=True))
    ])
    np.testing.assert_allclose(spectrum["band_values"], expected)
    np.testing.assert_allclose(spectrum["plotted_values"], expected / np.max(expected))
    low_band = np.searchsorted(edges, 257, side="right") - 1
    high_band = np.searchsorted(edges, 3001, side="right") - 1
    assert spectrum["band_values"][low_band] == pytest.approx(0.15, abs=1e-6)
    assert spectrum["band_values"][high_band] == pytest.approx(0.3, abs=1e-6)
    assert edges[0] == 0 and edges[-1] == sample_rate / 2
    image = Image.new("RGB", (481, 101), CANVAS)
    _draw_spectrum(ImageDraw.Draw(image), spectrum, (0, 0, 480, 100))
    assert image.getpixel((high_band * 10 + 5, 1)) == GREEN
    assert image.getpixel((low_band * 10 + 5, 55)) == GREEN
    assert image.getpixel((low_band * 10 + 5, 40)) == CANVAS


def test_antiphase_and_right_only_stereo_are_not_cancelled_or_ignored() -> None:
    timestamps = np.arange(4096) / 4096
    tone = 0.8 * np.sin(2 * np.pi * 1501 * timestamps)
    antiphase = AudioBuffer(np.column_stack((tone, -tone)), SampleRate(4096))
    right_only = AudioBuffer(np.column_stack((np.zeros_like(tone), tone)), SampleRate(4096))
    antiphase_spectrum = _audio_spectrum(antiphase)
    right_spectrum = _audio_spectrum(right_only)
    assert max(antiphase_spectrum["band_values"]) == pytest.approx(0.4, abs=1e-6)
    np.testing.assert_allclose(right_spectrum["band_values"], antiphase_spectrum["band_values"] / 2)
    assert right_spectrum["channel_indices"] == [0, 1]
    assert "per-channel" in right_spectrum["channel_rule"]
    assert right_spectrum["window"] == "rectangular (unwindowed)"


@pytest.mark.parametrize("sample_count", [1, 3, 1000, 1001])
def test_spectral_bands_include_dc_nyquist_and_empty_bands(sample_count: int) -> None:
    artifact = AudioBuffer(np.full(sample_count, 0.5), SampleRate(2000))
    spectrum = _audio_spectrum(artifact)
    assert len(spectrum["band_values"]) == 48
    assert spectrum["band_values"][0] == pytest.approx(0.5)
    assert np.isfinite(spectrum["plotted_values"]).all()
    if sample_count == 1000:
        nyquist = AudioBuffer(0.5 * (-1.0) ** np.arange(sample_count), SampleRate(2000))
        assert _audio_spectrum(nyquist)["band_values"][-1] == pytest.approx(0.5)
    silence = _audio_spectrum(AudioBuffer(np.zeros(sample_count), SampleRate(2000)))
    np.testing.assert_array_equal(silence["plotted_values"], np.zeros(48))


def test_default_audiovisual_render_and_serialized_trace_agree(tmp_path: Path) -> None:
    path = tmp_path / "timeline.png"
    digest, payload = _audiovisual(path)
    artifact = _generate("audiovisual.sound_induced_flash")
    assert payload["canonical_digest"] == canonical_digest(artifact)
    assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
    _write_json(tmp_path / "timeline.json", payload)
    saved = json.loads((tmp_path / "timeline.json").read_text())
    video = saved["plotted_traces"]["video"]
    np.testing.assert_allclose(video["timestamps_seconds"], np.repeat(np.arange(7) / 12, 2)[1:-1])
    assert video["timestamps_seconds"][6] == 0.25
    with Image.open(path) as image:
        assert image.getpixel((950, 250)) == RED
        assert image.getpixel((1090, 145)) == RED
        assert image.getpixel((900, 250)) != RED
    audio = saved["plotted_traces"]["audio"]
    np.testing.assert_allclose(audio["timestamps_seconds"], np.arange(artifact.audio.sample_count) / artifact.audio.sample_rate.value)
    np.testing.assert_array_equal(audio["values"], np.mean(np.abs(artifact.audio.samples), axis=1))


def test_audio_render_serializes_the_actual_band_values_and_channel_waveforms(tmp_path: Path) -> None:
    path = tmp_path / "audio.png"
    _, payload = _audio(path)
    _write_json(tmp_path / "audio.json", payload)
    saved = json.loads((tmp_path / "audio.json").read_text())
    with Image.open(path) as image:
        for row, record in enumerate(saved["signals"]):
            artifact = _generate(record["illusion_id"])
            expected = _audio_spectrum(artifact)
            np.testing.assert_array_equal(record["spectrum"]["band_values"], expected["band_values"])
            assert record["canonical_digest"] == canonical_digest(artifact)
            assert record["spectrum"]["sample_rate_hz"] == artifact.sample_rate.value
            band = int(np.argmax(expected["plotted_values"]))
            assert image.getpixel((1500 + band * 7 + 3, 115 + row * 290 + 66)) == GREEN
            rule_color = ACCENT if row % 2 == 0 else GREEN
            assert all(image.getpixel((column, 115 + row * 290 + 38)) == rule_color for column in range(1500, 1836))
            waveform = record["waveform"]
            assert len(waveform["values"][0]) == artifact.channels
            np.testing.assert_allclose(waveform["timestamps_seconds"], _audio_waveform(artifact)["timestamps_seconds"])


def test_centroid_definition_matches_unchanged_mean_channel_magnitude_metric() -> None:
    timestamps = np.arange(4000) / 4000
    samples = np.column_stack((0.6 * np.sin(2 * np.pi * 100 * timestamps), 0.3 * np.sin(2 * np.pi * 900 * timestamps)))
    artifact = AudioBuffer(samples, SampleRate(4000))
    magnitudes = np.mean(np.abs(np.fft.rfft(artifact.samples, axis=0)), axis=1)
    frequencies = np.fft.rfftfreq(4000, 1 / 4000)
    expected = np.sum(frequencies * magnitudes) / np.sum(magnitudes)
    assert measure_artifact(artifact).to_dict()["values"]["spectral_centroid_hz"] == pytest.approx(expected)
    energy_weighted = np.sum(frequencies * magnitudes ** 2) / np.sum(magnitudes ** 2)
    assert abs(expected - energy_weighted) > 100
    records = publication_table_payloads()["metrics_table"]["records"]
    definition = next(record["definition"] for record in records if record["metric"] == "spectral_centroid_hz")
    assert all(term in definition for term in ("mean-channel", "abs", "unwindowed rFFT", "not energy"))


def test_png_delivery_fact_does_not_claim_exact_float32_preservation(tmp_path: Path) -> None:
    _, payload = _encoding(tmp_path / "encoding.png")
    png = next(profile for profile in payload["profiles"] if profile["format"] == "PNG")
    assert png["delivery fact"] == "raster dimensions; uint8 quantization"
    assert "digest" not in png["delivery fact"]
    assert "Canonical digest retained in provenance" in payload["canonical_identity"]
    assert "exact canonical arrays only in NPZ" in payload["canonical_identity"]


def test_formalism_membership_uses_a_portable_textual_relation() -> None:
    definition = next(item for item in formalism_registry() if item.label == "eq:encoding_verification")
    assert "V(F, M) in {pass, fail}" in definition.equation
    assert "∈" not in definition.equation
