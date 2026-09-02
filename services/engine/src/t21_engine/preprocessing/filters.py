"""Configurable zero-phase biomedical signal filters."""

from __future__ import annotations

import numpy as np
from scipy import signal

from t21_engine.types import FloatArray


def _interpolate_missing(values: FloatArray) -> tuple[FloatArray, np.ndarray]:
    clean = np.asarray(values, dtype=np.float64).copy()
    finite = np.isfinite(clean)
    if finite.sum() < 2:
        return clean, ~finite
    indices = np.arange(clean.size)
    clean[~finite] = np.interp(indices[~finite], indices[finite], clean[finite])
    return clean, ~finite


def bandpass_filter(
    values: FloatArray,
    sample_rate_hz: float,
    low_hz: float,
    high_hz: float,
    *,
    order: int = 3,
) -> FloatArray:
    """Apply a Butterworth bandpass without mutating the raw array."""
    raw = np.asarray(values, dtype=np.float64)
    if raw.ndim != 1:
        raise ValueError("values must be one-dimensional")
    nyquist = sample_rate_hz / 2.0
    if not 0.0 < low_hz < high_hz < nyquist:
        raise ValueError("bandpass cutoffs must satisfy 0 < low < high < Nyquist")
    clean, missing = _interpolate_missing(raw)
    if np.isfinite(clean).sum() < max(12, order * 6):
        return raw.copy()
    sos = signal.butter(order, [low_hz, high_hz], btype="bandpass", fs=sample_rate_hz, output="sos")
    try:
        filtered = signal.sosfiltfilt(sos, clean)
    except ValueError:
        filtered = signal.sosfilt(sos, clean)
    filtered = np.asarray(filtered, dtype=np.float64)
    filtered[missing] = np.nan
    return filtered


def notch_filter(
    values: FloatArray,
    sample_rate_hz: float,
    mains_hz: float | None,
    *,
    quality_factor: float = 30.0,
) -> FloatArray:
    if mains_hz is None:
        return np.asarray(values, dtype=np.float64).copy()
    if not 0.0 < mains_hz < sample_rate_hz / 2.0:
        raise ValueError("mains frequency must be below Nyquist")
    clean, missing = _interpolate_missing(np.asarray(values, dtype=np.float64))
    b, a = signal.iirnotch(mains_hz, quality_factor, fs=sample_rate_hz)
    try:
        filtered = signal.filtfilt(b, a, clean)
    except ValueError:
        filtered = signal.lfilter(b, a, clean)
    filtered = np.asarray(filtered, dtype=np.float64)
    filtered[missing] = np.nan
    return filtered


def preprocess_ecg(
    values: FloatArray,
    sample_rate_hz: float,
    *,
    low_hz: float = 0.5,
    high_hz: float = 35.0,
    order: int = 3,
    mains_hz: float | None = None,
) -> FloatArray:
    filtered = bandpass_filter(values, sample_rate_hz, low_hz, high_hz, order=order)
    return notch_filter(filtered, sample_rate_hz, mains_hz)


def preprocess_ppg(
    values: FloatArray,
    sample_rate_hz: float,
    *,
    low_hz: float = 0.4,
    high_hz: float = 8.0,
    order: int = 3,
) -> FloatArray:
    filtered = bandpass_filter(values, sample_rate_hz, low_hz, high_hz, order=order)
    finite = np.isfinite(filtered)
    if finite.sum() < 2:
        return filtered
    median = float(np.nanmedian(filtered))
    mad = float(np.nanmedian(np.abs(filtered[finite] - median)))
    if mad > 1e-9:
        filtered[finite] = (filtered[finite] - median) / (1.4826 * mad)
    return filtered


def preprocess_abp(
    values: FloatArray,
    sample_rate_hz: float,
    *,
    low_hz: float = 0.3,
    high_hz: float = 12.0,
    order: int = 3,
) -> FloatArray:
    return bandpass_filter(values, sample_rate_hz, low_hz, high_hz, order=order)
