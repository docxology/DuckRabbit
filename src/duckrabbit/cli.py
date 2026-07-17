"""Command-line interface for cataloguing and rendering DuckRabbit stimuli."""

from __future__ import annotations

import argparse
import json
from json import JSONDecodeError
from pathlib import Path
from typing import Sequence

from .generators import default_parameters
from .audit import run_audit
from .errors import BackendUnavailableError, DuckRabbitError, ManifestValidationError, MediaInspectionError, VerificationError
from .inspection import inspect_media, verify_manifest
from .io import atomic_write_text
from .media import backend_capabilities
from .render import generate_artifact, jsonable, parameters_from_json
from .parameters import MediaFormat, OutputSpec
from .publication import generate_publication_outputs
from .schema import parameter_schema
from .synthetic_psychophysics import default_duck_rabbit_diagnostic
from .taxonomy import ImplementationStatus, get_taxonomy, taxonomy_entries


def _read_payload(path: Path | None) -> dict[str, object]:
    if path is None:
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read parameter file {path}: {exc}") from exc
    except JSONDecodeError as exc:
        raise ValueError(f"parameter file {path} is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("parameter file must contain a JSON object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="duckrabbit", description="Generate deterministic multimodal illusion stimuli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list taxonomy entries")
    list_parser.add_argument("--implemented-only", action="store_true")
    list_parser.add_argument("--status", choices=[status.value for status in ImplementationStatus])
    list_parser.add_argument("--json", action="store_true", dest="as_json")

    describe_parser = subparsers.add_parser("describe", help="describe one taxonomy entry and its typed defaults")
    describe_parser.add_argument("illusion_id")

    inspect_parser = subparsers.add_parser("inspect", help="decode and report media facts")
    inspect_parser.add_argument("path", type=Path)
    inspect_parser.add_argument("--format", dest="format_name", choices=[fmt.value for fmt in MediaFormat])

    verify_parser = subparsers.add_parser("verify", help="verify a generated artifact against its manifest")
    verify_parser.add_argument("manifest", type=Path)

    for command in ("validate", "generate"):
        command_parser = subparsers.add_parser(command, help=f"{command} typed parameters")
        command_parser.add_argument("illusion_id")
        command_parser.add_argument("--config", type=Path, help="JSON parameter overrides")
        if command == "generate":
            command_parser.add_argument("--output-dir", type=Path, default=Path("output/media"))
            command_parser.add_argument("--format", dest="format_name", choices=[fmt.value for fmt in MediaFormat])
            command_parser.add_argument("--seed", type=int, default=0)
            command_parser.add_argument("--no-manifest", action="store_true")
            command_parser.add_argument("--no-overwrite", action="store_true")
    publish_parser = subparsers.add_parser("publish", help="generate figures, tables, and publication registries")
    publish_parser.add_argument("--output-dir", type=Path, default=Path("output"))
    publish_parser.add_argument("--clean", action="store_true", help="remove stale generated files in figures/data")
    synthetic_parser = subparsers.add_parser("synthetic-psychophysics", help="run the transparent model-output diagnostic")
    synthetic_parser.add_argument("--output", type=Path, default=Path("output/data/synthetic_psychophysics_cli.json"))
    subparsers.add_parser("capabilities", help="probe available encoding and inspection backends")
    audit_parser = subparsers.add_parser("audit", help="run the independent package and publication verifier")
    audit_parser.add_argument("--project-root", type=Path)
    audit_parser.add_argument("--output-root", type=Path)
    audit_parser.add_argument("--release", action="store_true", help="fail on missing or incomplete publication-release outputs")
    return parser


def _run(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = build_parser().parse_args(argv)
    if args.command == "list":
        entries = taxonomy_entries(include_unimplemented=not args.implemented_only)
        if args.status:
            entries = tuple(entry for entry in entries if entry.implementation_status.value == args.status)
        if args.as_json:
            print(json.dumps(jsonable(entries), indent=2, sort_keys=True))
            return 0
        for entry in entries:
            print(f"{entry.illusion_id}\t{entry.implementation_status.value}\t{entry.description}")
        return 0

    if args.command == "describe":
        entry = get_taxonomy(args.illusion_id)
        description: dict[str, object] = {"taxonomy": jsonable(entry)}
        if entry.implementation_status is ImplementationStatus.IMPLEMENTED:
            parameters = default_parameters(args.illusion_id)
            description["parameter_type"] = type(parameters).__name__
            description["defaults"] = jsonable(parameters)
            description["parameter_schema"] = parameter_schema(parameters).to_json()
        else:
            description["parameter_type"] = None
            description["defaults"] = None
            description["parameter_schema"] = None
        if entry.output_kind is None:  # defensive guard for malformed external taxonomy data
            raise ValueError(f"taxonomy entry has no output kind: {entry.illusion_id}")
        description["output_kind"] = entry.output_kind.value
        description["input_requirement"] = entry.input_requirement.value
        description["claim_levels"] = [level.value for level in entry.claim_levels]
        print(json.dumps(description, indent=2, sort_keys=True))
        return 0

    if args.command == "inspect":
        print(json.dumps(inspect_media(args.path, args.format_name).to_dict(), indent=2, sort_keys=True))
        return 0

    if args.command == "verify":
        try:
            report = verify_manifest(args.manifest)
        except (BackendUnavailableError, ManifestValidationError, MediaInspectionError, VerificationError) as exc:
            report = {
                "status": "failed",
                "checks": [],
                "errors": [str(exc)],
                "manifest": str(args.manifest),
            }
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("status") == "verified" else 1

    if args.command == "publish":
        print(json.dumps(generate_publication_outputs(args.output_dir, clean=args.clean), indent=2, sort_keys=True))
        return 0

    if args.command == "synthetic-psychophysics":
        payload = default_duck_rabbit_diagnostic().to_dict()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(args.output, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"status": "written", "output": str(args.output), "claim_level": payload["summary"]["claim_level"], "human_data": payload["summary"]["human_data"]}, indent=2, sort_keys=True))
        return 0

    if args.command == "capabilities":
        print(json.dumps([capability.to_dict() for capability in backend_capabilities()], indent=2, sort_keys=True))
        return 0

    if args.command == "audit":
        audit_report = run_audit(project_root=args.project_root, output_root=args.output_root, release=args.release)
        print(json.dumps(audit_report.to_dict(), indent=2, sort_keys=True))
        return 0 if audit_report.status == "passed" else 1

    payload = _read_payload(args.config)
    parameters = default_parameters(args.illusion_id) if not payload else parameters_from_json(args.illusion_id, payload)
    if args.command == "validate":
        print(json.dumps({"illusion_id": args.illusion_id, "parameter_type": type(parameters).__name__, "schema": parameter_schema(parameters).to_json(), "valid": True}, sort_keys=True))
        return 0

    _, manifest = generate_artifact(
        args.illusion_id,
        parameters,
        seed=args.seed,
        output_dir=args.output_dir,
        format_name=args.format_name,
        output_spec=OutputSpec(
            format=args.format_name,
            include_manifest=not args.no_manifest,
            overwrite=not args.no_overwrite,
        ),
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI with structured JSON failures for expected user errors."""
    try:
        return _run(argv)
    except (DuckRabbitError, OSError, ValueError, KeyError, TypeError) as exc:
        command = argv[0] if argv else None
        print(json.dumps({"status": "failed", "command": command, "error_type": type(exc).__name__, "errors": [str(exc)]}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
