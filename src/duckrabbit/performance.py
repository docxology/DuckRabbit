"""Repeatable real-workload measurements; instrumentation uses separate passes."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import cProfile
from dataclasses import dataclass
import hashlib
from importlib.metadata import version
import inspect
import json
import math
import os
from pathlib import Path
import platform
import pstats
import statistics
import stat
import sys
import tempfile
import time
import tracemalloc
from typing import Callable, Iterator

from PIL import features

from .canonical import canonical_digest
from .errors import DuckRabbitError
from .generators import ApparentMotionParams, default_parameters, default_registry, generate_apparent_motion
from .inspection import inspect_media
from .io import atomic_write_text, sha256_file
from .media import read_npz, write_gif, write_npz, write_png, write_wav
from .metrics import measure_artifact
from .observer_analysis import build_trial_sequence, default_study_design, simulate_binary_responses
from .parameters import VideoConfig
from .serialization import jsonable
from .synthetic_psychophysics import default_duck_rabbit_diagnostic


SCHEMA = "duckrabbit/performance/v1"
WORKLOADS = ("catalog", "canonical", "video_metrics", "synthetic", "observer", "media", "publication", "audit")
SOURCE_ANCHORS = ("pyproject.toml", "scripts/profile_workloads.py", "src/duckrabbit/__init__.py", "src/duckrabbit/performance.py")


def _json(value: object) -> str:
    return json.dumps(jsonable(value), sort_keys=True, separators=(",", ":"), allow_nan=False)


def _signature(value: object) -> str:
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _files(root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): sha256_file(path) for path in sorted(root.rglob("*")) if path.is_file()}


def _sources(root: Path) -> dict[str, str]:
    paths = list((root / "src").rglob("*.py")) + [root / "scripts/profile_workloads.py", root / "pyproject.toml"]
    return {str(path.relative_to(root)): sha256_file(path) for path in sorted(paths) if path.is_file()}


def _validate_checkout(root: Path) -> None:
    if root.resolve() != Path(__file__).resolve().parents[2] or any(not (root / name).is_file() for name in SOURCE_ANCHORS):
        raise ValueError("root must be the executing source checkout with all required source files")
    package = (root / "src" / "duckrabbit").resolve()
    for name, module in tuple(sys.modules.items()):
        if name == "duckrabbit" or name.startswith("duckrabbit."):
            filename = getattr(module, "__file__", None)
            relative = Path(*name.split(".")[1:])
            candidates = ((package / "__init__.py",) if name == "duckrabbit" else
                          (package / relative.with_suffix(".py"), package / relative / "__init__.py"))
            if filename is None or Path(filename).resolve() not in candidates or not Path(filename).is_file():
                raise ValueError(f"loaded module {name} is not from the executing source checkout")


def _runtime_inputs(root: Path, *, audit: bool = False) -> dict[str, str]:
    directories = ("data", "docs/manuscript", "assets/cover", "src/duckrabbit/_resources") + (("output",) if audit else ())
    paths = [root / name for name in ("pyproject.toml", "codemeta.json", "CITATION.cff", ".zenodo.json")]
    paths += [path for name in directories for path in (root / name).rglob("*") if path.is_file()]
    return {str(path.relative_to(root)): sha256_file(path) for path in sorted(paths)}


@dataclass(frozen=True)
class Workload:
    """A fixed scenario whose setup is never part of measured time."""

    config: dict[str, object]
    prepare: Callable[[Path], Callable[[], object]]
    finish: Callable[[object, Path], object] = lambda result, directory: result


def build_workloads(root: Path, names: tuple[str, ...]) -> dict[str, Workload]:
    """Build only selected inputs before timing, without process-wide caches."""
    selected = {}
    if "catalog" in names:
        requests = tuple((spec.illusion_id, default_parameters(spec.illusion_id)) for spec in default_registry.list())

        def catalog() -> object:
            results = []
            for name, parameters in requests:
                artifact = default_registry.generate(name, parameters, seed=0)
                results.append((name, canonical_digest(artifact), measure_artifact(artifact).to_dict()))
            return results

        selected["catalog"] = Workload({"requests": jsonable(requests), "seed": 0}, lambda directory: catalog)
    if {"canonical", "video_metrics", "media"}.intersection(names):
        parameters = ApparentMotionParams(config=VideoConfig(width=512, height=384, frame_count=24))
        video = generate_apparent_motion(parameters, seed=0)
        config = {"parameters": jsonable(parameters), "input_digest": canonical_digest(video), "seed": 0}
        selected["canonical"] = Workload(config, lambda directory: lambda: canonical_digest(video))
        selected["video_metrics"] = Workload(config, lambda directory: lambda: measure_artifact(video).to_dict())
        if "media" in names:
            audio_parameters = default_parameters("audio.shepard_tone")
            audio = default_registry.generate("audio.shepard_tone", audio_parameters, seed=0)

            def media(directory: Path) -> Callable[[], object]:
                def run() -> object:
                    write_npz(video, directory / "video.npz")
                    restored = read_npz(directory / "video.npz")
                    digest = canonical_digest(restored)
                    if digest != config["input_digest"]:
                        raise ValueError("NPZ roundtrip changed canonical video")
                    write_png(video.frames[0], directory / "image.png")
                    write_gif(video, directory / "video.gif")
                    write_wav(audio, directory / "audio.wav")
                    return {suffix: jsonable(inspect_media(directory / filename)) for suffix, filename in
                            (("npz", "video.npz"), ("png", "image.png"), ("gif", "video.gif"), ("wav", "audio.wav"))}
                return run

            selected["media"] = Workload({**config, "audio": jsonable(audio_parameters), "formats": ["npz", "png", "gif", "wav"]},
                media, lambda result, directory: {"inspections": result, "encoded_sha256": _files(directory)})
    if "synthetic" in names:
        selected["synthetic"] = Workload({"diagnostic": "default_duck_rabbit_diagnostic", "human_data": False},
                                         lambda directory: lambda: default_duck_rabbit_diagnostic().to_dict())
    if "observer" in names:
        design = default_study_design()
        observers = tuple(f"observer-{index}" for index in range(design.observers))
        probabilities = {condition.condition_id: 0.65 for condition in design.conditions}
        selected["observer"] = Workload({"design": jsonable(design), "observers": observers, "probabilities": probabilities},
            lambda directory: lambda: (build_trial_sequence(design, observers), simulate_binary_responses(design, observers, probabilities)))
    if "publication" in names:
        from .publication import generate_publication_outputs

        def publication_result(result: object, directory: Path) -> object:
            return {name: hashlib.sha256(path.read_bytes().replace(str(directory).encode(), b"<TEMP>")
                                        .replace(json.dumps(str(directory))[1:-1].encode(), b"<TEMP>")).hexdigest()
                    for name, path in ((str(path.relative_to(directory)), path) for path in sorted(directory.rglob("*")) if path.is_file())}

        selected["publication"] = Workload({"bundle": "complete", "clean": False, "input_files": _runtime_inputs(root)},
            lambda directory: lambda: generate_publication_outputs(directory), publication_result)
    if "audit" in names:
        from .audit import run_audit

        def audit() -> object:
            report = run_audit(project_root=root, output_root=root / "output", release=True)
            if report.status != "passed":
                raise ValueError("strict checkout audit failed: " + _json(report.to_dict()))
            return report.to_dict()

        selected["audit"] = Workload({"release": True, "input_files": _runtime_inputs(root, audit=True)}, lambda directory: audit)
    definition = hashlib.sha256(inspect.getsource(build_workloads).encode()).hexdigest()
    return {name: Workload({**selected[name].config, "definition_sha256": definition}, selected[name].prepare, selected[name].finish) for name in names}


def _environment() -> dict[str, object]:
    from .publication import _font

    font = Path(_font(20).path)
    return {"python": sys.version, "implementation": platform.python_implementation(), "platform": platform.platform(),
            "machine": platform.machine(), "processor": platform.processor(),
            "dependencies": {name: version(name) for name in ("numpy", "Pillow")},
            "font": {"path": str(font), "sha256": sha256_file(font), "name": list(_font(20).getname()), "freetype": features.version("freetype2")},
            "zlib": features.version("zlib")}


@contextmanager
def _prepared(workload: Workload) -> Iterator[tuple[Callable[[], object], Path]]:
    with tempfile.TemporaryDirectory(prefix="duckrabbit-profile-") as temporary:
        directory = Path(temporary)
        yield workload.prepare(directory), directory


def _validate_report(report: object) -> dict:
    if not isinstance(report, dict) or report.get("schema_version") != SCHEMA or not isinstance(report.get("environment"), dict):
        raise ValueError("invalid baseline report schema/environment")
    sources = report.get("source_files")
    if not isinstance(sources, dict) or not sources or not set(SOURCE_ANCHORS).issubset(sources):
        raise ValueError("invalid baseline source provenance: missing source files/anchors")
    for name, digest in sources.items():
        if not isinstance(name, str) or not name or Path(name).is_absolute() or ".." in Path(name).parts or not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("invalid baseline source provenance: expected relative paths and SHA-256 hashes")
    if report.get("source_sha256") != _signature(sources):
        raise ValueError("invalid baseline source provenance: inconsistent aggregate SHA-256")
    environment = report["environment"]
    if not all(isinstance(environment.get(key), str) for key in ("python", "implementation", "platform", "machine", "processor")) or not all(isinstance(environment.get(key), dict) for key in ("dependencies", "font")):
        raise ValueError("invalid baseline environment fields")
    rows = report.get("workloads")
    if not isinstance(rows, dict) or not rows or len(rows) > len(WORKLOADS) or set(rows) - set(WORKLOADS):
        raise ValueError("invalid baseline workloads")
    for row in rows.values():
        if not isinstance(row, dict) or not isinstance(row.get("config"), dict):
            raise ValueError("invalid baseline workload configuration")
        signature, samples = row.get("result_signature"), row.get("samples_seconds")
        if not isinstance(signature, str) or len(signature) != 64 or any(char not in "0123456789abcdef" for char in signature):
            raise ValueError("invalid baseline result signature")
        if not isinstance(samples, list) or not 1 <= len(samples) <= 30 or any(type(sample) not in (int, float) or not 0 < sample < 1e12 or not math.isfinite(sample) for sample in samples):
            raise ValueError("invalid baseline timing samples")
        if type(row.get("median_seconds")) not in (int, float) or row["median_seconds"] != statistics.median(samples):
            raise ValueError("invalid baseline median")
    return report


def compare_reports(current: dict, baseline: dict) -> dict[str, object]:
    """Compare only matching scenarios/environments/results, not source revisions."""
    _validate_report(current)
    _validate_report(baseline)
    comparisons = {}
    for name, row in current["workloads"].items():
        previous = baseline["workloads"].get(name)
        reasons = (["missing baseline workload"] if previous is None else
                   [field for field in ("config", "result_signature") if _json(row[field]) != _json(previous[field])])
        if current["environment"] != baseline["environment"]:
            reasons.append("environment")
        comparisons[name] = {"comparable": not reasons, "mismatches": reasons}
        if not reasons:
            comparisons[name]["median_ratio_current_over_baseline"] = row["median_seconds"] / previous["median_seconds"]
    return comparisons


def run_workloads(*, root: Path, output_dir: Path, workloads: tuple[str, ...] = WORKLOADS,
                  iterations: int = 3, profile: bool = False, memory: bool = False, baseline: Path | None = None) -> dict:
    """Warm once; time uninstrumented iterations; optionally instrument extra calls."""
    monitoring = getattr(sys, "monitoring", None)
    if (tracemalloc.is_tracing() or sys.getprofile() is not None or sys.gettrace() is not None or
            (monitoring is not None and any(monitoring.get_tool(tool_id) is not None for tool_id in range(6)))):
        raise ValueError("uninstrumented timings require no active tracer, profiler or monitoring tool")
    return _run_workloads(root=root, output_dir=output_dir, workloads=workloads, iterations=iterations,
                          profile=profile, memory=memory, baseline=baseline)


def _run_workloads(*, root: Path, output_dir: Path, workloads: tuple[str, ...] = WORKLOADS,
                   iterations: int = 3, profile: bool = False, memory: bool = False, baseline: Path | None = None) -> dict:
    """Measurement engine; instrumented correctness-test outputs are not benchmark evidence."""
    if type(iterations) is not int or not 1 <= iterations <= 30:
        raise ValueError("iterations must be an integer in [1, 30]")
    if type(profile) is not bool or type(memory) is not bool:
        raise ValueError("profile and memory must be booleans")
    if not isinstance(workloads, (tuple, list)) or not workloads or len(workloads) > len(WORKLOADS) or any(type(name) is not str or name not in WORKLOADS for name in workloads) or len(set(workloads)) != len(workloads):
        raise ValueError("workloads must be unique known names: " + ", ".join(WORKLOADS))
    if not isinstance(root, Path) or not root.is_dir() or not isinstance(output_dir, Path) or (baseline is not None and not isinstance(baseline, Path)):
        raise ValueError("root/output_dir/baseline must be valid pathlib paths")
    root = root.resolve()
    _validate_checkout(root)
    previous = None
    if baseline is not None:
        if not stat.S_ISREG(baseline.stat().st_mode):
            raise ValueError("baseline must be a regular JSON file")
        with baseline.open("rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError("baseline must be a regular JSON file")
            payload = stream.read(8_000_001)
        if len(payload) > 8_000_000:
            raise ValueError("baseline exceeds 8 MB limit")
        previous = _validate_report(json.loads(payload.decode("utf-8")))
    sources = _sources(root)
    report = {"schema_version": SCHEMA, "source_sha256": _signature(sources), "source_files": sources,
              "environment": _environment(), "iterations": iterations, "warmup_iterations": 1,
              "notes": ["Only samples_seconds are unprofiled timings; cProfile/memory are separate extra calls.",
                        "tracemalloc peak measures traced allocations, not full process RSS."], "workloads": {}}
    selected = build_workloads(root, tuple(workloads))
    _validate_checkout(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, workload in selected.items():
        with _prepared(workload) as (run, directory):
            expected = _signature(workload.finish(run(), directory))
        row = {"config": jsonable(workload.config), "result_signature": expected, "samples_seconds": []}
        for mode in ["timing"] * iterations + (["profile"] if profile else []) + (["memory"] if memory else []):
            with _prepared(workload) as (run, directory):
                if mode == "timing":
                    start = time.perf_counter()
                    result = run()
                    elapsed = time.perf_counter() - start
                    row["samples_seconds"].append(elapsed)
                elif mode == "profile":
                    profiler = cProfile.Profile()
                    result = profiler.runcall(run)
                    profiler.dump_stats(str(output_dir / f"{name}.pstats"))
                    stats = pstats.Stats(profiler)
                    row["cprofile"] = [{"file": key[0], "line": key[1], "function": key[2], "primitive_calls": values[0],
                                        "calls": values[1], "self_seconds": values[2], "cumulative_seconds": values[3]}
                                       for key, values in sorted(stats.stats.items(), key=lambda item: item[1][3], reverse=True)[:25]]
                else:
                    tracemalloc.start()
                    try:
                        result = run()
                        row["traced_peak_bytes"] = tracemalloc.get_traced_memory()[1]
                    finally:
                        tracemalloc.stop()
                if _signature(workload.finish(result, directory)) != expected:
                    raise ValueError(f"non-repeatable result for {name} ({mode})")
        samples = row["samples_seconds"]
        row.update(median_seconds=statistics.median(samples), range_seconds=[min(samples), max(samples)])
        report["workloads"][name] = row
    if previous is not None:
        report["comparison"] = compare_reports(report, previous)
    if _sources(root) != sources:
        raise ValueError("source content changed during measurement; rerun against a stable checkout")
    _validate_checkout(root)
    for name in {"publication", "audit"}.intersection(selected):
        if _runtime_inputs(root, audit=name == "audit") != selected[name].config["input_files"]:
            raise ValueError(f"runtime inputs changed during measurement for {name}; rerun against a stable checkout")
    atomic_write_text(output_dir / "report.json", json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def main(argv: list[str] | None = None) -> int:
    """CLI boundary: explicit output, bounded iteration count, JSON baselines only."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workloads", nargs="+", choices=WORKLOADS, default=list(WORKLOADS))
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--profile", action="store_true", help="separate cProfile call, JSON rows and .pstats")
    parser.add_argument("--memory", action="store_true", help="separate tracemalloc call (not RSS)")
    args = parser.parse_args(argv)
    try:
        report = run_workloads(root=Path(__file__).resolve().parents[2], output_dir=args.output_dir,
                              workloads=tuple(args.workloads), iterations=args.iterations, profile=args.profile,
                              memory=args.memory, baseline=args.compare)
    except (OSError, ValueError, TypeError, RuntimeError, RecursionError, DuckRabbitError) as error:
        parser.exit(2, f"profile-workloads: {error}\n")
    print(args.output_dir / "report.json")
    if any(not row["comparable"] for row in report.get("comparison", {}).values()):
        parser.exit(2, "profile-workloads: incompatible comparison; no speedup claim; see report mismatches\n")
    return 0
