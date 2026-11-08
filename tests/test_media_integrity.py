"""Real-file negative controls for encoding, decoding, and provenance integrity."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import zipfile
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from duckrabbit.artifacts import (
    AudioBuffer,
    AudiovisualTimeline,
    EncodedArtifact,
    ImageFrame,
    VideoSequence,
)
from duckrabbit.errors import (
    ManifestValidationError,
    MediaEncodingError,
    MediaInspectionError,
    VerificationError,
)
from duckrabbit.generators import default_parameters
from duckrabbit.inspection import (
    _compare_expected_facts,
    inspect_media,
    verify_manifest,
)
from duckrabbit.manifest import read_manifest
from duckrabbit.media import (
    _atomic_destination,
    read_npz,
    write_audiovisual,
    write_gif,
    write_npz,
)
from duckrabbit.parameters import (
    BackendKind,
    FrameRate,
    MediaFormat,
    OutputSpec,
    SampleRate,
    SyncOffsetMs,
    Normalized,
    SpatialOffset,
    VideoConfig,
)
from duckrabbit.render import artifact_summary, build_manifest_v2, generate_artifact


def _video(frame_count: int, fps: float) -> VideoSequence:
    frames = tuple(
        ImageFrame(np.full((16, 16), index / frame_count, dtype=np.float32))
        for index in range(frame_count)
    )
    return VideoSequence(frames, FrameRate(fps))


def test_relative_output_directory_verifies_without_changing_api_path(tmp_path: Path):
    original = Path.cwd()
    try:
        os.chdir(tmp_path)
        _, payload = generate_artifact("visual.duck_rabbit", output_dir=Path("out"))
        assert payload["output"] == "out/visual_duck_rabbit.png"
        assert verify_manifest(Path(payload["manifest"]))["status"] == "verified"
        assert Path(payload["encoding"]["path"]).is_absolute()
    finally:
        os.chdir(original)


def test_generated_sidecars_remain_verifiable_when_bundle_moves(tmp_path: Path):
    original = tmp_path / "original"
    _, payload = generate_artifact("visual.duck_rabbit", output_dir=original)
    sidecar = Path(payload["manifest"])
    document = json.loads(sidecar.read_text(encoding="utf-8"))
    assert document["output"] == document["encoding"]["path"] == "visual_duck_rabbit.png"
    moved = original.rename(tmp_path / "moved")
    assert verify_manifest(moved / sidecar.name)["status"] == "verified"


@pytest.mark.parametrize("illusion_id,field,value", [
    ("visual.zollner", "line_count", -100),
    ("audio.shepard_tone", "partial_count", 1),
    ("audio.missing_fundamental", "harmonics", []),
])
def test_actual_manifest_parameters_obey_root_generator_constraints(tmp_path: Path, illusion_id: str, field: str, value: object):
    _, payload = generate_artifact(illusion_id, output_dir=tmp_path)
    sidecar = Path(payload["manifest"])
    document = json.loads(sidecar.read_text(encoding="utf-8"))
    document["parameters"][field] = value
    sidecar.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ManifestValidationError):
        read_manifest(sidecar)
    assert verify_manifest(sidecar)["status"] == "failed"


def test_gif_distributes_centiseconds_without_accumulating_drift(tmp_path: Path):
    from PIL import Image

    path = write_gif(_video(120, 24), tmp_path / "clock.gif")
    with Image.open(path) as image:
        durations = []
        for frame_index in range(image.n_frames):
            image.seek(frame_index)
            durations.append(image.info["duration"])
    assert sum(durations) == 5000
    assert set(durations) == {40, 50}
    for frame_index in range(1, 121):
        assert abs(sum(durations[:frame_index]) - frame_index * 1000 / 24) <= 5
    assert inspect_media(path).facts["duration_seconds"] == 5


def test_gif_rejects_unrepresentable_frame_rate_before_output(tmp_path: Path):
    path = tmp_path / "fast.gif"
    with pytest.raises(MediaEncodingError, match="centisecond"):
        write_gif(_video(2, 120), path)
    assert not path.exists()


def test_gif_comparison_uses_average_clock_not_first_quantized_delay(tmp_path: Path):
    video = _video(60, 60)
    output = write_gif(video, tmp_path / "sixty.gif")
    errors: list[str] = []
    checks: list[str] = []
    _compare_expected_facts(artifact_summary(video), inspect_media(output), errors, checks)
    assert not errors
    assert "decoded_frame_rate" in checks


def test_v2_cannot_bypass_validation_by_declaring_a_legacy_marker(tmp_path: Path):
    _, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path)
    sidecar = Path(payload["manifest"])
    document = json.loads(sidecar.read_text())
    document["legacy_manifest"] = "duckrabbit/artifact/v1"
    document["taxonomy"] = None
    sidecar.write_text(json.dumps(document))
    assert verify_manifest(sidecar)["status"] == "failed"


@pytest.mark.parametrize("illusion_id,cutoff", [("visual.duck_rabbit", 100), ("audio.missing_fundamental", 44)])
def test_truncated_payload_cannot_verify_with_refreshed_container_hash(tmp_path: Path, illusion_id: str, cutoff: int):
    _, payload = generate_artifact(illusion_id, output_dir=tmp_path)
    output = Path(payload["output"])
    output.write_bytes(output.read_bytes()[:cutoff])
    sidecar = Path(payload["manifest"])
    document = json.loads(sidecar.read_text())
    document["encoding"]["sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    document["encoding"]["size_bytes"] = output.stat().st_size
    sidecar.write_text(json.dumps(document))
    with pytest.raises(MediaInspectionError, match="decode"):
        verify_manifest(sidecar)


@pytest.mark.parametrize("field,value", [
    ("artifact", {"nbytes": 1}),
    ("canonical", {"digest": "bad"}),
    ("parameters", {"nonsense": None}),
    ("taxonomy", None),
    ("encoding", {"size_bytes": 1}),
])
def test_loaded_v2_manifest_rejects_invalid_contracts(tmp_path: Path, field: str, value: object):
    _, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path)
    sidecar = Path(payload["manifest"])
    document = json.loads(sidecar.read_text())
    if isinstance(value, dict) and field != "parameters":
        document[field].update(value)
    else:
        document[field] = value
    sidecar.write_text(json.dumps(document))
    if field != "encoding":
        with pytest.raises(ManifestValidationError):
            read_manifest(sidecar)
    report = verify_manifest(sidecar)
    assert report["status"] == "failed"
    assert report["errors"]


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="requires real ffmpeg and ffprobe")
@pytest.mark.parametrize("audio_duration", [.45, .5, .55])
@pytest.mark.parametrize("offset", [0, 120, -120])
@pytest.mark.parametrize("sample_rate", [8000, 48000])
def test_real_audiovisual_sync_uses_onsets_not_unequal_stream_ends(
    tmp_path: Path, audio_duration: float, offset: float, sample_rate: int,
):
    samples = (.5 * np.sin(np.arange(round(audio_duration * sample_rate)) * .13)).astype(np.float32)
    timeline = AudiovisualTimeline(
        AudioBuffer(samples, SampleRate(sample_rate)), _video(9, 18), sync_offset=SyncOffsetMs(offset),
    )
    output = write_audiovisual(timeline, tmp_path / "timeline.mp4")
    manifest = build_manifest_v2(
        "audiovisual.sound_induced_flash", default_parameters("audiovisual.sound_induced_flash"), timeline,
    )
    encoded = EncodedArtifact(
        path=str(output), format=MediaFormat.MP4, media_type="video/mp4", size_bytes=output.stat().st_size,
        sha256=hashlib.sha256(output.read_bytes()).hexdigest(), backend=BackendKind.FFMPEG,
    )
    sidecar = replace(manifest, encoding=encoded).write(tmp_path / "timeline.mp4.json")
    report = verify_manifest(sidecar)
    assert report["status"] == "verified", report
    assert "decoded_sync_offset_ms" in report["checks"]
    document = json.loads(sidecar.read_text())
    document["artifact"]["sync_offset_ms"] = offset + 100
    sidecar.write_text(json.dumps(document))
    failed = verify_manifest(sidecar)
    assert failed["status"] == "failed"
    assert any("sync_offset_ms" in error for error in failed["errors"])


def test_manifest_only_collision_prevents_any_media_output(tmp_path: Path):
    sidecar = tmp_path / "visual_duck_rabbit.png.json"
    sidecar.write_bytes(b"retained provenance")
    with pytest.raises(FileExistsError):
        generate_artifact("visual.duck_rabbit", output_dir=tmp_path, output_spec=OutputSpec(overwrite=False))
    assert sidecar.read_bytes() == b"retained provenance"
    assert not (tmp_path / "visual_duck_rabbit.png").exists()


def test_atomic_publication_does_not_clobber_a_competing_destination(tmp_path: Path):
    output = tmp_path / "race.png"
    with pytest.raises(FileExistsError), _atomic_destination(output, overwrite=False) as temporary:
        temporary.write_bytes(b"new contender")
        output.write_bytes(b"winner")
    assert output.read_bytes() == b"winner"
    assert list(tmp_path.iterdir()) == [output]


@pytest.mark.parametrize("filename", ["archive", "archive.binary", "archive.npz"])
def test_npz_preserves_requested_destination_and_arrays(tmp_path: Path, filename: str):
    image = ImageFrame(np.arange(256, dtype=np.float32).reshape(16, 16) / 255)
    output = write_npz(image, tmp_path / filename)
    restored = read_npz(output)
    np.testing.assert_array_equal(restored.pixels, image.pixels)
    assert output.name == filename
    assert list(tmp_path.iterdir()) == [output]


@pytest.mark.parametrize("corruption", ["metadata_list", "crc"])
def test_malformed_npz_uses_structured_inspection_and_cli_errors(tmp_path: Path, corruption: str):
    output = tmp_path / "bad.npz"
    if corruption == "metadata_list":
        np.savez(output, metadata_json=np.asarray("[]"), pixels=np.zeros((16, 16), dtype=np.float32))
    else:
        write_npz(ImageFrame(np.zeros((16, 16), dtype=np.float32)), output)
        with zipfile.ZipFile(output) as archive:
            member = archive.getinfo("metadata_json.npy")
        data = bytearray(output.read_bytes())
        filename_length, extra_length = struct.unpack_from("<HH", data, member.header_offset + 26)
        payload_start = member.header_offset + 30 + filename_length + extra_length
        data[payload_start + member.compress_size // 2] ^= 1
        output.write_bytes(data)
    with pytest.raises(MediaInspectionError):
        inspect_media(output)
    with pytest.raises(MediaEncodingError):
        read_npz(output)
    environment = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "duckrabbit", "inspect", str(output)],
        capture_output=True, text=True, env=environment, check=False,
    )
    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "failed"
    assert any("cannot decode NPZ" in error for error in report["errors"])


def _refresh_encoding(sidecar: Path, output: Path) -> None:
    document = json.loads(sidecar.read_text(encoding="utf-8"))
    document["encoding"]["sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    document["encoding"]["size_bytes"] = output.stat().st_size
    sidecar.write_text(json.dumps(document), encoding="utf-8")


@pytest.mark.parametrize("replacement", ["LA", "RGBA", "transparent_palette", "BMP", "APNG"])
def test_png_verification_binds_actual_container_and_opaque_mode(tmp_path: Path, replacement: str):
    from PIL import Image

    _, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path)
    output, sidecar = Path(payload["output"]), Path(payload["manifest"])
    with Image.open(output) as original:
        image = original.copy()
    if replacement in {"LA", "RGBA"}:
        image = image.convert(replacement)
        image.putalpha(0)
        image.save(output, format="PNG")
    elif replacement == "transparent_palette":
        image.convert("P").save(output, format="PNG", transparency=0)
    elif replacement == "APNG":
        inverted = Image.fromarray(255 - np.asarray(image), mode="L")
        image.save(output, format="PNG", save_all=True, append_images=[inverted], duration=[20, 20])
    else:
        image.save(output, format="BMP")
    _refresh_encoding(sidecar, output)
    report = verify_manifest(sidecar)
    assert report["status"] == "failed", report
    assert any("mode" in error or "transparency" in error or "container format" in error or "image_frame_count" in error for error in report["errors"])


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="requires real ffmpeg and ffprobe")
@pytest.mark.parametrize("maps", [("0:v:0",), ("0:a:0",), ("0:v:0", "0:a:0", "0:a:0"), ("0:v:0", "0:v:0", "0:a:0")])
def test_audiovisual_verification_requires_exact_stream_kind_and_count(tmp_path: Path, maps: tuple[str, ...]):
    _, payload = generate_artifact("audiovisual.sound_induced_flash", output_dir=tmp_path)
    output, sidecar = Path(payload["output"]), Path(payload["manifest"])
    replacement = tmp_path / "replacement.mp4"
    command = [shutil.which("ffmpeg"), "-v", "error", "-y", "-i", str(output)]
    for stream in maps:
        command.extend(("-map", stream))
    subprocess.run([*command, "-c", "copy", str(replacement)], check=True, capture_output=True)
    replacement.replace(output)
    _refresh_encoding(sidecar, output)
    report = verify_manifest(sidecar)
    assert report["status"] == "failed", report
    assert any("stream kind/count" in error for error in report["errors"])


@pytest.mark.parametrize("illusion_id,array_name,shape", [
    ("visual.duck_rabbit", "pixels", ()),
    ("audio.missing_fundamental", "samples", ()),
    ("visual.apparent_motion", "frames", (2, 16)),
    ("audiovisual.sound_induced_flash", "frames", ()),
])
def test_rank_malformed_npz_fails_through_structured_domain_error(tmp_path: Path, illusion_id: str, array_name: str, shape: tuple[int, ...]):
    _, payload = generate_artifact(illusion_id, output_dir=tmp_path, format_name=MediaFormat.NPZ)
    output, sidecar = Path(payload["output"]), Path(payload["manifest"])
    with np.load(output, allow_pickle=False) as archive:
        arrays = {name: archive[name].copy() for name in archive.files}
    arrays[array_name] = np.full(shape, .5, dtype=np.float32)
    np.savez(output, **arrays)
    _refresh_encoding(sidecar, output)
    with pytest.raises(MediaInspectionError, match="rank/shape"):
        inspect_media(output)
    with pytest.raises(MediaInspectionError, match="rank/shape"):
        verify_manifest(sidecar)


@pytest.mark.parametrize("illusion_id,field,value", [
    ("visual.duck_rabbit", "min_value", .1),
    ("visual.duck_rabbit", "max_value", .9),
    ("audio.missing_fundamental", "peak", 1.0),
    ("audio.missing_fundamental", "rms", 0.0),
    ("audiovisual.sound_induced_flash", "spatial_offset", .25),
])
def test_exact_npz_verification_binds_full_canonical_summary(tmp_path: Path, illusion_id: str, field: str, value: float):
    _, payload = generate_artifact(illusion_id, output_dir=tmp_path, format_name=MediaFormat.NPZ)
    sidecar = Path(payload["manifest"])
    document = json.loads(sidecar.read_text(encoding="utf-8"))
    assert document["artifact"][field] != value
    document["artifact"][field] = value
    sidecar.write_text(json.dumps(document), encoding="utf-8")
    report = verify_manifest(sidecar)
    assert report["status"] == "failed", report
    assert "canonical full summary does not match decoded NPZ artifact" in report["errors"]


def test_exact_npz_rejects_false_temporal_statistics_and_framed_byte_count(tmp_path: Path):
    _, payload = generate_artifact("visual.apparent_motion", output_dir=tmp_path, format_name=MediaFormat.NPZ)
    sidecar = Path(payload["manifest"])
    document = json.loads(sidecar.read_text(encoding="utf-8"))
    document["artifact"]["temporal_deltas"] = [0.0] * (document["artifact"]["frames"] - 1)
    document["artifact"]["mean_temporal_delta"] = 0.0
    document["canonical"]["byte_count"] = 1
    sidecar.write_text(json.dumps(document), encoding="utf-8")
    report = verify_manifest(sidecar)
    assert report["status"] == "failed", report
    assert "canonical byte_count does not match decoded NPZ artifact" in report["errors"]
    assert "canonical full summary does not match decoded NPZ artifact" in report["errors"]


@pytest.mark.parametrize("field,value", [("taxonomy", None), ("parameters", {"nonsense": None}), ("canonical_digest", "bad")])
def test_actual_v1_schema_downgrade_cannot_bypass_provenance(tmp_path: Path, field: str, value: object):
    _, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path)
    sidecar = Path(payload["manifest"])
    document = json.loads(sidecar.read_text(encoding="utf-8"))
    document.update(schema_version="duckrabbit/artifact/v1", duration_seconds=None)
    document[field] = value
    sidecar.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ManifestValidationError):
        read_manifest(sidecar)
    with pytest.raises(ManifestValidationError):
        verify_manifest(sidecar)


def test_legitimate_v1_provenance_is_validated_and_media_reinspected(tmp_path: Path):
    from duckrabbit.render import build_manifest
    from duckrabbit.serialization import jsonable

    artifact, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path, format_name=MediaFormat.NPZ)
    sidecar = Path(payload["manifest"])
    encoded_document = json.loads(sidecar.read_text(encoding="utf-8"))
    document = jsonable(build_manifest("visual.duck_rabbit", default_parameters("visual.duck_rabbit"), artifact))
    document.update(encoding=encoded_document["encoding"], output=encoded_document["output"])
    sidecar.write_text(json.dumps(document), encoding="utf-8")
    assert read_manifest(sidecar)["verification"]["status"] == "unverified"
    report = verify_manifest(sidecar)
    assert report["status"] == "verified", report
    assert {"decoded_media", "canonical_digest", "canonical_full_summary"} <= set(report["checks"])
    assert "canonical_byte_count" not in report["checks"]  # v1 never declared the framed size.
    output = Path(payload["output"])
    output.write_bytes(output.read_bytes()[:100])
    with pytest.raises(MediaInspectionError):
        verify_manifest(sidecar)


@pytest.mark.parametrize("offset", [None, SpatialOffset(0.0), SpatialOffset(.2)])
def test_optional_spatial_offset_round_trips_typed_manifest(tmp_path: Path, offset: SpatialOffset | None):
    from duckrabbit.generators import VentriloquistParams

    _, payload = generate_artifact("audiovisual.ventriloquist", VentriloquistParams(visual_offset=offset), output_dir=tmp_path, format_name=MediaFormat.NPZ)
    sidecar = Path(payload["manifest"])
    assert read_manifest(sidecar)["parameters"]["visual_offset"] == (None if offset is None else {"value": offset.value})
    report = verify_manifest(sidecar)
    assert report["status"] == "verified", report


def test_two_frame_sixty_hz_gif_obeys_centisecond_clock_not_fixed_fps_tolerance(tmp_path: Path):
    from PIL import Image
    from duckrabbit.generators import ApparentMotionParams

    parameters = ApparentMotionParams(config=VideoConfig(frame_count=2, frame_rate=FrameRate(60)))
    _, payload = generate_artifact("visual.apparent_motion", parameters, output_dir=tmp_path)
    output, sidecar = Path(payload["output"]), Path(payload["manifest"])
    assert inspect_media(output).facts["frame_durations_ms"] == (20, 10)
    assert verify_manifest(sidecar)["status"] == "verified"
    with Image.open(output) as image:
        frames = []
        for index in range(image.n_frames):
            image.seek(index)
            frames.append(image.convert("RGB"))
    frames[0].save(output, format="GIF", save_all=True, append_images=frames[1:], duration=[20, 20], disposal=2)
    _refresh_encoding(sidecar, output)
    report = verify_manifest(sidecar)
    assert report["status"] == "failed", report
    assert any("gif_frame_durations_ms" in error for error in report["errors"])


def test_generation_raises_after_real_postencode_failure_and_preserves_evidence(tmp_path: Path):
    from duckrabbit.generators import ApparentMotionParams

    # Pillow coalesces identical GIF frames; the encoded count no longer agrees.
    parameters = ApparentMotionParams(config=VideoConfig(frame_count=2), bar_width=Normalized(0), displacement=Normalized(0))
    with pytest.raises(VerificationError, match="post-encode verification failed"):
        generate_artifact("visual.apparent_motion", parameters, output_dir=tmp_path)
    sidecar = tmp_path / "visual_apparent_motion.gif.json"
    document = json.loads(sidecar.read_text(encoding="utf-8"))
    assert document["verification"]["status"] == "failed"
    assert document["verification"]["errors"]
    assert (tmp_path / document["encoding"]["path"]).is_file()
