"""Machine-readable formalism-to-code traceability for the methods paper."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .taxonomy import ClaimLevel
from .publication_specs import PUBLICATION_FIGURE_LABELS


@dataclass(frozen=True)
class FormalDefinition:
    label: str
    equation: str
    symbols: tuple[str, ...]
    implementation: tuple[str, ...]
    tests: tuple[str, ...]
    figures: tuple[str, ...]
    claim_level: ClaimLevel

    def __post_init__(self) -> None:
        if not self.label.startswith("eq:") or not self.equation.strip():
            raise ValueError("formal definitions require an equation label and expression")
        if not all((self.symbols, self.implementation, self.tests, self.figures)):
            raise ValueError("formal definitions require symbols, implementation, tests, and figures")
        if not isinstance(self.claim_level, ClaimLevel):
            raise ValueError("formal definition claim level must be ClaimLevel")

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "equation": self.equation,
            "symbols": list(self.symbols),
            "implementation": list(self.implementation),
            "tests": list(self.tests),
            "figures": list(self.figures),
            "claim_level": self.claim_level.value,
        }


def formalism_registry() -> tuple[FormalDefinition, ...]:
    """Return the numbered definitions used by prose, figures, and tests."""
    return (
        FormalDefinition("eq:typed_request", "q = (i, θ, s, e)", ("i", "θ", "s", "e"), ("registry.py", "schema.py"), ("test_generators.py",), ("fig:architecture", "fig:formalism_traceability"), ClaimLevel.CANONICAL_STIMULUS),
        FormalDefinition("eq:canonical_generation", "A = Gᵢ(θ; s)", ("A", "Gᵢ", "θ", "s"), ("registry.py", "generators.py"), ("test_generators.py", "test_v03_contracts.py"), ("fig:architecture", "fig:visual_panel"), ClaimLevel.CANONICAL_STIMULUS),
        FormalDefinition("eq:canonical_digest", "c(A) = Serialize_LE,float32(A, shape, clock, units); h_c(A) = H(c(A))", ("c(A)", "h_c", "H"), ("canonical.py", "manifest.py"), ("test_v03_contracts.py",), ("fig:architecture", "fig:encoding_verification"), ClaimLevel.PHYSICAL_METRIC),
        FormalDefinition("eq:encoding_verification", "F = Eₑ(A), I = D(F), V(F, M) ∈ {pass, fail}", ("F", "Eₑ", "D", "I", "V", "M"), ("render.py", "inspection.py", "manifest.py"), ("test_media_and_render.py", "test_v03_contracts.py"), ("fig:encoding_verification",), ClaimLevel.ENCODED_MEDIA),
        FormalDefinition("eq:clock_definition", "N = round(f_s T), t_k = k/f_r, Δ_AV = t_audio − t_video", ("N", "f_s", "T", "t_k", "f_r", "Δ_AV"), ("parameters.py", "artifacts.py"), ("test_parameters.py", "test_media_and_render.py"), ("fig:temporal_sequence", "fig:audiovisual_timeline"), ClaimLevel.PHYSICAL_METRIC),
        FormalDefinition("eq:objective_statistics", "μ_Y, σ_Y, RMS_X = M(A; units, tolerance, version)", ("μ_Y", "σ_Y", "RMS_X", "M"), ("metrics.py", "publication.py"), ("test_v04_scholarly.py",), ("fig:metrics_dashboard", "fig:audio_signals"), ClaimLevel.PHYSICAL_METRIC),
        FormalDefinition("eq:temporal_spectral_metrics", "D_k = mean absolute difference of adjacent frames; centroid(X) = Σ fP_X(f)/ΣP_X(f)", ("D_k", "P_X", "f"), ("metrics.py", "artifacts.py"), ("test_v04_scholarly.py",), ("fig:temporal_sequence", "fig:metrics_dashboard"), ClaimLevel.PHYSICAL_METRIC),
        FormalDefinition("eq:observer_estimand", "ψ = E[Y conditional on condition and protocol]", ("ψ", "Y", "condition", "protocol"), ("observer_analysis.py", "observer.py"), ("test_v04_scholarly.py",), ("fig:synthetic_psychophysics", "fig:observer_protocol"), ClaimLevel.OBSERVER_HYPOTHESIS),
        FormalDefinition("eq:synthetic_observer", "p_M(c|A_r,A_c) = σ((w·φ(A_c) − w·φ(A_r))/τ)", ("p_M", "c", "A_r", "A_c", "w", "φ", "τ"), ("synthetic_psychophysics.py", "metrics.py"), ("test_synthetic_psychophysics.py",), ("fig:synthetic_psychophysics",), ClaimLevel.SYNTHETIC_MODEL_OUTPUT),
    )


def validate_formalism_registry(
    definitions: tuple[FormalDefinition, ...] | None = None,
    *,
    project_root: Path | None = None,
) -> tuple[FormalDefinition, ...]:
    """Verify that every traceability edge resolves to a project artifact."""
    selected = formalism_registry() if definitions is None else definitions
    if not selected or len({item.label for item in selected}) != len(selected):
        raise ValueError("formalism labels must be non-empty and unique")
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[2]
    source_root = root / "src" / "duckrabbit"
    tests_root = root / "tests"
    for definition in selected:
        if not re.fullmatch(r"eq:[a-z0-9_]+", definition.label):
            raise ValueError(f"formalism label is invalid: {definition.label}")
        for relative in definition.implementation:
            if not (source_root / relative).is_file():
                raise ValueError(f"formalism implementation path does not exist: {relative}")
        for relative in definition.tests:
            if not (tests_root / relative).is_file():
                raise ValueError(f"formalism test path does not exist: {relative}")
    manuscript = root / "manuscript"
    missing_equations = [
        definition.label
        for definition in selected
        if not any(definition.label in path.read_text(encoding="utf-8") for path in manuscript.glob("*.md"))
    ]
    if missing_equations:
        raise ValueError(f"formalism equation labels are absent from manuscript: {missing_equations}")
    figure_labels = set(PUBLICATION_FIGURE_LABELS)
    missing_figures = sorted({figure for definition in selected for figure in definition.figures} - figure_labels)
    if missing_figures:
        raise ValueError(f"formalism figure labels are unresolved: {missing_figures}")
    return selected


__all__ = ["FormalDefinition", "formalism_registry", "validate_formalism_registry"]
