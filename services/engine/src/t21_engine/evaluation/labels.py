"""Generic research label v0 definitions; not DS or pediatric endpoints."""

from __future__ import annotations

import numpy as np

from t21_engine.types import FloatArray


def _sustained_mask(
    condition: np.ndarray,
    timestamps_s: FloatArray,
    duration_seconds: float,
) -> np.ndarray:
    timestamps = np.asarray(timestamps_s, dtype=np.float64)
    output = np.zeros(condition.size, dtype=bool)
    start: int | None = None
    for index, active in enumerate(condition):
        if active and start is None:
            start = index
        if not active and start is not None:
            if timestamps[index] - timestamps[start] >= duration_seconds:
                output[start:index] = True
            start = None
    if start is not None:
        sample_interval = float(np.median(np.diff(timestamps))) if timestamps.size >= 2 else 0.0
        if timestamps[-1] - timestamps[start] + sample_interval >= duration_seconds:
            output[start:] = True
    return output


def hypotension_candidate(
    timestamps_s: FloatArray,
    map_mm_hg: FloatArray,
    *,
    threshold_mm_hg: float = 65.0,
    duration_seconds: float = 60.0,
) -> np.ndarray:
    """Adult generic MAP candidate; not a DS or pediatric clinical criterion."""
    values = np.asarray(map_mm_hg, dtype=np.float64)
    return _sustained_mask(
        np.isfinite(values) & (values < threshold_mm_hg), timestamps_s, duration_seconds
    )


def bradycardia_candidate(
    timestamps_s: FloatArray,
    hr_bpm: FloatArray,
    *,
    absolute_threshold_bpm: float,
    baseline_hr_bpm: float,
    relative_decline_pct: float = 20.0,
    duration_seconds: float = 30.0,
) -> np.ndarray:
    values = np.asarray(hr_bpm, dtype=np.float64)
    relative_threshold = baseline_hr_bpm * (1.0 - relative_decline_pct / 100.0)
    condition = np.isfinite(values) & (
        (values < absolute_threshold_bpm) | (values < relative_threshold)
    )
    return _sustained_mask(condition, timestamps_s, duration_seconds)


def composite_instability_candidate(*candidates: np.ndarray) -> np.ndarray:
    if not candidates:
        return np.asarray([], dtype=bool)
    shape = candidates[0].shape
    if any(candidate.shape != shape for candidate in candidates):
        raise ValueError("all candidate arrays must have the same shape")
    return np.asarray(np.logical_or.reduce(candidates), dtype=bool)
