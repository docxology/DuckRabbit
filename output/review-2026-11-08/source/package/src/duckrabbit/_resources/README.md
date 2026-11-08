# Installed evidence resources

These distribution snapshots mirror `data/evidence_matrix.json` and
`docs/manuscript/references.bib`. Update them together with their canonical
checkout sources. `tests/test_packaging_contracts.py` checks byte equality.

Source checkouts validate the original files; installed wheels use these
resources through `importlib.resources`, without assuming a repository layout.
Manuscript rendering and release audits still require a complete checkout.
