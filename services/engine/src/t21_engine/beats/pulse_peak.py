"""PPG/ABP pulse peak detector with confidence score."""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks

from t21_engine.types import BeatSeries, FloatArray


def detect_pulse_peaks(ppg: FloatArray, sample_rate_hz: float) -> BeatSeries:
    values = np.asarray(ppg, dtype=np.float64)
    finite = np.isfinite(values)
    if finite.sum() < max(10, int(sample_rate_hz * 2.0)):
        return BeatSeries(
            np.asarray([], dtype=np.int64), np.asarray([], dtype=np.float64), 0.0, "PULSE"
        )
    clean = values.copy()
    clean[~finite] = float(np.nanmedian(values))
    spread = float(np.nanpercentile(clean, 95) - np.nanpercentile(clean, 5))
    indices, properties = find_peaks(
        clean,
        distance=max(1, int(0.3 * sample_rate_hz)),
        prominence=max(0.08 * spread, 1e-6),
    )
    times = indices.astype(np.float64) / sample_rate_hz
    rr = np.diff(times)
    plausible = float(np.mean((rr >= 0.3) & (rr <= 2.0))) if rr.size else 0.0
    prominences = np.asarray(properties.get("prominences", []), dtype=np.float64)
    prominence_score = (
        min(1.0, float(np.median(prominences)) / (0.25 * spread + 1e-9))
        if prominences.size
        else 0.0
    )
    missing_penalty = float(np.mean(finite))
    confidence = float(
        np.clip((0.7 * plausible + 0.3 * prominence_score) * missing_penalty, 0.0, 1.0)
    )
    return BeatSeries(indices.astype(np.int64), times, confidence, "PULSE")
