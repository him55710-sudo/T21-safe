"""Deterministic R-peak candidate detector."""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks

from t21_engine.types import BeatSeries, FloatArray


def detect_r_peaks(ecg: FloatArray, sample_rate_hz: float) -> BeatSeries:
    values = np.asarray(ecg, dtype=np.float64)
    finite = np.isfinite(values)
    if finite.sum() < max(10, int(sample_rate_hz * 2.0)):
        return BeatSeries(
            np.asarray([], dtype=np.int64), np.asarray([], dtype=np.float64), 0.0, "ECG_R"
        )
    clean = values.copy()
    clean[~finite] = float(np.nanmedian(values))
    centered = clean - float(np.median(clean))
    scale = float(np.median(np.abs(centered))) * 1.4826
    prominence = max(scale * 2.5, float(np.std(centered)) * 0.35, 1e-6)
    indices, properties = find_peaks(
        centered,
        distance=max(1, int(0.3 * sample_rate_hz)),
        prominence=prominence,
    )
    if indices.size < 2:
        inverted, inverted_properties = find_peaks(
            -centered,
            distance=max(1, int(0.3 * sample_rate_hz)),
            prominence=prominence,
        )
        if inverted.size > indices.size:
            indices, properties = inverted, inverted_properties
    times = indices.astype(np.float64) / sample_rate_hz
    rr = np.diff(times)
    plausible = float(np.mean((rr >= 0.3) & (rr <= 2.0))) if rr.size else 0.0
    prominences = np.asarray(properties.get("prominences", []), dtype=np.float64)
    prominence_score = (
        min(1.0, float(np.median(prominences)) / (5.0 * scale + 1e-9)) if prominences.size else 0.0
    )
    confidence = float(np.clip(0.75 * plausible + 0.25 * prominence_score, 0.0, 1.0))
    return BeatSeries(indices.astype(np.int64), times, confidence, "ECG_R")
