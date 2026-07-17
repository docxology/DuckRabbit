"""Executable checks for evidence-gated input fixture contracts."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from duckrabbit.errors import ParameterValidationError
from duckrabbit.fixtures import SpeechFixtureManifest, speech_fixture_from_mapping, verify_speech_fixture_files
from duckrabbit.parameters import DurationSeconds, SampleRate


def _payload(audio: bytes = b"audio", video: bytes = b"video") -> tuple[dict[str, object], bytes, bytes]:
    return (
        {
            "fixture_id": "example/mcgurk-01",
            "audio_path": "audio.wav",
            "video_path": "video.mp4",
            "audio_sha256": hashlib.sha256(audio).hexdigest(),
            "video_sha256": hashlib.sha256(video).hexdigest(),
            "duration_seconds": 1.25,
            "sample_rate_hz": 16000,
            "channels": 1,
        },
        audio,
        video,
    )


def test_speech_fixture_manifest_parses_and_verifies_hashes(tmp_path: Path):
    payload, audio, video = _payload()
    (tmp_path / "audio.wav").write_bytes(audio)
    (tmp_path / "video.mp4").write_bytes(video)
    manifest = speech_fixture_from_mapping(payload)
    assert isinstance(manifest, SpeechFixtureManifest)
    assert manifest.duration == DurationSeconds(1.25)
    assert manifest.sample_rate == SampleRate(16000)
    verify_speech_fixture_files(manifest, tmp_path)

    (tmp_path / "audio.wav").write_bytes(b"changed")
    with pytest.raises(ParameterValidationError, match="digest mismatch"):
        verify_speech_fixture_files(manifest, tmp_path)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda value: value.pop("fixture_id"), "missing keys"),
        (lambda value: value.update(extra=True), "unknown keys"),
        (lambda value: value.update(audio_path="/tmp/audio.wav"), "relative path"),
        (lambda value: value.update(audio_sha256="bad"), "SHA-256"),
        (lambda value: value.update(channels=3), "channels"),
    ],
)
def test_speech_fixture_contract_rejects_unsafe_or_incomplete_payloads(change, message):
    payload, _, _ = _payload()
    change(payload)
    with pytest.raises(ParameterValidationError, match=message):
        speech_fixture_from_mapping(payload)


def test_speech_fixture_verifier_rejects_missing_and_escaping_files(tmp_path: Path):
    payload, _, _ = _payload()
    manifest = speech_fixture_from_mapping(payload)
    with pytest.raises(ParameterValidationError, match="does not exist"):
        verify_speech_fixture_files(manifest, tmp_path)
    escaping = dict(payload, audio_path="../audio.wav")
    with pytest.raises(ParameterValidationError, match="relative path"):
        speech_fixture_from_mapping(escaping)

