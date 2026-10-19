"""Strict JSON values, typed schema ranges, and streaming canonical hashes."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import tracemalloc
from types import MappingProxyType

import numpy as np
import pytest

from duckrabbit.artifacts import ImageFrame, VideoSequence
from duckrabbit.canonical import canonical_bytes, canonical_chunks, canonical_digest, canonical_digest_and_size
from duckrabbit.errors import ParameterValidationError
from duckrabbit.generators import default_parameters
from duckrabbit.parameters import FrameRate, replace_from_mapping
from duckrabbit.schema import parameter_payload, parameter_schema
from duckrabbit.serialization import jsonable
from duckrabbit.render import build_manifest_v2
from duckrabbit.taxonomy import taxonomy_entries


@pytest.mark.parametrize("entry", taxonomy_entries(include_unimplemented=False), ids=lambda entry: entry.illusion_id)
def test_every_default_parameter_payload_validates(entry) -> None:
    parameters = default_parameters(entry.illusion_id)
    parameter_schema(parameters).validate_payload(parameter_payload(parameters))


@pytest.mark.parametrize(
    ("field", "value"),
    [("width", 0), ("width", True), ("mode", []), ("quantization_levels", 1)],
)
def test_nested_schema_rejects_invalid_typed_values(field: str, value: object) -> None:
    parameters = default_parameters("visual.duck_rabbit")
    payload = parameter_payload(parameters)
    payload["config"][field] = value
    with pytest.raises(ParameterValidationError, match="parameter field config"):
        parameter_schema(parameters).validate_payload(payload)


def test_schema_rejects_out_of_range_value_objects_and_nonstring_keys() -> None:
    parameters = default_parameters("visual.duck_rabbit")
    payload = parameter_payload(parameters)
    payload["duck_weight"] = {"value": 2.0}
    with pytest.raises(ParameterValidationError, match="duck_weight"):
        parameter_schema(parameters).validate_payload(payload)
    for malformed in ({0: 1, "unexpected": 2}, {"config": {0: 1, "width": 2}}):
        with pytest.raises(ParameterValidationError, match="keys must be strings"):
            parameter_schema(parameters).validate_payload(malformed)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), np.float32("nan")])
def test_jsonable_rejects_nonfinite_numbers_recursively(value: object) -> None:
    with pytest.raises(ParameterValidationError, match="finite"):
        jsonable({"values": [value]})


def test_jsonable_rejects_ambiguous_keys_and_dataclass_types() -> None:
    with pytest.raises(ParameterValidationError, match="duplicate JSON mapping key"):
        jsonable({1: "numeric", "1": "text"})

    @dataclass(frozen=True)
    class Record:
        value: int = 1

    with pytest.raises(ParameterValidationError, match="not JSON serializable"):
        jsonable(Record)
    assert json.loads(json.dumps(jsonable({"path": Path("example"), "record": Record()}), allow_nan=False)) == {
        "path": "example", "record": {"value": 1},
    }


def test_canonical_hash_streams_frames_without_materializing_the_video() -> None:
    frame = ImageFrame(np.zeros((256, 256), dtype=np.float32))
    video = VideoSequence((frame,) * 12, FrameRate(12.0))
    expected = hashlib.sha256(canonical_bytes(video)).hexdigest()
    tracemalloc.start()
    try:
        actual = canonical_digest(video)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert actual == expected
    assert peak < video.nbytes


@pytest.mark.parametrize("illusion_id", [
    "visual.duck_rabbit", "audio.shepard_tone", "visual.apparent_motion",
    "audiovisual.sound_induced_flash",
])
def test_buffer_hash_matches_public_bytes_for_every_artifact_kind(illusion_id: str) -> None:
    from duckrabbit import generate

    artifact = generate(illusion_id)
    serialized = canonical_bytes(artifact)
    assert all(isinstance(chunk, bytes) for chunk in canonical_chunks(artifact))
    assert canonical_digest_and_size(artifact) == (hashlib.sha256(serialized).hexdigest(), len(serialized))


def test_contiguous_image_hash_does_not_allocate_an_image_sized_copy() -> None:
    frame = ImageFrame(np.linspace(0.0, 1.0, 1024 * 1024, dtype=np.float32).reshape(1024, 1024))
    expected = hashlib.sha256(canonical_bytes(frame)).hexdigest()
    tracemalloc.start()
    try:
        digest, byte_count = canonical_digest_and_size(frame)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert digest == expected
    assert byte_count > frame.nbytes
    assert peak < frame.nbytes // 8


def test_buffer_hash_normalizes_fortran_layout_without_changing_canonical_bytes() -> None:
    frame = ImageFrame(np.asfortranarray(np.arange(60, dtype=np.float32).reshape(5, 4, 3) / 60), mode="RGB")
    assert not frame.pixels.flags.c_contiguous
    expected = canonical_bytes(frame)
    assert canonical_digest_and_size(frame) == (hashlib.sha256(expected).hexdigest(), len(expected))


def test_parameter_overrides_accept_immutable_mappings_without_mutation() -> None:
    parameters = default_parameters("visual.duck_rabbit")
    overrides = MappingProxyType({"config": MappingProxyType({"width": 64})})
    updated = replace_from_mapping(parameters, overrides)
    assert updated.config.width == 64
    assert parameters.config.width != updated.config.width


def test_manifest_hash_and_byte_count_are_streamed() -> None:
    frame = ImageFrame(np.zeros((256, 256), dtype=np.float32))
    video = VideoSequence((frame,) * 12, FrameRate(12.0))
    expected = canonical_bytes(video)
    parameters = replace_from_mapping(default_parameters("visual.apparent_motion"), {"config": {"frame_count": 12}})
    tracemalloc.start()
    try:
        manifest = build_manifest_v2("visual.apparent_motion", parameters, video)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert manifest.canonical.digest == hashlib.sha256(expected).hexdigest()
    assert manifest.canonical.byte_count == len(expected)
    assert peak < video.nbytes


@pytest.mark.parametrize("payload", [{"sweep_octaves": True}, {"partial_count": 2.0}, {0: 1, "unknown": 2}])
def test_parameter_overrides_reject_ambiguous_scalar_types(payload: dict) -> None:
    with pytest.raises(ParameterValidationError):
        replace_from_mapping(default_parameters("audio.shepard_tone"), payload)
