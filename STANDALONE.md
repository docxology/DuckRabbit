# DuckRabbit Standalone Guide

## Purpose

DuckRabbit is an installable Python package from the Active Inference Institute
for typed, deterministic generation of visual, auditory, temporal, and
audio-visual illusion stimuli. The intended public source is
`https://github.com/docxology/DuckRabbit`.

## Install and run

```bash
git clone https://github.com/docxology/DuckRabbit
cd DuckRabbit
uv sync --extra dev
```

Then validate and exercise the package:

```bash
uv run pytest tests/ --cov=src/duckrabbit --cov-fail-under=90
uv run duckrabbit list
uv run python -m duckrabbit generate visual.duck_rabbit --output-dir output/media
```

Install ffmpeg separately to exercise MP4 and muxed audio-visual output.

The project is maintained as a private sidecar checkout rendered and validated
through a sibling template engine; see README.md "Template integration".

## Scope boundary

The catalog is extensible rather than falsely exhaustive. Each entry carries
an implementation status. `input_required` means the generator needs validated
external stimuli, such as speech audio/video, before it can be promoted.
