# Methodology {#sec:methodology}

## Request and canonical artifact

DuckRabbit starts from a typed request

$$
q = (i, \theta, s, e)
$$ {#eq:typed_request}

where $i$ is an illusion identifier, $\theta$ is an immutable parameter
object, $s$ is a deterministic seed, and $e$ is an optional encoding
request. A registered generator maps the request to a canonical artifact:

$$
A = G_i(\theta; s), \qquad A \in \{I, X, V, AV\}
$$ {#eq:canonical_generation}

The four artifact types are an image frame $I$, audio buffer $X$, video
sequence $V$, and audiovisual timeline $AV$. The generator core is
independent of Pillow, WAV containers, GIF, MP4, and ffmpeg. Each artifact
retains its shape, dtype, units, clock, channels, and timing offsets.

## Typed parameter domains

Value objects validate finite ranges at construction time. Image parameters
include dimensions, color mode, luminance bounds, grayscale levels, and
quantization levels. Audio parameters include frequency, phase, amplitude,
duration, envelope, sample rate, channel count, and PCM depth. Video parameters
include dimensions, rational frame rate, frame count, and temporal offsets.
Audiovisual parameters compose audio and video clocks with declared
synchronization and spatial discrepancies.

The canonical sample count and frame timestamps are explicit. For audio
duration $T$ and sample rate $f_s$, $N$ is rounded once at construction. For a
video with frame rate $f_r$, frame index $k$ is timestamped on the presentation
clock. The audio-minus-video sign convention is explicit:

$$
N = \operatorname{round}(f_s T), \qquad t_k = k/f_r, \qquad
\Delta_{AV} = t_{\mathrm{audio}} - t_{\mathrm{video}}
$$ {#eq:clock_definition}

The package rejects non-finite values, invalid shapes, out-of-range samples,
aliasing frequencies, incompatible channel layouts, impossible frame rates,
and contradictory encoding requests.

## Canonical serialization and provenance

Canonical arrays are contiguous little-endian float32 buffers with explicit
metadata. Serialization includes the array values, shape, clock, and units;
metadata are part of the identity rather than an informal annotation:

$$
c(A) = \operatorname{Serialize}_{\mathrm{LE,float32}}
 (A, \mathrm{shape}, \mathrm{clock}, \mathrm{units}),
\qquad h_c(A) = H(c(A))
$$ {#eq:canonical_digest}

The canonical digest is independent of PNG, WAV, GIF, MP4, and NPZ delivery
choices. The v2 manifest records the parameter schema, serialized parameters,
taxonomy, evidence boundary, canonical facts, objective metrics, encoding
profile, backend identity, decoded inspection, and verification status. A v1
reader remains available and marks upconverted records unverified until the
encoded file is re-inspected.

This separation follows a reproducibility principle from computational
research: a result is not made reproducible merely by publishing a final file;
the executable inputs, transformation steps, versioned software, and provenance
must remain identifiable [@sandve2013simple; @wilson2014bestpractices]. The
manifest therefore records the construction identity and delivery identity
separately. A downstream user can cite the software version and regenerate the
canonical object, or cite a particular encoded artifact when the delivery file
itself is the relevant research object [@smith2016software].

The distinction also follows the older psychophysical problem of relating a
controlled physical increment to a measured sensation. Fechner's 1860 treatise
made measurement, stimulus control, and response comparison explicit parts of
the scientific object [@fechner1860psychophysics]. DuckRabbit adopts the
stimulus-control and provenance aspects of that tradition, but it does not
pretend that a canonical digest or media metric is a sensation measurement:
observer data still require a task, presentation conditions, and a registered
analysis.

## Encoding and verification

For an encoding request $e$, the delivered file $F$ and decoded inspection $I$
are:

$$
F = E_e(A), \qquad I = D(F), \qquad V(F,M) \in \{\mathrm{pass},\mathrm{fail}\}
$$ {#eq:encoding_verification}

The manifest $M$ binds $A$, $F$, and $I$ through hashes, typed summaries, and
format-specific tolerances. PNG, GIF, WAV, and NPZ use local deterministic
adapters. MP4 and muxed
audiovisual output use an optional ffmpeg backend. Missing backends are
reported as capability errors. Writes are atomic, parent directories are
created, overwrite behavior is explicit, and a conflicting format argument is
rejected.

## Objective metric definitions {#sec:objective_metric_definitions}

`MetricRecord` and `MetricSuite` carry a metric name, value, unit, computation
version, source artifact, tolerance, and claim level. Luminance statistics,
quantization levels, RMS and peak amplitude, spectral summaries, frame deltas,
stream durations, and synchronization offsets are physical or decoded-media
facts. They are not observer responses and cannot by themselves establish an
illusion effect. For canonical image samples $y_1,\ldots,y_n$, audio samples
$x_1,\ldots,x_n$, and adjacent video frames $Y_k,Y_{k+1}$, the principal
metrics are:

$$
\mu_Y = \frac{1}{n}\sum_{j=1}^{n} y_j, \qquad
\sigma_Y = \sqrt{\frac{1}{n}\sum_{j=1}^{n}(y_j-\mu_Y)^2}, \qquad
RMS_X = \sqrt{\frac{1}{n}\sum_{j=1}^{n}x_j^2}
$$ {#eq:objective_statistics}

$$
D_k = \frac{1}{\lvert Y\rvert}\sum_{p}\lvert Y_{k+1}(p)-Y_k(p)\rvert, \qquad
\mathrm{centroid}(X) = \frac{\sum_f f\,P_X(f)}{\sum_f P_X(f)}
$$ {#eq:temporal_spectral_metrics}

The level count is the cardinality of the finite-value set after canonical
quantization; an empty or non-finite artifact is invalid rather than assigned
a default statistic. Every metric record carries units and a deterministic
computation version. Observer interpretations are represented separately by
the typed observer protocol and claim levels.

For a future observer study, the estimand is defined by the protocol rather
than by the generator itself:

$$
\psi = \mathbb{E}[Y \mid \mathrm{condition},\ \mathrm{protocol}]
$$ {#eq:observer_estimand}

This symbol names a planned analysis target only. DuckRabbit ships no human
responses, fitted coefficients, or validated observer-level estimate.

### Synthetic psychophysics boundary

DuckRabbit v0.5.0 adds a transparent synthetic-psychophysics diagnostic for
method orchestration. It is a hand-specified feature observer, not a
pretrained vision model and not an empirical psychophysics substitute. Let
$\phi(A)$ be the bounded feature vector extracted from a canonical artifact,
$w$ the code-owned feature weights, and $\tau>0$ the declared temperature:

$$
p_M(c\mid A_r,A_c) =
\sigma\left(\frac{w^\mathsf{T}\phi(A_c)-w^\mathsf{T}\phi(A_r)}{\tau}\right)
$$ {#eq:synthetic_observer}

The model identity, version, preprocessing features, weights, temperature,
seed, calibration statement, and the `human_data=false` flag are serialized with
each prediction. The diagnostic is useful for checking that typed parameter
sweeps produce deterministic, inspectable model outputs and for exercising
analysis orchestration end to end. It does not estimate a human psychometric
function, establish a sensitivity threshold, or support an observer-level
claim. Human psychophysics remains future work requiring a preregistered task,
calibrated display/playback, participant data, and an analysis contract.
