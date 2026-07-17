# DuckRabbit source style

- Prefer frozen dataclasses and explicit value objects over unvalidated dicts.
- Keep canonical arrays finite, normalized, and immutable after construction.
- Keep generator functions deterministic and free of filesystem side effects.
- Use lazy imports for optional encoders and raise `BackendUnavailableError`
  rather than silently changing output behavior.
- Use type hints and concise docstrings on public APIs.
- Keep serialization, encoding, and CLI concerns at the package boundary.

