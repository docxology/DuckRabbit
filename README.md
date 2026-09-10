# DuckRabbit

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21419693.svg)](https://doi.org/10.5281/zenodo.21419693)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

DuckRabbit is a typed, deterministic Python package for generating
visual, auditory, temporal, and audio-visual illusion stimuli. It separates
canonical in-memory media from optional encoders so the same typed request can
be reproduced, inspected, hashed, and exported as PNG, WAV, GIF, MP4, or an
exact canonical NPZ archive.

This private sidecar checkout (located at
`projects/ongoing/docxology/DuckRabbit` in the private monorepo and mirrored
into the template checkout at `projects/ongoing/Art/DuckRabbit`) is the
release source for the public
DuckRabbit GitHub repository at https://github.com/docxology/DuckRabbit. The
public repository carries the software, manuscript, evidence matrix, and
release bundle (including the DOI-bearing PDF under `output/pdf/`). DuckRabbit
is released under the MIT License. It is an extensible v0.5.0, not a claim
that every known illusion has already been implemented; the catalog
distinguishes `implemented`, `planned`, and `input_required` entries.

## Authorship and citation

DuckRabbit is authored by Daniel Ari Friedman of the Active Inference Institute
(ORCID
[`0000-0001-6232-9096`](https://orcid.org/0000-0001-6232-9096)). The release
is archived on Zenodo:

- Concept DOI (always resolves to the latest version):
  [10.5281/zenodo.21419693](https://doi.org/10.5281/zenodo.21419693)
- Version DOI for v0.5.0:
  [10.5281/zenodo.21419694](https://doi.org/10.5281/zenodo.21419694)
  ([Zenodo record](https://zenodo.org/records/21419694))

Cite the release metadata in `CITATION.cff`, the public repository, and the
underlying scholarship listed in `docs/manuscript/references.bib`.

## Quick start

From this project directory:

```bash
uv sync --extra dev
uv run python -m duckrabbit list
uv run python -m duckrabbit generate visual.duck_rabbit --output-dir output/media
uv run python -m duckrabbit generate audio.shepard_tone --output-dir output/media
uv run python -m duckrabbit generate audiovisual.sound_induced_flash --output-dir output/media
uv run python -m duckrabbit inspect output/media/visual_duck_rabbit.png
uv run python -m duckrabbit verify output/media/visual_duck_rabbit.png.json
uv run python -m duckrabbit capabilities
uv run python scripts/generate_publication_outputs.py
uv run python scripts/generate_manuscript_variables.py
uv run python scripts/validate_scholarship.py
uv run python scripts/audit_scholarship.py --output output/reports/scholarship_audit.json
uv run python -m duckrabbit synthetic-psychophysics
uv run python -m duckrabbit audit --output-root output
uv run python -m duckrabbit audit --output-root output --release
```

`docs/publication.md` documents the canonical end-to-end release sequence
(network scholarship audit included, release-time only).

`Pillow` writes PNG and GIF image/animation assets; the standard-library WAV
adapter writes PCM audio. MP4 output requires an installed `ffmpeg` executable;
the package reports a clear capability error when it is absent.

The publication workflow generates 15 deterministic scientific figures plus a
separately provenance-recorded editorial cover, source-data sidecars, a
validated figure registry, 10 tables, and reports under disposable `output/`.
It uses NumPy/Pillow primitives and does not require Matplotlib. The cover is
an editorial illustration, not an experimental stimulus or observer result.
The complete source-tiered catalog matrix is rendered in the standalone
`docs/manuscript/09_appendix_catalog.md` appendix, while the visual atlas is generated
from every currently implemented visual entry in the live registry.

## Compact glossary

- **Canonical artifact:** deterministic, little-endian float32 in-memory media
  with explicit shape, clock, units, and digest.
- **Encoded artifact:** a delivery file such as PNG, WAV, GIF, MP4, or NPZ.
- **Decoded inspection:** facts measured from the delivered file and its
  streams, independently of the encoder request.
- **Source-supported claim:** the narrow statement recorded in the checked-in
  evidence snapshot and supported by a cited source; it is not validation of a
  DuckRabbit percept.
- **Synthetic model output:** serialized output from the hand-specified
  diagnostic with `human_data=false`, not a participant result.

## Public API

```python
from duckrabbit import ImageConfig, OutputSpec, PcmBitDepth, QuantizationLevels, generate
from duckrabbit.generators import DuckRabbitParams

stimulus = generate(
    "visual.duck_rabbit",
    DuckRabbitParams(
        config=ImageConfig(quantization_levels=QuantizationLevels(8)),
    ),
)
print(stimulus.width, stimulus.height, stimulus.mode)
```

Typed output requests can select a container and PCM depth while keeping the
canonical float buffer unchanged:

```python
from duckrabbit import AudioEncoding, MediaFormat
from duckrabbit.render import generate_artifact

_, manifest = generate_artifact(
    "audio.missing_fundamental",
    output_dir="output/media",
    output_spec=OutputSpec(
        format=MediaFormat.WAV,
        audio_encoding=AudioEncoding(PcmBitDepth(24)),
    ),
)
print(manifest["schema_version"], manifest["verification"]["status"])
```

The core contracts are defined in `src/duckrabbit/parameters.py`,
`src/duckrabbit/artifacts.py`, `src/duckrabbit/registry.py`, and
`src/duckrabbit/taxonomy.py`.

## Implemented catalog

| ID | Modality | Canonical output |
| --- | --- | --- |
| `visual.duck_rabbit` | visual | image / PNG |
| `visual.simultaneous_contrast` | visual | image / PNG |
| `visual.muller_lyer` | visual | image / PNG |
| `visual.apparent_motion` | visual-temporal | frame sequence / GIF or MP4 |
| `visual.poggendorff` | visual | image / PNG |
| `visual.ponzo` | visual | image / PNG |
| `visual.kanizsa_triangle` | visual | image / PNG |
| `visual.ebbinghaus` | visual | image / PNG |
| `visual.zollner` | visual | image / PNG |
| `audio.shepard_tone` | auditory | audio / WAV |
| `audio.missing_fundamental` | auditory | audio / WAV |
| `audio.tritone_paradox` | auditory | audio / WAV |
| `audio.octave_illusion` | auditory | stereo audio / WAV |
| `audio.auditory_continuity` | auditory | audio / WAV |
| `audiovisual.sound_induced_flash` | audio-visual | synchronized timeline / MP4 |
| `audiovisual.ventriloquist` | audio-visual | synchronized stereo timeline / MP4 |
| `audiovisual.temporal_ventriloquism` | audio-visual | synchronized timeline / MP4 |

`audiovisual.mcgurk` is catalogued as `input_required` because a defensible
implementation needs validated speech audio and video fixtures.
It remains `input_required` until the fixture contract in
`src/duckrabbit/fixtures.py` is fulfilled by real, checksummed speech assets.

## Design boundaries

- Generators return canonical NumPy-backed `ImageFrame`, `AudioBuffer`,
  `VideoSequence`, or `AudiovisualTimeline` objects.
- Frozen scalar value objects validate luminance, grayscale, quantization,
  frequency, duration, sample rate, frame rate, synchronization ranges, pixel
  dimensions, channel counts, frame counts, PCM depths, and deterministic
  seeds.
- Canonical artifact objects expose storage size, signal statistics, temporal
  deltas, presentation timing, and typed encoded-output records.
- Encoders create parent directories, publish through same-directory atomic
  replacement, and honor explicit overwrite controls from `OutputSpec`.
- Registry entries carry orthogonal modality, mechanism, signature, cognitive
  process, stimulus-requirement, typed evidence-status, bibliography keys, and
  implementation-status, output-kind, input-requirement, and claim-level metadata.
- Parameter schemas expose JSON-safe field names, defaults, and constraints;
  v2 manifests bind those schemas to canonical bytes and decoded media facts.
- Objective metrics describe generated signals only. They are not observer
  reports or evidence that every observer experiences the named illusion.
- `evidence.py` validates a source-tiered matrix for every catalog entry;
  source records identify the exact claim supported and the limitation that
  remains.
- `inspection.py` treats manifests as untrusted input: it rejects missing or
  conflicting encoded metadata, unsafe output paths, malformed summaries, and
  stale canonical NPZ digests after real decode/reconstruction.
- v2 manifest summaries are relationally validated: shape, dtype, byte count,
  sample/frame rate, duration, signal range, frame deltas, and audiovisual
  offset fields must agree rather than merely being present. Public mappings
  are recursively frozen at the typed boundary.
- `publication.py` and `cover.py` expose independent registry validators so
  generated figures and editorial assets cannot silently bypass their
  source-data, caption, hash, or provenance contracts.
- `observer_analysis.py` provides typed study designs, estimands, synthetic
  response generation, Wilson intervals, and future-study power scenarios;
  `synthetic_psychophysics.py` provides a separate hand-specified feature
  observer with serialized weights and an explicit `human_data=false` boundary.
  No participant data or pretrained vision-model output are bundled.
- `publication.py` generates the 15-figure visualization atlas, typed caption
  and alt-text registry, source-data JSON, formalism traceability, 10
  machine-derived markdown tables, and publication report. `cover.py` records
  the separately generated editorial cover and its PNG/WebP/thumbnail hashes.
- Generated stimuli document intended perceptual mechanisms; they do not make
  universal claims about what every observer will perceive.
- `scripts/` contains thin entry points. Package behavior belongs in `src/`.

`duckrabbit capabilities` reports the environment-dependent encode/inspect
matrix for Pillow, the standard-library WAV path, NumPy NPZ archives, and
ffmpeg/ffprobe. A missing optional backend is a typed capability result before
encoding is attempted.

Figure rendering environment: the publication figures render with Pillow
using the first available TrueType font — `$DUCKRABBIT_FONT_PATH` when set,
otherwise common platform fonts (Arial on macOS/Windows, DejaVu Sans or
Liberation Sans on Linux). Byte-identical regeneration is guaranteed within
one platform/font combination; set `DUCKRABBIT_FONT_PATH` to pin the font
explicitly.

`duckrabbit synthetic-psychophysics` writes the end-to-end model diagnostic
sidecar. Its output includes the feature schema, weights, temperature, seed,
canonical digests, predictions, `human_data: false`, and the explicit statement
that the result is model output rather than human psychophysics.

## Discovery and output inspection

```bash
uv run python -m duckrabbit list --json
uv run python -m duckrabbit list --status planned
uv run python -m duckrabbit describe visual.duck_rabbit
uv run python -m duckrabbit generate audio.missing_fundamental \
  --format wav --output-dir output/media
uv run python -m duckrabbit generate visual.duck_rabbit \
  --format npz --output-dir output/media
uv run python -m duckrabbit verify output/media/visual_duck_rabbit.png.json
```

Every encoded v2 manifest records the typed request, taxonomy/evidence boundary,
canonical little-endian float32 digest, objective metrics, output path, format,
backend/profile, decoded media inspection, verification status, byte size, and
SHA-256 digest. Legacy v1 manifests can be read and explicitly upconverted as
unverified records; legacy top-level output fields remain for compatibility.

## Tests and coverage

`pytest` and `pytest-cov` are declared in the `dev` optional-dependency group,
so run `uv sync --extra dev` (already covered by the quick-start above) before
invoking them:

```bash
uv run pytest tests/ --cov=src/duckrabbit --cov-report=term-missing --cov-fail-under=90
```

Tests use real deterministic arrays, files, Pillow round trips, and ffmpeg
when available. No mock framework is used.

## Template integration

The project is rendered through the sibling public template checkout. The
original fork used the private-safe command:

```bash
cd <template-checkout>
uv run python scripts/audit/copy_exemplar.py \
  --source templates/template_code_project \
  --dest <projects-root>/ongoing/Art/DuckRabbit \
  --new-name duckrabbit \
  --project-only
```

`--project-only` is intentional: it keeps the shared template engine outside
this private project tree.

The active checkout lives at `projects/ongoing/docxology/DuckRabbit` in the
private workspace.
