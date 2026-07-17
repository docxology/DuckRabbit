# DuckRabbit architecture

```text
typed request
    │
    ▼
registry ──► deterministic generator ──► canonical artifact ──► typed render result
    │                                      │
    ▼                                      ├── PNG / GIF / WAV adapters
 taxonomy + parameter schema                 ├── optional ffmpeg MP4 adapter
                                             └── exact canonical NPZ archive
                                                        │
                                                        ▼
                                           decode inspection + v2 manifest
                                                        │
                                                        ▼
                                      objective metrics + publication outputs
```

## Core boundary

`src/duckrabbit/parameters.py` defines validated value objects and modality
configuration. `src/duckrabbit/artifacts.py` defines immutable canonical image,
audio, video, and audio-visual objects. `src/duckrabbit/generators.py` contains
pure deterministic generators. `src/duckrabbit/registry.py` binds each typed
parameter class to a taxonomy entry and callable generator.

The public type surface includes arithmetic-compatible bounded integer values
for pixel dimensions, channel counts, frame counts, PCM depth, and seeds;
explicit color, channel, backend, and media-format enums; rational timing and
timestamp values; parameter schemas; and output specifications that keep
encoding choices separate from canonical stimulus parameters.

## Encoding boundary

`src/duckrabbit/media.py` is the only codec boundary. Pillow is loaded lazily
for PNG/GIF. WAV uses the standard library and supports 8/16/24/32-bit PCM.
NumPy writes exact canonical NPZ archives. ffmpeg is discovered at runtime for
MP4 and audio-visual muxing; absence produces `BackendUnavailableError`.

`src/duckrabbit/render.py` coordinates generation, encoding, canonical hashing,
objective metrics, typed render results, and v2 JSON manifests. `inspection.py`
reopens generated files and verifies hashes, dimensions, rates, frame counts,
and stream structure. For exact NPZ delivery it additionally reconstructs the
canonical object and recomputes its digest; refreshing only the container hash
cannot certify altered canonical content. These modules are package
boundaries, not generator implementations.

`evidence.py` validates the source-tiered evidence matrix. `metrics.py` emits
unit-bearing `MetricRecord` values inside an immutable `MetricSuite`.
`observer_analysis.py` contains study schemas, pseudonymous participant and
stimulus-hash records, explicit trial missingness/exclusion states, typed
estimands, model specifications, and synthetic-data utilities.
`synthetic_psychophysics.py` is a separate model-output boundary: its feature
extractors, weights, temperature, seed, calibration statement, and
`human_data=false` marker are serialized with every diagnostic. The default
feature observer is deliberately hand-specified and has no training corpus;
its curve is useful for testing end-to-end orchestration and stimulus
sensitivity, but it is not a pretrained vision model, a psychometric function,
or evidence about human perception. The human observer layer remains a future
study contract with calibrated display/playback, consent, preregistration, and
observed responses.
`publication.py` renders a 15-figure deterministic PNG atlas, typed captions and
alt text, sidecar source data, formalism traceability, 10 publication tables,
and a machine-readable publication report from the live registry. `cover.py`
installs a separately provenance-recorded editorial cover with PNG, WebP, and
thumbnail variants. `validate_figure_registry()` and
`validate_cover_manifest()` independently audit generated publication files;
they reject stale hashes, missing source-data lineage, unsafe paths, and
incomplete editorial provenance.

The manifest verifier is relational rather than presence-only. It checks that
canonical summary fields agree—for example, image bytes equal width × height ×
channel count × four bytes, audio duration agrees with samples and sample rate,
video deltas have exactly frame-count minus one elements, and audiovisual
presentation duration follows the declared signed offset. `Manifest.parameters`,
decoded inspection facts, and nested JSON-like mappings are recursively frozen
after validation. `backend_capabilities()` exposes the same dependency
boundary as a read-only typed probe.

The formalism registry is an executable traceability contract. Every equation
points to existing package modules, tests, manuscript labels, and registered
figures; publication generation fails before writing an atlas if an edge becomes
stale.

`audit.py` is the package-level verifier oracle. It runs the taxonomy and
source graph, confirms the implemented registry is exactly the implemented
catalog, generates every default artifact, recomputes canonical SHA-256
digests, measures every artifact with unit-bearing metrics, and optionally
validates a generated figure registry. Missing disposable publication output
is a warning; malformed or inconsistent project state is an error. This keeps
the release gate independent from the renderer that produced the files.

## Taxonomy boundary

Taxonomy is intentionally orthogonal rather than a single hierarchy. A record
can have multiple mechanisms or modalities and always records its evidence and
implementation status, plus stable bibliography keys for the evidence claim.
This prevents a catalog label from being mistaken for an observer-level
perceptual result. `metrics.py` records deterministic signal properties and
`observer.py` records preregistered trial/response structures without making
human-perception claims.
