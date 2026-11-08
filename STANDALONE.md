# Install and use DuckRabbit without external infrastructure

DuckRabbit's public checkout owns stimulus construction, real-media tests,
publication figures/tables, Markdown hydration, and offline audits. These
operations do not require a private workspace, renderer installation, or
sibling checkout.

## Prepare the native checkout

```bash
git clone https://github.com/docxology/DuckRabbit
cd DuckRabbit
uv sync --locked --extra dev
uv run python -m duckrabbit list
uv run python -m duckrabbit generate visual.duck_rabbit --output-dir output/media
uv run python -m duckrabbit verify output/media/visual_duck_rabbit.png.json
```

Python 3.11 is the supported floor; `.python-version` selects the 3.15
minor line for checkout development, not an exact patch. Install optional
ffmpeg/ffprobe separately for MP4 and muxed audiovisual delivery. Discover
actual capabilities with `uv run python -m duckrabbit capabilities`.

Follow the [quickstart](docs/quickstart.md) for parameters and other modalities,
[architecture](docs/architecture.md) for the typed API boundaries, and
[testing guide](docs/testing_philosophy.md) for native gates. Wheels carry the
runtime evidence snapshot and bibliography; publication and checkout audits
also need repository-owned manuscript, metadata, and cover assets.

## Produce publication inputs without a renderer

Use the single [native publication recipe](docs/publication.md#generate-and-audit-a-native-bundle).
It selects one fresh repository-local destination for figures, sidecar data,
reports, and hydrated Markdown; it does not typeset a PDF. Do not regenerate
into retained historical review bundles or use destructive cleanup as a default.

Optional PDF/HTML/slides typesetting consumes those inputs through a separately
bound, read-only renderer snapshot with repository-local output and caches.
[Renderer isolation](docs/publication.md#isolate-optional-typesetting) explains
the boundary. Compiling is not page-by-page visual acceptance.

## Keep scope and release claims explicit

The catalog distinguishes `implemented`, `planned`, and `input_required`.
A stimulus file or synthetic diagnostic (`human_data=false`) is not an observed
percept. Offline lineage/replay, live scholarship identity checks, and actual
visual inspection are separate forms of evidence.

**0.6.0 remains unreleased with DOI forthcoming.** The v0.5.0 archive and earlier
review outputs are immutable. Use the [documentation index](docs/README.md) to
find current guidance, the designated visual-review bundle, and dated receipts.
