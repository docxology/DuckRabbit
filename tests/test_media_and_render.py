"""Real media round-trip, digest, manifest, and backend-boundary tests."""

from __future__ import annotations

import json
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest

import duckrabbit
from duckrabbit import media
from duckrabbit.artifacts import ArtifactManifest, AudioBuffer, AudiovisualTimeline, EncodedArtifact, ImageFrame, VideoSequence
from duckrabbit.errors import BackendUnavailableError, MediaEncodingError, ParameterValidationError
from duckrabbit.generators import ApparentMotionParams, SoundInducedFlashParams
from duckrabbit.parameters import AudioEncoding, AudiovisualConfig, ColorMode, FrameRate, MediaFormat, PcmBitDepth, SampleRate, SyncOffsetMs, VideoConfig
from duckrabbit.render import artifact_digest, artifact_summary, build_manifest, encode_artifact, generate_artifact, jsonable, parameters_from_json
from duckrabbit.taxonomy import Modality


def test_real_png_gif_wav_round_trips(tmp_path: Path):
    image = duckrabbit.generate("visual.duck_rabbit")
    video = duckrabbit.generate("visual.apparent_motion")
    audio = duckrabbit.generate("audio.missing_fundamental")
    png = media.write_png(image, tmp_path / "duck.png")
    gif = media.write_gif(video, tmp_path / "motion.gif")
    wav = media.write_wav(audio, tmp_path / "tone.wav")
    assert png.stat().st_size > 0
    assert gif.stat().st_size > 0
    assert wav.stat().st_size > 44

    from PIL import Image

    with Image.open(png) as decoded_png:
        assert decoded_png.size == (image.width, image.height)
        assert decoded_png.mode == image.mode
    with Image.open(gif) as decoded_gif:
        assert decoded_gif.n_frames == len(video.frames)
        # GIF stores durations in 10 ms units, so Pillow may quantize 83.3 ms
        # to 80 ms even though the requested frame rate is 12 Hz.
        assert abs(decoded_gif.info["duration"] - 1000.0 / video.frame_rate.value) <= 10
    with wave.open(str(wav), "rb") as decoded_wav:
        assert decoded_wav.getnchannels() == audio.channels
        assert decoded_wav.getframerate() == audio.sample_rate.value
        assert decoded_wav.getnframes() == audio.samples.shape[0]

    rgb = ImageFrame(np.zeros((8, 8, 3), dtype=np.float32), mode="RGB")
    rgb_path = media.write_png(rgb, tmp_path / "rgb.png")
    assert rgb_path.stat().st_size > 0


def test_wav_pcm_depths_are_real_and_size_consistent(tmp_path: Path):
    audio = duckrabbit.generate("audio.missing_fundamental")
    for depth in (8, 16, 24, 32):
        path = media.write_wav(audio, tmp_path / f"tone_{depth}.wav", encoding=AudioEncoding(PcmBitDepth(depth)))
        with wave.open(str(path), "rb") as decoded:
            assert decoded.getsampwidth() == depth // 8
            assert decoded.getnframes() == audio.sample_count
            assert decoded.getnchannels() == audio.channels

    with pytest.raises(MediaEncodingError, match="AudioEncoding"):
        media.write_wav(audio, tmp_path / "invalid.wav", encoding=object())  # type: ignore[arg-type]


def test_manifest_and_digest_are_stable(tmp_path: Path):
    first, first_manifest = generate_artifact("visual.duck_rabbit", output_dir=tmp_path)
    second, second_manifest = generate_artifact("visual.duck_rabbit", output_dir=tmp_path)
    assert artifact_digest(first) == artifact_digest(second)
    assert first_manifest["canonical_digest"] == second_manifest["canonical_digest"]
    manifest_path = Path(first_manifest["manifest"])
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["schema_version"] == "duckrabbit/artifact/v2"
    assert jsonable(Modality.VISUAL) == "visual"
    assert jsonable((Modality.VISUAL, "x")) == ["visual", "x"]

    audio = duckrabbit.generate("audio.missing_fundamental")
    video = duckrabbit.generate("visual.apparent_motion")
    timeline = duckrabbit.generate("audiovisual.sound_induced_flash")
    assert artifact_digest(audio)
    assert artifact_digest(video)
    assert artifact_digest(timeline)
    assert artifact_summary(duckrabbit.generate("visual.duck_rabbit"))["type"] == "image"
    assert artifact_summary(audio)["type"] == "audio"
    assert artifact_summary(video)["type"] == "video"
    typed_manifest = build_manifest("visual.duck_rabbit", duckrabbit.generators.default_parameters("visual.duck_rabbit"), first)
    assert isinstance(typed_manifest, ArtifactManifest)
    assert typed_manifest.illusion_id == "visual.duck_rabbit"
    assert artifact_summary(timeline)["video"]["temporal_deltas"]
    generated_manifest = json.loads(Path(first_manifest["manifest"]).read_text(encoding="utf-8"))
    assert generated_manifest["format"] == "png"
    assert generated_manifest["encoded_size_bytes"] > 0
    assert generated_manifest["artifact"]["type"] == "image"
    assert generated_manifest["artifact"]["channels"] == 1
    assert generated_manifest["encoding"]["format"] == "png"
    assert len(generated_manifest["encoding"]["sha256"]) == 64
    same_bytes_different_shape = ImageFrame(np.zeros((2, 8), dtype=np.float32))
    other_shape = ImageFrame(np.zeros((4, 4), dtype=np.float32))
    assert artifact_digest(same_bytes_different_shape) != artifact_digest(other_shape)


def test_jsonable_handles_numpy_paths_dataclasses_and_rejects_unknown_values() -> None:
    @dataclass(frozen=True)
    class Payload:
        path: Path
        values: tuple[int, ...]

    payload = jsonable(
        {
            "array": np.array([np.int64(2), np.float32(0.5)]),
            "payload": Payload(Path("nested/file.json"), (1, 2)),
        }
    )
    assert payload == {
        "array": [2, pytest.approx(0.5)],
        "payload": {"path": "nested/file.json", "values": [1, 2]},
    }
    assert jsonable(np.int64(7)) == 7

    class NumericValue:
        value = 11

    assert jsonable(NumericValue()) == 11
    with pytest.raises(ParameterValidationError, match="not JSON serializable"):
        jsonable(object())


def test_typed_output_spec_controls_manifest_and_overwrite(tmp_path: Path):
    spec = duckrabbit.OutputSpec(format=MediaFormat.PNG, include_manifest=False, overwrite=False)
    _, first = generate_artifact("visual.duck_rabbit", output_dir=tmp_path, output_spec=spec)
    assert first["format"] == "png"
    assert first["manifest"] is None
    with pytest.raises(FileExistsError, match="overwrite"):
        generate_artifact("visual.duck_rabbit", output_dir=tmp_path, output_spec=spec)


def test_parameter_json_and_format_boundaries(tmp_path: Path):
    parameters = parameters_from_json("visual.apparent_motion", {"config": {"frame_count": 4}})
    assert parameters.config.frame_count == 4
    video = duckrabbit.generate("visual.apparent_motion", parameters)
    with pytest.raises(ValueError, match="incompatible"):
        encode_artifact(video, tmp_path / "wrong.wav", "wav")
    with pytest.raises(ValueError, match="unsupported output format"):
        generate_artifact("visual.duck_rabbit", output_dir=tmp_path, format_name="flac")
    with pytest.raises(TypeError, match="unsupported artifact"):
        artifact_digest("not-an-artifact")  # type: ignore[arg-type]


def test_mp4_encoder_when_ffmpeg_is_available(tmp_path: Path):
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg is not installed")
    video = duckrabbit.generate(
        "visual.apparent_motion",
        ApparentMotionParams(config=VideoConfig(width=32, height=24, frame_rate=FrameRate(8), frame_count=4)),
    )
    path = media.write_mp4(video, tmp_path / "motion.mp4")
    assert path.stat().st_size > 0

    timeline = duckrabbit.generate("audiovisual.sound_induced_flash")
    av_path = media.write_audiovisual(timeline, tmp_path / "flash.mp4")
    assert av_path.stat().st_size > 0

    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        probe = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "stream=codec_type,start_time,duration", "-of", "json", str(av_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        streams = json.loads(probe.stdout)["streams"]
        assert {stream["codec_type"] for stream in streams} == {"video", "audio"}


def test_ffmpeg_mux_preserves_declared_sync_offset_in_packet_timestamps(tmp_path: Path):
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("ffmpeg and ffprobe are required")
    for offset in (120.0, -120.0):
        timeline = duckrabbit.generate(
            "audiovisual.sound_induced_flash",
            SoundInducedFlashParams(config=AudiovisualConfig(sync_offset=SyncOffsetMs(offset))),
        )
        path = media.write_audiovisual(timeline, tmp_path / f"sync_{offset}.mp4")
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "packet=codec_type,pts_time",
                "-of",
                "json",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        packets = json.loads(probe.stdout)["packets"]
        shifted_kind = "audio" if offset > 0 else "video"
        nonnegative_pts = [
            float(packet["pts_time"])
            for packet in packets
            if packet["codec_type"] == shifted_kind and float(packet["pts_time"]) >= 0
        ]
        assert nonnegative_pts
        assert abs(nonnegative_pts[0] - abs(offset) / 1000.0) <= 0.03


def test_missing_ffmpeg_is_an_explicit_capability_error(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(media.shutil, "which", lambda _: None)
    video = duckrabbit.generate("visual.apparent_motion")
    with pytest.raises(BackendUnavailableError, match="ffmpeg"):
        media.write_mp4(video, tmp_path / "motion.mp4", ffmpeg_bin="not-installed")


def test_mp4_rejects_odd_dimensions_before_codec_failure(tmp_path: Path):
    video = duckrabbit.generate(
        "visual.apparent_motion",
        ApparentMotionParams(config=VideoConfig(width=33, height=24)),
    )
    with pytest.raises(MediaEncodingError, match="even"):
        media.write_mp4(video, tmp_path / "odd.mp4", ffmpeg_bin="/usr/bin/false")


def test_real_ffmpeg_failure_is_reported(tmp_path: Path):
    video = duckrabbit.generate("visual.apparent_motion")
    with pytest.raises(MediaEncodingError, match="ffmpeg"):
        media.write_mp4(video, tmp_path / "motion.mp4", ffmpeg_bin="/usr/bin/false")


def test_audio_buffer_rejects_invalid_shape_and_range():
    with pytest.raises(ParameterValidationError):
        AudioBuffer(np.zeros((4, 3)), SampleRate(4000))
    with pytest.raises(ParameterValidationError):
        ImageFrame(np.full((4, 4), 2.0))
    with pytest.raises(ParameterValidationError, match="shape"):
        ImageFrame(np.zeros((0, 4), dtype=np.float32))
    with pytest.raises(ParameterValidationError, match="shape"):
        AudioBuffer(np.zeros((0, 1), dtype=np.float32), SampleRate(4000))
    with pytest.raises(ParameterValidationError, match="sample_rate"):
        AudioBuffer(np.zeros((4, 1), dtype=np.float32), 4000)  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="non-finite"):
        AudioBuffer(np.array([np.nan]), SampleRate(4000))
    with pytest.raises(ParameterValidationError, match=r"\[-1, 1\]"):
        AudioBuffer(np.array([2.0]), SampleRate(4000))
    assert AudioBuffer(np.zeros(4, dtype=np.float32), SampleRate(4000)).channels == 1
    with pytest.raises(ParameterValidationError, match="non-finite"):
        ImageFrame(np.array([[np.nan]], dtype=np.float32))


def test_artifact_shape_and_timeline_invariants():
    frame = ImageFrame(np.zeros((4, 4), dtype=np.float32))
    with pytest.raises(ParameterValidationError, match="grayscale"):
        ImageFrame(np.zeros((4, 4, 3), dtype=np.float32))
    with pytest.raises(ParameterValidationError, match="RGB"):
        ImageFrame(np.zeros((4, 4), dtype=np.float32), mode="RGB")
    with pytest.raises(ParameterValidationError, match="unsupported"):
        ImageFrame(np.zeros((4, 4), dtype=np.float32), mode="CMYK")
    with pytest.raises(ParameterValidationError, match="at least one"):
        VideoSequence((), duckrabbit.FrameRate(12))
    with pytest.raises(ParameterValidationError, match="frame_rate"):
        VideoSequence((frame,), 12)  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="ImageFrame"):
        VideoSequence((object(),), duckrabbit.FrameRate(12))  # type: ignore[arg-type]
    assert list(VideoSequence((frame,), duckrabbit.FrameRate(12))) == [frame]
    with pytest.raises(ParameterValidationError, match="identical"):
        VideoSequence((frame, ImageFrame(np.zeros((5, 4), dtype=np.float32))), duckrabbit.FrameRate(12))
    audio = AudioBuffer(np.zeros((100, 1), dtype=np.float32), duckrabbit.SampleRate(4000))
    video = VideoSequence((frame,) * 24, duckrabbit.FrameRate(12))
    with pytest.raises(ParameterValidationError, match="duration"):
        AudiovisualTimeline(audio, video)
    with pytest.raises(ParameterValidationError, match="metadata"):
        AudiovisualTimeline(audio=duckrabbit.generate("audio.missing_fundamental"), video=duckrabbit.generate("visual.apparent_motion"), metadata={1: "bad"})
    with pytest.raises(ParameterValidationError, match="audio/video"):
        AudiovisualTimeline(audio=object(), video=video)  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="offsets"):
        AudiovisualTimeline(audio=audio, video=video, sync_offset=0)  # type: ignore[arg-type]
    timeline = duckrabbit.generate("audiovisual.sound_induced_flash")
    with pytest.raises(TypeError):
        timeline.metadata["mutated"] = "no"  # type: ignore[index]
    assert isinstance(timeline.video.frames, tuple)
    rgb = ImageFrame(np.zeros((4, 4, 3), dtype=np.float32), mode=ColorMode.RGB)
    with pytest.raises(ParameterValidationError, match="color modes"):
        VideoSequence((frame, rgb), duckrabbit.FrameRate(12))
    assert frame.channels == 1
    assert rgb.channels == 3
    assert frame.nbytes == 4 * 4 * 4
    assert audio.peak == 0.0
    assert audio.rms == 0.0
    assert video.frame_count == 24
    assert video.mean_temporal_delta == 0.0
    assert timeline.presentation_duration_seconds >= timeline.duration_seconds


def test_artifact_manifest_rejects_invalid_provenance_fields():
    from duckrabbit.taxonomy import taxonomy_entries

    entry = taxonomy_entries()[0]
    values = {
        "schema_version": "duckrabbit/artifact/v1",
        "illusion_id": entry.illusion_id,
        "implementation_status": entry.implementation_status,
        "modality": entry.modalities,
        "taxonomy": entry,
        "parameters": duckrabbit.generators.default_parameters(entry.illusion_id),
        "seed": 0,
        "canonical_digest": "a" * 64,
        "duration_seconds": 0.0,
    }
    with pytest.raises(ParameterValidationError, match="schema_version"):
        ArtifactManifest(**{**values, "schema_version": ""})
    with pytest.raises(ParameterValidationError, match="seed"):
        ArtifactManifest(**{**values, "seed": True})
    with pytest.raises(ParameterValidationError, match="implementation_status"):
        ArtifactManifest(**{**values, "implementation_status": "implemented"})  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="taxonomy"):
        ArtifactManifest(**{**values, "taxonomy": object()})  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="duration"):
        ArtifactManifest(**{**values, "duration_seconds": float("nan")})


def test_encoded_artifact_record_is_strictly_typed():
    encoded = EncodedArtifact("artifact.png", MediaFormat.PNG, "image/png", 10, "a" * 64)
    assert encoded.format is MediaFormat.PNG
    assert encoded.size_bytes == 10
    with pytest.raises(ParameterValidationError, match="format"):
        EncodedArtifact("artifact.png", "png", "image/png", 10, "a" * 64)  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="size_bytes"):
        EncodedArtifact("artifact.png", MediaFormat.PNG, "image/png", 0, "a" * 64)
    with pytest.raises(ParameterValidationError, match="sha256"):
        EncodedArtifact("artifact.png", MediaFormat.PNG, "image/png", 10, "not-a-hash")
