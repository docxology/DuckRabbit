"""Source-tiered evidence records for the DuckRabbit catalog.

The evidence layer is deliberately separate from the generator registry.  A
source can support a historical phenomenon or mechanism without proving that a
particular DuckRabbit approximation produces the same observer effect.
"""

from __future__ import annotations

import json
from importlib.resources import files
from dataclasses import dataclass
from datetime import date
from enum import Enum
from html.parser import HTMLParser
from pathlib import Path
import re
from typing import TYPE_CHECKING, Mapping
from urllib.parse import urlparse
import unicodedata

from .errors import ParameterValidationError
from .taxonomy import ClaimLevel, EvidenceStatus, ImplementationStatus, taxonomy_entries
from .urls import DOI_RESOLVER_PREFIX

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable


class EvidenceRole(str, Enum):
    """Role played by a record in the source-to-claim lineage."""

    PRIMARY_DEMONSTRATION = "primary_demonstration"
    REVIEW_OR_SYNTHESIS = "review_or_synthesis"
    THEORETICAL_ACCOUNT = "theoretical_account"
    ENGINEERING_BASIS = "engineering_basis"
    LIMITATION = "limitation"
    INPUT_GAP = "input_gap"


class SourceVerificationStatus(str, Enum):
    """Evidence metadata status; reachability alone is not verification."""

    SNAPSHOT_VALIDATED = "snapshot_validated"
    DOI_METADATA_MATCH = "doi_metadata_match"
    URL_REACHABLE_UNRESOLVED = "url_reachable_unresolved"
    ACCESS_CONTROLLED = "access_controlled"
    METADATA_MISMATCH = "metadata_mismatch"
    UNAVAILABLE = "unavailable"
    DOI_LESS_ARCHIVAL = "doi_less_archival"


def _immutable_strings(value: object, *, context: str) -> tuple[str, ...]:
    """Detach supported caller-owned sequences before validating their elements."""
    if not isinstance(value, (tuple, list)) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ParameterValidationError(f"{context} must be a sequence of non-empty strings")
    return tuple(value)


@dataclass(frozen=True)
class EvidenceLineage:
    """One typed edge from evidence or engineering state to a claim."""

    role: EvidenceRole
    statement: str
    source_keys: tuple[str, ...] = ()
    claim_level: ClaimLevel = ClaimLevel.SOURCE_SUPPORTED

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_keys", _immutable_strings(self.source_keys, context="evidence lineage source_keys"))
        if not isinstance(self.role, EvidenceRole) or not isinstance(self.statement, str) or not self.statement.strip():
            raise ParameterValidationError("evidence lineage requires a role and statement")
        if not all(isinstance(key, str) and key.strip() for key in self.source_keys):
            raise ParameterValidationError("evidence lineage source_keys must be non-empty strings")
        if not isinstance(self.claim_level, ClaimLevel):
            raise ParameterValidationError("evidence lineage claim_level must be ClaimLevel")

    def to_dict(self) -> dict[str, object]:
        return {
            "role": self.role.value,
            "statement": self.statement,
            "source_keys": list(self.source_keys),
            "claim_level": self.claim_level.value,
        }


@dataclass(frozen=True)
class SourceRecord:
    """A verified scholarly source and the role it plays in the evidence graph."""

    key: str
    citation_key: str
    title: str
    source_type: str
    url: str
    doi: str | None
    supports: str
    verification_status: SourceVerificationStatus = SourceVerificationStatus.SNAPSHOT_VALIDATED
    verified_on: str | None = None
    resolver: str = "offline_snapshot"
    authors: tuple[str, ...] = ()
    year: int | None = None

    def __post_init__(self) -> None:
        for name in ("key", "citation_key", "title", "source_type", "url", "supports"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ParameterValidationError(f"source {name} is required")
        parsed = urlparse(self.url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ParameterValidationError(f"source {self.key} has an invalid URL")
        if self.source_type not in {"primary", "review", "theory"}:
            raise ParameterValidationError(f"source {self.key} has an invalid source type")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9:_-]*", self.key) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9:_-]*", self.citation_key):
            raise ParameterValidationError(f"source {self.key} has an invalid citation identifier")
        if self.doi is not None and (not isinstance(self.doi, str) or not re.fullmatch(r"10\.\d{4,9}/\S+", self.doi)):
            raise ParameterValidationError(f"source {self.key} has an invalid DOI")
        if not isinstance(self.verification_status, SourceVerificationStatus):
            raise ParameterValidationError(f"source {self.key} has an invalid verification status")
        if self.verified_on is not None:
            if not isinstance(self.verified_on, str):
                raise ParameterValidationError(f"source {self.key} verified_on must be an ISO date")
            try:
                date.fromisoformat(self.verified_on)
            except ValueError as exc:
                raise ParameterValidationError(f"source {self.key} verified_on must be an ISO date") from exc
        if not isinstance(self.resolver, str) or not self.resolver.strip():
            raise ParameterValidationError(f"source {self.key} resolver is required")
        object.__setattr__(self, "authors", _immutable_strings(self.authors, context=f"source {self.key} authors"))
        # Historical scholarship is part of the evidence graph; do not impose
        # a modern-publication floor on source years.  Year 0 is excluded
        # because the proleptic Gregorian convention has no year zero.
        if self.year is not None and (type(self.year) is not int or not 1 <= self.year <= date.today().year + 1):
            raise ParameterValidationError(f"source {self.key} year is invalid")

    @property
    def role(self) -> EvidenceRole:
        """Map the compact matrix source type to its explicit evidence role."""
        return {
            "primary": EvidenceRole.PRIMARY_DEMONSTRATION,
            "review": EvidenceRole.REVIEW_OR_SYNTHESIS,
            "theory": EvidenceRole.THEORETICAL_ACCOUNT,
        }[self.source_type]


@dataclass(frozen=True)
class EvidenceRecord:
    """Evidence boundary for one catalog entry."""

    illusion_id: str
    evidence_status: EvidenceStatus
    implementation_status: ImplementationStatus
    primary_sources: tuple[str, ...]
    review_sources: tuple[str, ...]
    theory_sources: tuple[str, ...]
    engineering_basis: str
    evidence_limitations: tuple[str, ...]
    supported_claim: str
    supported_claim_level: ClaimLevel = ClaimLevel.SOURCE_SUPPORTED
    missing_contract: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.illusion_id, str) or not self.illusion_id.strip() or not isinstance(self.evidence_status, EvidenceStatus):
            raise ParameterValidationError("evidence identity and status are required")
        if not isinstance(self.implementation_status, ImplementationStatus):
            raise ParameterValidationError("evidence implementation_status must be ImplementationStatus")
        for name in ("primary_sources", "review_sources", "theory_sources", "evidence_limitations"):
            object.__setattr__(self, name, _immutable_strings(getattr(self, name), context=f"evidence {self.illusion_id} {name}"))
        source_keys = self.primary_sources + self.review_sources + self.theory_sources
        if not source_keys:
            raise ParameterValidationError(f"evidence {self.illusion_id} requires at least one source")
        if not all(isinstance(key, str) and key for key in source_keys) or len(set(source_keys)) != len(source_keys):
            raise ParameterValidationError(f"evidence {self.illusion_id} has invalid or duplicate source keys")
        if not all(isinstance(item, str) and item.strip() for item in (self.engineering_basis, self.supported_claim)):
            raise ParameterValidationError(f"evidence {self.illusion_id} requires claim text")
        if not self.evidence_limitations or not all(isinstance(item, str) and item.strip() for item in self.evidence_limitations):
            raise ParameterValidationError(f"evidence {self.illusion_id} requires limitations")
        if not isinstance(self.supported_claim_level, ClaimLevel):
            raise ParameterValidationError(f"evidence {self.illusion_id} has an invalid claim level")
        if self.supported_claim_level is not ClaimLevel.SOURCE_SUPPORTED:
            raise ParameterValidationError(f"evidence {self.illusion_id} must remain source_supported")
        if self.implementation_status in {ImplementationStatus.PLANNED, ImplementationStatus.INPUT_REQUIRED}:
            if not isinstance(self.missing_contract, str) or not self.missing_contract.strip():
                raise ParameterValidationError(f"evidence {self.illusion_id} requires an explicit missing_contract")
        elif self.missing_contract is not None and not isinstance(self.missing_contract, str):
            raise ParameterValidationError(f"evidence {self.illusion_id} missing_contract must be a string or null")

    def lineage_records(self, sources: Mapping[str, SourceRecord]) -> tuple[EvidenceLineage, ...]:
        """Expand compact source arrays and free-text boundaries into typed edges."""
        rows = [
            EvidenceLineage(
                sources[key].role,
                sources[key].supports,
                (key,),
                ClaimLevel.SOURCE_SUPPORTED,
            )
            for key in self.primary_sources + self.review_sources + self.theory_sources
        ]
        rows.append(EvidenceLineage(EvidenceRole.ENGINEERING_BASIS, self.engineering_basis, (), ClaimLevel.CANONICAL_STIMULUS))
        rows.extend(EvidenceLineage(EvidenceRole.LIMITATION, limitation, (), ClaimLevel.SOURCE_SUPPORTED) for limitation in self.evidence_limitations)
        if self.missing_contract:
            rows.append(EvidenceLineage(EvidenceRole.INPUT_GAP, self.missing_contract, (), ClaimLevel.OBSERVER_HYPOTHESIS))
        return tuple(rows)


def default_manuscript_dir() -> Path:
    """Return the sole canonical checkout manuscript directory."""
    return Path(__file__).resolve().parents[2] / "docs" / "manuscript"


def _runtime_resource(name: str) -> Traversable:
    root = Path(__file__).resolve().parents[2]
    if (root / "pyproject.toml").is_file() and (root / "src" / "duckrabbit").is_dir():
        if name == "references.bib":
            return default_manuscript_dir() / name
        return root / "data" / name
    return files("duckrabbit").joinpath("_resources").joinpath(name)


def _default_matrix_path() -> Traversable:
    return _runtime_resource("evidence_matrix.json")


def _text_field(row: Mapping[str, object], name: str, *, context: str, required: bool = True) -> str | None:
    """Read a text field without silently coercing malformed JSON values."""
    value = row.get(name)
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ParameterValidationError(f"{context} {name} must be a non-empty string")
    return value


def _string_tuple_field(row: Mapping[str, object], name: str, *, context: str) -> tuple[str, ...]:
    """Read a JSON string array with element-level type validation."""
    value = row.get(name, ())
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ParameterValidationError(f"{context} {name} must be an array of non-empty strings")
    return tuple(value)


def load_evidence_matrix(
    path: Path | None = None,
    *,
    bibliography_path: Path | None = None,
    manuscript_dir: Path | None = None,
) -> tuple[dict[str, SourceRecord], dict[str, EvidenceRecord]]:
    """Load the evidence snapshot and validate its selected bibliography.

    Installed distributions use bundled resources. Checkout audits can select
    their own bibliography and optionally check manuscript citation coverage.
    """
    matrix_path = Path(path) if path is not None else _default_matrix_path()
    try:
        payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ParameterValidationError(f"cannot read evidence matrix {matrix_path}: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise ParameterValidationError("evidence matrix must be a JSON object")
    if payload.get("schema_version") != "duckrabbit/evidence/v1":
        raise ParameterValidationError("unsupported evidence matrix schema version")
    verified_on = payload.get("verified_on")
    if not isinstance(verified_on, str):
        raise ParameterValidationError("evidence matrix verified_on is required")
    try:
        date.fromisoformat(verified_on)
    except ValueError as exc:
        raise ParameterValidationError("evidence matrix verified_on must be ISO date") from exc
    if not isinstance(payload.get("verification_policy"), str) or not payload["verification_policy"].strip():
        raise ParameterValidationError("evidence matrix verification_policy is required")
    raw_sources = payload.get("sources")
    raw_entries = payload.get("entries")
    if not isinstance(raw_sources, list) or not isinstance(raw_entries, list):
        raise ParameterValidationError("evidence matrix requires sources and entries arrays")
    sources: dict[str, SourceRecord] = {}
    for row in raw_sources:
        if not isinstance(row, Mapping):
            raise ParameterValidationError("evidence sources must be objects")
        try:
            raw_authors = row.get("authors", [])
            if not isinstance(raw_authors, list) or not all(isinstance(author, str) and author.strip() for author in raw_authors):
                raise ParameterValidationError("evidence source authors must be an array of non-empty strings")
            raw_year = row.get("year")
            if raw_year is not None and type(raw_year) is not int:
                raise ParameterValidationError("evidence source year must be an integer")
            source = SourceRecord(
                key=_text_field(row, "key", context="evidence source") or "",
                citation_key=_text_field(row, "citation_key", context="evidence source") or "",
                title=_text_field(row, "title", context="evidence source") or "",
                source_type=_text_field(row, "source_type", context="evidence source") or "",
                url=_text_field(row, "url", context="evidence source") or "",
                doi=_text_field(row, "doi", context="evidence source", required=False),
                supports=_text_field(row, "supports", context="evidence source") or "",
                verification_status=SourceVerificationStatus(row.get("verification_status", SourceVerificationStatus.SNAPSHOT_VALIDATED.value)),
                verified_on=_text_field(row, "verified_on", context="evidence source", required=False),
                resolver=_text_field(row, "resolver", context="evidence source", required=False) or "offline_snapshot",
                authors=tuple(raw_authors or ()),
                year=raw_year,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ParameterValidationError(f"invalid evidence source {row!r}: {exc}") from exc
        if source.key in sources:
            raise ParameterValidationError(f"duplicate evidence source {source.key}")
        sources[source.key] = source
    entries: dict[str, EvidenceRecord] = {}
    for row in raw_entries:
        if not isinstance(row, Mapping):
            raise ParameterValidationError("evidence entries must be objects")
        try:
            record = EvidenceRecord(
                illusion_id=_text_field(row, "illusion_id", context="evidence record") or "",
                evidence_status=EvidenceStatus(_text_field(row, "evidence_status", context="evidence record") or ""),
                implementation_status=ImplementationStatus(_text_field(row, "implementation_status", context="evidence record") or ""),
                primary_sources=_string_tuple_field(row, "primary_sources", context="evidence record"),
                review_sources=_string_tuple_field(row, "review_sources", context="evidence record"),
                theory_sources=_string_tuple_field(row, "theory_sources", context="evidence record"),
                engineering_basis=_text_field(row, "engineering_basis", context="evidence record") or "",
                evidence_limitations=_string_tuple_field(row, "evidence_limitations", context="evidence record"),
                supported_claim=_text_field(row, "supported_claim", context="evidence record") or "",
                supported_claim_level=ClaimLevel(row.get("supported_claim_level", ClaimLevel.SOURCE_SUPPORTED.value)),
                missing_contract=row.get("missing_contract"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ParameterValidationError(f"invalid evidence record {row!r}: {exc}") from exc
        if record.illusion_id in entries:
            raise ParameterValidationError(f"duplicate evidence entry {record.illusion_id}")
        entries[record.illusion_id] = record
        for source_key in record.primary_sources + record.review_sources + record.theory_sources:
            if source_key not in sources:
                raise ParameterValidationError(f"{record.illusion_id} references unknown source {source_key}")
    validate_evidence_matrix(sources, entries)
    validate_citation_keys(sources, bibliography_path)
    validate_bibliography_links(sources, bibliography_path)
    if manuscript_dir is not None:
        validate_bibliography_integrity(bibliography_path, manuscript_dir)
    return sources, entries


def validate_citation_keys(sources: Mapping[str, SourceRecord], bibliography_path: Path | None = None) -> None:
    """Verify that every evidence source has a matching BibTeX citation key."""
    path = Path(bibliography_path) if bibliography_path is not None else _runtime_resource("references.bib")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ParameterValidationError(f"cannot read bibliography {path}: {exc}") from exc
    keys = set(re.findall(r"@[A-Za-z]+\{([^,]+),", text))
    missing = sorted({source.citation_key for source in sources.values()} - keys)
    if missing:
        raise ParameterValidationError(f"evidence sources missing bibliography keys: {missing}")


def _bibliographic_tokens(value: str) -> tuple[str, ...]:
    """Normalize case, grouping, punctuation and explicit TeX accents, not words."""
    accents = {'"': '\u0308', "'": '\u0301', '`': '\u0300', '^': '\u0302', '~': '\u0303', '=': '\u0304', '.': '\u0307'}
    # Accept both conventional TeX accents and the legacy {"u} spelling in
    # the checked-in bibliography; unknown commands are uncertain, not erased.
    value = re.sub(r'\{\\?(["\'`^~=\.])\s*([A-Za-z])\}', lambda m: unicodedata.normalize("NFC", m[2] + accents[m[1]]), value)
    value = re.sub(r'\\(["\'`^~=\.])\s*\{?([A-Za-z])\}?', lambda m: unicodedata.normalize("NFC", m[2] + accents[m[1]]), value)
    value = value.replace(r"\&", "&").replace(r"\ss", "ß")
    if "\\" in value:
        raise ParameterValidationError("uncertain bibliography identity: unsupported TeX command")
    value = unicodedata.normalize("NFC", value.replace("{", "").replace("}", "")).casefold()
    return tuple(re.findall(r"[^\W_]+", value))


def _author_identity(value: str) -> tuple[str, ...]:
    """Compare full names, retaining sequence and all supplied name components."""
    parts = value.split(",")
    if len(parts) == 2:
        value = f"{parts[1]} {parts[0]}"
    elif len(parts) > 2:
        raise ParameterValidationError("uncertain bibliography identity: unsupported author name form")
    return _bibliographic_tokens(value)


def validate_bibliography_links(sources: Mapping[str, SourceRecord], bibliography_path: Path | None = None) -> None:
    """Check resolver and bibliographic identity against every supplied source field.

    Matrix author lists may include credited translators, so compare the ordered
    author and translator fields together. Absent matrix fields are not invented.
    """
    entries = _bibliography_entries(bibliography_path)
    missing = sorted({source.citation_key for source in sources.values()} - entries.keys())
    if missing:
        raise ParameterValidationError(f"bibliography sources missing URL fields: {missing}")
    for source in sources.values():
        record = entries[source.citation_key]
        if record.get("url") != source.url or record.get("doi") != source.doi:
            raise ParameterValidationError(f"bibliography link metadata disagrees with evidence matrix: {source.citation_key}")
        try:
            if not record.get("title") or _bibliographic_tokens(record["title"]) != _bibliographic_tokens(source.title):
                raise ParameterValidationError("title differs")
            if source.year is not None and record.get("year") != str(source.year):
                raise ParameterValidationError("year differs")
            if source.authors:
                credited = []
                for field in ("author", "translator"):
                    if record.get(field):
                        credited.extend(re.split(r"\s+and\s+", record[field]))
                if tuple(_author_identity(name) for name in credited) != tuple(_author_identity(name) for name in source.authors):
                    raise ParameterValidationError("authors differ")
        except ParameterValidationError as exc:
            raise ParameterValidationError(f"bibliography identity disagrees or is uncertain for {source.citation_key}: {exc}") from exc


def _bibliography_entries(bibliography_path: Path | None = None) -> dict[str, dict[str, str | None]]:
    """Parse literal BibTeX values with balanced braces; reject uncertain macros."""
    path = Path(bibliography_path) if bibliography_path is not None else _runtime_resource("references.bib")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ParameterValidationError(f"cannot read bibliography {path}: {exc}") from exc
    entries: dict[str, dict[str, str | None]] = {}
    for match in re.finditer(r"(?m)^@[A-Za-z]+\s*\{\s*([^,]+),", text):
        key = match[1].strip()
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9:_-]*", key):
            raise ParameterValidationError(f"bibliography citation identifier is invalid: {key!r}")
        if key in entries:
            raise ParameterValidationError(f"duplicate bibliography citation key: {key}")
        fields: dict[str, str | None] = {"doi": None, "url": None}
        position = match.end()
        while position < len(text):
            separator = re.match(r"\s*,?\s*", text[position:])
            position += separator.end()
            if position < len(text) and text[position] == "}":
                break
            field = re.match(r"([A-Za-z]+)\s*=\s*", text[position:])
            if field is None:
                raise ParameterValidationError(f"uncertain BibTeX field for {key}")
            name = field[1].lower()
            position += field.end()
            if position >= len(text):
                raise ParameterValidationError(f"unterminated BibTeX entry {key}")
            opening = text[position]
            if opening in {'{', '"'}:
                position += 1
                start = position
                depth = 1
                while position < len(text):
                    character = text[position]
                    if character == "\\":
                        position += 2
                        continue
                    if opening == "{" and character == "{":
                        depth += 1
                    if (opening == "{" and character == "}") or (opening == '"' and character == '"'):
                        depth -= 1
                        if depth == 0:
                            break
                    position += 1
                if depth:
                    raise ParameterValidationError(f"unterminated BibTeX value for {key}: {name}")
                value = text[start:position]
                position += 1
            else:
                literal = re.match(r"\d+", text[position:])
                if literal is None:
                    raise ParameterValidationError(f"uncertain BibTeX macro for {key}: {name}")
                value = literal[0]
                position += literal.end()
            if name in fields and fields[name] is not None:
                raise ParameterValidationError(f"duplicate BibTeX field for {key}: {name}")
            fields[name] = value.strip()
        else:
            raise ParameterValidationError(f"unterminated BibTeX entry {key}")
        entries[key] = fields
    if not entries:
        raise ParameterValidationError(f"bibliography contains no entries: {path}")
    return entries


def _manuscript_citation_keys(manuscript_dir: Path | None = None) -> set[str]:
    """Return Pandoc citation keys from numbered manuscript sections only."""
    root = Path(manuscript_dir) if manuscript_dir is not None else default_manuscript_dir()
    keys: set[str] = set()
    for path in sorted(root.glob("*.md")):
        if not re.match(r"(?:0[0-9]|99)_", path.name):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ParameterValidationError(f"cannot read manuscript section {path}: {exc}") from exc
        keys.update(key for key in re.findall(r"@([A-Za-z][A-Za-z0-9:_-]*)", text) if ":" not in key)
    return keys


def validate_bibliography_integrity(
    bibliography_path: Path | None = None,
    manuscript_dir: Path | None = None,
) -> dict[str, int]:
    """Require complete DOI/URL metadata and exact manuscript citation linkage."""
    entries = _bibliography_entries(bibliography_path)
    cited = _manuscript_citation_keys(manuscript_dir)
    missing_entries = sorted(cited - entries.keys())
    uncited_entries = sorted(entries.keys() - cited)
    missing_links = sorted(key for key, record in entries.items() if not record["doi"] and not record["url"])
    if missing_entries:
        raise ParameterValidationError(f"manuscript citations missing bibliography entries: {missing_entries}")
    if uncited_entries:
        raise ParameterValidationError(f"bibliography entries are not cited by the manuscript: {uncited_entries}")
    if missing_links:
        raise ParameterValidationError(f"bibliography entries missing DOI and URL metadata: {missing_links}")
    return {"entry_count": len(entries), "cited_count": len(cited), "linked_count": len(entries) - len(missing_links)}


class _CitationHTML(HTMLParser):
    """Collect actual anchors and their containing reference, ignoring comments."""

    _VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: dict[str, int] = {}
        self.anchors: list[tuple[str, str | None]] = []
        self.stack: list[tuple[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        identity = attributes.get("id")
        if identity:
            self.ids[identity] = self.ids.get(identity, 0) + 1
        reference = identity if identity and identity.startswith("ref-") else next((ref for _, ref in reversed(self.stack) if ref), None)
        if tag == "a" and attributes.get("href"):
            self.anchors.append((attributes["href"], reference))
        if tag not in self._VOID:
            self.stack.append((tag, reference))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in self._VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def _validate_html_links(html_path: Path, resolvers: Mapping[str, str], *, context: str) -> None:
    try:
        html = Path(html_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ParameterValidationError(f"cannot read rendered HTML {html_path}: {exc}") from exc
    document = _CitationHTML()
    document.feed(html)
    document.close()
    missing_anchors = []
    missing_resolvers = []
    for key, resolver in resolvers.items():
        reference = f"ref-{key}"
        if document.ids.get(reference) != 1 or not any(href == f"#{reference}" and parent != reference for href, parent in document.anchors):
            missing_anchors.append(key)
        if not any(href == resolver and parent == reference for href, parent in document.anchors):
            missing_resolvers.append(key)
    if missing_anchors:
        raise ParameterValidationError(f"rendered HTML is missing {context} anchors or unique reference destinations: {sorted(missing_anchors)}")
    if missing_resolvers:
        raise ParameterValidationError(f"rendered HTML is missing {context} resolver links inside their references: {sorted(missing_resolvers)}")


def validate_rendered_bibliography_links(html_path: Path, bibliography_path: Path | None = None) -> None:
    """Require citation anchors, unique destinations and reference-local resolvers."""
    entries = _bibliography_entries(bibliography_path)
    resolvers = {key: f"{DOI_RESOLVER_PREFIX}{record['doi']}" if record["doi"] else record["url"] for key, record in entries.items()}
    if any(not resolver for resolver in resolvers.values()):
        raise ParameterValidationError("bibliography entries missing DOI and URL metadata")
    _validate_html_links(html_path, resolvers, context="bibliography")


def validate_rendered_citation_links(html_path: Path, sources: Mapping[str, SourceRecord] | None = None) -> None:
    """Require real citation/reference/resolver edges for the selected sources."""
    selected = sources if sources is not None else load_evidence_matrix()[0]
    resolvers = {source.citation_key: f"{DOI_RESOLVER_PREFIX}{source.doi}" if source.doi else source.url for source in selected.values()}
    _validate_html_links(html_path, resolvers, context="citation")


def validate_evidence_matrix(
    sources: Mapping[str, SourceRecord], entries: Mapping[str, EvidenceRecord]
) -> None:
    """Check source coverage and status consistency against the live taxonomy."""
    catalog = {entry.illusion_id: entry for entry in taxonomy_entries()}
    if set(entries) != set(catalog):
        missing = sorted(set(catalog) - set(entries))
        extra = sorted(set(entries) - set(catalog))
        raise ParameterValidationError(f"evidence catalog mismatch; missing={missing}, extra={extra}")
    for illusion_id, entry in catalog.items():
        record = entries[illusion_id]
        if record.implementation_status is not entry.implementation_status:
            raise ParameterValidationError(f"evidence status disagrees for {illusion_id}")
        if record.evidence_status is not entry.evidence_status:
            raise ParameterValidationError(f"evidence evidence_status disagrees for {illusion_id}")
        if entry.implementation_status is ImplementationStatus.IMPLEMENTED and not (record.primary_sources or record.review_sources):
            raise ParameterValidationError(f"implemented entry {illusion_id} lacks primary or review evidence")
        if any(reference not in sources for reference in entry.evidence_references):
            raise ParameterValidationError(f"taxonomy evidence reference is not in the evidence matrix for {illusion_id}")
        source_keys = record.primary_sources + record.review_sources + record.theory_sources
        if set(source_keys) != set(entry.evidence_references):
            raise ParameterValidationError(f"taxonomy evidence edges disagree for {illusion_id}")
        for role, keys in (("primary", record.primary_sources), ("review", record.review_sources), ("theory", record.theory_sources)):
            if any(key not in sources or sources[key].source_type != role for key in keys):
                raise ParameterValidationError(f"evidence source role disagrees for {illusion_id}: {role}")
        if record.supported_claim_level is not ClaimLevel.SOURCE_SUPPORTED:
            raise ParameterValidationError(f"evidence claim level must be source_supported for {illusion_id}")
        for lineage in record.lineage_records(sources):
            if lineage.role in {EvidenceRole.PRIMARY_DEMONSTRATION, EvidenceRole.REVIEW_OR_SYNTHESIS, EvidenceRole.THEORETICAL_ACCOUNT} and not lineage.source_keys:
                raise ParameterValidationError(f"scholarly lineage missing source key for {illusion_id}")
        if entry.implementation_status is ImplementationStatus.IMPLEMENTED:
            selected = record.primary_sources + record.review_sources
            if not selected or not any(sources[key].supports.strip() for key in selected):
                raise ParameterValidationError(f"implemented entry {illusion_id} lacks an exact source-supported claim")


def evidence_for(illusion_id: str) -> EvidenceRecord:
    """Return one validated evidence record."""
    return load_evidence_matrix()[1][illusion_id]


__all__ = [
    "EvidenceLineage",
    "EvidenceRecord",
    "EvidenceRole",
    "SourceRecord",
    "SourceVerificationStatus",
    "evidence_for",
    "load_evidence_matrix",
    "validate_bibliography_links",
    "validate_bibliography_integrity",
    "validate_citation_keys",
    "validate_rendered_bibliography_links",
    "validate_rendered_citation_links",
    "validate_evidence_matrix",
]
