"""Typed, code-owned caption and publication metadata contracts."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .taxonomy import ClaimLevel


_OVERCLAIM_PATTERNS = (
    r"\bcauses?\b",
    r"\bproves?\b",
    r"\buniversal(?:ly)?\b",
    r"\bevery (?:viewer|observer|participant)\b",
    r"\bobservers? (?:will|do|perceive|see|hear)\b",
    r"\bparticipants? (?:reported|showed|perceived)\b",
    r"\bguarantee[sd]?\b",
    r"\bensures?\b",
    r"\bconfirms?\b",
    r"\b(?:is|are)\s+perceived\b",
    r"\b(?:will|does|do)\s+(?:appear|look|sound|seem)\b",
    r"\bobservers?\s+(?:always|must|certainly)\b",
)

PUBLICATION_FIGURE_LABELS = (
    "fig:architecture",
    "fig:catalog_matrix",
    "fig:visual_panel",
    "fig:visual_sweep",
    "fig:temporal_sequence",
    "fig:audio_signals",
    "fig:audiovisual_timeline",
    "fig:encoding_verification",
    "fig:synthetic_psychophysics",
    "fig:claim_boundary",
    "fig:scholarship_map",
    "fig:formalism_traceability",
    "fig:metrics_dashboard",
    "fig:parameter_domains",
    "fig:observer_protocol",
)


@dataclass(frozen=True)
class CaptionSpec:
    """A figure caption with explicit provenance and epistemic boundary."""

    label: str
    stem: str
    title: str
    caption: str
    alt_text: str
    claim_level: ClaimLevel
    source_data: str
    evidence_references: tuple[str, ...]
    limitations: tuple[str, ...]
    accessibility_notes: tuple[str, ...]
    seed: int | None = 0
    controls: str = ""
    objective_facts: str = ""
    boundary_statement: str = ""

    def __post_init__(self) -> None:
        if not re.fullmatch(r"fig:[a-z0-9_]+", self.label) or not re.fullmatch(r"[a-z0-9_]+", self.stem):
            raise ValueError("caption label/stem must be stable figure identifiers")
        for name in ("title", "caption", "alt_text", "source_data"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"caption {name} is required")
        if not isinstance(self.claim_level, ClaimLevel):
            raise ValueError("caption claim_level must be ClaimLevel")
        if not self.source_data.startswith("output/data/"):
            raise ValueError("caption source_data must point to output/data")
        if not self.evidence_references:
            raise ValueError("caption requires at least one evidence or provenance reference")
        if not self.limitations or not all(item.strip() for item in self.limitations):
            raise ValueError("caption requires explicit limitations")
        if not self.accessibility_notes or not all(item.strip() for item in self.accessibility_notes):
            raise ValueError("caption requires accessibility notes")
        text = f"{self.title} {self.caption} {self.alt_text}".lower()
        if any(re.search(pattern, text) for pattern in _OVERCLAIM_PATTERNS):
            raise ValueError(f"caption contains observer overclaim language: {self.stem}")
        if "source data" not in text:
            raise ValueError("caption must name its source data")
        if self.claim_level is ClaimLevel.OBSERVER_HYPOTHESIS and "synthetic" not in text and "assumed" not in text:
            raise ValueError("observer-hypothesis captions must identify synthetic or assumed values")
        for name in ("controls", "objective_facts", "boundary_statement"):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise ValueError(f"caption {name} must be text")

    @property
    def rendered_caption(self) -> str:
        """Return the complete publication caption with epistemic metadata."""
        seed_text = "not applicable" if self.seed is None else f"{self.seed}"
        controls = self.controls or f"canonical generator seed {seed_text}"
        objective = self.objective_facts or "no unit-bearing objective quantity is applicable to this diagram; structural facts are reported in the source-data sidecar"
        boundary = self.boundary_statement or "this figure does not establish an observer-level perceptual effect"
        limitations = " ".join(self.limitations)
        evidence = ", ".join(self.evidence_references)

        def sentence(value: str) -> str:
            cleaned = value.strip()
            return cleaned if cleaned.endswith((".", "!", "?")) else f"{cleaned}."

        return (
            f"What this figure shows: {sentence(self.alt_text)} {sentence(self.caption)} "
            f"Controls: {sentence(controls)} Objective facts: {sentence(objective)} "
            f"Claim level: {self.claim_level.value}. Source data: {self.source_data} "
            f"(SHA-256 digest recorded in the figure registry). Evidence lineage: {evidence}. "
            f"Limitations: {sentence(limitations)} Boundary: {sentence(boundary)}"
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "stem": self.stem,
            "title": self.title,
            "caption": self.rendered_caption,
            "caption_core": self.caption,
            "alt_text": self.alt_text,
            "claim_level": self.claim_level.value,
            "source_data": self.source_data,
            "evidence_references": list(self.evidence_references),
            "limitations": list(self.limitations),
            "accessibility_notes": list(self.accessibility_notes),
            "seed": self.seed,
            "controls": self.controls,
            "objective_facts": self.objective_facts,
            "boundary_statement": self.boundary_statement,
        }


def caption_variable_name(stem: str, kind: str) -> str:
    """Return the stable manuscript variable for a figure caption or alt text."""
    if kind not in {"caption", "alt"}:
        raise ValueError("caption variable kind must be caption or alt")
    return f"FIGURE_{kind.upper()}_{stem.upper()}"


__all__ = ["CaptionSpec", "PUBLICATION_FIGURE_LABELS", "caption_variable_name"]
