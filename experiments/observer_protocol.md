# Observer validation protocol scaffold

This document is a study-ready design contract, not a completed observer study.
It separates perceptual evidence from deterministic stimulus construction. The
package contains no participant data and no fitted human-response model.

## Study object

Each preregistered condition specifies:

- a stable condition ID and DuckRabbit illusion ID;
- complete typed parameter overrides and generation seed;
- canonical artifact digest and encoded-file hash;
- response kind and allowed response labels;
- presentation constraints, calibration, and playback requirements;
- primary estimand, reference condition, contrast, and uncertainty rule.

`StudyDesign` records condition order, trial count, observer count, randomization
seed, inclusion rules, exclusion rules, and analysis-model templates. The
default design includes a sound-induced-flash count contrast and a temporal
binding timing contrast, but its effect sizes are not empirical results.

`ParticipantId` accepts only a pseudonymous token. `StimulusReference` binds a
trial to a manifest SHA-256 digest and, when a delivery file exists, an encoded
file SHA-256 digest. `TrialRecord` then binds the participant, condition,
randomization seed, response kind/value, reaction time, and explicit complete,
excluded, or missing disposition. `AggregateRecord` carries an estimate, unit,
sample count, uncertainty interval, and observer-level claim boundary.

## Randomization and responses

`build_trial_sequence()` creates observer-specific trial IDs and uses a recorded
local seed for counterbalancing. Raw responses should contain only pseudonymous
observer keys, trial IDs, response values, reaction times, and presentation
timestamps. `simulate_binary_responses()` exists only for deterministic harness
tests. `summarize_binary_responses()` reports counts, proportions, and Wilson
intervals for synthetic or future records.

## Analysis templates

The analysis plan selects a model family before data collection:

- logistic mixed model for forced-choice responses;
- linear mixed model for continuous magnitude or localization responses;
- lognormal or Gamma mixed model for reaction times;
- Poisson, negative-binomial, or ordinal model for event counts;
- transition-rate or survival-style analysis for perceptual reversals.

The primary estimand, reference condition, planned contrast, missing-data rule,
exclusion criteria, confidence interval, multiplicity correction, and subject
or item random effects must be fixed before unblinding. Power curves use
explicitly assumed probability differences and are labeled as planning
quantities.

`AnalysisModelSpec` records the formula, outcome family, link, and participant
or item random effects for each template. The serialized plan records these
templates and the explicit `none_bundled` participant-data status so that a
future study can be preregistered without being confused with package tests.

## Presentation and ethics

Before collecting data, specify display calibration, luminance range, viewing
distance, audio level, headphone or speaker model, channel separation,
inter-event timing, accessibility warnings, and stop criteria for discomfort.
Avoid high-contrast flicker or loud playback without an appropriate safety
review. Speech-dependent fixtures require licensing or consent records and
checksums. McGurk cannot move to `implemented` until these requirements and a
perceptual validation contract are satisfied.
