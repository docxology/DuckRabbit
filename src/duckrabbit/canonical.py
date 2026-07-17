"""Versioned canonical byte serialization for deterministic artifacts."""

from __future__ import annotations

import hashlib
import json
import struct
from collections.abc import Iterable

import numpy as np

from .artifacts import AudioBuffer, AudiovisualTimeline, CanonicalArtifact, ImageFrame, VideoSequence


CANONICAL_SCHEMA_VERSION = "duckrabbit/canonical/v1"


def _header(kind: str, metadata: dict[str, object]) -> bytes:
    payload = json.dumps(
        {"schema_version": CANONICAL_SCHEMA_VERSION, "kind": kind, **metadata},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return struct.pack("<Q", len(payload)) + payload


def _array_bytes(values: np.ndarray) -> bytes:
    normalized = np.ascontiguousarray(values, dtype=np.dtype("<f4"))
    return struct.pack("<Q", normalized.nbytes) + normalized.tobytes(order="C")


def canonical_chunks(artifact: CanonicalArtifact) -> Iterable[bytes]:
    """Yield unambiguous metadata and little-endian canonical array chunks."""
    if isinstance(artifact, ImageFrame):
        yield _header("image", {"mode": artifact.mode.value, "shape": list(artifact.pixels.shape), "dtype": "<f4"})
        yield _array_bytes(artifact.pixels)
        return
    if isinstance(artifact, AudioBuffer):
        yield _header("audio", {"shape": list(artifact.samples.shape), "dtype": "<f4", "sample_rate": artifact.sample_rate.value})
        yield _array_bytes(artifact.samples)
        return
    if isinstance(artifact, VideoSequence):
        yield _header(
            "video",
            {
                "shape": [artifact.frame_count, artifact.height, artifact.width, artifact.frames[0].channels],
                "mode": artifact.pixel_mode.value,
                "frame_rate": artifact.frame_rate.value,
                "dtype": "<f4",
            },
        )
        for frame in artifact.frames:
            yield _array_bytes(frame.pixels)
        return
    if isinstance(artifact, AudiovisualTimeline):
        yield _header(
            "audiovisual",
            {
                "sync_offset_ms": artifact.sync_offset.value,
                "spatial_offset": artifact.spatial_offset.value,
                "metadata": dict(sorted(artifact.metadata.items())),
            },
        )
        yield from canonical_chunks(artifact.audio)
        yield from canonical_chunks(artifact.video)
        return
    raise TypeError(f"unsupported artifact type: {type(artifact).__name__}")


def canonical_bytes(artifact: CanonicalArtifact) -> bytes:
    """Materialize the stable canonical representation for archives and hashing."""
    return b"".join(canonical_chunks(artifact))


def canonical_digest(artifact: CanonicalArtifact) -> str:
    """Return SHA-256 over versioned canonical bytes."""
    return hashlib.sha256(canonical_bytes(artifact)).hexdigest()
