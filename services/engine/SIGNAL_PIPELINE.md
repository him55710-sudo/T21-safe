# Signal pipeline

```text
adapter -> timestamp normalization -> bounded ring buffer
        -> raw/processed provenance split
        -> configurable filtering and artifact candidates
        -> ECG/PPG/ABP SQI and quality gate
        -> R/pulse beat detection and ECG-PPG alignment
        -> first-180-second patient baseline (configurable)
        -> 30/60/180-second feature windows
        -> uncertainty/OOD gate
        -> deterministic Research Instability Index + reasons
        -> versioned SSE event
```

## Data and streaming

Adapters return only available canonical signals. Timestamps are sorted, duplicate
timestamps retain the newest value, out-of-order input is counted, and gaps are exposed.
The ring buffer is bounded and cleared when a replay completes or is cancelled. Source
download latency and per-update processing latency are reported as engineering metrics,
not clinical performance.

SSE separates waveform chunks (`ecg_ii`, `ppg`, `abp`) from current numeric trends.
Missing values are JSON `null`; stale valid scores are never substituted for an invalid
update.

## Preprocessing and quality

Filter cutoffs are in `config.py` and are limited below the actual source Nyquist.
Functions never overwrite the raw arrays. Flatline, clipping, abrupt motion, missing
data, implausible ABP range, and pulse regularity contribute to SQI values from 0 to 1.

An index is withheld when the beat source or pressure source is unusable, gaps exceed
the configured threshold, timestamps are unsynchronized, valid beats are insufficient,
or baseline calibration has not completed. Missing PPG can degrade confidence while ECG
and pressure continue; loss of all usable beat or pressure sources is invalid.

## Baseline and features

The default baseline is the first 180 seconds and does not slide after calibration.
Calibration records HR/MAP/PPG summaries, HRV, quality, modalities, and confidence. An
unstable or low-quality baseline fails explicitly. Change features prioritize the
individual baseline over a fixed DS normal range.

The engine calculates each configured 30-, 60-, and 180-second feature window on every
update. The existing flat SSE contract exposes the 60-second window (or the configured
window nearest 60 seconds) as its primary view; all window results remain available to
engine evaluation callers through `extract_feature_windows`.

LF/HF is optional, requires at least 180 seconds and 20 valid beats, reports respiratory
confounding, and is not used by the core index.

## Index

`rii-v0.1` is a transparent weighted engineering hypothesis. HR decline, MAP decline,
PPG amplitude decline, adverse slopes, and low SpO2 can contribute to a bounded 0-100
index. The value is not probability-calibrated. Quality/baseline/OOD checks execute
before scoring, and invalid output is always `score=null`, `level=INVALID`.
