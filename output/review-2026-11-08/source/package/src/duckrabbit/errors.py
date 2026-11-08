"""Domain errors raised by DuckRabbit."""


class DuckRabbitError(Exception):
    """Base class for expected DuckRabbit failures."""


class ParameterValidationError(DuckRabbitError, ValueError):
    """A typed parameter or canonical artifact violates its contract."""


class UnknownIllusionError(DuckRabbitError, KeyError):
    """The requested illusion is not registered."""


class BackendUnavailableError(DuckRabbitError, RuntimeError):
    """An optional encoding backend is not installed or discoverable."""


class MediaEncodingError(DuckRabbitError, RuntimeError):
    """A media encoder failed while writing an artifact."""


class MediaInspectionError(DuckRabbitError, RuntimeError):
    """A previously encoded artifact could not be decoded or inspected."""


class ManifestValidationError(DuckRabbitError, ValueError):
    """A provenance manifest is malformed or inconsistent with its artifact."""


class VerificationError(DuckRabbitError, ValueError):
    """An artifact failed an explicit integrity or media invariant check."""


class UnsupportedFormatError(DuckRabbitError, ValueError):
    """A requested format is unknown or incompatible with a canonical artifact."""


class RegistryFrozenError(DuckRabbitError, RuntimeError):
    """The generator registry is frozen and rejects new registrations."""
