# Verification failure modes and negative controls

| Failure mode | Control | Expected result |
| --- | --- | --- |
| altered encoded file | recompute encoded SHA-256 | fail |
| stale canonical digest | recompute canonical little-endian float32 digest | fail |
| incorrect decoded dimensions | compare inspection facts with manifest summary | fail |
| stream timing mismatch | compare duration/timebase and declared sync offset | fail |
| unsupported backend | capability probe before encoding | explicit capability error |
| conflicting format requests | reject format_name/output_spec disagreement | parameter error |

: Negative controls define package failure behavior, not scientific null results. {#tbl:verification}
