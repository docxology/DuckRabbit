"""Real correctness tests, not benchmark evidence, even when measuring under coverage."""

from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tracemalloc

import pytest

from duckrabbit.performance import WORKLOADS, _run_workloads, _runtime_inputs, _signature, _sources, build_workloads, compare_reports, main, run_workloads


ROOT = Path(__file__).resolve().parents[1]


def test_baseline_read_is_bounded_and_regular(tmp_path) -> None:
    oversized = tmp_path / "oversized.json"
    with oversized.open("wb") as stream:
        stream.truncate(8_000_001)
    for baseline, expected in ((oversized, "8 MB"), (Path(os.devnull), "regular JSON file")):
        with pytest.raises(ValueError, match=expected):
            _run_workloads(root=ROOT, output_dir=tmp_path / "untouched", workloads=("observer",),
                           iterations=1, baseline=baseline)
    assert not (tmp_path / "untouched").exists()


def _subprocess(arguments: list[str], *, root: Path = ROOT) -> subprocess.CompletedProcess:
    environment = {name: value for name, value in os.environ.items()
                   if name != "COVERAGE_PROCESS_START" and not name.startswith("COV_CORE_")}
    environment["PYTHONPATH"] = str(root / "src")
    return subprocess.run([sys.executable, *arguments], cwd=root, env=environment, capture_output=True, text=True)


def _checkout(destination: Path) -> Path:
    for name in ("src", "scripts", "tests", "data", "docs/manuscript", "assets/cover", "output"):
        shutil.copytree(ROOT / name, destination / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for name in ("pyproject.toml", "codemeta.json", "CITATION.cff", ".zenodo.json"):
        shutil.copy2(ROOT / name, destination / name)
    return destination


def test_separate_instrumentation_and_repeatable_baseline(tmp_path) -> None:
    baseline = _run_workloads(root=ROOT, output_dir=tmp_path / "before", workloads=("observer",),
                             iterations=3, profile=True, memory=True)
    row = baseline["workloads"]["observer"]
    assert len(row["samples_seconds"]) == 3
    assert row["range_seconds"] == [min(row["samples_seconds"]), max(row["samples_seconds"])]
    assert row["cprofile"] and row["cprofile"][0]["calls"] > 0
    assert row["traced_peak_bytes"] > 0
    assert (tmp_path / "before" / "observer.pstats").stat().st_size > 0
    assert not tracemalloc.is_tracing()
    assert baseline["source_files"]["src/duckrabbit/performance.py"]
    assert baseline["environment"]["font"]["sha256"]
    current = _run_workloads(root=ROOT, output_dir=tmp_path / "after", workloads=("observer",),
                            iterations=1, baseline=tmp_path / "before" / "report.json")
    assert current["comparison"]["observer"]["comparable"] is True
    assert "cprofile" not in current["workloads"]["observer"]
    assert "traced_peak_bytes" not in current["workloads"]["observer"]
    assert not list((tmp_path / "after").glob("*.pstats"))
    assert json.loads((tmp_path / "after" / "report.json").read_text()) == current
    changed_source = deepcopy(current)
    changed_source["source_files"]["src/duckrabbit/performance.py"] = "0" * 64
    changed_source["source_sha256"] = _signature(changed_source["source_files"])
    assert compare_reports(changed_source, baseline)["observer"]["comparable"] is True
    for field in ("config", "result_signature", "environment"):
        incompatible = deepcopy(current)
        if field == "environment":
            incompatible[field]["python"] = "different Python"
        elif field == "config":
            incompatible["workloads"]["observer"][field]["scenario"] = "different scenario"
        else:
            incompatible["workloads"]["observer"][field] = "0" * 64
        comparison = compare_reports(incompatible, baseline)["observer"]
        assert comparison["comparable"] is False
        assert field in comparison["mismatches"]
        assert "median_ratio_current_over_baseline" not in comparison


def test_prebuilt_video_metrics_and_real_media_roundtrip(tmp_path) -> None:
    report = _run_workloads(root=ROOT, output_dir=tmp_path, workloads=("canonical", "video_metrics", "media"), iterations=1)
    rows = report["workloads"]
    assert rows["canonical"]["config"]["input_digest"] == rows["video_metrics"]["config"]["input_digest"]
    parameters = rows["canonical"]["config"]["parameters"]["config"]
    assert parameters["width"] == 512 and parameters["height"] == 384 and parameters["frame_count"] >= 24
    assert rows["media"]["config"]["formats"] == ["npz", "png", "gif", "wav"]
    assert set(path.name for path in tmp_path.iterdir()) == {"report.json"}
    assert all(len(row["result_signature"]) == 64 for row in rows.values())


def test_catalog_and_synthetic_are_repeatable_real_computations(tmp_path) -> None:
    report = _run_workloads(root=ROOT, output_dir=tmp_path, workloads=("catalog", "synthetic"), iterations=1)
    assert len(report["workloads"]["catalog"]["config"]["requests"]) >= 17
    assert report["workloads"]["synthetic"]["config"]["human_data"] is False


def test_source_binding_detects_added_changed_and_removed_files(tmp_path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    module = source / "module.py"
    module.write_text("value = 1\n")
    original = _sources(tmp_path)
    added = source / "added.py"
    added.write_text("value = 2\n")
    assert _sources(tmp_path) != original
    added.unlink()
    assert _sources(tmp_path) == original
    module.write_text("value = 3\n")
    assert _sources(tmp_path) != original
    module.unlink()
    assert _sources(tmp_path) != original


def test_incompatible_cli_comparison_exits_nonzero_with_report(tmp_path) -> None:
    script = str(ROOT / "scripts/profile_workloads.py")
    before = _subprocess([script, "--output-dir", str(tmp_path / "before"), "--workloads", "observer", "--iterations", "1"])
    assert before.returncode == 0, before.stderr
    report = json.loads((tmp_path / "before/report.json").read_text())
    report["environment"]["python"] = "different interpreter"
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps(report))
    result = _subprocess([script, "--output-dir", str(tmp_path / "after"), "--workloads", "observer", "--iterations", "1", "--compare", str(baseline)])
    assert result.returncode == 2
    assert "no speedup claim" in result.stderr
    assert (tmp_path / "after" / "report.json").is_file()


@pytest.mark.parametrize("options", [
    {"iterations": True}, {"iterations": 0}, {"iterations": 31}, {"iterations": 3.0},
    {"workloads": ()}, {"workloads": "observer"}, {"workloads": ("missing",)},
    {"workloads": ("observer", "observer")}, {"workloads": ([],)},
    {"profile": 1}, {"memory": "yes"}, {"output_dir": "not-a-path"},
])
def test_inputs_fail_before_output_creation(tmp_path, options) -> None:
    arguments = {"root": ROOT, "output_dir": tmp_path / "untouched", "workloads": ("observer",), "iterations": 1}
    arguments.update(options)
    with pytest.raises(ValueError):
        _run_workloads(**arguments)
    assert not (tmp_path / "untouched").exists()


@pytest.mark.parametrize("payload", ["[]", "{}", "null", "not JSON", '{"schema_version":"duckrabbit/performance/v1","environment":{}}'])
def test_invalid_baseline_is_clean_cli_error(tmp_path, payload, capsys) -> None:
    baseline = tmp_path / "baseline.json"
    baseline.write_text(payload)
    with pytest.raises(SystemExit) as error:
        main(["--workloads", "observer", "--iterations", "1", "--output-dir", str(tmp_path / "new"), "--compare", str(baseline)])
    assert error.value.code == 2
    assert "profile-workloads:" in capsys.readouterr().err
    assert not (tmp_path / "new").exists()


def test_malformed_samples_and_missing_comparison_workload(tmp_path) -> None:
    report = _run_workloads(root=ROOT, output_dir=tmp_path, workloads=("observer",), iterations=1)
    for samples in ([True], [float("nan")], [0], [-1], [10 ** 400], [], [1] * 31, "bad"):
        invalid = deepcopy(report)
        invalid["workloads"]["observer"]["samples_seconds"] = samples
        with pytest.raises(ValueError, match="timing samples"):
            compare_reports(report, invalid)
    invalid = deepcopy(report)
    invalid["workloads"]["observer"]["median_seconds"] = True
    with pytest.raises(ValueError, match="median"):
        compare_reports(report, invalid)
    baseline = deepcopy(report)
    baseline["workloads"]["canonical"] = baseline["workloads"].pop("observer")
    assert compare_reports(report, baseline)["observer"]["mismatches"] == ["missing baseline workload"]


def test_active_memory_tracer_is_not_mislabeled_as_unprofiled(tmp_path) -> None:
    tracemalloc.start()
    try:
        with pytest.raises(ValueError, match="no active tracer"):
            run_workloads(root=ROOT, output_dir=tmp_path, workloads=("observer",), iterations=1)
    finally:
        tracemalloc.stop()


def test_public_guard_rejects_real_reserved_monitoring_tools(tmp_path) -> None:
    result = _subprocess(["-c", f"""
from pathlib import Path
import sys
from duckrabbit.performance import run_workloads
output = Path({str(tmp_path / 'measurement')!r})
monitoring = getattr(sys, 'monitoring', None)
if monitoring is None:
    assert sys.version_info < (3, 12)
    report = run_workloads(root=Path.cwd(), output_dir=output, workloads=('observer',), iterations=1)
    assert report['workloads']['observer']['samples_seconds']
else:
    original = [monitoring.get_tool(tool_id) for tool_id in range(6)]
    for tool_id, owner in enumerate(original):
        if owner is None:
            monitoring.use_tool_id(tool_id, 'duckrabbit-correctness-test')
        try:
            try:
                run_workloads(root=Path.cwd(), output_dir=output, workloads=('observer',), iterations=1)
            except ValueError as error:
                assert 'monitoring tool' in str(error)
            else:
                raise AssertionError('reserved monitoring tool accepted')
            assert not output.exists()
        finally:
            if owner is None:
                monitoring.free_tool_id(tool_id)
    assert [monitoring.get_tool(tool_id) for tool_id in range(6)] == original
"""])
    assert result.returncode == 0, result.stderr


def test_thin_cli_missing_unknown_and_valid_workload(tmp_path) -> None:
    script = ROOT / "scripts" / "profile_workloads.py"
    for arguments in ([], ["--output-dir", str(tmp_path), "--workloads", "unknown"],
                      ["--output-dir", str(tmp_path), "--workloads"]):
        result = _subprocess([str(script), *arguments])
        assert result.returncode == 2
        assert "Traceback" not in result.stderr
    result = _subprocess([str(script), "--output-dir", str(tmp_path), "--workloads", "observer", "--iterations", "1"])
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "report.json").is_file()
    assert set(build_workloads(ROOT, ("publication", "audit"))) == {"publication", "audit"}
    assert len(WORKLOADS) == 8


def test_arbitrary_existing_root_cannot_bind_unrelated_sources(tmp_path) -> None:
    with pytest.raises(ValueError, match="executing source checkout"):
        _run_workloads(root=tmp_path, output_dir=tmp_path / "untouched", workloads=("observer",), iterations=1)
    assert not (tmp_path / "untouched").exists()


@pytest.mark.parametrize("damage", ["missing-anchor", "foreign-module"])
def test_checkout_requires_source_anchors_and_loaded_module_origins(tmp_path, damage) -> None:
    checkout = _checkout(tmp_path / "checkout")
    setup = ""
    if damage == "missing-anchor":
        (checkout / "scripts/profile_workloads.py").unlink()
    else:
        foreign = tmp_path / "foreign.py"
        foreign.write_text("value = 1\n")
        setup = f"""
import importlib.util
import sys
spec = importlib.util.spec_from_file_location('duckrabbit.foreign', {str(foreign)!r})
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
"""
    result = _subprocess(["-c", f"""
from pathlib import Path
from duckrabbit.performance import _run_workloads
{setup}
try:
    _run_workloads(root=Path.cwd(), output_dir=Path('untouched'), workloads=('observer',), iterations=1)
except ValueError as error:
    print(error)
else:
    raise AssertionError('invalid checkout accepted')
"""], root=checkout)
    assert result.returncode == 0, result.stderr
    assert "executing source checkout" in result.stdout
    assert not (checkout / "untouched").exists()


def test_missing_and_corrupt_baseline_source_provenance(tmp_path) -> None:
    report = _run_workloads(root=ROOT, output_dir=tmp_path / "valid", workloads=("observer",), iterations=1)
    for damage in ("missing-map", "empty-map", "missing-anchor", "invalid-hash", "invalid-path", "missing-aggregate", "inconsistent-aggregate"):
        invalid = deepcopy(report)
        if damage == "missing-map":
            invalid.pop("source_files")
        elif damage == "empty-map":
            invalid["source_files"] = {}
        elif damage == "missing-anchor":
            invalid["source_files"].pop("pyproject.toml")
        elif damage == "invalid-hash":
            invalid["source_files"]["pyproject.toml"] = "not a SHA-256"
        elif damage == "invalid-path":
            invalid["source_files"]["../foreign.py"] = "0" * 64
        elif damage == "missing-aggregate":
            invalid.pop("source_sha256")
        else:
            invalid["source_sha256"] = "0" * 64
        with pytest.raises(ValueError, match="source provenance"):
            compare_reports(report, invalid)
        baseline = tmp_path / "invalid.json"
        baseline.write_text(json.dumps(invalid))
        with pytest.raises(ValueError, match="source provenance"):
            _run_workloads(root=ROOT, output_dir=tmp_path / "untouched", workloads=("observer",), iterations=1, baseline=baseline)
        assert not (tmp_path / "untouched").exists()


def test_publication_and_audit_bind_runtime_inputs_and_comparison(tmp_path) -> None:
    checkout = _checkout(tmp_path / "checkout")
    selected = build_workloads(checkout, ("publication", "audit"))
    required = ("data/evidence_matrix.json", "docs/manuscript/references.bib", "docs/manuscript/config.yaml",
                "docs/manuscript/01_introduction.md", "assets/cover/duckrabbit-cover-v2.png", "codemeta.json",
                "CITATION.cff", ".zenodo.json", "src/duckrabbit/_resources/evidence_matrix.json",
                "src/duckrabbit/_resources/references.bib")
    for workload in selected.values():
        assert set(required).issubset(workload.config["input_files"])
    assert "output/figures/figure_registry.json" in selected["audit"].config["input_files"]
    assert not any(name.startswith("output/") for name in selected["publication"].config["input_files"])
    report = _run_workloads(root=ROOT, output_dir=tmp_path / "report", workloads=("observer",), iterations=1)
    for name in required + ("output/figures/figure_registry.json",):
        path = checkout / name
        original = path.read_bytes()
        path.write_bytes(original + b"\n")
        changed = build_workloads(checkout, ("publication", "audit"))
        for scenario in ("audit",) if name.startswith("output/") else ("publication", "audit"):
            assert changed[scenario].config["input_files"][name] != selected[scenario].config["input_files"][name]
            baseline = deepcopy(report)
            baseline["workloads"]["observer"]["config"] = selected[scenario].config
            current = deepcopy(baseline)
            current["workloads"]["observer"]["config"] = changed[scenario].config
            comparison = compare_reports(current, baseline)["observer"]
            assert comparison["mismatches"] == ["config"]
            assert "median_ratio_current_over_baseline" not in comparison
        path.write_bytes(original)
    original = _runtime_inputs(checkout)
    added = checkout / "src/duckrabbit/_resources/added.json"
    added.write_text("{}")
    assert _runtime_inputs(checkout) != original
    added.unlink()
    assert _runtime_inputs(checkout) == original
    (checkout / "data/evidence_matrix.json").unlink()
    assert _runtime_inputs(checkout) != original


@pytest.mark.parametrize("target, scenario, boundary, expected", [
    ("codemeta.json", "publication", "generate_publication_outputs", "runtime inputs changed"),
    ("output/AGENTS.md", "audit", "run_audit", "runtime inputs changed"),
    ("src/duckrabbit/performance.py", "observer", "simulate_binary_responses", "source content changed"),
])
def test_real_input_changes_during_measurement_fail_closed(tmp_path, target, scenario, boundary, expected) -> None:
    checkout = _checkout(tmp_path / "checkout")
    result = _subprocess(["-c", f"""
from pathlib import Path
import sys
from duckrabbit.performance import _run_workloads
if {scenario!r} == 'audit':
    from duckrabbit.publication import generate_publication_outputs
    generate_publication_outputs(Path('output'))
changed = False
def mutate_after_operation(frame, event, argument):
    global changed
    if not changed and event == 'return' and frame.f_code.co_name == {boundary!r}:
        changed = True
        path = Path({target!r})
        path.write_bytes(path.read_bytes() + b'\\n')
sys.setprofile(mutate_after_operation)
try:
    _run_workloads(root=Path.cwd(), output_dir=Path('measurement'), workloads=({scenario!r},), iterations=1)
except ValueError as error:
    assert {expected!r} in str(error), str(error)
else:
    raise AssertionError('unstable inputs accepted')
finally:
    sys.setprofile(None)
assert changed
assert not Path('measurement/report.json').exists()
"""], root=checkout)
    assert result.returncode == 0, result.stderr
