"""Pulse morphology features."""

from __future__ import annotations

import numpy as np
from scipy.signal import peak_widths

from t21_engine.types import BeatSeries, FloatArray


def pulse_amplitudes(
    ppg: FloatArray,
    peaks: BeatSeries,
    sample_rate_hz: float,
) -> FloatArray:
    values = np.asarray(ppg, dtype=np.float64)
    amplitudes: list[float] = []
    lookback = max(1, int(0.5 * sample_rate_hz))
    for peak in peaks.indices:
        start = max(0, int(peak) - lookback)
        segment = values[start : int(peak) + 1]
        if segment.size and np.isfinite(segment).any() and np.isfinite(values[peak]):
            amplitudes.append(float(values[peak] - np.nanmin(segment)))
    return np.asarray(amplitudes, dtype=np.float64)


def extract_ppg_features(
    ppg: FloatArray,
    peaks: BeatSeries,
    sample_rate_hz: float,
) -> dict[str, float | None]:
    values = np.asarray(ppg, dtype=np.float64)
    amplitudes = pulse_amplitudes(values, peaks, sample_rate_hz)
    widths: np.ndarray = np.asarray([], dtype=np.float64)
    if peaks.indices.size and np.isfinite(values).all():
        widths = np.asarray(peak_widths(values, peaks.indices, rel_height=0.5)[0]) / sample_rate_hz
    rise_times: list[float] = []
    areas: list[float] = []
    lookback = max(1, int(0.5 * sample_rate_hz))
    for peak in peaks.indices:
        start = max(0, int(peak) - lookback)
        segment = values[start : int(peak) + 1]
        if not segment.size or not np.isfinite(segment).all():
            continue
        trough = int(np.argmin(segment))
        rise_times.append((segment.size - 1 - trough) / sample_rate_hz)
        baseline = segment[trough]
        areas.append(float(np.trapezoid(segment[trough:] - baseline, dx=1.0 / sample_rate_hz)))
    return {
        "ppg_amplitude": float(np.median(amplitudes)) if amplitudes.size else None,
        "ppg_pulse_width_s": float(np.median(widths)) if widths.size else None,
        "ppg_rise_time_s": float(np.median(rise_times)) if rise_times else None,
        "ppg_pulse_area": float(np.median(areas)) if areas else None,
        "ppg_amplitude_variability": (
            float(np.std(amplitudes, ddof=1)) if amplitudes.size >= 2 else None
        ),
        "ppg_peak_confidence": peaks.confidence,
        "perfusion_trend_proxy": float(np.median(amplitudes)) if amplitudes.size else None,
    }
