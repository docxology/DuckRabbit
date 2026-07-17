#!/usr/bin/env python3
"""Explicit network audit of the checked-in scholarship URL snapshot."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from duckrabbit.evidence import SourceRecord, SourceVerificationStatus, load_evidence_matrix
from duckrabbit.io import atomic_write_text
from duckrabbit.urls import CROSSREF_API_PREFIX, DOI_RESOLVER_PREFIX

_ALLOWED_SCHEMES = frozenset({"http", "https"})


def _open_http(request: Request, *, timeout: float):
    """Open a request after rejecting non-HTTP(S) schemes (CWE-22 hardening)."""
    scheme = urlsplit(request.full_url).scheme.lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f"refusing non-http(s) scheme {scheme!r} for {request.full_url!r}")
    return urlopen(request, timeout=timeout)  # nosec B310 -- scheme allowlisted above


def _title_tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def title_matches(expected: str, observed: str) -> bool:
    """Compare normalized title identity without requiring punctuation parity."""
    expected_tokens = _title_tokens(expected)
    observed_tokens = _title_tokens(observed)
    if not expected_tokens or not observed_tokens:
        return False
    # Crossref often stores a short title while the checked-in record retains
    # a subtitle; a substantial observed-title subset is still identity
    # evidence, unlike a loose keyword hit.
    if observed_tokens <= expected_tokens and len(observed_tokens) / len(expected_tokens) >= 0.50:
        return True
    overlap = len(expected_tokens & observed_tokens) / max(len(expected_tokens), len(observed_tokens))
    return overlap >= 0.70


def classify_http(status: int | None, error: str | None) -> SourceVerificationStatus:
    """Map transport outcomes to epistemic status; blocked is never verified."""
    if status in {401, 403, 405}:
        return SourceVerificationStatus.ACCESS_CONTROLLED
    if status is None or status >= 400 or error:
        return SourceVerificationStatus.UNAVAILABLE
    return SourceVerificationStatus.URL_REACHABLE_UNRESOLVED


def compare_doi_metadata(source: SourceRecord, metadata: dict[str, object]) -> SourceVerificationStatus:
    """Return DOI identity status based on DOI and title, with optional author/year checks."""
    observed_doi = str(metadata.get("DOI", "")).lower().removeprefix(DOI_RESOLVER_PREFIX)
    if not source.doi or observed_doi != source.doi.lower():
        return SourceVerificationStatus.METADATA_MISMATCH
    titles = metadata.get("title", [])
    observed_title = str(titles[0]) if isinstance(titles, list) and titles else ""
    if not title_matches(source.title, observed_title):
        return SourceVerificationStatus.METADATA_MISMATCH
    if source.year is not None and str(metadata.get("published-print", metadata.get("published-online", {}))).find(str(source.year)) < 0:
        return SourceVerificationStatus.METADATA_MISMATCH
    return SourceVerificationStatus.DOI_METADATA_MATCH


def audit_source(source: SourceRecord, *, timeout: float) -> dict[str, object]:
    """Audit URL reachability and, where possible, DOI metadata identity."""
    result: dict[str, object] = {"key": source.key, "url": source.url, "doi": source.doi, "resolver": "network"}
    if source.doi:
        doi_url = f"{CROSSREF_API_PREFIX}{quote(source.doi, safe='')}"
        try:
            with _open_http(Request(doi_url, headers={"User-Agent": "DuckRabbit scholarship audit"}), timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            metadata = payload.get("message", {}) if isinstance(payload, dict) else {}
            status = compare_doi_metadata(source, metadata if isinstance(metadata, dict) else {})
            result.update({"doi_http_status": 200, "metadata": metadata, "verification_status": status.value, "verified": status is SourceVerificationStatus.DOI_METADATA_MATCH})
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            status = classify_http(getattr(exc, "code", None), str(exc))
            result.update({"doi_http_status": getattr(exc, "code", None), "error": str(exc), "verification_status": status.value, "verified": False})
    else:
        request = Request(source.url, method="HEAD", headers={"User-Agent": "DuckRabbit scholarship audit"})
        try:
            with _open_http(request, timeout=timeout) as response:
                status_code = int(response.status)
            status = SourceVerificationStatus.DOI_LESS_ARCHIVAL if 200 <= status_code < 400 else classify_http(status_code, None)
            result.update({"http_status": status_code, "verification_status": status.value, "verified": status is SourceVerificationStatus.DOI_LESS_ARCHIVAL})
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            status = classify_http(getattr(exc, "code", None), str(exc))
            result.update({"http_status": getattr(exc, "code", None), "error": str(exc), "verification_status": status.value, "verified": False})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output/reports/scholarship_audit.json"))
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    sources, entries = load_evidence_matrix()
    results = []
    for source in sources.values():
        results.append(audit_source(source, timeout=args.timeout))
    entry_audit = []
    source_role_counts = {"primary": 0, "review": 0, "theory": 0}
    for record in entries.values():
        for role, keys in (
            ("primary", record.primary_sources),
            ("review", record.review_sources),
            ("theory", record.theory_sources),
        ):
            source_role_counts[role] += len(keys)
        entry_audit.append(
            {
                "illusion_id": record.illusion_id,
                "implementation_status": record.implementation_status.value,
                "evidence_status": record.evidence_status.value,
                "source_keys": list(record.primary_sources + record.review_sources + record.theory_sources),
                "supported_claim": record.supported_claim,
                "supported_claim_level": record.supported_claim_level.value,
                "engineering_basis": record.engineering_basis,
                "evidence_limitations": list(record.evidence_limitations),
                "missing_contract": record.missing_contract,
                "evidence_gap": record.implementation_status.value != "implemented",
            }
        )
    payload = {
        "schema_version": "duckrabbit/scholarship-audit/v1",
        "audited_on": date.today().isoformat(),
        "entry_count": len(entries),
        "source_count": len(sources),
        "verified_count": sum(1 for result in results if result["verified"]),
        "verification_status_counts": {status.value: sum(1 for result in results if result.get("verification_status") == status.value) for status in SourceVerificationStatus},
        "results": results,
        "source_role_counts": source_role_counts,
        "entry_audit": entry_audit,
        "evidence_gap_entries": [row["illusion_id"] for row in entry_audit if row["evidence_gap"]],
        "offline_snapshot": "data/evidence_matrix.json",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(args.output, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("entry_count", "source_count", "verified_count", "audited_on")}, sort_keys=True))
    return 0 if payload["verified_count"] == len(sources) else 1


if __name__ == "__main__":
    raise SystemExit(main())
