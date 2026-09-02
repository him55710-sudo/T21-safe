"""Blood-pressure trends and generic adult research event candidates."""

from __future__ import annotations

import numpy as np

from t21_engine.beats.pulse_peak import detect_pulse_peaks
from t21_engine.types import FloatArray


def slope_per_minute(timestamps_s: FloatArray, values: FloatArray) -> float | None:
    timestamps = np.asarray(timestamps_s, dtype=np.float64)
    samples = np.asarray(values, dtype=np.float64)
    finite = np.isfinite(timestamps) & np.isfinite(samples)
    if finite.sum() < 2 or float(np.ptp(timestamps[finite])) <= 0.0:
        return None
    centered = timestamps[finite] - float(np.mean(timestamps[finite]))
    denominator = float(np.sum(centered**2))
    if denominator <= 0.0:
        return None
    slope_per_second = float(
        np.sum(centered * (samples[finite] - float(np.mean(samples[finite])))) / denominator
    )
    return slope_per_second * 60.0


def duration_below_threshold(
    timestamps_s: FloatArray,
    values: FloatArray,
    threshold: float,
) -> float:
    timestamps = np.asarray(timestamps_s, dtype=np.float64)
    samples = np.asarray(values, dtype=np.float64)
    if timestamps.size < 2:
        return 0.0
    intervals = np.diff(timestamps, append=timestamps[-1])
    valid_below = np.isfinite(samples) & (samples < threshold)
    return float(np.sum(intervals[valid_below]))


def extract_blood_pressure_features(
    timestamps_s: FloatArray,
    signals: dict[str, FloatArray],
    sample_rate_hz: float,
    *,
    hypotension_threshold: float = 65.0,
) -> dict[str, float | None]:
    map_values = signals.get("map_mm_hg")
    if map_values is None and "abp" in signals:
        map_values = signals["abp"]
    recent_samples = max(1, int(round(5.0 * sample_rate_hz)))
    current_map = (
        float(np.nanmedian(map_values[-recent_samples:]))
        if map_values is not None and np.isfinite(map_values).any()
        else None
    )
    waveform_sbp, waveform_dbp, waveform_variability = _abp_beat_pressures(
        signals.get("abp"), sample_rate_hz
    )
    numeric_sbp = _last_finite_median(signals.get("sbp_mm_hg"), recent_samples)
    numeric_dbp = _last_finite_median(signals.get("dbp_mm_hg"), recent_samples)
    return {
        "current_sbp_mm_hg": numeric_sbp if numeric_sbp is not None else waveform_sbp,
        "current_dbp_mm_hg": numeric_dbp if numeric_dbp is not None else waveform_dbp,
        "current_map_mm_hg": current_map,
        "map_slope_mm_hg_min": slope_per_minute(timestamps_s, map_values)
        if map_values is not None
        else None,
        "map_duration_below_threshold_s": (
            duration_below_threshold(timestamps_s, map_values, hypotension_threshold)
            if map_values is not None
            else None
        ),
        "pressure_variability": waveform_variability
        if waveform_variability is not None
        else (
            float(np.nanstd(map_values, ddof=1))
            if map_values is not None and np.isfinite(map_values).sum() >= 2
            else None
        ),
    }


def _abp_beat_pressures(
    abp: FloatArray | None,
    sample_rate_hz: float,
) -> tuple[float | None, float | None, float | None]:
    if abp is None:
        return None, None, None
    values = np.asarray(abp, dtype=np.float64)
    beats = detect_pulse_peaks(values, sample_rate_hz)
    systolic: list[float] = []
    diastolic: list[float] = []
    lookback = max(1, int(round(1.5 * sample_rate_hz)))
    for peak in beats.indices:
        peak_index = int(peak)
        start = max(0, peak_index - lookback)
        segment = values[start : peak_index + 1]
        if np.isfinite(values[peak_index]) and np.isfinite(segment).any():
            systolic.append(float(values[peak_index]))
            diastolic.append(float(np.nanmin(segment)))
    if not systolic:
        return None, None, None
    recent_count = min(5, len(systolic))
    recent_systolic = np.asarray(systolic[-recent_count:], dtype=np.float64)
    recent_diastolic = np.asarray(diastolic[-recent_count:], dtype=np.float64)
    pulse_pressures = recent_systolic - recent_diastolic
    variability = float(np.std(pulse_pressures, ddof=1)) if pulse_pressures.size >= 2 else None
    return (
        float(np.median(recent_systolic)),
        float(np.median(recent_diastolic)),
        variability,
    )


def _last_finite_median(values: FloatArray | None, recent_samples: int) -> float | None:
    if values is None:
        return None
    samples = np.asarray(values, dtype=np.float64)
    return float(np.nanmedian(samples[-recent_samples:])) if np.isfinite(samples).any() else None
