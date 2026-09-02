# Model flow

## Current scoring path

```text
raw signals
→ raw-window SQI and transport checks
→ stable 180 s patient baseline
→ current 60 s feature window (shorter during startup)
→ OOD/uncertainty gate
→ fixed transparent feature contributions
→ bounded Research Instability Index (0–100) + reasons
```

The registered artifact `rii-v0.1` is not a trained model. It has no learned coefficients, target label, fitted calibration, probability semantics, or validated prediction horizon. The API exposes `observation_context_seconds=120` as display/context metadata; it is not a forecast horizon.

## Contributions

| Input | Maximum contribution | Interpretation |
|---|---:|---|
| Relative HR decline | 25 | Change from the individual baseline |
| Relative MAP decline | 35 | Change from the individual baseline |
| Relative PPG amplitude decline | 15 | Exploratory peripheral pulse change |
| Adverse HR slope | 5 | Current-window trend |
| Adverse MAP slope | 10 | Current-window trend |
| Low SpO2 | 10 | Generic engineering contribution |

Thresholds (`WATCH=25`, `ELEVATED=50`, `HIGH=75`) are UI/research bins only. They are not intervention thresholds and were not tuned on a clinical test set.

## Gate order

Scoring occurs only after usable beat/pressure sources, acceptable missingness, timestamp synchronization, acceptable source latency, no reported dropout, enough valid beats, a completed stable baseline, and supported engineering ranges are confirmed. Missing or individually low-quality core modalities reduce confidence. DS hypothesis mode and unsupported age groups also reduce confidence. Any hard-gate failure yields `score=null`, `level=INVALID`, and an explanatory reason.

## Future fitted-model boundary

The dormant evaluation utilities support patient-level grouped splits and calibration experiments, but no resulting estimator is registered. A future model requires a versioned dataset manifest, leakage review, development/validation/test separation, predeclared target and horizon, class-imbalance plan, calibration assessment, uncertainty/OOD plan, external validation, and signed clinical/statistical review. Test data must never tune features or thresholds.
