"""Strict, JSON-friendly schemas for typed generator parameters."""

from __future__ import annotations

from dataclasses import InitVar, MISSING, dataclass, fields, is_dataclass
from enum import Enum
from collections.abc import Mapping
from numbers import Integral
from typing import get_type_hints

from .errors import ParameterValidationError
from .parameters import _finite, _optional_type
from .serialization import jsonable


@dataclass(frozen=True)
class ParameterField:
    """One introspectable parameter field and its validated default."""

    name: str
    type_name: str
    required: bool
    default: object
    constraints: tuple[str, ...] = ()
    annotation: InitVar[object] = None

    def __post_init__(self, annotation: object) -> None:
        # Runtime hints must not alter the serialized parameters/v1 schema.
        object.__setattr__(self, "_annotation", annotation)


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
        if not all(isinstance(key, str) for key in payload):
            raise ParameterValidationError("parameter payload keys must be strings")
        expected = {field.name: field for field in self.fields}
        unknown = sorted(set(payload) - set(expected))
        if unknown:
            raise ParameterValidationError(f"unknown parameter field(s): {', '.join(str(item) for item in unknown)}")
        missing = [field.name for field in self.fields if field.required and field.name not in payload]
        if missing:
            raise ParameterValidationError(f"missing required parameter field(s): {', '.join(missing)}")
        for field in self.fields:
            if field.name in payload:
                _validate_json_value(field.name, field.default, payload[field.name], getattr(field, "_annotation", None))

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
                annotation=hints.get(field.name, field.type),
            )
        )
    return ParameterSchema("duckrabbit/parameters/v1", type(parameters).__name__, tuple(result))


def parameter_payload(parameters: object) -> dict[str, object]:
    """Return a validated JSON object for a parameter dataclass."""
    payload = jsonable_parameter(parameters)
    if not isinstance(payload, dict):
        raise ParameterValidationError("parameters must serialize to a JSON object")
    return payload


def _validate_json_value(path: str, expected: object, value: object, annotation: object = None) -> object:
    """Restore serialized values using typed defaults and declared Optional hints."""
    optional_type = _optional_type(annotation)
    if optional_type is not None:
        if value is None:
            return None
        if expected is None:
            expected = optional_type
    expected_type = expected if isinstance(expected, type) else type(expected)
    if issubclass(expected_type, Enum):
        try:
            return expected_type(value)
        except (TypeError, ValueError) as exc:
            choices = [member.value for member in expected_type]
            raise ParameterValidationError(f"parameter field {path} must be one of {choices}") from exc
    if is_dataclass(expected):
        if not isinstance(value, Mapping):
            raise ParameterValidationError(f"parameter field {path} must be a JSON object")
        if not all(isinstance(key, str) for key in value):
            raise ParameterValidationError(f"parameter field {path} keys must be strings")
        hints = get_type_hints(expected_type)
        expected_fields = {
            field.name: hints.get(field.name, field.type) if isinstance(expected, type) else getattr(expected, field.name)
            for field in fields(expected)
        }
        unknown = sorted(set(value) - set(expected_fields))
        if unknown:
            raise ParameterValidationError(f"parameter field {path} has unknown field(s): {', '.join(str(item) for item in unknown)}")
        missing = sorted(set(expected_fields) - set(value))
        if missing:
            raise ParameterValidationError(f"parameter field {path} is missing field(s): {', '.join(missing)}")
        converted = {
            name: _validate_json_value(f"{path}.{name}", default, value[name], hints.get(name))
            for name, default in expected_fields.items()
        }
        try:
            return expected_type(**converted)
        except (TypeError, ValueError) as exc:
            raise ParameterValidationError(f"parameter field {path} is invalid: {exc}") from exc
    if issubclass(expected_type, bool):
        if type(value) is not bool:
            raise ParameterValidationError(f"parameter field {path} must be bool")
        return value
    if issubclass(expected_type, int):
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise ParameterValidationError(f"parameter field {path} must be int")
        try:
            return expected_type(value)
        except ValueError as exc:
            raise ParameterValidationError(f"parameter field {path} is invalid: {exc}") from exc
    if issubclass(expected_type, float):
        return _finite(value, f"parameter field {path}")
    if issubclass(expected_type, str):
        if not isinstance(value, str):
            raise ParameterValidationError(f"parameter field {path} must be string")
        return value
    if isinstance(expected, (tuple, list)):
        if not isinstance(value, (list, tuple)):
            raise ParameterValidationError(f"parameter field {path} must be a JSON array")
        converted = [
            _validate_json_value(f"{path}[{index}]", expected[0], item) if expected else item
            for index, item in enumerate(value)
        ]
        return tuple(converted) if isinstance(expected, tuple) else converted
    if value is not None:
        raise ParameterValidationError(f"parameter field {path} has unsupported serialized type")
    return None
