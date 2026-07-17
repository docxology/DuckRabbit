"""Typed claim lineage for prose, publication outputs, and model diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

from .evidence import load_evidence_matrix
from .taxonomy import ClaimLevel, taxonomy_entries


class ClaimBasis(str, Enum):
    """Permitted epistemic origins for a package claim."""

    DERIVED_FROM_CODE = "derived_from_code"
    DERIVED_FROM_CANONICAL_ARTIFACT = "derived_from_canonical_artifact"
    DERIVED_FROM_DECODED_MEDIA = "derived_from_decoded_media"
    CHECKED_IN_SCHOLARSHIP = "checked_in_scholarship"
    SYNTHETIC_MODEL_OUTPUT = "synthetic_model_output"
    FUTURE_OBSERVER_HYPOTHESIS = "future_observer_hypothesis"
    PUBLICATION_ILLUSTRATION = "publication_illustration"


_OVERCLAIM = re.compile(r"\b(universal|causes?|proves?|participants? reported|observers? (?:will|do|always|must))\b", re.I)


@dataclass(frozen=True)
class ClaimRecord:
    """One claim with explicit basis, lineage, location, and limitation."""

    claim_id: str
    text: str
    basis: ClaimBasis
    claim_level: ClaimLevel
    source_or_artifact_lineage: tuple[str, ...]
    limitation: str
    manuscript_location: str

    def __post_init__(self) -> None:
        if not self.claim_id or not self.text.strip() or not self.manuscript_location.strip():
            raise ValueError("claim requires an id, text, and manuscript location")
        if not isinstance(self.basis, ClaimBasis) or not isinstance(self.claim_level, ClaimLevel):
            raise ValueError("claim basis and level must be typed enums")
        if not self.source_or_artifact_lineage or not all(isinstance(item, str) and item.strip() for item in self.source_or_artifact_lineage):
            raise ValueError("claim requires non-empty source or artifact lineage")
        if not self.limitation.strip():
            raise ValueError("claim requires an explicit limitation")
        if _OVERCLAIM.search(self.text) and self.claim_level not in {ClaimLevel.OBSERVER_HYPOTHESIS, ClaimLevel.VALIDATED_OBSERVER_EFFECT}:
            raise ValueError("deterministic or source claim contains observer overclaim language")

    def to_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "basis": self.basis.value,
            "claim_level": self.claim_level.value,
            "source_or_artifact_lineage": list(self.source_or_artifact_lineage),
            "limitation": self.limitation,
            "manuscript_location": self.manuscript_location,
        }


def validate_claim_registry(records: tuple[ClaimRecord, ...] | list[ClaimRecord]) -> tuple[ClaimRecord, ...]:
    """Validate uniqueness and the deterministic/observer boundary."""
    normalized = tuple(records)
    ids = [record.claim_id for record in normalized]
    if len(ids) != len(set(ids)):
        raise ValueError("claim registry contains duplicate claim IDs")
    return normalized


def default_claim_registry() -> tuple[ClaimRecord, ...]:
    """Build the code-owned catalog and scope claims from the live snapshot."""
    sources, evidence = load_evidence_matrix()
    records: list[ClaimRecord] = [
        ClaimRecord(
            "catalog:count",
            f"The catalog contains {len(taxonomy_entries())} entries.",
            ClaimBasis.DERIVED_FROM_CODE,
            ClaimLevel.CANONICAL_STIMULUS,
            ("taxonomy_entries()",),
            "Catalog membership is not a completeness claim about all known illusions.",
            "manuscript/09_appendix_catalog.md",
        ),
        ClaimRecord(
            "evidence:source_count",
            f"The checked-in evidence matrix contains {len(sources)} source records.",
            ClaimBasis.CHECKED_IN_SCHOLARSHIP,
            ClaimLevel.SOURCE_SUPPORTED,
            ("data/evidence_matrix.json::sources",),
            "The offline snapshot does not imply that every URL is currently reachable or that a source supports more than its exact record.",
            "manuscript/06_scope_and_related_work.md",
        ),
        ClaimRecord(
            "scope:no_participant_data",
            "No participant data are bundled with the package.",
            ClaimBasis.DERIVED_FROM_CODE,
            ClaimLevel.OBSERVER_HYPOTHESIS,
            ("experiments/observer_protocol.md", "output/data/synthetic_psychophysics.json"),
            "Future observer studies require preregistration, consent, calibrated presentation, and separate data governance.",
            "manuscript/07_publication_audit.md",
        ),
        ClaimRecord(
            "synthetic:diagnostic_boundary",
            "The synthetic observer is a deterministic model-output diagnostic, not human psychophysics.",
            ClaimBasis.SYNTHETIC_MODEL_OUTPUT,
            ClaimLevel.SYNTHETIC_MODEL_OUTPUT,
            ("src/duckrabbit/synthetic_psychophysics.py", "output/data/synthetic_psychophysics.json"),
            "The hand-specified model has no training data and has not been calibrated against observers.",
            "manuscript/02_methodology.md",
        ),
        ClaimRecord(
            "cover:editorial_boundary",
            "The cover is a publication illustration, not an experimental stimulus or observer result.",
            ClaimBasis.PUBLICATION_ILLUSTRATION,
            ClaimLevel.PUBLICATION_ILLUSTRATION,
            ("output/reports/cover_visualization.json",),
            "The editorial asset is not part of the deterministic scientific stimulus registry.",
            "manuscript/07_publication_audit.md",
        ),
    ]
    for entry in taxonomy_entries():
        record = evidence[entry.illusion_id]
        records.append(
            ClaimRecord(
                f"evidence:{entry.illusion_id}",
                record.supported_claim,
                ClaimBasis.CHECKED_IN_SCHOLARSHIP,
                record.supported_claim_level,
                tuple(record.primary_sources + record.review_sources + record.theory_sources) + ("data/evidence_matrix.json",),
                " ".join(record.evidence_limitations),
                "manuscript/06_scope_and_related_work.md",
            )
        )
    return validate_claim_registry(records)


__all__ = ["ClaimBasis", "ClaimRecord", "default_claim_registry", "validate_claim_registry"]
