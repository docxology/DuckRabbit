"""Typed generator registry and dispatch contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from .artifacts import CanonicalArtifact
from .errors import ParameterValidationError, RegistryFrozenError, UnknownIllusionError
from .parameters import Seed
from .taxonomy import ImplementationStatus, TaxonomyEntry, taxonomy_entries

ParamsT = TypeVar("ParamsT")
ArtifactT = TypeVar("ArtifactT")


class IllusionGenerator(Protocol, Generic[ParamsT, ArtifactT]):
    """Protocol implemented by deterministic typed generators."""

    def __call__(self, parameters: ParamsT, *, seed: int = 0) -> ArtifactT:
        """Generate one canonical artifact."""


@dataclass(frozen=True)
class GeneratorSpec(Generic[ParamsT, ArtifactT]):
    """Registered generator plus its parameter and taxonomy contracts."""

    illusion_id: str
    parameter_type: type[ParamsT]
    generator: IllusionGenerator[ParamsT, ArtifactT]
    taxonomy: TaxonomyEntry

    def __post_init__(self) -> None:
        if not isinstance(self.illusion_id, str) or not self.illusion_id.strip():
            raise ParameterValidationError("generator illusion_id is required")
        if not isinstance(self.parameter_type, type) or not callable(self.generator):
            raise ParameterValidationError("generator specs require a parameter type and callable")
        if not isinstance(self.taxonomy, TaxonomyEntry) or self.taxonomy.illusion_id != self.illusion_id:
            raise ParameterValidationError("generator spec identity must match its taxonomy entry")
        if self.taxonomy.implementation_status is not ImplementationStatus.IMPLEMENTED:
            raise ParameterValidationError("only implemented taxonomy entries can be registered")

    def __call__(self, parameters: ParamsT, *, seed: int = 0) -> ArtifactT:
        if not isinstance(parameters, self.parameter_type):
            raise ParameterValidationError(
                f"{self.illusion_id} expects {self.parameter_type.__name__}, "
                f"got {type(parameters).__name__}"
            )
        return self.generator(parameters, seed=Seed(seed))


class IllusionRegistry:
    """Discoverable mapping from illusion IDs to typed generator specs."""

    def __init__(self) -> None:
        self._specs: dict[str, GeneratorSpec[object, object]] = {}
        self._frozen = False

    def register(self, spec: GeneratorSpec[object, object]) -> None:
        if self._frozen:
            raise RegistryFrozenError("registry is frozen")
        if spec.illusion_id in self._specs:
            raise ValueError(f"illusion already registered: {spec.illusion_id}")
        self._specs[spec.illusion_id] = spec

    def freeze(self) -> None:
        """Prevent accidental mutation of a published/default registry."""
        self._frozen = True

    def get(self, illusion_id: str) -> GeneratorSpec[object, object]:
        try:
            return self._specs[illusion_id]
        except KeyError as exc:
            raise UnknownIllusionError(f"unknown illusion id: {illusion_id}") from exc

    def list(self) -> tuple[GeneratorSpec[object, object], ...]:
        return tuple(self._specs[key] for key in sorted(self._specs))

    def catalog(self) -> tuple[TaxonomyEntry, ...]:
        """Return the complete taxonomy catalog, including future entries."""
        return taxonomy_entries()

    def registered_catalog(self) -> tuple[TaxonomyEntry, ...]:
        """Return only taxonomy entries represented by this registry."""
        return tuple(spec.taxonomy for spec in self.list())

    def status_counts(self) -> dict[ImplementationStatus, int]:
        """Count catalog entries by explicit implementation status."""
        counts = {status: 0 for status in ImplementationStatus}
        for entry in self.catalog():
            counts[entry.implementation_status] += 1
        return counts

    def generate(self, illusion_id: str, parameters: object, *, seed: int = 0) -> CanonicalArtifact:
        return self.get(illusion_id)(parameters, seed=Seed(seed))  # type: ignore[return-value]


def generate(registry: IllusionRegistry, illusion_id: str, parameters: object, *, seed: int = 0) -> CanonicalArtifact:
    """Dispatch a typed request through a registry."""
    return registry.generate(illusion_id, parameters, seed=seed)
