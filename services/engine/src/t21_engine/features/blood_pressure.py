"""Blood-pressure trends and generic adult research event candidates."""

from __future__ import annotations

import numpy as np

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
    *,
    hypotension_threshold: float = 65.0,
) -> dict[str, float | None]:
    map_values = signals.get("map_mm_hg")
    if map_values is None and "abp" in signals:
        map_values = signals["abp"]
    current_map = (
        float(np.nanmedian(map_values[-100:]))
        if map_values is not None and np.isfinite(map_values).any()
        else None
    )
    return {
        "current_sbp_mm_hg": _last_finite_median(signals.get("sbp_mm_hg")),
        "current_dbp_mm_hg": _last_finite_median(signals.get("dbp_mm_hg")),
        "current_map_mm_hg": current_map,
        "map_slope_mm_hg_min": slope_per_minute(timestamps_s, map_values)
        if map_values is not None
        else None,
        "map_duration_below_threshold_s": (
            duration_below_threshold(timestamps_s, map_values, hypotension_threshold)
            if map_values is not None
            else None
        ),
        "pressure_variability": (
            float(np.nanstd(map_values, ddof=1))
            if map_values is not None and np.isfinite(map_values).sum() >= 2
            else None
        ),
    }


def _last_finite_median(values: FloatArray | None) -> float | None:
    if values is None:
        return None
    samples = np.asarray(values, dtype=np.float64)
    return float(np.nanmedian(samples[-100:])) if np.isfinite(samples).any() else None
