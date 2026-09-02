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
    if timestamps.size != samples.size or timestamps.size < 2:
        raise ValueError("timestamps and values must have equal length >= 2")
    if target_rate_hz <= 0:
        raise ValueError("target_rate_hz must be positive")
    order = np.argsort(timestamps, kind="stable")
    timestamps = timestamps[order]
    samples = samples[order]
    unique, unique_indices = np.unique(timestamps, return_index=True)
    samples = samples[unique_indices]
    target = np.arange(unique[0], unique[-1] + 0.5 / target_rate_hz, 1.0 / target_rate_hz)
    finite = np.isfinite(samples)
    if finite.sum() < 2:
        return target.astype(np.float64), np.full_like(target, np.nan)
    output = np.interp(target, unique[finite], samples[finite])
    return target.astype(np.float64), output.astype(np.float64)
