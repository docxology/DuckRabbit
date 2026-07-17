"""v0.3 typed manifest, inspection, metrics, and observer-contract tests."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest
import numpy as np

import duckrabbit
import duckrabbit.inspection as inspection_module
from duckrabbit.artifacts import ArtifactManifest, _validate_artifact_summary
from duckrabbit.errors import BackendUnavailableError, ManifestValidationError, MediaInspectionError, ParameterValidationError, VerificationError
from duckrabbit.inspection import inspect_media, verify_manifest
from duckrabbit.media import read_npz, write_gif, write_npz, write_png, write_wav
from duckrabbit.parameters import CanonicalArchiveEncoding, GifEncoding, MediaFormat
from duckrabbit.manifest import CanonicalRecord, Manifest, RenderResult, VerificationReport, VerificationStatus, read_manifest, upconvert_v1_manifest, verify_file_hash
from duckrabbit.metrics import measure_artifact
from duckrabbit.observer import ObserverResponse, TrialSpec, aggregate_responses, randomized_trials
from duckrabbit.parameters import Seed
from duckrabbit.render import artifact_summary, build_manifest_v2, generate_artifact, render_artifact
from duckrabbit.schema import jsonable_parameter, parameter_schema
from duckrabbit.taxonomy import ImplementationStatus, validate_taxonomy_catalog


def test_v2_manifest_is_typed_and_schema_describes_nested_defaults(tmp_path: Path):
    artifact, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path)
    assert payload["schema_version"] == "duckrabbit/artifact/v2"
    assert payload["canonical"]["byte_order"] == "little"
    assert payload["verification"]["status"] == "verified"
    assert payload["metrics"]["artifact_type"] == "image"
    typed = build_manifest_v2("visual.duck_rabbit", duckrabbit.generators.default_parameters("visual.duck_rabbit"), artifact)
    assert isinstance(typed, Manifest)
    assert typed.parameter_schema.schema_version == "duckrabbit/parameters/v1"
    assert parameter_schema(duckrabbit.generators.default_parameters("visual.duck_rabbit")).fields
    result = render_artifact("visual.duck_rabbit", output_dir=tmp_path)
    assert result.manifest.encoding is not None
    assert isinstance(result.manifest.decoded_inspection, duckrabbit.DecodedInspection)
    assert result.manifest.verification.status is VerificationStatus.VERIFIED

    with pytest.raises(ManifestValidationError, match="taxonomy"):
        Manifest(**{**typed.__dict__, "taxonomy": object()})
    with pytest.raises(ManifestValidationError, match="canonical digest"):
        Manifest(**{**typed.__dict__, "canonical": type(typed.canonical)("duckrabbit/canonical/v1", "sha256", "bad", "little", "<f4", 1)})
    with pytest.raises(ManifestValidationError, match="unknown parameter"):
        Manifest(**{**typed.__dict__, "parameters": {**typed.parameters, "unexpected": 1}})
    with pytest.raises(ManifestValidationError, match="parameter field config"):
        Manifest(**{**typed.__dict__, "parameters": {**typed.parameters, "config": 0}})
    with pytest.raises(TypeError):
        typed.parameters["duck_weight"] = 0.1  # type: ignore[index]
    with pytest.raises(TypeError):
        typed.parameters["config"]["width"] = 8  # type: ignore[index]
    decoded = result.manifest.decoded_inspection
    assert decoded is not None
    with pytest.raises(TypeError):
        decoded.facts["width"] = 8  # type: ignore[index]


def test_manifest_summary_relationships_are_verified_not_only_present():
    typed = build_manifest_v2("visual.duck_rabbit", duckrabbit.generators.default_parameters("visual.duck_rabbit"), duckrabbit.generate("visual.duck_rabbit"))
    for field, value, message in (
        ("nbytes", 1, "nbytes"),
        ("channels", 3, "channels disagree"),
        ("min_value", -1.0, "values must"),
    ):
        with pytest.raises(ManifestValidationError, match=message):
            Manifest(**{**typed.__dict__, "artifact": {**typed.artifact, field: value}})
    audio = build_manifest_v2("audio.missing_fundamental", duckrabbit.generators.default_parameters("audio.missing_fundamental"), duckrabbit.generate("audio.missing_fundamental"))
    with pytest.raises(ManifestValidationError, match="duration disagrees"):
        Manifest(**{**audio.__dict__, "artifact": {**audio.artifact, "duration_seconds": 99.0}})


def test_artifact_summary_negative_controls_cover_each_modality_contract():
    def invalid(summary, field, value, message):
        candidate = dict(summary)
        if field == "missing":
            candidate.pop(value, None)
        else:
            candidate[field] = value
        with pytest.raises(ParameterValidationError, match=message):
            _validate_artifact_summary(candidate)

    image = artifact_summary(duckrabbit.generate("visual.duck_rabbit"))
    string_mode_image = dict(image)
    string_mode_image["mode"] = "L"
    _validate_artifact_summary(string_mode_image)
    invalid(image, "type", "bad", "unsupported type")
    invalid(image, "missing", "mode", "missing fields")
    invalid(image, "width", 0, "positive integer")
    invalid(image, "mode", "bad", "mode")
    invalid(image, "channels", 3, "channels disagree")
    invalid(image, "dtype", "u8", "dtype")
    invalid(image, "min_value", float("nan"), "finite")
    invalid(image, "min_value", -0.1, "values must")
    invalid(image, "nbytes", 1, "nbytes")

    audio = artifact_summary(duckrabbit.generate("audio.missing_fundamental"))
    invalid(audio, "dtype", "i16", "dtype")
    invalid(audio, "sample_rate", 999, "sample_rate")
    invalid(audio, "channels", 3, "channels")
    invalid(audio, "duration_seconds", 0, "out of range")
    invalid(audio, "rms", 0.9, "out of range")
    invalid(audio, "duration_seconds", 99.0, "duration disagrees")
    invalid(audio, "nbytes", 1, "nbytes")

    video = artifact_summary(duckrabbit.generate("visual.apparent_motion"))
    invalid(video, "mode", "bad", "mode")
    invalid(video, "dtype", "u8", "dtype")
    invalid(video, "frame_rate", 0, "frame_rate")
    invalid(video, "duration_seconds", 99.0, "duration disagrees")
    invalid(video, "temporal_deltas", [], "frames - 1")
    invalid(video, "temporal_deltas", [2.0] * (video["frames"] - 1), "temporal_deltas must be finite")
    invalid(video, "mean_temporal_delta", 0.0, "mean_temporal_delta disagrees")
    invalid(video, "nbytes", 1, "nbytes")

    audiovisual = artifact_summary(duckrabbit.generate("audiovisual.sound_induced_flash"))
    invalid(audiovisual, "sync_offset_ms", 10001, "offsets")
    invalid(audiovisual, "spatial_offset", 2, "offsets")
    invalid(audiovisual, "duration_seconds", 99.0, "duration disagrees")
    invalid(audiovisual, "audio_start_seconds", 99.0, "audio_start_seconds")
    invalid(audiovisual, "video_start_seconds", 99.0, "video_start_seconds")
    invalid(audiovisual, "presentation_duration_seconds", 99.0, "presentation duration")
    invalid(audiovisual, "nbytes", 1, "nbytes")


def test_v1_manifest_is_strict_and_upconverts(tmp_path: Path):
    artifact, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path)
    v1 = duckrabbit.render.build_manifest("visual.duck_rabbit", duckrabbit.generators.default_parameters("visual.duck_rabbit"), artifact)
    v1_payload = duckrabbit.render.jsonable(v1)
    assert isinstance(v1_payload, dict)
    converted = upconvert_v1_manifest(v1_payload)
    assert converted["schema_version"] == "duckrabbit/artifact/v2"
    assert converted["verification"]["status"] == "unverified"
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(v1_payload), encoding="utf-8")
    assert read_manifest(path)["legacy_manifest"] == "duckrabbit/artifact/v1"

    with pytest.raises(ParameterValidationError, match="modality"):
        ArtifactManifest(**{**v1.__dict__, "modality": ("visual",)})  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="canonical_digest"):
        ArtifactManifest(**{**v1.__dict__, "canonical_digest": "bad"})


def test_npz_decode_and_manifest_verification_negative_control(tmp_path: Path):
    _, payload = generate_artifact("audio.missing_fundamental", output_dir=tmp_path, format_name=MediaFormat.NPZ)
    output = Path(payload["output"])
    assert inspect_media(output).kind == "audio"
    original = duckrabbit.generate("audio.missing_fundamental")
    restored = read_npz(output)
    assert duckrabbit.render.artifact_digest(original) == duckrabbit.render.artifact_digest(restored)
    manifest_path = Path(payload["manifest"])
    report = verify_manifest(manifest_path)
    assert report["status"] == "verified"

    with np.load(output, allow_pickle=False) as archive:
        arrays = {key: archive[key].copy() for key in archive.files}
    arrays["samples"].flat[0] = np.float32(float(arrays["samples"].flat[0]) + 0.01)
    replacement = output.with_name("replacement.npz")
    np.savez_compressed(replacement, **arrays)
    replacement.replace(output)
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    document["encoding"]["sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    tampered = verify_manifest(manifest_path)
    assert tampered["status"] == "failed"
    assert any("canonical digest" in error for error in tampered["errors"])

    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    document.pop("canonical", None)
    document.pop("canonical_digest", None)
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    missing_digest = verify_manifest(manifest_path)
    assert missing_digest["status"] == "failed"
    assert any("canonical digest is missing" in error for error in missing_digest["errors"])

    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    document["encoding"]["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    failed = verify_manifest(manifest_path)
    assert failed["status"] == "failed"
    assert "encoded SHA-256" in failed["errors"][0]


def test_metrics_and_observer_records_are_reproducible():
    artifact = duckrabbit.generate("visual.apparent_motion")
    metrics = measure_artifact(artifact)
    assert metrics.values["frames"] == artifact.frame_count
    trials = tuple(
        TrialSpec(f"trial-{index}", "visual.duck_rabbit", "default", Seed(index), ("duck", "rabbit"))
        for index in range(4)
    )
    assert randomized_trials(trials, Seed(7)) == randomized_trials(trials, Seed(7))
    responses = tuple(ObserverResponse(trial.trial_id, "observer-a", "duck", 0.4) for trial in trials)
    aggregate = aggregate_responses(trials, responses)
    assert aggregate[0].sample_count == 4
    with pytest.raises(ValueError, match="not allowed"):
        aggregate_responses(trials, (ObserverResponse("trial-0", "observer-a", "cat", 0.4),))


def test_real_inspection_matrix_and_media_negative_controls(tmp_path: Path):
    image = duckrabbit.generate("visual.duck_rabbit")
    video = duckrabbit.generate("visual.apparent_motion")
    audio = duckrabbit.generate("audio.missing_fundamental")
    png = write_png(image, tmp_path / "image.png")
    gif = write_gif(video, tmp_path / "video.gif", encoding=GifEncoding(loop=2))
    wav = write_wav(audio, tmp_path / "audio.wav")
    assert inspect_media(png).kind == "image"
    assert inspect_media(gif).kind == "video"
    assert inspect_media(wav).kind == "audio"
    nested_png = write_png(image, tmp_path / "nested" / "atomic.png")
    assert nested_png.is_file()
    with pytest.raises(FileExistsError, match="overwrite"):
        write_png(image, nested_png, overwrite=False)
    with pytest.raises(Exception, match="does not exist"):
        inspect_media(tmp_path / "missing.png")
    with pytest.raises(Exception, match="unsupported inspection"):
        inspect_media(png, "flac")
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not an image")
    with pytest.raises(Exception, match="cannot decode"):
        inspect_media(broken)
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        _, mp4_payload = generate_artifact("visual.apparent_motion", output_dir=tmp_path, format_name=MediaFormat.MP4)
        assert inspect_media(Path(mp4_payload["output"])).kind == "video"


def test_npz_round_trips_every_canonical_kind(tmp_path: Path):
    for illusion_id in (
        "visual.duck_rabbit",
        "audio.missing_fundamental",
        "visual.apparent_motion",
        "audiovisual.sound_induced_flash",
    ):
        original = duckrabbit.generate(illusion_id)
        path = tmp_path / f"{illusion_id.replace('.', '_')}.npz"
        write_npz(original, path, encoding=CanonicalArchiveEncoding(compressed=False))
        restored = read_npz(path)
        assert duckrabbit.render.artifact_digest(original) == duckrabbit.render.artifact_digest(restored)
    with pytest.raises(Exception, match="NPZ encoding"):
        write_npz(duckrabbit.generate("visual.duck_rabbit"), tmp_path / "bad.npz", encoding=object())  # type: ignore[arg-type]


def test_verification_checks_every_real_container_and_timeline_kind(tmp_path: Path):
    cases = (
        ("visual.duck_rabbit", MediaFormat.PNG),
        ("audio.missing_fundamental", MediaFormat.WAV),
        ("visual.apparent_motion", MediaFormat.GIF),
        ("audiovisual.sound_induced_flash", MediaFormat.NPZ),
    )
    for illusion_id, format_name in cases:
        output_dir = tmp_path / format_name.value
        _, payload = generate_artifact(illusion_id, output_dir=output_dir, format_name=format_name)
        report = verify_manifest(Path(payload["manifest"]))
        assert report["status"] == "verified", report
        assert "decoded_media" in report["checks"]
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        for illusion_id in ("visual.apparent_motion", "audiovisual.sound_induced_flash"):
            output_dir = tmp_path / "mp4" / illusion_id.replace(".", "_")
            _, payload = generate_artifact(illusion_id, output_dir=output_dir, format_name=MediaFormat.MP4)
            report = verify_manifest(Path(payload["manifest"]))
            assert report["status"] == "verified", report
        for offset in (120.0, -120.0):
            parameters = duckrabbit.generators.SoundInducedFlashParams(
                config=duckrabbit.AudiovisualConfig(sync_offset=duckrabbit.SyncOffsetMs(offset))
            )
            output_dir = tmp_path / "sync" / str(offset)
            _, payload = generate_artifact(
                "audiovisual.sound_induced_flash",
                parameters,
                output_dir=output_dir,
                format_name=MediaFormat.MP4,
            )
            report = verify_manifest(Path(payload["manifest"]))
            assert report["status"] == "verified", report


def test_inspection_normalization_helpers_cover_malformed_stream_metadata():
    assert inspection_module._frame_rate_from_inspection({"r_frame_rate": "12/1"}) == 12.0
    assert inspection_module._frame_rate_from_inspection({"r_frame_rate": "12/0"}) is None
    assert inspection_module._frame_rate_from_inspection({"duration_ms": 80}) == 12.5
    assert inspection_module._frame_rate_from_inspection({}) is None
    assert inspection_module._video_duration_from_inspection({"duration_seconds": 0.5}) == 0.5
    assert inspection_module._video_duration_from_inspection({"duration_ms": 80, "frames": 6}) == pytest.approx(0.48)
    assert inspection_module._video_duration_from_inspection({}) is None
    stream = {"streams": [{"codec_type": "video", "width": 8}]}
    assert inspection_module._stream_of_type(stream, "video") == stream["streams"][0]
    assert inspection_module._stream_of_type({"streams": "bad"}, "video") is None
    assert inspection_module._stream_float({"duration": "bad"}, "duration", 1.0) == 1.0
    assert inspection_module._stream_float({}, "duration", 1.0) == 1.0
    assert inspection_module._stream_float({"duration": "2.5"}, "duration", 1.0) == 2.5
    errors: list[str] = []
    checks: list[str] = []
    inspection_module._compare_expected_facts(
        {"type": "image", "width": "expected", "height": 8, "channels": 1},
        duckrabbit.DecodedInspection(MediaFormat.PNG, duckrabbit.BackendKind.PILLOW, "image", {"width": "observed", "height": 8, "mode": "L"}),
        errors,
        checks,
    )
    assert any("decoded width" in error for error in errors)


def test_inspection_fact_comparisons_cover_valid_modality_paths():
    cases = (
        (
            {"type": "image", "width": 4, "height": 3, "channels": 3},
            duckrabbit.DecodedInspection(MediaFormat.NPZ, duckrabbit.BackendKind.NUMPY, "image", {"width": 4, "height": 3, "mode": "RGB", "pixels_shape": [3, 4, 3]}),
        ),
        (
            {"type": "audio", "channels": 2, "sample_rate": 10, "samples": 4, "duration_seconds": 0.4},
            duckrabbit.DecodedInspection(MediaFormat.NPZ, duckrabbit.BackendKind.NUMPY, "audio", {"channels": 2, "sample_rate": 10, "frames": 4, "duration_seconds": 0.4, "samples_shape": [4, 2]}),
        ),
        (
            {"type": "video", "width": 4, "height": 3, "frames": 2, "frame_rate": 10, "duration_seconds": 0.2},
            duckrabbit.DecodedInspection(MediaFormat.NPZ, duckrabbit.BackendKind.NUMPY, "video", {"width": 4, "height": 3, "frames": 2, "frame_rate": 10, "duration_seconds": 0.2, "frames_shape": [2, 3, 4]}),
        ),
    )
    for expected, inspection in cases:
        errors: list[str] = []
        checks: list[str] = []
        inspection_module._compare_expected_facts(expected, inspection, errors, checks)
        assert errors == []
        assert checks

    audiovisual = {
        "type": "audiovisual",
        "audio": {"type": "audio", "channels": 2, "sample_rate": 10, "samples": 4, "duration_seconds": 0.4},
        "video": {"type": "video", "width": 4, "height": 3, "frames": 2, "frame_rate": 10, "duration_seconds": 0.2},
        "sync_offset_ms": 5.0,
        "presentation_duration_seconds": 0.405,
    }
    errors = []
    checks = []
    inspection_module._compare_expected_facts(
        audiovisual,
        duckrabbit.DecodedInspection(
            MediaFormat.NPZ,
            duckrabbit.BackendKind.NUMPY,
            "audiovisual",
            {
                "audio_channels": 2,
                "sample_rate": 10,
                "audio_frames": 4,
                "audio_duration_seconds": 0.4,
                "video_width": 4,
                "video_height": 3,
                "video_frames": 2,
                "video_duration_seconds": 0.2,
                "frame_rate": 10,
                "sync_offset_ms": 5.0,
            },
        ),
        errors,
        checks,
    )
    assert errors == []
    assert "decoded_presentation_duration_seconds" in checks


def test_manifest_and_schema_boundary_negative_controls(tmp_path: Path):
    typed = build_manifest_v2("visual.duck_rabbit", duckrabbit.generators.default_parameters("visual.duck_rabbit"), duckrabbit.generate("visual.duck_rabbit"))
    with pytest.raises(ManifestValidationError, match="verification status"):
        type(typed.verification)("verified")  # type: ignore[arg-type]
    with pytest.raises(ManifestValidationError, match="failed verification"):
        type(typed.verification)(VerificationStatus.FAILED)
    with pytest.raises(ManifestValidationError, match="byte_count"):
        type(typed.canonical)("duckrabbit/canonical/v1", "sha256", "a" * 64, "little", "<f4", 0)
    with pytest.raises(ManifestValidationError, match="unsupported canonical"):
        type(typed.canonical)("duckrabbit/canonical/v2", "sha256", "a" * 64, "little", "<f4", 1)
    with pytest.raises(ManifestValidationError, match="metrics"):
        Manifest(**{**typed.__dict__, "metrics": []})  # type: ignore[arg-type]
    with pytest.raises(ParameterValidationError, match="dataclass"):
        parameter_schema(object())
    with pytest.raises(ParameterValidationError, match="serializable"):
        jsonable_parameter(object())
    entry = duckrabbit.taxonomy_entries()[0]
    with pytest.raises(ValueError, match="unique"):
        validate_taxonomy_catalog((entry, entry))


def test_objective_metrics_cover_audio_visual_and_observer_errors():
    audio_metrics = measure_artifact(duckrabbit.generate("audio.shepard_tone"))
    av_metrics = measure_artifact(duckrabbit.generate("audiovisual.sound_induced_flash"))
    assert audio_metrics.values["spectral_centroid_hz"] > 0
    assert av_metrics.values["audio_rms"] >= 0
    with pytest.raises(ValueError, match="identity"):
        TrialSpec("", "visual.duck_rabbit", "condition", 0, ("yes",))
    with pytest.raises(ValueError, match="response labels"):
        TrialSpec("t", "visual.duck_rabbit", "condition", 0, ())
    with pytest.raises(ValueError, match="identity"):
        ObserverResponse("", "observer", "yes", 0.2)
    with pytest.raises(ValueError, match="sample_count"):
        duckrabbit.ObserverAggregate("visual.duck_rabbit", "condition", (("yes", 1),), 0.2, 0)
    with pytest.raises(ValueError, match="unknown trial"):
        aggregate_responses((), (ObserverResponse("missing", "observer", "yes", 0.2),))


def test_manifest_nested_contracts_and_file_helpers(tmp_path: Path):
    parameters = duckrabbit.generators.default_parameters("visual.duck_rabbit")
    typed = build_manifest_v2("visual.duck_rabbit", parameters, duckrabbit.generate("visual.duck_rabbit"))

    with pytest.raises(ManifestValidationError, match="little-endian"):
        CanonicalRecord("duckrabbit/canonical/v1", "md5", "a" * 64, "little", "<f4", 1)
    with pytest.raises(ManifestValidationError, match="lowercase"):
        CanonicalRecord("duckrabbit/canonical/v1", "sha256", "A" * 64, "little", "<f4", 1)
    with pytest.raises(ManifestValidationError, match="positive"):
        CanonicalRecord("duckrabbit/canonical/v1", "sha256", "a" * 64, "little", "<f4", 0)
    with pytest.raises(ManifestValidationError, match="checks"):
        VerificationReport(VerificationStatus.VERIFIED, checks=(1,))  # type: ignore[arg-type]
    with pytest.raises(ManifestValidationError, match="failed verification"):
        VerificationReport(VerificationStatus.FAILED)

    invalid_manifest_fields = (
        ("schema_version", "duckrabbit/artifact/v9", "unsupported manifest"),
        ("package_version", "", "manifest package_version"),
        ("generator_version", "", "manifest generator_version"),
        ("illusion_id", "visual.other", "identity"),
        ("implementation_status", "implemented", "implementation_status must"),
        ("evidence_status", "literature_backed_engineering_entry", "evidence_status must"),
        ("claim_level", "canonical_stimulus", "claim_level must"),
        ("modality", ("visual",), "modality must"),
        ("implementation_status", ImplementationStatus.PLANNED, "taxonomy disagrees"),
        ("parameter_schema", object(), "parameter_schema"),
        ("parameters", [], "parameters must"),
        ("seed", "not-a-seed", "signed 64-bit"),
        ("artifact", object(), "artifact summary"),
        ("canonical", object(), "canonical record"),
        ("verification", object(), "verification report"),
        ("metrics", [], "metrics"),
        ("encoding", object(), "encoding"),
        ("decoded_inspection", [], "decoded inspection"),
        ("legacy_manifest", 4, "legacy_manifest"),
    )
    for field, value, message in invalid_manifest_fields:
        with pytest.raises((ManifestValidationError, ParameterValidationError), match=message):
            Manifest(**{**typed.__dict__, field: value})

    written = typed.write(tmp_path / "nested" / "typed.json")
    assert read_manifest(written)["schema_version"] == "duckrabbit/artifact/v2"
    digest = hashlib.sha256(written.read_bytes()).hexdigest()
    assert verify_file_hash(written, digest)
    assert not verify_file_hash(written, "0" * 64)
    assert RenderResult(typed.artifact and duckrabbit.generate("visual.duck_rabbit"), typed, written, None).to_dict()["manifest"] is None

    with pytest.raises(ManifestValidationError, match="upconversion"):
        upconvert_v1_manifest({"schema_version": "duckrabbit/artifact/v2"})
    missing = tmp_path / "missing.json"
    with pytest.raises(ManifestValidationError, match="cannot read"):
        read_manifest(missing)
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("not json", encoding="utf-8")
    with pytest.raises(ManifestValidationError, match="cannot read"):
        read_manifest(invalid_json)
    non_object = tmp_path / "array.json"
    non_object.write_text("[]", encoding="utf-8")
    with pytest.raises(ManifestValidationError, match="object"):
        read_manifest(non_object)
    unsupported = tmp_path / "unsupported.json"
    unsupported.write_text(json.dumps({"schema_version": "duckrabbit/artifact/v9"}), encoding="utf-8")
    with pytest.raises(ManifestValidationError, match="unsupported manifest"):
        read_manifest(unsupported)


def test_inspection_capability_and_verification_boundaries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    bad_wav = tmp_path / "bad.wav"
    bad_wav.write_bytes(b"RIFF but not a wave")
    with pytest.raises(MediaInspectionError, match="cannot decode WAV"):
        inspect_media(bad_wav)
    bad_npz = tmp_path / "bad.npz"
    bad_npz.write_bytes(b"not an archive")
    with pytest.raises(MediaInspectionError, match="cannot decode NPZ"):
        inspect_media(bad_npz)
    fake_mp4 = tmp_path / "fake.mp4"
    fake_mp4.write_bytes(b"mp4")
    monkeypatch.setattr(inspection_module.shutil, "which", lambda _: None)
    with pytest.raises(BackendUnavailableError, match="ffprobe"):
        inspect_media(fake_mp4, MediaFormat.MP4)
    monkeypatch.setattr(inspection_module.shutil, "which", lambda _: "ffprobe")
    monkeypatch.setattr(inspection_module.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(stdout="bad json"))
    with pytest.raises(MediaInspectionError, match="ffprobe could not inspect"):
        inspect_media(fake_mp4, MediaFormat.MP4)
    monkeypatch.setattr(inspection_module.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(stdout=json.dumps({"streams": []})))
    with pytest.raises(MediaInspectionError, match="no streams"):
        inspect_media(fake_mp4, MediaFormat.MP4)

    _, payload = generate_artifact("visual.duck_rabbit", output_dir=tmp_path)
    manifest_path = Path(payload["manifest"])
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    output = Path(payload["output"])
    original_artifact = dict(document["artifact"])
    document["encoding"].pop("sha256")
    document["encoding"]["path"] = output.name
    document["output"] = output.name
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    verified = verify_manifest(manifest_path)
    assert verified["status"] == "failed"
    assert any("SHA-256 is missing" in error for error in verified["errors"])
    assert "encoded_sha256" not in verified["checks"]

    document["artifact"] = {"type": "image"}
    document["encoding"]["path"] = output.name
    document["output"] = output.name
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    malformed = verify_manifest(manifest_path)
    assert malformed["status"] == "failed"
    assert any("artifact summary is missing" in error for error in malformed["errors"])

    document["artifact"] = {**original_artifact, "type": "unknown"}
    document["encoding"]["sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    document["encoding"]["format"] = "wav"
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    unsupported_type = verify_manifest(manifest_path)
    assert unsupported_type["status"] == "failed"
    assert any("artifact type is unsupported" in error for error in unsupported_type["errors"])
    assert any("format does not match" in error for error in unsupported_type["errors"])

    document["artifact"] = original_artifact
    document["encoding"]["format"] = "png"
    document["encoding"]["path"] = None
    document["output"] = output.name
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    missing_encoding_path = verify_manifest(manifest_path)
    assert missing_encoding_path["status"] == "failed"
    assert any("encoding path is missing" in error for error in missing_encoding_path["errors"])

    document["encoding"]["path"] = output.name
    document["encoding"]["sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    document["encoding"]["format"] = None
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    missing_format = verify_manifest(manifest_path)
    assert missing_format["status"] == "failed"
    assert any("format is missing" in error for error in missing_format["errors"])
    document["encoding"]["format"] = "not-a-format"
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    unsupported_format = verify_manifest(manifest_path)
    assert unsupported_format["status"] == "failed"
    assert any("format is unsupported" in error for error in unsupported_format["errors"])
    document["encoding"]["format"] = "png"
    document["output"] = "other.png"
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    conflicting_output = verify_manifest(manifest_path)
    assert conflicting_output["status"] == "failed"
    assert any("top-level output path conflicts" in error for error in conflicting_output["errors"])
    document["encoding"] = None
    document["output"] = output.name
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(VerificationError, match="encoding is missing"):
        verify_manifest(manifest_path)
    document["encoding"] = {}
    document["output"] = None
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(VerificationError, match="does not identify"):
        verify_manifest(manifest_path)

    shutil.copy2(output, tmp_path.parent / "outside.png")
    document["encoding"] = {"path": "../outside.png", "format": "png", "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
    document["encoding"]["path"] = "../outside.png"
    document["encoding"]["format"] = "png"
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(VerificationError, match="within the manifest directory"):
        verify_manifest(manifest_path)

    document["encoding"]["path"] = output.name
    document["output"] = output.name
    document["artifact"] = {**original_artifact, "width": original_artifact["width"] + 1}
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    failed = verify_manifest(manifest_path)
    assert failed["status"] == "failed"
    assert any("decoded width" in error for error in failed["errors"])
    document["artifact"] = None
    document["encoding"]["path"] = "missing.png"
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(VerificationError, match="does not exist"):
        verify_manifest(manifest_path)
    document["encoding"] = None
    document["output"] = None
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(VerificationError, match="does not identify"):
        verify_manifest(manifest_path)


def test_new_generator_parameter_boundaries():
    generators = duckrabbit.generators
    with pytest.raises(TypeError, match="ImageConfig"):
        generators.PoggendorffParams(config=object())
    with pytest.raises(ParameterValidationError, match="occluder_fraction"):
        generators.PoggendorffParams(occluder_fraction=duckrabbit.Normalized(0.0))
    with pytest.raises(ParameterValidationError, match="target_separation"):
        generators.PonzoParams(target_separation=duckrabbit.Normalized(0.0))
    with pytest.raises(ParameterValidationError, match="inducer_radius"):
        generators.KanizsaParams(inducer_radius=duckrabbit.Normalized(0.0))
    with pytest.raises(ValueError, match="context_count"):
        generators.EbbinghausParams(context_count=3)
    with pytest.raises(ValueError, match="partial_count"):
        generators.TritoneParadoxParams(partial_count=1)
    with pytest.raises(ValueError, match="six semitones"):
        generators.TritoneParadoxParams(interval_semitones=5)
    with pytest.raises(ParameterValidationError, match="stereo"):
        generators.OctaveIllusionParams(config=duckrabbit.AudioConfig(channels=1))
    with pytest.raises(ParameterValidationError, match="one octave"):
        generators.OctaveIllusionParams(high_frequency=duckrabbit.FrequencyHz(330.0))
    with pytest.raises(ValueError, match="cycles"):
        generators.OctaveIllusionParams(cycles=0)
    with pytest.raises(ParameterValidationError, match="Nyquist"):
        generators.TemporalVentriloquismParams(click_frequency=duckrabbit.FrequencyHz(24000.0))
    with pytest.raises(TypeError, match="AudiovisualConfig"):
        generators.TemporalVentriloquismParams(config=object())
    with pytest.raises(TypeError, match="unsupported artifact"):
        measure_artifact("not-an-artifact")  # type: ignore[arg-type]
