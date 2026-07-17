# Publication and release procedure

DuckRabbit is authored by Daniel Ari Friedman of the Active Inference Institute
(ORCID
[`0000-0001-6232-9096`](https://orcid.org/0000-0001-6232-9096)). The package
version is synchronized at `0.5.0` across `pyproject.toml`, the manuscript,
CITATION.cff, codemeta, and Zenodo metadata. A DOI is intentionally not minted
in this checkout: the publication metadata contains an empty DOI and
`doi_status: forthcoming` until a real identifier is issued.
The intended public software repository is
the [DuckRabbit public GitHub repository](https://github.com/docxology/DuckRabbit).

The publication bundle is code-owned. Run:

```bash
uv run python -m duckrabbit publish --output-dir output
uv run python -m duckrabbit audit --output-root output --release
uv run python scripts/validate_scholarship.py
```

`publish` regenerates the 15 scientific figures, 10 tables, source-data
sidecars, figure registry, cover variants, and visual-QA report. The cover is
an editorial charcoal illustration with recorded provenance; it is not a
scientific stimulus or observer result. Scientific captions state controls,
units or non-applicability, source-data lineage, limitations, and the boundary
between deterministic media facts and future observer hypotheses.

The complete catalog/source-tier matrix is rendered in the standalone
`manuscript/09_appendix_catalog.md` section rather than embedded in the main
results narrative. Its `tbl:catalog` rows are still generated from the live
taxonomy and evidence registries, so moving the table changes publication
placement, not its provenance or validation contract. The visual coverage
figure is likewise generated from all currently implemented visual entries;
temporal visual families contribute a representative first frame while their
sequence facts remain in source data.

The checked-in scholarship matrix is an offline snapshot. It validates source
shape, bibliography linkage, exact supported claims, and evidence gaps without
pretending that a URL is currently reachable. The explicit network audit
(`scripts/audit_scholarship.py`) distinguishes DOI metadata matches,
access-controlled pages, unresolved reachable URLs, mismatches, unavailable
records, and DOI-less archival sources.

Release requires no participant data, no universal perceptual claim, no stale
hash, and no unresolved manuscript token. A future observer study needs its own
preregistration, consent/data-governance record, playback and display controls,
estimand, and analysis report.

## Public-release checklist

This checkout is a release candidate, not a claim that a public repository or
DOI already exists. Before publishing externally, the maintainer should:

1. transfer or mirror the source to the intended public repository and confirm
   that the MIT license, author identity, citation files, and release notes are
   visible there;
2. run the source tests, offline scholarship validation, network scholarship
   audit, package release audit, and sibling-template output validation from a
   clean release worktree;
3. review the generated PDF, HTML, and slide outputs, including reference
   anchors and resolver links, rather than relying only on machine checks;
4. create the immutable public version tag and archive the exact source and
   generated release bundle; and
5. mint a DOI only after the public record exists, then replace the empty DOI
   and `forthcoming` status atomically across `manuscript/config.yaml`,
   `CITATION.cff`, and any repository deposit metadata.

The DOI step is intentionally external to this private sidecar. Until it is
performed, an empty DOI is the correct metadata value; a plausible-looking
placeholder would make citations non-resolving and would weaken provenance.
