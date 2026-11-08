"""Independent verifier tests and CLI audit smoke coverage."""

from __future__ import annotations

import json

import pytest

import duckrabbit
from duckrabbit.audit import AuditIssue, AuditReport, _check, run_audit
from duckrabbit.cli import main


def test_audit_covers_every_implemented_generator_without_generated_output(tmp_path, capsys) -> None:
    report = run_audit(project_root=None, output_root=tmp_path / "not-generated")
    assert report.status == "passed"
    assert report.generated_artifacts == len(duckrabbit.default_registry.list())
    assert "generators" in report.checks
    assert any(issue.code == "figure_registry.not_generated" for issue in report.issues)
    assert report.to_dict()["error_count"] == 0
    assert main(["audit", "--output-root", str(tmp_path / "not-generated")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "passed"


def test_audit_contracts_are_immutable_and_fail_closed() -> None:
    issue = AuditIssue("x", "warning", "surface", "message")
    report = AuditReport("duckrabbit/audit/v1", "passed", ("check",), (issue,), 0)
    assert report.errors == ()
    assert report.to_dict()["warning_count"] == 1


def test_audit_contract_rejects_malformed_records_and_captures_errors(publication_bundle) -> None:
    with pytest.raises(ValueError, match="audit issue"):
        AuditIssue("", "warning", "surface", "message")
    with pytest.raises(ValueError, match="audit report"):
        AuditReport("bad", "passed", (), (), 0)
    with pytest.raises(ValueError, match="generated_artifacts"):
        AuditReport("duckrabbit/audit/v1", "passed", (), (), -1)
    issues, checks = [], []
    assert _check(issues, checks, "exploding", lambda: (_ for _ in ()).throw(RuntimeError("boom"))) is None
    assert issues[0].severity == "error"
    assert "boom" in issues[0].message
    report = run_audit(output_root=publication_bundle)
    assert report.status == "passed"
    assert not any(issue.code == "figure_registry.not_generated" for issue in report.issues)
