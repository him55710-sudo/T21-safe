"""Optional respiratory trend features."""

from __future__ import annotations

import numpy as np
from scipy import signal

from t21_engine.features.blood_pressure import slope_per_minute
from t21_engine.types import FloatArray


def _respiratory_waveform_features(
    timestamps_s: FloatArray,
    respiratory_waveform: FloatArray,
) -> dict[str, float | None]:
    timestamps = np.asarray(timestamps_s, dtype=np.float64)
    values = np.asarray(respiratory_waveform, dtype=np.float64)
    finite = np.isfinite(timestamps) & np.isfinite(values)
    unavailable = {
        "resp_waveform_irregularity": None,
        "resp_missing_breath_candidate": None,
    }
    if finite.sum() < 20 or float(np.mean(finite)) < 0.8:
        return {"respiratory_rate_bpm": None, **unavailable}
    finite_times = timestamps[finite]
    intervals = np.diff(finite_times)
    positive_intervals = intervals[intervals > 0.0]
    if not positive_intervals.size:
        return {"respiratory_rate_bpm": None, **unavailable}
    sample_interval = float(np.median(positive_intervals))
    if sample_interval <= 0.0:
        return {"respiratory_rate_bpm": None, **unavailable}

    clean = values.copy()
    indices = np.arange(clean.size)
    clean[~finite] = np.interp(indices[~finite], indices[finite], clean[finite])
    centered = clean - float(np.median(clean))
    spread = float(np.std(centered))
    if spread <= 1e-9:
        return {"respiratory_rate_bpm": None, **unavailable}
    peaks, _ = signal.find_peaks(
        centered,
        distance=max(1, int(round(0.8 / sample_interval))),
        prominence=max(1e-9, 0.2 * spread),
    )
    if peaks.size < 2:
        return {"respiratory_rate_bpm": None, **unavailable}
    breath_intervals = np.diff(timestamps[peaks])
    plausible = breath_intervals[(breath_intervals >= 0.8) & (breath_intervals <= 10.0)]
    if not plausible.size:
        return {"respiratory_rate_bpm": None, **unavailable}
    median_breath_interval = float(np.median(plausible))
    irregularity = (
        float(np.std(plausible, ddof=1) / np.mean(plausible)) if plausible.size >= 2 else 0.0
    )
    missing_candidate = float(
        bool(
            breath_intervals.size
            and float(np.max(breath_intervals)) > max(10.0, 2.5 * median_breath_interval)
        )
    )
    return {
        "respiratory_rate_bpm": 60.0 / median_breath_interval,
        "resp_waveform_irregularity": irregularity,
        "resp_missing_breath_candidate": missing_candidate,
    }


def extract_respiratory_features(
    timestamps_s: FloatArray,
    signals: dict[str, FloatArray],
) -> dict[str, float | None]:
    output: dict[str, float | None] = {
        "current_spo2_pct": None,
        "spo2_slope_pct_min": None,
        "current_etco2_mm_hg": None,
        "etco2_slope_mm_hg_min": None,
        "respiratory_rate_bpm": None,
        "resp_waveform_irregularity": None,
        "resp_missing_breath_candidate": None,
    }
    for name, current_key, slope_key in (
        ("spo2_pct", "current_spo2_pct", "spo2_slope_pct_min"),
        ("etco2_mm_hg", "current_etco2_mm_hg", "etco2_slope_mm_hg_min"),
    ):
        values = signals.get(name)
        if values is not None and np.isfinite(values).any():
            output[current_key] = float(np.nanmedian(values[-100:]))
            output[slope_key] = slope_per_minute(timestamps_s, values)
    respiratory = signals.get("resp_bpm")
    if respiratory is not None and np.isfinite(respiratory).any():
        output["respiratory_rate_bpm"] = float(np.nanmedian(respiratory[-100:]))
    waveform = signals.get("resp")
    if waveform is not None:
        waveform_features = _respiratory_waveform_features(timestamps_s, waveform)
        if output["respiratory_rate_bpm"] is None:
            output["respiratory_rate_bpm"] = waveform_features["respiratory_rate_bpm"]
        output["resp_waveform_irregularity"] = waveform_features["resp_waveform_irregularity"]
        output["resp_missing_breath_candidate"] = waveform_features["resp_missing_breath_candidate"]
    return output
