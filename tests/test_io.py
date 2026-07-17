from pathlib import Path

from duckrabbit.io import atomic_write_text


def test_atomic_write_text_replaces_complete_payload(tmp_path: Path) -> None:
    destination = tmp_path / "nested" / "payload.json"

    result = atomic_write_text(destination, '{"version": 1}\n')

    assert result == destination
    assert destination.read_text(encoding="utf-8") == '{"version": 1}\n'
    assert not list(destination.parent.glob(".payload.json.*.tmp"))
