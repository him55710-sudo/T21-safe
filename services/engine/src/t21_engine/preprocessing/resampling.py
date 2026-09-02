"""Timestamp-aware resampling that preserves missing-tail semantics."""

from __future__ import annotations

import numpy as np

from t21_engine.types import FloatArray


def resample_signal(
    timestamps_s: FloatArray,
    values: FloatArray,
    target_rate_hz: float,
) -> tuple[FloatArray, FloatArray]:
    timestamps = np.asarray(timestamps_s, dtype=np.float64)
    samples = np.asarray(values, dtype=np.float64)
    if timestamps.ndim != 1 or samples.ndim != 1:
        raise ValueError("timestamps and values must be one-dimensional")
    if timestamps.size != samples.size or timestamps.size < 2:
        raise ValueError("timestamps and values must have equal length >= 2")
    if not np.isfinite(timestamps).all():
        raise ValueError("timestamps must be finite")
    if not np.isfinite(target_rate_hz) or target_rate_hz <= 0:
        raise ValueError("target_rate_hz must be positive and finite")
    order = np.argsort(timestamps, kind="stable")
    timestamps = timestamps[order]
    samples = samples[order]
    _, reverse_unique_indices = np.unique(timestamps[::-1], return_index=True)
    keep = np.sort(timestamps.size - 1 - reverse_unique_indices)
    unique = timestamps[keep]
    samples = samples[keep]
    if unique.size < 2:
        raise ValueError("timestamps must contain at least two unique values")
    target = np.arange(unique[0], unique[-1] + 0.5 / target_rate_hz, 1.0 / target_rate_hz)
    finite = np.isfinite(samples)
    if finite.sum() < 2:
        return target.astype(np.float64), np.full_like(target, np.nan)
    output = np.interp(target, unique[finite], samples[finite])
    output[(target < unique[finite][0]) | (target > unique[finite][-1])] = np.nan
    return target.astype(np.float64), output.astype(np.float64)
