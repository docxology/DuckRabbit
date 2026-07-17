"""Validated input-fixture contracts for evidence-dependent illusion families."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from numbers import Integral
from pathlib import Path
from typing import Mapping

from .errors import ParameterValidationError
from .parameters import DurationSeconds, SampleRate

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_KEYS = frozenset(
    {
        "fixture_id",
        "audio_path",
        "video_path",
        "audio_sha256",
        "video_sha256",
        "duration_seconds",
        "sample_rate_hz",
        "channels",
    }
)


@dataclass(frozen=True)
class SpeechFixtureManifest:
    """Portable manifest for a reproducible speech audio/video fixture.

    This is deliberately a fixture contract, not a claim that a speech sample
    is perceptually validated. McGurk remains ``input_required`` until a real
    fixture and an observer-level validation protocol are supplied.
    """

    fixture_id: str
    audio_path: str
    video_path: str
    audio_sha256: str
    video_sha256: str
    duration: DurationSeconds
    sample_rate: SampleRate
    channels: int

    def __post_init__(self) -> None:
        for name in ("fixture_id", "audio_path", "video_path"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ParameterValidationError(f"{name} must be a non-empty string")
        for name in ("audio_path", "video_path"):
            if Path(getattr(self, name)).is_absolute() or ".." in Path(getattr(self, name)).parts:
                raise ParameterValidationError(f"{name} must be a relative path inside the fixture root")
        for name in ("audio_sha256", "video_sha256"):
            digest = getattr(self, name)
            if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
                raise ParameterValidationError(f"{name} must be a lowercase SHA-256 digest")
        if not isinstance(self.duration, DurationSeconds):
            raise ParameterValidationError("duration must be DurationSeconds")
        if not isinstance(self.sample_rate, SampleRate):
            raise ParameterValidationError("sample_rate must be SampleRate")
        if isinstance(self.channels, bool) or not isinstance(self.channels, Integral) or self.channels not in {1, 2}:
            raise ParameterValidationError("channels must be 1 or 2")
        object.__setattr__(self, "channels", int(self.channels))


def speech_fixture_from_mapping(payload: Mapping[str, object]) -> SpeechFixtureManifest:
    """Parse a strict JSON-compatible fixture manifest mapping."""
    if not isinstance(payload, Mapping):
        raise ParameterValidationError("speech fixture manifest must be a mapping")
    missing = _REQUIRED_KEYS - payload.keys()
    unknown = payload.keys() - _REQUIRED_KEYS
    if missing:
        raise ParameterValidationError(f"speech fixture manifest missing keys: {sorted(missing)}")
    if unknown:
        raise ParameterValidationError(f"speech fixture manifest has unknown keys: {sorted(unknown)}")
    return SpeechFixtureManifest(
        fixture_id=payload["fixture_id"],  # type: ignore[arg-type]
        audio_path=payload["audio_path"],  # type: ignore[arg-type]
        video_path=payload["video_path"],  # type: ignore[arg-type]
        audio_sha256=payload["audio_sha256"],  # type: ignore[arg-type]
        video_sha256=payload["video_sha256"],  # type: ignore[arg-type]
        duration=DurationSeconds(payload["duration_seconds"]),  # type: ignore[arg-type]
        sample_rate=SampleRate(payload["sample_rate_hz"]),  # type: ignore[arg-type]
        channels=payload["channels"],  # type: ignore[arg-type]
    )


def verify_speech_fixture_files(manifest: SpeechFixtureManifest, root: Path) -> None:
    """Verify fixture existence, containment, and declared SHA-256 digests."""
    root = Path(root).resolve()
    for relative, expected in (
        (manifest.audio_path, manifest.audio_sha256),
        (manifest.video_path, manifest.video_sha256),
    ):
        path = (root / relative).resolve()
        if path != root and root not in path.parents:
            raise ParameterValidationError(f"fixture path escapes root: {relative}")
        if not path.is_file():
            raise ParameterValidationError(f"fixture file does not exist: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ParameterValidationError(f"fixture digest mismatch for {relative}")
