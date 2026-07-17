# DuckRabbit Standalone Guide

## Purpose

DuckRabbit is an installable Python package from the Active Inference Institute
for typed, deterministic generation of visual, auditory, temporal, and
audio-visual illusion stimuli. The intended public source is
`https://github.com/docxology/DuckRabbit`.

## Clean copy

From `/Users/4d/Documents/GitHub/template`:

```bash
uv run python scripts/audit/copy_exemplar.py \
  --source templates/template_code_project \
  --dest /Users/4d/Documents/GitHub/projects/working/DuckRabbit \
  --new-name duckrabbit \
  --project-only
```

The private sidecar owns the project contents. The sibling template checkout
owns the shared rendering and validation engine.

## Validation

```bash
uv sync --extra dev
uv run pytest tests/ --cov=src/duckrabbit --cov-fail-under=90
uv run python -m duckrabbit list
uv run python -m duckrabbit generate visual.duck_rabbit --output-dir output/media
```

Install ffmpeg separately to exercise MP4 and muxed audio-visual output.

## Scope boundary

The catalog is extensible rather than falsely exhaustive. Each entry carries
an implementation status. `input_required` means the generator needs validated
external stimuli, such as speech audio/video, before it can be promoted.
