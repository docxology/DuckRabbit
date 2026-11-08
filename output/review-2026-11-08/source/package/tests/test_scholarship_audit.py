"""Offline, no-mock scholarly identity and reachability classification contracts."""

from __future__ import annotations

from urllib.request import Request

import pytest

import duckrabbit.scholarship as scholarship
from duckrabbit.evidence import SourceRecord, SourceVerificationStatus
from duckrabbit.scholarship import classify_http, compare_doi_metadata, title_matches


def _source(**overrides: object) -> SourceRecord:
    fields = {
        "key": "test_source", "citation_key": "testsource1997",
        "title": "Visual Capture of Gravity", "source_type": "primary",
        "url": "https://example.org/paper", "doi": "10.1234/abc",
        "supports": "A bounded claim", "year": 1997,
    }
    fields.update(overrides)
    return SourceRecord(**fields)


def _metadata() -> dict[str, object]:
    return {
        "DOI": "https://doi.org/10.1234/ABC",
        "title": ["Visual Capture of Gravity!"],
        "published-print": {"date-parts": [[1997, 5, 1]]},
    }


@pytest.mark.parametrize("expected,observed", [
    ("Visual Capture of Gravity!", "visual capture of gravity"),
    ("Visual Capture of Gravity: A Mechanistic Account", "Visual Capture of Gravity"),
    ("Visual Capture of Gravity", "Visual Capture of Gravity: A Mechanistic Account"),
    ("The Müller-Lyer Illusion", "The Müller Lyer illusion"),
])
def test_title_matches_ordered_identity_and_explicit_subtitles(expected: str, observed: str) -> None:
    assert title_matches(expected, observed)


@pytest.mark.parametrize("expected,observed", [
    ("What you see is what you hear", "What you see is not what you hear"),
    ("Visual Capture of Gravity", "Gravity Capture of Visual"),
    ("Perception of Illusory Motion in Static Patterns and Related Phenomena", "Perception of Illusory Motion in Static Patterns"),
    ("Visual Capture of Gravity", "Visual Visual Capture of Gravity"),
    ("Motion Perception: A Review", "Motion Perception"),
    ("Visual Capture of Gravity: One Account", "Visual Capture of Gravity: Another Account"),
    ("Visual Capture of Gravity: Not a Replication", "Visual Capture of Gravity"),
    ("Visual Capture of Gravity: A Long Subtitle That Dominates The Supplied Full Title", "Visual Capture of Gravity"),
    ("", "Visual Capture"), ("Visual Capture", ""),
])
def test_title_matches_rejects_semantic_changes_and_arbitrary_subsets(expected: str, observed: str) -> None:
    assert not title_matches(expected, observed)


@pytest.mark.parametrize("status,error,expected", [
    (401, None, SourceVerificationStatus.ACCESS_CONTROLLED),
    (403, None, SourceVerificationStatus.ACCESS_CONTROLLED),
    (405, None, SourceVerificationStatus.ACCESS_CONTROLLED),
    (None, "timed out", SourceVerificationStatus.UNAVAILABLE),
    (500, None, SourceVerificationStatus.UNAVAILABLE),
    (100, None, SourceVerificationStatus.UNAVAILABLE),
    (200, None, SourceVerificationStatus.URL_REACHABLE_UNRESOLVED),
    (302, None, SourceVerificationStatus.URL_REACHABLE_UNRESOLVED),
])
def test_reachability_never_establishes_scholarly_identity(status: int | None, error: str | None, expected: SourceVerificationStatus) -> None:
    assert classify_http(status, error) is expected
    assert expected is not SourceVerificationStatus.DOI_METADATA_MATCH
    assert expected is not SourceVerificationStatus.DOI_LESS_ARCHIVAL


def test_doi_metadata_requires_doi_ordered_title_and_year() -> None:
    metadata = _metadata()
    assert compare_doi_metadata(_source(), metadata) is SourceVerificationStatus.DOI_METADATA_MATCH
    for replacement in ({"DOI": "10.9999/other"}, {"DOI": 123}, {"title": [None]}, {"title": ["Visual Capture is not Gravity"]}, {"published-print": "1997-05-01"}):
        assert compare_doi_metadata(_source(), {**metadata, **replacement}) is SourceVerificationStatus.METADATA_MISMATCH
    assert compare_doi_metadata(_source(doi=None), metadata) is SourceVerificationStatus.METADATA_MISMATCH


@pytest.mark.parametrize("authors", [
    None, [], [{"family": "Other", "given": "George"}],
    [{"family": "Berkeley", "given": "Nobody"}],
    [{"family": "Berkeley"}], ["George Berkeley"],
    [{"family": "Berkeley", "given": "George"}, {"family": "Extra", "given": "Author"}],
])
def test_supplied_authors_require_full_ordered_identity(authors: object) -> None:
    source = _source(authors=("George Berkeley",))
    assert compare_doi_metadata(source, {**_metadata(), "author": authors}) is SourceVerificationStatus.METADATA_MISMATCH


def test_supplied_authors_accept_normalized_names_but_not_reordering() -> None:
    source = _source(authors=("Matthias Schemmel", "William G. Boltz"))
    authors = [{"family": "Schemmel", "given": "Matthias"}, {"family": "Boltz", "given": "William G"}]
    assert compare_doi_metadata(source, {**_metadata(), "author": authors}) is SourceVerificationStatus.DOI_METADATA_MATCH
    assert compare_doi_metadata(source, {**_metadata(), "author": list(reversed(authors))}) is SourceVerificationStatus.METADATA_MISMATCH


def test_person_and_group_authors_require_exact_ordered_identity() -> None:
    source = _source(authors=("Ada Example", "Example Methods Working Group"))
    authors = [{"family": "Example", "given": "Ada"}, {"name": "Example Methods Working Group"}]
    assert compare_doi_metadata(source, {**_metadata(), "author": authors}) is SourceVerificationStatus.DOI_METADATA_MATCH
    assert compare_doi_metadata(source, {**_metadata(), "author": list(reversed(authors))}) is SourceVerificationStatus.METADATA_MISMATCH
    assert compare_doi_metadata(source, {**_metadata(), "author": [authors[0], {"name": "Other Methods Working Group"}]}) is SourceVerificationStatus.METADATA_MISMATCH


@pytest.mark.parametrize("author", [
    {"name": None}, {"name": ""}, {"name": 42},
    {"name": "Example Methods Working Group", "family": "Group"},
    {"name": "Example Methods Working Group", "given": "Example"},
    {"name": "Example Methods Working Group", "family": None},
])
def test_group_author_metadata_rejects_malformed_or_ambiguous_identity(author: object) -> None:
    source = _source(authors=("Example Methods Working Group",))
    assert compare_doi_metadata(source, {**_metadata(), "author": [author]}) is SourceVerificationStatus.METADATA_MISMATCH


def test_non_http_schemes_fail_before_network_io() -> None:
    with pytest.raises(ValueError):
        scholarship._open_http(Request("file:///etc/passwd"), timeout=1.0)
