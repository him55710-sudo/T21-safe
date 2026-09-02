"""Arterial pressure waveform quality index."""

from __future__ import annotations

import numpy as np

from t21_engine.beats.pulse_peak import detect_pulse_peaks
from t21_engine.preprocessing.artifact_detection import summarize_artifacts
from t21_engine.types import FloatArray


def compute_abp_sqi(abp: FloatArray, sample_rate_hz: float) -> float:
    samples = np.asarray(abp, dtype=np.float64)
    artifacts = summarize_artifacts(samples, plausible_range=(20.0, 300.0))
    beats = detect_pulse_peaks(samples, sample_rate_hz)
    finite = samples[np.isfinite(samples)]
    pulse_span = (
        float(np.nanpercentile(finite, 95) - np.nanpercentile(finite, 5)) if finite.size else 0.0
    )
    pressure_score = float(np.clip(pulse_span / 25.0, 0.0, 1.0))
    penalty = (
        0.35 * artifacts.missing_fraction
        + 0.25 * min(1.0, artifacts.flatline_fraction * 3.0)
        + 0.15 * min(1.0, artifacts.abrupt_change_fraction * 10.0)
        + 0.25 * artifacts.implausible_fraction
    )
    return float(
        np.clip(
            (0.55 * beats.confidence + 0.45 * pressure_score) * (1.0 - penalty),
            0.0,
            1.0,
        )
    )
