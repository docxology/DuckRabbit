"""Small filesystem helpers used by generated, machine-readable outputs."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> Path:
    """Write text beside ``path`` and publish it with an atomic rename."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding=encoding, dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    """Hash a file in chunks so large encoded media never loads fully."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


__all__ = ["atomic_write_text", "sha256_file"]


__all__ = ["atomic_write_text"]
