"""Quality-gated patient-specific baseline calibration."""

from __future__ import annotations

import numpy as np

from t21_engine.beats.pulse_peak import detect_pulse_peaks
from t21_engine.beats.rpeak import detect_r_peaks
from t21_engine.features.hrv import rr_intervals_ms, time_domain_hrv
from t21_engine.features.ppg import pulse_amplitudes
from t21_engine.types import BaselineState, DistributionSummary, FloatArray, QualityResult


def _distribution(values: FloatArray) -> DistributionSummary | None:
    finite = np.asarray(values, dtype=np.float64)
    finite = finite[np.isfinite(finite)]
    if not finite.size:
        return None
    return DistributionSummary(
        minimum=float(np.min(finite)),
        p25=float(np.percentile(finite, 25)),
        median=float(np.median(finite)),
        p75=float(np.percentile(finite, 75)),
        maximum=float(np.max(finite)),
    )


def calibrate_baseline(
    timestamps_s: FloatArray,
    signals: dict[str, FloatArray],
    sample_rate_hz: float,
    quality: QualityResult,
    *,
    baseline_seconds: int = 180,
    minimum_fraction: float = 0.8,
) -> BaselineState:
    timestamps = np.asarray(timestamps_s, dtype=np.float64)
    if baseline_seconds <= 0:
        raise ValueError("baseline_seconds must be positive")
    if not timestamps.size:
        return BaselineState(False, 0.0, 0.0, reasons=("No baseline samples are available.",))
    finite_times = timestamps[np.isfinite(timestamps)]
    if finite_times.size < 2:
        return BaselineState(False, 0.0, 0.0, reasons=("Baseline timestamps are insufficient.",))
    median_interval = float(np.median(np.diff(finite_times)))
    observed_seconds = max(0.0, float(finite_times[-1] - finite_times[0] + median_interval))
    progress = float(np.clip(observed_seconds / baseline_seconds, 0.0, 1.0))
    baseline_end = finite_times[0] + baseline_seconds
    mask = timestamps < baseline_end
    baseline_signals = {name: np.asarray(values)[mask] for name, values in signals.items()}

    ecg_beats = (
        detect_r_peaks(baseline_signals["ecg_ii"], sample_rate_hz)
        if "ecg_ii" in baseline_signals
        else None
    )
    pulse_beats = (
        detect_pulse_peaks(baseline_signals["ppg"], sample_rate_hz)
        if "ppg" in baseline_signals
        else None
    )
    hr_values = baseline_signals.get("hr_bpm")
    median_hr: float | None
    if hr_values is not None and np.isfinite(hr_values).any():
        finite_hr = hr_values[np.isfinite(hr_values)]
        median_hr = float(np.median(finite_hr))
        hr_iqr = float(np.percentile(finite_hr, 75) - np.percentile(finite_hr, 25))
        hr_distribution = _distribution(finite_hr)
    elif ecg_beats is not None:
        rr_ms = rr_intervals_ms(ecg_beats)
        median_hr = float(60000.0 / np.median(rr_ms)) if rr_ms.size else None
        hr_iqr = None
        hr_distribution = _distribution(60000.0 / rr_ms) if rr_ms.size else None
    else:
        median_hr = None
        hr_iqr = None
        hr_distribution = None

    map_values = baseline_signals.get("map_mm_hg")
    if map_values is None:
        map_values = baseline_signals.get("abp")
    finite_map = map_values[np.isfinite(map_values)] if map_values is not None else np.asarray([])
    median_map = float(np.median(finite_map)) if finite_map.size else None

    ppg_amplitudes = (
        pulse_amplitudes(baseline_signals["ppg"], pulse_beats, sample_rate_hz)
        if pulse_beats is not None
        else np.asarray([], dtype=np.float64)
    )
    median_ppg_amplitude = float(np.median(ppg_amplitudes)) if ppg_amplitudes.size else None
    hrv = (
        time_domain_hrv(rr_intervals_ms(ecg_beats))
        if ecg_beats is not None
        else {"rmssd_ms": None, "sdnn_ms": None}
    )
    sqi_values = [
        value for value in (quality.ecg_sqi, quality.ppg_sqi, quality.abp_sqi) if value is not None
    ]
    quality_median = float(np.median(sqi_values)) if sqi_values else 0.0
    quality_distribution = _distribution(np.asarray(sqi_values, dtype=np.float64))
    modalities = tuple(
        name
        for name in ("ecg_ii", "ppg", "abp", "map_mm_hg", "spo2_pct", "etco2_mm_hg")
        if name in baseline_signals and np.isfinite(baseline_signals[name]).any()
    )

    reasons: list[str] = []
    if progress < 1.0:
        reasons.append("Baseline calibration is incomplete.")
    if observed_seconds < baseline_seconds * minimum_fraction:
        reasons.append("Too little baseline coverage is available.")
    if not quality.usable:
        reasons.append("Baseline signal quality is insufficient.")
    if median_hr is None:
        reasons.append("No reliable baseline heart rate is available.")
    if median_map is None:
        reasons.append("No reliable baseline MAP or ABP is available.")
    if median_hr is not None and hr_iqr is not None and hr_iqr / max(median_hr, 1.0) > 0.25:
        reasons.append("Heart rate is too unstable for baseline calibration.")
    if median_map is not None and finite_map.size >= 4:
        map_iqr = float(np.percentile(finite_map, 75) - np.percentile(finite_map, 25))
        if map_iqr / max(median_map, 1.0) > 0.2:
            reasons.append("MAP is too unstable for baseline calibration.")

    completeness = min(1.0, len(modalities) / 3.0)
    confidence = float(np.clip(progress * quality_median * completeness, 0.0, 1.0))
    calibrated = not reasons and confidence >= 0.5
    return BaselineState(
        calibrated=calibrated,
        progress=progress,
        confidence=confidence,
        median_hr=median_hr,
        hr_iqr=hr_iqr,
        median_map=median_map,
        median_ppg_amplitude=median_ppg_amplitude,
        rmssd_ms=hrv.get("rmssd_ms"),
        sdnn_ms=hrv.get("sdnn_ms"),
        quality_median=quality_median,
        available_modalities=modalities,
        reasons=tuple(dict.fromkeys(reasons)),
        hr_distribution=hr_distribution,
        quality_distribution=quality_distribution,
    )
