from pathlib import Path
import hashlib

import pytest

from duckrabbit.io import atomic_write_text, sha256_file


def test_atomic_write_text_replaces_complete_payload(tmp_path: Path) -> None:
    destination = tmp_path / "nested" / "payload.json"

    result = atomic_write_text(destination, '{"version": 1}\n')

    assert result == destination
    assert destination.read_text(encoding="utf-8") == '{"version": 1}\n'
    assert not list(destination.parent.glob(".payload.json.*.tmp"))


@pytest.mark.parametrize("chunk_size", [0, -1, True, 1.5])
def test_file_hash_rejects_invalid_chunk_sizes(tmp_path: Path, chunk_size: object) -> None:
    destination = tmp_path / "payload.bin"
    destination.write_bytes(b"payload")
    with pytest.raises(ValueError, match="positive integer"):
        sha256_file(destination, chunk_size=chunk_size)


def test_file_hash_reads_all_chunks_and_empty_files(tmp_path: Path) -> None:
    destination = tmp_path / "payload.bin"
    payload = bytes(range(256)) * 3
    destination.write_bytes(payload)
    assert sha256_file(destination, chunk_size=7) == hashlib.sha256(payload).hexdigest()
    destination.write_bytes(b"")
    assert sha256_file(destination) == hashlib.sha256(b"").hexdigest()
