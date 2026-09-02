"""Windowed feature extraction."""

from __future__ import annotations

import numpy as np

from t21_engine.beats.pulse_peak import detect_pulse_peaks
from t21_engine.beats.rpeak import detect_r_peaks
from t21_engine.features.blood_pressure import (
    extract_blood_pressure_features,
    slope_per_minute,
)
from t21_engine.features.hrv import (
    frequency_domain_hrv,
    rr_intervals_ms,
    time_domain_hrv,
)
from t21_engine.features.multimodal import extract_multimodal_features
from t21_engine.features.ppg import extract_ppg_features
from t21_engine.features.respiratory import extract_respiratory_features
from t21_engine.types import BaselineState, FeatureSet, FloatArray


def _relative_delta(
    value: float | None, baseline: float | None
) -> tuple[float | None, float | None]:
    if value is None or baseline is None:
        return None, None
    delta = value - baseline
    percentage = 100.0 * delta / baseline if abs(baseline) > 1e-9 else None
    return delta, percentage


def extract_features(
    timestamps_s: FloatArray,
    signals: dict[str, FloatArray],
    baseline: BaselineState,
    sample_rate_hz: float,
    *,
    window_seconds: int = 60,
) -> FeatureSet:
    timestamps = np.asarray(timestamps_s, dtype=np.float64)
    if not timestamps.size:
        return FeatureSet({}, window_seconds, 0, ("No samples are available.",))
    cutoff = timestamps[-1] - window_seconds
    mask = timestamps >= cutoff
    window_times = timestamps[mask]
    window_signals = {name: np.asarray(values)[mask] for name, values in signals.items()}

    r_peaks = (
        detect_r_peaks(window_signals["ecg_ii"], sample_rate_hz)
        if "ecg_ii" in window_signals
        else None
    )
    pulse_peaks = (
        detect_pulse_peaks(window_signals["ppg"], sample_rate_hz)
        if "ppg" in window_signals
        else None
    )
    empty_r = detect_r_peaks(np.asarray([], dtype=np.float64), sample_rate_hz)
    empty_pulse = detect_pulse_peaks(np.asarray([], dtype=np.float64), sample_rate_hz)
    r_peaks = r_peaks or empty_r
    pulse_peaks = pulse_peaks or empty_pulse
    primary_beats = r_peaks if r_peaks.indices.size else pulse_peaks

    rr_ms = rr_intervals_ms(primary_beats)
    hrv = time_domain_hrv(rr_ms)
    frequency_hrv, frequency_limitation = frequency_domain_hrv(primary_beats)
    hr_values = window_signals.get("hr_bpm")
    current_hr: float | None
    if hr_values is not None and np.isfinite(hr_values).any():
        current_hr = float(np.nanmedian(hr_values[-max(1, int(sample_rate_hz * 5.0)) :]))
        hr_slope = slope_per_minute(window_times, hr_values)
        finite_hr = hr_values[np.isfinite(hr_values)]
        acceleration = float(np.nanmax(np.diff(finite_hr))) if finite_hr.size >= 2 else None
        deceleration = float(np.nanmin(np.diff(finite_hr))) if finite_hr.size >= 2 else None
    else:
        current_hr = 60000.0 / hrv["rr_mean_ms"] if hrv["rr_mean_ms"] else None
        instantaneous_hr = 60000.0 / rr_ms if rr_ms.size else np.asarray([], dtype=np.float64)
        beat_times = (
            primary_beats.times_s[1:][
                (np.diff(primary_beats.times_s) >= 0.3) & (np.diff(primary_beats.times_s) <= 2.0)
            ]
            if primary_beats.times_s.size >= 2
            else np.asarray([], dtype=np.float64)
        )
        hr_slope = slope_per_minute(beat_times, instantaneous_hr) if instantaneous_hr.size else None
        acceleration = (
            float(np.max(np.diff(instantaneous_hr))) if instantaneous_hr.size >= 2 else None
        )
        deceleration = (
            float(np.min(np.diff(instantaneous_hr))) if instantaneous_hr.size >= 2 else None
        )
    delta_hr, delta_hr_pct = _relative_delta(current_hr, baseline.median_hr)

    ppg_features = (
        extract_ppg_features(window_signals["ppg"], pulse_peaks, sample_rate_hz)
        if "ppg" in window_signals
        else {
            "ppg_amplitude": None,
            "ppg_pulse_width_s": None,
            "ppg_rise_time_s": None,
            "ppg_pulse_area": None,
            "ppg_amplitude_variability": None,
            "ppg_peak_confidence": None,
            "perfusion_trend_proxy": None,
        }
    )
    ppg_amp_delta, ppg_amp_delta_pct = _relative_delta(
        ppg_features["ppg_amplitude"], baseline.median_ppg_amplitude
    )
    bp_features = extract_blood_pressure_features(window_times, window_signals)
    delta_map, delta_map_pct = _relative_delta(
        bp_features["current_map_mm_hg"], baseline.median_map
    )
    values: dict[str, float | None] = {
        "current_hr_bpm": current_hr,
        "delta_hr_bpm": delta_hr,
        "delta_hr_pct": delta_hr_pct,
        "hr_slope_bpm_min": hr_slope,
        "hr_acceleration_bpm_sample": acceleration,
        "hr_deceleration_bpm_sample": deceleration,
        "beat_detection_confidence": primary_beats.confidence,
        **hrv,
        **frequency_hrv,
        **ppg_features,
        "ppg_amplitude_delta": ppg_amp_delta,
        "ppg_amp_delta_pct": ppg_amp_delta_pct,
        **bp_features,
        "delta_map_mm_hg": delta_map,
        "delta_map_pct": delta_map_pct,
        **extract_respiratory_features(window_times, window_signals),
    }
    values.update(
        extract_multimodal_features(
            r_peaks,
            pulse_peaks,
            current_hr=current_hr,
            current_map=bp_features["current_map_mm_hg"],
            ppg_amplitude_delta_pct=ppg_amp_delta_pct,
            delta_hr_pct=delta_hr_pct,
            delta_map_pct=delta_map_pct,
            available_modalities=sum(
                1
                for name in ("ecg_ii", "ppg", "abp", "map_mm_hg", "spo2_pct", "etco2_mm_hg")
                if name in window_signals and np.isfinite(window_signals[name]).any()
            ),
        )
    )
    limitations = tuple(item for item in (frequency_limitation,) if item)
    return FeatureSet(values, window_seconds, int(primary_beats.indices.size), limitations)


def extract_feature_windows(
    timestamps_s: FloatArray,
    signals: dict[str, FloatArray],
    baseline: BaselineState,
    sample_rate_hz: float,
    *,
    windows_seconds: tuple[int, ...] = (30, 60, 180),
) -> dict[int, FeatureSet]:
    """Calculate each configured research window without changing the flat API view."""
    if not windows_seconds or any(window <= 0 for window in windows_seconds):
        raise ValueError("feature windows must contain positive durations")
    if len(set(windows_seconds)) != len(windows_seconds):
        raise ValueError("feature windows must be unique")
    return {
        window: extract_features(
            timestamps_s,
            signals,
            baseline,
            sample_rate_hz,
            window_seconds=window,
        )
        for window in windows_seconds
    }


__all__ = ["extract_feature_windows", "extract_features"]
