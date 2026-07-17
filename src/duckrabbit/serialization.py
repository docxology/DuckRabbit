"""Strict conversion of typed package values to JSON-compatible primitives."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
from collections.abc import Mapping

import numpy as np

from .errors import ParameterValidationError


def jsonable(value: object) -> object:
    """Convert supported typed values without silently stringifying objects."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, Mapping):
        return {str(key): jsonable(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (tuple, list)):
        return [jsonable(item) for item in value]
    if is_dataclass(value):
        return {field.name: jsonable(getattr(value, field.name)) for field in fields(value)}
    if hasattr(value, "value") and isinstance(value.value, (str, int, float, bool)):
        return value.value
    raise ParameterValidationError(f"value {type(value).__name__} is not JSON serializable")


__all__ = ["jsonable"]
