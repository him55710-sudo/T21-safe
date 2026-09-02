# Model audit

Audit date: 2026-09-02. Audited runtime: `rii-v0.1` with `pipeline-v0.2` and `features-v0.1`.

## Finding summary

The live path is a transparent deterministic index, not a fitted statistical/ML model. It is correctly registered with `calibrated_probability=false`, DS/pediatric validation false, and all performance metrics `NOT_EVALUATED`. The score must not be interpreted as event probability, prognosis, or an intervention threshold.

| Audit item | Current state | Assessment/action |
|---|---|---|
| Feature definitions/units | Implemented and documented | Traceability matrix added; some source units remain adapter-dependent |
| Baseline window | First 180 seconds, configurable 3–600 for tests/research | Stable quality required; no bypass |
| Feature window | Up to current 60 seconds; 30/60/180 declared for future work | Runtime currently emits the current up-to-60-second calculation only |
| Prediction/target horizon | None | Misleading `horizon_seconds` field removed; observation context is not a forecast |
| Target label | None for registered index | Candidate label utilities are dormant research code |
| Missing values | Runtime uses NaN/null and feature withholding | Training demo now rejects missing/non-finite features unless a predeclared train-fitted imputation pipeline is supplied |
| Class imbalance | Not applicable to current index | Optional demo uses `class_weight=balanced`; no empirical evaluation |
| Split unit | Patient | Corrected from case-level to patient-level to prevent repeated-procedure leakage |
| Threshold selection | Fixed engineering bins for index | Not clinically tuned; optional demo selects on validation only, never test |
| Calibration | None for current index | Optional demo can fit sigmoid calibration on validation; no artifact registered |
| Uncertainty/OOD | Implemented engineering gate | Quality, baseline, ranges, age, modality, DS mode, dropout, latency, and timestamp checks |
| SQI gate | Implemented | Runs on raw windows so filters cannot hide rough motion/clipping |
| External validation | None | Required before any clinical or DS claim |

## Index construction

Maximum fixed contributions are HR decline 25, MAP decline 35, PPG amplitude decline 15, HR slope 5, MAP slope 10, and low SpO2 10. Values are clipped to 0–100. The fixed contribution scales and display bins are engineering hypotheses; they were not learned, probability-calibrated, or validated against patient outcomes.

## Fail-safe decision

The index is withheld for unusable beat/pressure sources, excessive missingness, source-reported dropout, source latency over 1000 ms, synchronization error over 100 ms, out-of-order timestamps, insufficient beats, incomplete/unstable baseline, or out-of-range core features. Missing or low-quality individual modalities reduce confidence when redundant sources allow continued calculation.

## Critical gaps

1. No DS perioperative cohort, pediatric cohort, adjudicated endpoint set, or external-site result exists.
2. No run manifest demonstrates patient-level partitioning on real data.
3. No fitted model artifact, hyperparameter record, calibration plot, decision-curve analysis, subgroup analysis, or confidence interval exists.
4. Adult generic thresholds and current engineering ranges may be inappropriate for pediatric or DS populations.
5. Feature extraction assumes a common sample rate per batch; mixed-rate device streams require explicit resampling validation.

## Required next gate

Do not activate a fitted or DS-specific mode until dataset/label governance, patient-level partitions, temporal leakage tests, locked preprocessing, calibration and OOD plans, external validation, and signed clinician/statistician review are complete.
