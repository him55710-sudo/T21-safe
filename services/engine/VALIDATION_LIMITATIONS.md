# Validation limitations

## Current status

This is a software and signal-processing prototype, not a clinically validated device.
The deterministic Research Instability Index has not been probability-calibrated, has
not been prospectively evaluated, and has no established alert threshold.
The bundled CSV fixture is generated synthetic data and contains no real patient record.

## Population limits

- VitalDB and similar public sources are used only for generic, primarily adult,
  perioperative signal validation.
- Down syndrome data are unavailable in the implemented training/evaluation path.
- No pediatric or Down syndrome sensitivity, specificity, lead time, calibration, or
  clinical utility is claimed.
- Public non-DS outcomes must never be presented as DS performance.

## Known failure modes

- Motion, electrocautery, clipping, flatline, flush artifacts, poor perfusion, and sensor
  displacement can corrupt beats and morphology.
- Numerics may be sparse, delayed, or disagree with their waveforms.
- ECG-PPG timing can include device clock and resampling delay, so `ptt_ms` is a proxy.
- Short-window HRV and entropy are unstable with few beats; LF/HF has strong respiratory
  confounding and is not a core feature.
- An unstable first baseline window prevents calibration; a later score is not forced.
- Missing modalities reduce confidence. Missing usable beat or pressure sources,
  excessive gaps, synchronization failure, or OOD values withhold the index.

## Evaluation status

`models/research-index-v0/metrics.json` deliberately reports `NOT_EVALUATED` where data
are insufficient. Metrics must not be populated with invented values. A future generic
evaluation must use case-level splits, validation-only threshold tuning, deterministic
seeds, checksums, class-balance reporting, and a separately held-out test set.

## Prohibited use

No pump control, anesthetic dose recommendation, drug/treatment instruction, clinical
alarm replacement, PHI storage, or LLM inference is permitted in the real-time path.
