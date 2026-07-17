# Objective metric definitions

| Metric | Unit | Definition | Tolerance | Claim level |
| --- | --- | --- | --- | --- |
| mean_luminance | normalized_luminance | mean Rec. 709 relative luminance (grayscale is identity) | exact canonical | physical_metric |
| unique_values | levels | count of distinct canonical image values | exact integer | physical_metric |
| rms | normalized_amplitude | root-mean-square audio amplitude | finite scalar | physical_metric |
| peak | normalized_amplitude | maximum absolute audio amplitude | finite scalar | physical_metric |
| spectral_centroid_hz | Hz | energy-weighted one-sided spectral centroid | finite scalar | physical_metric |
| spectral_bandwidth_hz | Hz | spectral standard deviation around the one-sided centroid | finite scalar | physical_metric |
| crest_factor | ratio | audio peak divided by RMS with zero-RMS guard | finite scalar | physical_metric |
| mean_temporal_delta | normalized_pixel_difference | mean adjacent-frame absolute difference | finite scalar | physical_metric |
| sync_offset | ms | declared audio-minus-video offset | typed value | physical_metric |

: Metrics are deterministic artifact properties and do not report observer outcomes. {#tbl:metrics}
