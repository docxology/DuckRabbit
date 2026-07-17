"""A deliberately orthogonal cognitive taxonomy for illusion generators.

The taxonomy is an engineering ontology, not a claim that the literature has a
single agreed hierarchy. Entries record the intended mechanism, perceptual
signature, stimulus requirements, and evidence status separately so one
phenomenon can legitimately occupy multiple facets.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class Modality(str, Enum):
    """Primary media channel used by an illusion stimulus."""

    VISUAL = "visual"
    AUDITORY = "auditory"
    AUDIOVISUAL = "audio_visual"


class ImplementationStatus(str, Enum):
    """How much of a catalogued illusion is implemented in this project."""

    IMPLEMENTED = "implemented"
    PLANNED = "planned"
    INPUT_REQUIRED = "input_required"


class EvidenceStatus(str, Enum):
    """Evidence boundary recorded independently from implementation status."""

    LITERATURE_BACKED_ENGINEERING_ENTRY = "literature_backed_engineering_entry"
    REVIEW_BACKED_ENGINEERING_ENTRY = "review_backed_engineering_entry"
    LITERATURE_BACKED_PLANNED_ENTRY = "literature_backed_planned_entry"
    LITERATURE_BACKED_INPUT_DEPENDENT_ENTRY = "literature_backed_input_dependent_entry"


class OutputKind(str, Enum):
    """Canonical artifact kind emitted by a generator."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    AUDIOVISUAL = "audiovisual"


class ClaimLevel(str, Enum):
    """What kind of statement DuckRabbit is entitled to make."""

    CANONICAL_STIMULUS = "canonical_stimulus"
    PHYSICAL_METRIC = "physical_metric"
    ENCODED_MEDIA = "encoded_media"
    SOURCE_SUPPORTED = "source_supported"
    OBSERVER_HYPOTHESIS = "observer_hypothesis"
    SYNTHETIC_MODEL_OUTPUT = "synthetic_model_output"
    OBSERVER_EFFECT = "observer_effect"
    VALIDATED_OBSERVER_EFFECT = "validated_observer_effect"
    GENERALIZATION = "generalization"
    PUBLICATION_ILLUSTRATION = "publication_illustration"


class InputRequirement(str, Enum):
    """External stimulus dependency required for a catalog entry."""

    NONE = "none"
    CONTROLLED_PLAYBACK = "controlled_playback"
    STEREO_PLAYBACK = "stereo_playback"
    VALIDATED_SPEECH_FIXTURE = "validated_speech_fixture"


class Mechanism(str, Enum):
    """Stimulus or processing mechanism used as a taxonomy facet."""

    AMBIGUITY = "ambiguity"
    CONTRAST = "contrast_and_context"
    GEOMETRIC = "geometric_alignment"
    TEMPORAL_MOTION = "temporal_motion"
    SPECTRAL = "spectral_harmonic"
    STREAM_SEGREGATION = "stream_segregation"
    CROSSMODAL_TEMPORAL = "crossmodal_temporal"
    CROSSMODAL_SPATIAL = "crossmodal_spatial"
    SPEECH_CATEGORIZATION = "speech_categorization"


class PerceptualSignature(str, Enum):
    """Observable signature the generated stimulus is designed to probe."""

    BISTABILITY = "bistability"
    CONTRAST_DISTORTION = "contrast_distortion"
    GEOMETRIC_DISTORTION = "geometric_distortion"
    ILLUSORY_MOTION = "illusory_motion"
    CONTINUITY = "continuity"
    FILLING_IN = "filling_in"
    FUSION_FISSION = "fusion_or_fission"
    SPATIAL_CAPTURE = "spatial_capture"
    TEMPORAL_BINDING = "temporal_binding_or_recalibration"
    CATEGORICAL_RECODING = "categorical_recoding"


class CognitiveProcess(str, Enum):
    """Cognitive or perceptual process named by the catalog entry."""

    PERCEPTUAL_ORGANIZATION = "perceptual_organization"
    CONTEXTUAL_INFERENCE = "contextual_inference"
    TEMPORAL_INFERENCE = "temporal_inference"
    SPECTRAL_INFERENCE = "spectral_inference"
    MULTISENSORY_INTEGRATION = "multisensory_integration"
    SPEECH_PERCEPTION = "speech_perception"


@dataclass(frozen=True)
class TaxonomyEntry:
    """Structured metadata for one catalogued illusion."""

    illusion_id: str
    name: str
    modalities: tuple[Modality, ...]
    mechanisms: tuple[Mechanism, ...]
    signatures: tuple[PerceptualSignature, ...]
    cognitive_processes: tuple[CognitiveProcess, ...]
    stimulus_requirements: tuple[str, ...]
    evidence_status: EvidenceStatus
    evidence_references: tuple[str, ...]
    implementation_status: ImplementationStatus
    description: str
    output_kind: OutputKind | None = None
    input_requirement: InputRequirement = InputRequirement.NONE
    claim_levels: tuple[ClaimLevel, ...] = (ClaimLevel.CANONICAL_STIMULUS, ClaimLevel.PHYSICAL_METRIC)

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z]+\.[a-z0-9_]+", self.illusion_id):
            raise ValueError(f"invalid illusion id: {self.illusion_id!r}")
        if not self.name or not self.description:
            raise ValueError("taxonomy name and description are required")
        if not self.modalities or not all(isinstance(item, Modality) for item in self.modalities):
            raise ValueError("taxonomy modalities must be non-empty Modality values")
        for name, values, enum_type in (
            ("mechanisms", self.mechanisms, Mechanism),
            ("signatures", self.signatures, PerceptualSignature),
            ("cognitive_processes", self.cognitive_processes, CognitiveProcess),
        ):
            if not values or not all(isinstance(item, enum_type) for item in values):
                raise ValueError(f"taxonomy {name} must contain non-empty enum values")
        if not self.stimulus_requirements or not all(isinstance(item, str) and item for item in self.stimulus_requirements):
            raise ValueError("taxonomy stimulus_requirements must be non-empty strings")
        if not isinstance(self.evidence_status, EvidenceStatus) or not self.evidence_references:
            raise ValueError("taxonomy evidence status and references are required")
        if not all(isinstance(item, str) and item for item in self.evidence_references):
            raise ValueError("taxonomy evidence references must be strings")
        if not isinstance(self.implementation_status, ImplementationStatus):
            raise ValueError("taxonomy implementation_status must be ImplementationStatus")
        if self.output_kind is None:
            if self.illusion_id in {"visual.apparent_motion", "visual.phi_motion"}:
                inferred = OutputKind.VIDEO
            else:
                inferred = OutputKind.AUDIOVISUAL if self.illusion_id.startswith("audiovisual.") else OutputKind.AUDIO if self.illusion_id.startswith("audio.") else OutputKind.IMAGE
            object.__setattr__(self, "output_kind", inferred)
        if not isinstance(self.output_kind, OutputKind) or not isinstance(self.input_requirement, InputRequirement):
            raise ValueError("taxonomy output_kind and input_requirement are invalid")
        try:
            claim_levels = tuple(item if isinstance(item, ClaimLevel) else ClaimLevel(item) for item in self.claim_levels)
        except (TypeError, ValueError) as exc:
            raise ValueError("taxonomy claim_levels must contain ClaimLevel values") from exc
        if not claim_levels:
            raise ValueError("taxonomy claim_levels must be non-empty ClaimLevel values")
        object.__setattr__(self, "claim_levels", claim_levels)


_ENTRIES: tuple[TaxonomyEntry, ...] = (
    TaxonomyEntry(
        "visual.duck_rabbit",
        "Duck-rabbit ambiguous figure",
        (Modality.VISUAL,),
        (Mechanism.AMBIGUITY,),
        (PerceptualSignature.BISTABILITY,),
        (CognitiveProcess.PERCEPTUAL_ORGANIZATION,),
        ("display with sufficient contrast",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("gregory1997visual", "brugger1999duckrabbit"),
        ImplementationStatus.IMPLEMENTED,
        "A controllable ambiguous silhouette with a continuous duck/rabbit blend.",
    ),
    TaxonomyEntry(
        "visual.simultaneous_contrast",
        "Simultaneous contrast stimulus",
        (Modality.VISUAL,),
        (Mechanism.CONTRAST,),
        (PerceptualSignature.CONTRAST_DISTORTION,),
        (CognitiveProcess.CONTEXTUAL_INFERENCE,),
        ("stable display luminance",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("gregory1997visual",),
        ImplementationStatus.IMPLEMENTED,
        "Matched central patches embedded in different luminance surrounds.",
    ),
    TaxonomyEntry(
        "visual.apparent_motion",
        "Apparent-motion frame sequence",
        (Modality.VISUAL,),
        (Mechanism.TEMPORAL_MOTION,),
        (PerceptualSignature.ILLUSORY_MOTION,),
        (CognitiveProcess.TEMPORAL_INFERENCE,),
        ("fixed frame timing",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("gregory1997visual", "sekuler1996wertheimer", "wertheimer1912motion"),
        ImplementationStatus.IMPLEMENTED,
        "Alternating spatial positions designed to probe apparent motion.",
    ),
    TaxonomyEntry(
        "audio.shepard_tone",
        "Shepard-tone continuity stimulus",
        (Modality.AUDITORY,),
        (Mechanism.SPECTRAL,),
        (PerceptualSignature.CONTINUITY,),
        (CognitiveProcess.SPECTRAL_INFERENCE,),
        ("headphones or controlled playback",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("shepard1984scale",),
        ImplementationStatus.IMPLEMENTED,
        "Overlapping octave-spaced partials with a deterministic spectral envelope.",
    ),
    TaxonomyEntry(
        "audio.missing_fundamental",
        "Missing-fundamental stimulus",
        (Modality.AUDITORY,),
        (Mechanism.SPECTRAL,),
        (PerceptualSignature.FILLING_IN,),
        (CognitiveProcess.SPECTRAL_INFERENCE,),
        ("controlled playback level",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("zatorre2005missing",),
        ImplementationStatus.IMPLEMENTED,
        "Harmonic partials are rendered while the fundamental component is omitted.",
    ),
    TaxonomyEntry(
        "audiovisual.sound_induced_flash",
        "Sound-induced flash stimulus",
        (Modality.AUDIOVISUAL,),
        (Mechanism.CROSSMODAL_TEMPORAL,),
        (PerceptualSignature.FUSION_FISSION,),
        (CognitiveProcess.MULTISENSORY_INTEGRATION,),
        ("stable audio/video clock",),
        EvidenceStatus.REVIEW_BACKED_ENGINEERING_ENTRY,
        ("hirst2020sound",),
        ImplementationStatus.IMPLEMENTED,
        "A flash and one- or two-beep timing contrast on a shared timeline.",
        input_requirement=InputRequirement.CONTROLLED_PLAYBACK,
    ),
    TaxonomyEntry(
        "audiovisual.ventriloquist",
        "Ventriloquist spatial-discrepancy stimulus",
        (Modality.AUDIOVISUAL,),
        (Mechanism.CROSSMODAL_SPATIAL,),
        (PerceptualSignature.SPATIAL_CAPTURE,),
        (CognitiveProcess.MULTISENSORY_INTEGRATION,),
        ("stereo playback and spatially resolved display",),
        EvidenceStatus.REVIEW_BACKED_ENGINEERING_ENTRY,
        ("bruns2019ventriloquist",),
        ImplementationStatus.IMPLEMENTED,
        "A moving visual marker is paired with a stereo spatial discrepancy.",
        input_requirement=InputRequirement.STEREO_PLAYBACK,
    ),
    TaxonomyEntry(
        "visual.muller_lyer",
        "Müller-Lyer geometric illusion",
        (Modality.VISUAL,),
        (Mechanism.GEOMETRIC,),
        (PerceptualSignature.GEOMETRIC_DISTORTION,),
        (CognitiveProcess.CONTEXTUAL_INFERENCE,),
        ("stable display geometry",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("howe2005muller", "gregory1997visual"),
        ImplementationStatus.IMPLEMENTED,
        "Two equal-length bars with controllable inward or outward arrow wings.",
    ),
    TaxonomyEntry(
        "visual.poggendorff",
        "Poggendorff geometric illusion",
        (Modality.VISUAL,),
        (Mechanism.GEOMETRIC,),
        (PerceptualSignature.GEOMETRIC_DISTORTION,),
        (CognitiveProcess.CONTEXTUAL_INFERENCE,),
        ("stable display geometry",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("morgan1999poggendorff", "gregory1997visual"),
        ImplementationStatus.IMPLEMENTED,
        "An occluded diagonal-line alignment stimulus with controllable geometry.",
    ),
    TaxonomyEntry(
        "visual.ponzo",
        "Ponzo perspective illusion",
        (Modality.VISUAL,),
        (Mechanism.GEOMETRIC,),
        (PerceptualSignature.GEOMETRIC_DISTORTION,),
        (CognitiveProcess.CONTEXTUAL_INFERENCE,),
        ("stable display geometry",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("gregory1997visual", "yildiz2022ponzo"),
        ImplementationStatus.IMPLEMENTED,
        "Equal target bars embedded in converging perspective lines.",
    ),
    TaxonomyEntry(
        "visual.kanizsa_triangle",
        "Kanizsa illusory-contour triangle",
        (Modality.VISUAL,),
        (Mechanism.CONTRAST, Mechanism.GEOMETRIC),
        (PerceptualSignature.FILLING_IN,),
        (CognitiveProcess.PERCEPTUAL_ORGANIZATION,),
        ("stable display contrast",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("gregory1997visual", "kanizsa1976contours"),
        ImplementationStatus.IMPLEMENTED,
        "Pacman-like inducers arranged to support an illusory triangular contour.",
    ),
    TaxonomyEntry(
        "visual.ebbinghaus",
        "Ebbinghaus context-size illusion",
        (Modality.VISUAL,),
        (Mechanism.CONTRAST, Mechanism.GEOMETRIC),
        (PerceptualSignature.GEOMETRIC_DISTORTION,),
        (CognitiveProcess.CONTEXTUAL_INFERENCE,),
        ("stable display geometry",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("gregory1997visual", "mruczek2015ebbinghaus"),
        ImplementationStatus.IMPLEMENTED,
        "Equal central circles surrounded by differently sized contextual circles.",
    ),
    TaxonomyEntry(
        "visual.zollner",
        "Zöllner orientation illusion",
        (Modality.VISUAL,),
        (Mechanism.GEOMETRIC,),
        (PerceptualSignature.GEOMETRIC_DISTORTION,),
        (CognitiveProcess.CONTEXTUAL_INFERENCE,),
        ("stable display geometry",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("gregory1997visual", "earle1995zollner"),
        ImplementationStatus.IMPLEMENTED,
        "Crossing oblique-line construction with explicit line spacing and inducer angle.",
    ),
    TaxonomyEntry(
        "audio.tritone_paradox",
        "Tritone paradox pitch pair",
        (Modality.AUDITORY,),
        (Mechanism.SPECTRAL,),
        (PerceptualSignature.CATEGORICAL_RECODING,),
        (CognitiveProcess.SPECTRAL_INFERENCE,),
        ("controlled playback level",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("deutsch1986tritone", "repp1997tritone"),
        ImplementationStatus.IMPLEMENTED,
        "Two Shepard-like pitch complexes separated by a tritone interval.",
    ),
    TaxonomyEntry(
        "audio.octave_illusion",
        "Deutsch octave illusion stimulus",
        (Modality.AUDITORY,),
        (Mechanism.STREAM_SEGREGATION,),
        (PerceptualSignature.FUSION_FISSION,),
        (CognitiveProcess.SPECTRAL_INFERENCE,),
        ("stereo headphones with channel separation",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("deutsch1974octave",),
        ImplementationStatus.IMPLEMENTED,
        "Alternating high and low tones presented dichotically across stereo channels.",
        input_requirement=InputRequirement.STEREO_PLAYBACK,
    ),
    TaxonomyEntry(
        "audio.auditory_continuity",
        "Auditory continuity illusion",
        (Modality.AUDITORY,),
        (Mechanism.STREAM_SEGREGATION,),
        (PerceptualSignature.CONTINUITY,),
        (CognitiveProcess.SPECTRAL_INFERENCE,),
        ("controlled playback level and masker calibration",),
        EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
        ("warren1970continuity", "riecke2011continuity"),
        ImplementationStatus.IMPLEMENTED,
        "Interrupted carrier with a deterministic tone or white-noise masker.",
    ),
    TaxonomyEntry(
        "audiovisual.temporal_ventriloquism",
        "Temporal ventriloquism stimulus",
        (Modality.AUDIOVISUAL,),
        (Mechanism.CROSSMODAL_TEMPORAL,),
        (PerceptualSignature.TEMPORAL_BINDING,),
        (CognitiveProcess.TEMPORAL_INFERENCE,),
        ("stable audio/video clock",),
        EvidenceStatus.REVIEW_BACKED_ENGINEERING_ENTRY,
        ("hirst2020sound", "vroomen2004temporal", "hartcherobrien2011temporal"),
        ImplementationStatus.IMPLEMENTED,
        "A visual event is paired with an audio click at a controlled temporal offset.",
        input_requirement=InputRequirement.CONTROLLED_PLAYBACK,
    ),
    TaxonomyEntry(
        "audiovisual.mcgurk",
        "McGurk speech stimulus",
        (Modality.AUDIOVISUAL,),
        (Mechanism.SPEECH_CATEGORIZATION,),
        (PerceptualSignature.CATEGORICAL_RECODING,),
        (CognitiveProcess.SPEECH_PERCEPTION,),
        ("validated speech audio and face/video input",),
        EvidenceStatus.LITERATURE_BACKED_INPUT_DEPENDENT_ENTRY,
        ("mcgurk1976speech",),
        ImplementationStatus.INPUT_REQUIRED,
        "Catalogued for a future fixture-backed speech/audio-visual adapter.",
        input_requirement=InputRequirement.VALIDATED_SPEECH_FIXTURE,
    ),
)


def taxonomy_entries(*, include_unimplemented: bool = True) -> tuple[TaxonomyEntry, ...]:
    """Return stable catalog entries, optionally excluding future entries."""
    if include_unimplemented:
        return _ENTRIES
    return tuple(entry for entry in _ENTRIES if entry.implementation_status is ImplementationStatus.IMPLEMENTED)


def get_taxonomy(illusion_id: str) -> TaxonomyEntry:
    """Return metadata for one illusion or raise ``KeyError``."""
    for entry in _ENTRIES:
        if entry.illusion_id == illusion_id:
            return entry
    raise KeyError(f"unknown illusion id: {illusion_id}")


def validate_taxonomy_catalog(entries: tuple[TaxonomyEntry, ...] | None = None) -> tuple[TaxonomyEntry, ...]:
    """Validate uniqueness and status invariants for the complete catalog."""
    selected = taxonomy_entries() if entries is None else entries
    ids = [entry.illusion_id for entry in selected]
    if len(ids) != len(set(ids)):
        raise ValueError("taxonomy illusion IDs must be unique")
    for entry in selected:
        if entry.implementation_status is ImplementationStatus.INPUT_REQUIRED and entry.input_requirement is InputRequirement.NONE:
            raise ValueError(f"input_required entry {entry.illusion_id} must declare an input requirement")
        if entry.implementation_status is ImplementationStatus.PLANNED and entry.evidence_status is not EvidenceStatus.LITERATURE_BACKED_PLANNED_ENTRY:
            raise ValueError(f"planned entry {entry.illusion_id} must use planned evidence status")
        if entry.implementation_status is ImplementationStatus.IMPLEMENTED and entry.evidence_status not in {
            EvidenceStatus.LITERATURE_BACKED_ENGINEERING_ENTRY,
            EvidenceStatus.REVIEW_BACKED_ENGINEERING_ENTRY,
        }:
            raise ValueError(f"implemented entry {entry.illusion_id} must have engineering evidence status")
        if entry.implementation_status is ImplementationStatus.INPUT_REQUIRED and entry.evidence_status is not EvidenceStatus.LITERATURE_BACKED_INPUT_DEPENDENT_ENTRY:
            raise ValueError(f"input_required entry {entry.illusion_id} must use input-dependent evidence status")
        if len(set(entry.evidence_references)) != len(entry.evidence_references):
            raise ValueError(f"taxonomy evidence references must be unique for {entry.illusion_id}")
        if entry.output_kind is OutputKind.AUDIOVISUAL and Modality.AUDIOVISUAL not in entry.modalities:
            raise ValueError(f"audiovisual output {entry.illusion_id} must declare audio_visual modality")
        expected_kind = (
            OutputKind.VIDEO
            if entry.illusion_id == "visual.apparent_motion"
            else OutputKind.IMAGE
            if entry.illusion_id.startswith("visual.")
            else OutputKind.AUDIO
            if entry.illusion_id.startswith("audio.")
            else OutputKind.AUDIOVISUAL
        )
        if entry.output_kind is not expected_kind:
            raise ValueError(f"taxonomy output_kind disagrees with illusion id for {entry.illusion_id}")
        if entry.input_requirement is InputRequirement.VALIDATED_SPEECH_FIXTURE and Modality.AUDIOVISUAL not in entry.modalities:
            raise ValueError(f"speech fixture input requirement is only valid for audiovisual entries: {entry.illusion_id}")
        if entry.implementation_status is ImplementationStatus.IMPLEMENTED and ClaimLevel.CANONICAL_STIMULUS not in entry.claim_levels:
            raise ValueError(f"implemented entry {entry.illusion_id} must declare canonical_stimulus claim level")
        if entry.implementation_status is not ImplementationStatus.IMPLEMENTED and any(
            level in {ClaimLevel.OBSERVER_EFFECT, ClaimLevel.VALIDATED_OBSERVER_EFFECT, ClaimLevel.GENERALIZATION}
            for level in entry.claim_levels
        ):
            raise ValueError(f"future taxonomy entry {entry.illusion_id} cannot claim an observer effect or generalization")
    return selected
