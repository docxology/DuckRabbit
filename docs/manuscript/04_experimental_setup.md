# Experimental and Computational Setup {#sec:experimental_setup}

Core generation uses Python, NumPy, Pillow, and the standard library. The
default seed is 0 and generation is offline. The generators are analytic in
their typed parameters: the seed is recorded in manifests and study plans but
does not yet alter artifact bytes; seed-driven stimulus randomization awaits a
stochastic generator. PNG, GIF, WAV, and NPZ are
available without ffmpeg; MP4 and muxed audiovisual output require both
ffmpeg and ffprobe. Optional capabilities fail explicitly rather than silently
changing the requested artifact.

The deterministic validation suite executes real NumPy synthesis and real
temporary-file media round trips. It checks finite normalized arrays, typed
parameter boundaries, canonical hashes, dimensions, channel layouts, sample
rates, frame counts, timebases, duration agreement, synchronization offsets,
decoded stream facts, and registry/evidence consistency.

This is a software-validation protocol, not a psychophysical experiment. The
tests establish repeatability under the declared software and dependency
conditions; they do not establish replicability of an observer effect under a
new display, playback chain, population, or task. That distinction is why the
release reports both the exact environment contract and the missing observer
evidence.

The publication workflow writes {{PUBLICATION_FIGURES}} scientific PNG figures
plus a separately provenance-recorded editorial cover, machine-readable
source-data sidecars, a typed figure registry, {{PUBLICATION_TABLES}} markdown
tables, and a publication report.
Each generated figure records its source function, seed, caption, alt text,
claim level, and SHA-256 digest. Generated files are disposable; the tracked
source is the generator and its tests.

The registry and cover report are independently revalidated after generation.
The registry validator rechecks code-owned captions, evidence namespaces,
source-data hashes, and figure hashes. The cover validator rechecks the
editorial source digest, portrait dimensions, variant set, and delivery hashes.
These checks prevent a successfully rendered image from becoming an
unexamined publication claim.

The observer harness is a data-free design layer. It creates reproducibly
randomized trial records, exports typed study plans, generates synthetic
responses for contract tests, and exposes model templates. It does not collect
or ship participant data. The publication atlas additionally runs
`duckrabbit.synthetic.feature_observer`, an explicitly hand-specified feature
model with no training corpus. Its canonical pairwise probabilities are
serialized as model output and are useful for end-to-end orchestration tests;
they are not a real vision-model estimate, a psychometric function, or an
observer result. Human sensitivity is deferred until a calibrated,
consented, preregistered study supplies response data and an analysis contract.
