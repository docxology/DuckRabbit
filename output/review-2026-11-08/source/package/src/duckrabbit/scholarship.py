"""Explicit network audit of the checked-in scholarship evidence matrix.

Transport, DOI-metadata comparison, and title-identity logic live here so
they are importable and testable; ``scripts/audit_scholarship.py`` is the
thin orchestrator that owns argparse, the output path, and the exit code.
"""

from __future__ import annotations

import json
from datetime import date
from typing import IO
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from .errors import ParameterValidationError
from .evidence import SourceRecord, SourceVerificationStatus, _author_identity, _bibliographic_tokens, load_evidence_matrix
from .urls import CROSSREF_API_PREFIX, DOI_RESOLVER_PREFIX

_ALLOWED_SCHEMES = frozenset({"http", "https"})


def _open_http(request: Request, *, timeout: float) -> IO[bytes]:
    """Open a request after rejecting non-HTTP(S) schemes (CWE-22 hardening)."""
    scheme = urlsplit(request.full_url).scheme.lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f"refusing non-http(s) scheme {scheme!r} for {request.full_url!r}")
    return urlopen(request, timeout=timeout)  # nosec B310 -- scheme allowlisted above


def title_matches(expected: str, observed: str) -> bool:
    """Require ordered title identity, allowing only an explicit omitted subtitle.

    A colon-delimited subtitle may be absent when the complete main title has
    at least four words. Arbitrary subsets, reordered words and negations never
    establish identity. Offline bibliography checks require the full title.
    """
    if not isinstance(expected, str) or not isinstance(observed, str):
        return False
    try:
        expected_tokens = _bibliographic_tokens(expected)
        observed_tokens = _bibliographic_tokens(observed)
        if not expected_tokens or not observed_tokens:
            return False
        if expected_tokens == observed_tokens:
            return True
        for full, short in ((expected, observed), (observed, expected)):
            main, delimiter, subtitle = full.partition(":")
            if delimiter and subtitle.strip():
                main_tokens = _bibliographic_tokens(main)
                subtitle_tokens = _bibliographic_tokens(subtitle)
                negations = {"no", "not", "never", "neither", "nor", "without", "cannot"}
                if len(main_tokens) >= 4 and len(subtitle_tokens) <= len(main_tokens) and not negations.intersection(subtitle_tokens) and main_tokens == _bibliographic_tokens(short):
                    return True
    except ParameterValidationError:
        return False
    return False


def classify_http(status: int | None, error: str | None) -> SourceVerificationStatus:
    """Map transport outcomes to epistemic status; blocked is never verified."""
    if status in {401, 403, 405}:
        return SourceVerificationStatus.ACCESS_CONTROLLED
    if status is None or not 200 <= status < 400 or error:
        return SourceVerificationStatus.UNAVAILABLE
    return SourceVerificationStatus.URL_REACHABLE_UNRESOLVED


def compare_doi_metadata(source: SourceRecord, metadata: dict[str, object]) -> SourceVerificationStatus:
    """Return DOI identity status based on DOI and title, with optional author/year checks."""
    raw_doi = metadata.get("DOI")
    observed_doi = raw_doi.casefold().removeprefix(DOI_RESOLVER_PREFIX) if isinstance(raw_doi, str) else ""
    if not source.doi or observed_doi != source.doi.casefold():
        return SourceVerificationStatus.METADATA_MISMATCH
    titles = metadata.get("title", [])
    observed_title = titles[0] if isinstance(titles, list) and titles else ""
    if not isinstance(observed_title, str) or not title_matches(source.title, observed_title):
        return SourceVerificationStatus.METADATA_MISMATCH
    if source.authors:
        authors = metadata.get("author")
        if not isinstance(authors, list) or not authors:
            return SourceVerificationStatus.METADATA_MISMATCH
        observed_authors = []
        for author in authors:
            if not isinstance(author, dict):
                return SourceVerificationStatus.METADATA_MISMATCH
            if "name" in author:
                name = author["name"]
                if not isinstance(name, str) or not name.strip() or "family" in author or "given" in author:
                    return SourceVerificationStatus.METADATA_MISMATCH
                observed_authors.append(name)
                continue
            family, given = author.get("family"), author.get("given", "")
            if not isinstance(family, str) or not family.strip() or not isinstance(given, str):
                return SourceVerificationStatus.METADATA_MISMATCH
            observed_authors.append(f"{given} {family}")
        try:
            if tuple(_author_identity(name) for name in observed_authors) != tuple(_author_identity(name) for name in source.authors):
                return SourceVerificationStatus.METADATA_MISMATCH
        except ParameterValidationError:
            return SourceVerificationStatus.METADATA_MISMATCH
    if source.year is not None:
        years: set[int] = set()
        for field in ("published-print", "published-online"):
            published = metadata.get(field)
            if not isinstance(published, dict):
                continue
            date_parts = published.get("date-parts")
            if not isinstance(date_parts, list):
                continue
            for parts in date_parts:
                if (
                    isinstance(parts, list)
                    and 1 <= len(parts) <= 3
                    and all(type(part) is int for part in parts)
                    and 1 <= parts[0] <= 9999
                    and (len(parts) < 2 or 1 <= parts[1] <= 12)
                    and (len(parts) < 3 or 1 <= parts[2] <= 31)
                ):
                    try:
                        date(parts[0], parts[1] if len(parts) > 1 else 1, parts[2] if len(parts) > 2 else 1)
                    except ValueError:
                        continue
                    years.add(parts[0])
        if source.year not in years:
            return SourceVerificationStatus.METADATA_MISMATCH
    return SourceVerificationStatus.DOI_METADATA_MATCH


def audit_source(source: SourceRecord, *, timeout: float) -> dict[str, object]:
    """Audit URL reachability and, where possible, DOI metadata identity."""
    result: dict[str, object] = {"key": source.key, "url": source.url, "doi": source.doi, "resolver": "network", "reachable": False}
    if source.doi:
        doi_url = f"{CROSSREF_API_PREFIX}{quote(source.doi, safe='')}"
        result["reachability_url"] = doi_url
        try:
            with _open_http(Request(doi_url, headers={"User-Agent": "DuckRabbit scholarship audit"}), timeout=timeout) as response:
                result.update({"doi_http_status": int(response.status), "reachable": 200 <= int(response.status) < 400})
                payload = json.loads(response.read().decode("utf-8"))
            metadata = payload.get("message", {}) if isinstance(payload, dict) else {}
            status = compare_doi_metadata(source, metadata if isinstance(metadata, dict) else {})
            result.update({"metadata": metadata, "verification_status": status.value, "verified": status is SourceVerificationStatus.DOI_METADATA_MATCH and result["reachable"]})
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            status = classify_http(getattr(exc, "code", None), str(exc))
            result.update({"doi_http_status": getattr(exc, "code", result.get("doi_http_status")), "error": str(exc), "verification_status": status.value, "verified": False})
    else:
        request = Request(source.url, method="HEAD", headers={"User-Agent": "DuckRabbit scholarship audit"})
        result["reachability_url"] = source.url
        try:
            with _open_http(request, timeout=timeout) as response:
                status_code = int(response.status)
            status = classify_http(status_code, None)
            result.update({"http_status": status_code, "reachable": 200 <= status_code < 400, "verification_status": status.value, "verified": False})
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            status = classify_http(getattr(exc, "code", None), str(exc))
            result.update({"http_status": getattr(exc, "code", None), "error": str(exc), "verification_status": status.value, "verified": False})
    return result


def run_scholarship_audit(timeout: float, *, audited_on: str | None = None) -> dict[str, object]:
    """Audit every evidence source and assemble the dated audit payload."""
    sources, entries = load_evidence_matrix()
    results = []
    for source in sources.values():
        results.append(audit_source(source, timeout=timeout))
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
    return {
        "schema_version": "duckrabbit/scholarship-audit/v1",
        "audited_on": audited_on if audited_on is not None else date.today().isoformat(),
        "entry_count": len(entries),
        "source_count": len(sources),
        "verified_count": sum(1 for result in results if result["verified"]),
        "reachable_count": sum(1 for result in results if result["reachable"]),
        "verification_status_counts": {status.value: sum(1 for result in results if result.get("verification_status") == status.value) for status in SourceVerificationStatus},
        "results": results,
        "source_role_counts": source_role_counts,
        "entry_audit": entry_audit,
        "evidence_gap_entries": [row["illusion_id"] for row in entry_audit if row["evidence_gap"]],
        "offline_snapshot": "data/evidence_matrix.json",
    }
