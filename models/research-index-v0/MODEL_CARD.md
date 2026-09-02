# Model card: Research Instability Index v0.1

## Intended use

Research-only visualization and software validation of patient-specific physiological
change in a shadow-mode prototype. `GENERIC_VALIDATION_MODE` may evaluate signal
processing and generic adult research labels. `DS_HYPOTHESIS_MODE` may visualize
candidate features without claiming a DS clinical model.

## Non-intended use

Diagnosis, prognosis, treatment, anesthetic or other drug dosing, pump control, alarm
replacement, autonomous action, and clinical monitoring are prohibited. The output is
not a calibrated probability and has no validated intervention threshold.

## Model

The default is a deterministic weighted research index. Version-pinned contributions
include relative HR decline, relative MAP decline, relative PPG amplitude decline,
adverse HR/MAP slopes, and low SpO2. Quality, baseline, and OOD gates run before scoring.
No LLM is used in the inference path.

## Training data

No fitted model is registered in v0.1. Public VitalDB/WFDB data are adapters for generic
signal-processing validation only. Dataset checksum and training environment are
`NOT_EVALUATED` because no training run has occurred.

## DS and pediatric limitations

DS data are unavailable. Pediatric and Down syndrome clinical performance has not been
evaluated. Public non-DS adult data cannot establish DS performance.

## Metrics

AUROC, AUPRC, sensitivity, specificity, PPV, NPV, false alarms/hour, median lead time,
calibration curve, Brier score, and bootstrap confidence intervals are `NOT_EVALUATED`.
Runtime tests cover invalid prediction and SQI failure behavior but are not performance
estimates.

## Signal requirements

At least one usable beat source (ECG or PPG), usable ABP/MAP information, synchronized
timestamps, sufficient valid beats, acceptable gap fraction, and a completed stable
patient baseline are required. Optional modalities reduce uncertainty when present.

## OOD handling

Low SQI, excessive gaps, timestamp failure, insufficient beats, incomplete baseline, or
feature values outside supported engineering ranges withhold the index. Missing
modalities, unsupported age groups, and DS hypothesis mode reduce confidence and produce
explicit reasons. Silent fallback is forbidden.

## Known failure modes

Motion/electrocautery, clipping, sensor loss, arterial flush, poor perfusion, sparse or
delayed numerics, device timing offsets, unstable baseline, and short-window HRV can
produce invalid or unreliable features.

## Clinical status

No clinical validation has been performed. No dosing recommendation is generated.
