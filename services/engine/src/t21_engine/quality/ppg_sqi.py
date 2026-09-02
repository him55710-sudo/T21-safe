"""PPG quality based on pulse regularity, availability, and artifact candidates."""

from __future__ import annotations

import numpy as np

from t21_engine.beats.pulse_peak import detect_pulse_peaks
from t21_engine.preprocessing.artifact_detection import summarize_artifacts
from t21_engine.types import FloatArray


def compute_ppg_sqi(ppg: FloatArray, sample_rate_hz: float) -> float:
    samples = np.asarray(ppg, dtype=np.float64)
    artifacts = summarize_artifacts(samples)
    beats = detect_pulse_peaks(samples, sample_rate_hz)
    duration = samples.size / sample_rate_hz if sample_rate_hz > 0 else 0.0
    count_score = min(1.0, beats.indices.size / max(1.0, duration * 0.4))
    penalty = (
        0.5 * artifacts.missing_fraction
        + 0.25 * min(1.0, artifacts.flatline_fraction * 3.0)
        + 0.1 * min(1.0, artifacts.clipping_fraction * 5.0)
        + 0.15 * min(1.0, artifacts.abrupt_change_fraction * 10.0)
    )
    return float(np.clip((0.7 * beats.confidence + 0.3 * count_score) * (1.0 - penalty), 0.0, 1.0))
