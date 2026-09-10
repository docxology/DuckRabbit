"""Stable variables used by the DuckRabbit manuscript and reports."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from collections.abc import Mapping

from .version import __version__
from .evidence import load_evidence_matrix
from .generators import default_parameters, default_registry
from .io import atomic_write_text
from .metrics import measure_artifact
from .publication import publication_table_payloads
from .publication import publication_caption_specs
from .publication_specs import caption_variable_name
from .taxonomy import ImplementationStatus, taxonomy_entries


def generate_variables() -> dict[str, object]:
    """Build manuscript values from the live registry, not prose constants."""
    entries = taxonomy_entries()
    implemented = [spec.illusion_id for spec in default_registry.list()]
    modality_labels = sorted({modality.value.replace("_", "-") for entry in entries for modality in entry.modalities})
    sources, evidence = load_evidence_matrix()
    default_metrics = measure_artifact(default_registry.generate("visual.duck_rabbit", default_parameters("visual.duck_rabbit")))
    unique_values = default_metrics.record("unique_values").value
    mean_luminance = default_metrics.record("mean_luminance").value
    if not isinstance(unique_values, int) or not isinstance(mean_luminance, float):
        raise TypeError("default metric values do not satisfy the manuscript variable contract")
    status_counts = default_registry.status_counts()
    table_payloads = publication_table_payloads()
    variables: dict[str, object] = {
        "PACKAGE_VERSION": __version__,
        "CATALOG_ENTRIES": len(entries),
        "IMPLEMENTED_GENERATORS": len(implemented),
        "IMPLEMENTED_IDS": ", ".join(implemented),
        "MODALITIES": ", ".join(modality_labels),
        "STATUS_LABELS": "implemented, planned, input_required",
        "IMPLEMENTED_COUNT": status_counts[ImplementationStatus.IMPLEMENTED],
        "PLANNED_COUNT": status_counts[ImplementationStatus.PLANNED],
        "INPUT_REQUIRED_COUNT": status_counts[ImplementationStatus.INPUT_REQUIRED],
        "EVIDENCE_RECORDS": len(evidence),
        "SCHOLARLY_SOURCES": len(sources),
        "CLAIM_LEVELS": "canonical_stimulus, physical_metric, encoded_media, source_supported, observer_hypothesis, synthetic_model_output, validated_observer_effect, publication_illustration",
        "DEFAULT_IMAGE_UNIQUE_LEVELS": unique_values,
        "DEFAULT_IMAGE_MEAN_LUMINANCE": f"{mean_luminance:.4f}",
        "PUBLICATION_FIGURES": len(publication_caption_specs()),
        "PUBLICATION_TABLES": len(table_payloads),
        "SCHOLARSHIP_AUDIT_COVERAGE": f"{len(evidence)}/{len(entries)} catalog entries",
        "OBSERVER_DATA_STATUS": "No participant data are bundled; synthetic model output is explicitly nonhuman.",
        "SYNTHETIC_PSYCHOPHYSICS_STATUS": "hand-specified deterministic feature observer; no training data; human_data=false",
        "SYNTHETIC_MODEL_ID": "duckrabbit.synthetic.feature_observer",
        "CATALOG_TABLE_ROWS": table_payloads["catalog_table"]["body"],
        "PARAMETER_TABLE_ROWS": table_payloads["parameter_domains_table"]["body"],
        "ENCODING_TABLE_ROWS": table_payloads["encoding_profiles_table"]["body"],
        "METRIC_TABLE_ROWS": table_payloads["metrics_table"]["body"],
        "OBSERVER_TABLE_ROWS": table_payloads["observer_estimands_table"]["body"],
        "VERIFICATION_TABLE_ROWS": table_payloads["verification_failure_modes_table"]["body"],
        "CAPTION_AUDIT_TABLE_ROWS": table_payloads["caption_audit_table"]["body"],
        "EVIDENCE_AUDIT_TABLE_ROWS": table_payloads["evidence_source_audit_table"]["body"],
        "FORMALISM_TABLE_ROWS": table_payloads["formalism_traceability_table"]["body"],
        "CLAIM_LEDGER_TABLE_ROWS": table_payloads["claim_ledger_table"]["body"],
    }
    for spec in publication_caption_specs():
        variables[caption_variable_name(spec.stem, "caption")] = spec.rendered_caption
        variables[caption_variable_name(spec.stem, "alt")] = spec.alt_text
    return variables


def save_variables(variables: Mapping[str, object], path: Path) -> Path:
    """Write a stable JSON variable mapping."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return atomic_write_text(path, json.dumps(variables, indent=2, sort_keys=True) + "\n")


def hydrate_manuscript_files(variables: Mapping[str, object], project_root: Path) -> Path:
    """Hydrate manuscript files when the sibling template extras are absent."""
    source_dir = project_root / "docs" / "manuscript"
    if not source_dir.is_dir():
        source_dir = project_root / "manuscript"
    output_dir = project_root / "output" / "manuscript"
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("*.md"):
        stale.unlink()
    for stale in output_dir.glob("*.bib"):
        stale.unlink()
    token_pattern = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
    replacements = {key: str(value) for key, value in variables.items()}
    excluded = {"AGENTS.md", "MANUSCRIPT_STATUS.md", "README.md", "SYNTAX.md"}
    for manuscript_file in sorted(source_dir.glob("*.md")):
        if manuscript_file.name in excluded:
            continue
        text = manuscript_file.read_text(encoding="utf-8")
        hydrated = token_pattern.sub(lambda match: replacements.get(match.group(1), match.group(0)), text)
        atomic_write_text(output_dir / manuscript_file.name, hydrated)
    for auxiliary in ("config.yaml", "preamble.md"):
        source = source_dir / auxiliary
        if source.is_file():
            shutil.copy2(source, output_dir / auxiliary)
    for bibliography in source_dir.glob("*.bib"):
        shutil.copy2(bibliography, output_dir / bibliography.name)
    return output_dir
