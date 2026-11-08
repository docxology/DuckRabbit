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


def _array_chunks(values: np.ndarray, *, copy_arrays: bool) -> Iterable[bytes | memoryview]:
    normalized = np.ascontiguousarray(values, dtype=np.dtype("<f4"))
    prefix = struct.pack("<Q", normalized.nbytes)
    if copy_arrays:
        yield prefix + normalized.tobytes(order="C")
    else:
        yield prefix
        yield memoryview(normalized).cast("B")


def _canonical_chunks(artifact: CanonicalArtifact, *, copy_arrays: bool) -> Iterable[bytes | memoryview]:
    if isinstance(artifact, ImageFrame):
        yield _header("image", {"mode": artifact.mode.value, "shape": list(artifact.pixels.shape), "dtype": "<f4"})
        yield from _array_chunks(artifact.pixels, copy_arrays=copy_arrays)
        return
    if isinstance(artifact, AudioBuffer):
        yield _header("audio", {"shape": list(artifact.samples.shape), "dtype": "<f4", "sample_rate": artifact.sample_rate.value})
        yield from _array_chunks(artifact.samples, copy_arrays=copy_arrays)
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
            yield from _array_chunks(frame.pixels, copy_arrays=copy_arrays)
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
        yield from _canonical_chunks(artifact.audio, copy_arrays=copy_arrays)
        yield from _canonical_chunks(artifact.video, copy_arrays=copy_arrays)
        return
    raise TypeError(f"unsupported artifact type: {type(artifact).__name__}")


def canonical_chunks(artifact: CanonicalArtifact) -> Iterable[bytes]:
    """Yield stable byte chunks, preserving the public serialization boundaries."""
    yield from _canonical_chunks(artifact, copy_arrays=True)


def canonical_bytes(artifact: CanonicalArtifact) -> bytes:
    """Materialize the stable canonical representation for explicit byte consumers."""
    return b"".join(canonical_chunks(artifact))


def canonical_digest_and_size(artifact: CanonicalArtifact) -> tuple[str, int]:
    """Hash canonical buffers without copying contiguous little-endian arrays."""
    digest = hashlib.sha256()
    byte_count = 0
    for chunk in _canonical_chunks(artifact, copy_arrays=False):
        digest.update(chunk)
        byte_count += len(chunk)
    return digest.hexdigest(), byte_count


def canonical_digest(artifact: CanonicalArtifact) -> str:
    """Return SHA-256 over versioned canonical bytes."""
    return canonical_digest_and_size(artifact)[0]
