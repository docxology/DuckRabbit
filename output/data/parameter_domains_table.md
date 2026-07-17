# Typed parameter domains and units

| Type | Unit | Validated domain | Role |
| --- | --- | --- | --- |
| PixelDimension | pixels | 8–4096 | image/video width and height |
| GrayscaleLevels | levels | 2–256 | representable grayscale levels |
| QuantizationLevels | levels | 2–256 | output quantization buckets |
| FrequencyHz | Hz | > 0 and finite | oscillator and harmonic frequencies |
| SampleRate | samples/s | 1,000–384,000 | audio sampling clock |
| FrameRate | frames/s | 1–240 | video presentation clock |
| SyncOffsetMs | ms | −10,000–10,000 | audio relative to video |
| SpatialOffset | normalized | −1–1 | declared crossmodal spatial discrepancy |

: Typed domains are validation contracts, not estimates of perceptual sensitivity. {#tbl:parameters}
