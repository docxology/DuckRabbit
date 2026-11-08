# Trace typed requests through canonical media and publication layers

## Keep startup light and profiling reproducible

The root package retains its documented exports and original owning-module
identities. Analysis and publication exports resolve on demand; importing the
package or listing the CLI catalog does not load the publication/audit stack.
CLI-only heavy imports belong in their selected command branches.

Canonical hashing and manifest byte counts share one buffer-streaming primitive;
the public byte serializer retains its original chunk boundaries and schema.
Temporal consumers reuse one adjacent-frame scan per operation, without
persistent array caches. Non-C-contiguous inputs preserve the original NumPy
reduction order rather than trading numerical identity for speed.

`performance.py` owns real, fixed profiling workloads. Script wrappers only
delegate. Measurements bind source, runtime inputs, environment, workload
configuration, and deterministic results; instrumentation runs separately from
ordinary timing samples. See [`performance.md`](performance.md).

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

## Construct canonical media with validated typed requests

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

## Encode and verify delivered media at explicit boundaries

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

## Separate physical metrics, source evidence, and observer models

`evidence.py` validates the source-tiered evidence matrix. `metrics.py` emits
unit-bearing `MetricRecord` values inside an immutable `MetricSuite`.
Every generated metric records explicit color/transfer semantics, its complete
window, NumPy and implementation identity, and SHA-256 hashes of its computation
and window definitions. These hashes identify definitions, not input buffers or
empirical calibration; canonical digests identify the actual stimuli.
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
## Produce source-bound figures and editorial assets separately

`publication.py` produces the registered scientific PNG figures, typed captions
and alt text, source-data sidecars, formalism traceability, publication tables,
and reports. The [visualization guide](visualization.md) owns the live roster,
graphical-abstract interface, display conventions, and readability criteria.
`publication_panels.py` derives readable catalog, audio, scholarship and formalism
views from those exact source-data records. Their dedicated report binds every
variant to its source, paths, dimensions, font and implementation; native audit
replays them. Presentation variants do not increment the scientific figure count.
`cover.py` installs the separate editorial cover with PNG, WebP, and thumbnail
variants. Source bytes, dimensions, transforms, and variant roles are checked;
reported historical generation is explicitly unverified, and arbitrary inputs
acquire no invented history. Registries reject stale hashes, unsafe paths, and
invalid lineage. Follow the [native publication recipe](publication.md#generate-and-audit-a-native-bundle)
for one selected repository-local bundle; hydration is not typesetting.

## Validate relational manifests and executable traceability

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

`audit.py` is the package-level structural/replay verifier. It checks the live
taxonomy/evidence graph, agreement between registry and implemented catalog,
default canonical digests, metrics, and available publication registries.
Missing disposable publication output is a warning outside release mode;
release mode fails closed and additionally replays every registered scientific
data/raster producer and exact hydrated manuscript delivery. This uses the
current trusted implementations, not an independent scientific oracle.
Matching hashes, replay, and structural `visual_qa` are not authenticated
authorship, actual visual inspection, live source identity, or human evidence.
Execution audits require the selected root to be the executing checkout.

## Classify catalog intent without claiming observed perception

Taxonomy is intentionally orthogonal rather than a single hierarchy. A record
can have multiple mechanisms or modalities and always records its evidence and
implementation status, plus stable bibliography keys for the evidence claim.
This prevents a catalog label from being mistaken for an observer-level
perceptual result. `metrics.py` records deterministic signal properties and
`observer.py` records preregistered trial/response structures without making
human-perception claims.
