"""Strict, JSON-friendly schemas for typed generator parameters."""

from __future__ import annotations

from dataclasses import MISSING, dataclass, fields, is_dataclass
from enum import Enum
from math import isfinite
from collections.abc import Mapping
from numbers import Integral, Real
from typing import get_type_hints

from .errors import ParameterValidationError
from .serialization import jsonable


@dataclass(frozen=True)
class ParameterField:
    """One introspectable parameter field and its validated default."""

    name: str
    type_name: str
    required: bool
    default: object
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class ParameterSchema:
    """Stable schema description for one frozen parameter dataclass."""

    schema_version: str
    parameter_type: str
    fields: tuple[ParameterField, ...]

    def validate_payload(self, payload: Mapping[str, object]) -> None:
        """Validate a JSON-decoded parameter payload with field-level errors."""
        if not isinstance(payload, Mapping):
            raise ParameterValidationError("parameter payload must be a JSON object")
        expected = {field.name: field for field in self.fields}
        unknown = sorted(set(payload) - set(expected))
        if unknown:
            raise ParameterValidationError(f"unknown parameter field(s): {', '.join(str(item) for item in unknown)}")
        missing = [field.name for field in self.fields if field.required and field.name not in payload]
        if missing:
            raise ParameterValidationError(f"missing required parameter field(s): {', '.join(missing)}")
        for field in self.fields:
            if field.name in payload:
                _validate_json_value(field.name, field.default, payload[field.name])

    def to_json(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "parameter_type": self.parameter_type,
            "fields": [
                {
                    "name": field.name,
                    "type": field.type_name,
                    "required": field.required,
                    "default": jsonable_parameter(field.default),
                    "constraints": list(field.constraints),
                }
                for field in self.fields
            ],
        }


def jsonable_parameter(value: object) -> object:
    """Convert typed parameters into JSON primitives without losing enums."""
    return jsonable(value)


def _constraints(default: object) -> tuple[str, ...]:
    constraints: list[str] = []
    value_type = type(default)
    if hasattr(value_type, "minimum") and hasattr(value_type, "maximum"):
        constraints.append(f"{value_type.minimum} <= value <= {value_type.maximum}")
    if isinstance(default, Enum):
        choices = getattr(type(default), "__members__", {})
        constraints.append("choices=" + ",".join(member.value for member in choices.values()))
    if default.__class__.__name__ in {"DurationSeconds", "FrequencyHz"}:
        constraints.append("finite and > 0")
    return tuple(constraints)


def parameter_schema(parameters: object) -> ParameterSchema:
    """Describe a validated dataclass recursively at the public boundary."""
    if not is_dataclass(parameters) or isinstance(parameters, type):
        raise ParameterValidationError("parameter schema requires a dataclass instance")
    hints = get_type_hints(type(parameters))
    result = []
    for field in fields(parameters):
        default = getattr(parameters, field.name)
        result.append(
            ParameterField(
                name=field.name,
                type_name=getattr(hints.get(field.name, field.type), "__name__", str(hints.get(field.name, field.type))),
                required=field.default is MISSING and field.default_factory is MISSING,
                default=default,
                constraints=_constraints(default),
            )
        )
    return ParameterSchema("duckrabbit/parameters/v1", type(parameters).__name__, tuple(result))


def parameter_payload(parameters: object) -> dict[str, object]:
    """Return a validated JSON object for a parameter dataclass."""
    payload = jsonable_parameter(parameters)
    if not isinstance(payload, dict):
        raise ParameterValidationError("parameters must serialize to a JSON object")
    return payload


def _validate_json_value(path: str, expected: object, value: object) -> None:
    """Validate one serialized value against the observed typed default."""
    if isinstance(expected, Enum):
        choices = {member.value for member in type(expected)}
        if value not in choices:
            raise ParameterValidationError(f"parameter field {path} must be one of {sorted(choices)}")
        return
    if is_dataclass(expected):
        if not isinstance(value, Mapping):
            raise ParameterValidationError(f"parameter field {path} must be a JSON object")
        expected_fields = {field.name: getattr(expected, field.name) for field in fields(expected)}
        unknown = sorted(set(value) - set(expected_fields))
        if unknown:
            raise ParameterValidationError(f"parameter field {path} has unknown field(s): {', '.join(str(item) for item in unknown)}")
        missing = sorted(set(expected_fields) - set(value))
        if missing:
            raise ParameterValidationError(f"parameter field {path} is missing field(s): {', '.join(missing)}")
        for name, default in expected_fields.items():
            _validate_json_value(f"{path}.{name}", default, value[name])
        return
    if isinstance(expected, bool):
        if type(value) is not bool:
            raise ParameterValidationError(f"parameter field {path} must be bool")
        return
    if isinstance(expected, int):
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise ParameterValidationError(f"parameter field {path} must be int")
        return
    if isinstance(expected, float):
        if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(float(value)):
            raise ParameterValidationError(f"parameter field {path} must be a finite number")
        return
    if isinstance(expected, str):
        if not isinstance(value, str):
            raise ParameterValidationError(f"parameter field {path} must be string")
        return
    if isinstance(expected, (tuple, list)):
        if not isinstance(value, (list, tuple)):
            raise ParameterValidationError(f"parameter field {path} must be a JSON array")
        if expected:
            for index, item in enumerate(value):
                _validate_json_value(f"{path}[{index}]", expected[0], item)
        return
    if value is not None:
        raise ParameterValidationError(f"parameter field {path} has unsupported serialized type")
