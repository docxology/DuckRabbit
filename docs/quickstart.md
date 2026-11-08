# Generate, inspect, and verify your first stimulus

Run these commands from the DuckRabbit checkout root. Python 3.11 is the
supported floor; `.python-version` selects the 3.15 development line. See
[standalone use](../STANDALONE.md) for checkout versus installed-wheel scope.

## Install and discover typed requests

```bash
uv sync --locked --extra dev
uv run python -m duckrabbit list
uv run python -m duckrabbit list --json
uv run python -m duckrabbit describe visual.duck_rabbit
uv run python -m duckrabbit validate visual.duck_rabbit
uv run python -m duckrabbit capabilities
```

`describe` exposes defaults and parameter schema only for implemented entries.
Use `list --status input_required` to inspect families that cannot yet generate
without an external fixture contract. A catalog label is not evidence of a
human percept.

## Generate actual media and decode it

```bash
uv run python -m duckrabbit generate visual.duck_rabbit --output-dir output/media
uv run python -m duckrabbit inspect output/media/visual_duck_rabbit.png
uv run python -m duckrabbit verify output/media/visual_duck_rabbit.png.json
uv run python -m duckrabbit generate visual.apparent_motion --output-dir output/media
uv run python -m duckrabbit inspect output/media/visual_apparent_motion.gif
uv run python -m duckrabbit verify output/media/visual_apparent_motion.gif.json
uv run python -m duckrabbit generate audio.missing_fundamental --output-dir output/media
uv run python -m duckrabbit generate visual.duck_rabbit --format npz --output-dir output/media
```

The optional audiovisual path needs system ffmpeg/ffprobe:

```bash
uv run python -m duckrabbit generate audiovisual.sound_induced_flash --output-dir output/media
uv run python -m duckrabbit inspect output/media/audiovisual_sound_induced_flash.mp4
uv run python -m duckrabbit verify output/media/audiovisual_sound_induced_flash.mp4.json
```

Select a compatible `--format` from `png`, `wav`, `gif`, `mp4`, and `npz`.
NPZ preserves canonical float32 arrays and clocks; PNG and PCM delivery involve
quantization. `--seed` controls the deterministic request and `--no-overwrite`
protects existing media paths. Default generation can replace its named files;
keep historical bundles out of exploratory output directories.

## Validate JSON parameter overrides before generation

Save this JSON object as `params.json` in your owned working directory:

```json
{"duck_weight": 0.8, "config": {"width": 320, "height": 240, "quantization_levels": 8}}
```

```bash
uv run python -m duckrabbit validate visual.duck_rabbit --config params.json
uv run python -m duckrabbit generate visual.duck_rabbit --config params.json --output-dir output/custom-media
```

The v2 manifest binds typed parameters, canonical digest, objective metrics,
encoded SHA-256, backend profile, and decoded media facts. Inspection measures
the delivered file; verification checks those facts against the manifest.
Supported NPZ metric declarations are replayed against reconstructed canonical
arrays. Unsupported historical identities remain unverified; missing metrics
do not earn a `canonical_metrics` assurance. Legacy v1 upconversion is not a
fresh verification.

Expected parameter/codec failures are structured JSON with `status`,
`error_type`, and `errors`. Missing optional backends are capability failures,
not simulated successful exports. Capability probing is read-only and says
nothing about human perception or calibrated playback.

## Continue to publication or verification

Use [architecture](architecture.md) for owning modules, [testing](testing_philosophy.md)
for native gates, and the [publication recipe](publication.md#generate-and-audit-a-native-bundle)
for figures, sidecar data, tables, and hydrated Markdown in one fresh bundle.
The [visualization guide](visualization.md) explains how to interpret and
actually inspect those outputs. Package generation does not typeset a PDF or
clear the separate [live scholarship gate](scholarship.md#separate-offline-lineage-from-live-identity).
