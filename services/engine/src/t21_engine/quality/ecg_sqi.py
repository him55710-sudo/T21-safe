"""ECG signal quality index in the closed interval 0..1."""

from __future__ import annotations

import numpy as np

from t21_engine.beats.rpeak import detect_r_peaks
from t21_engine.preprocessing.artifact_detection import summarize_artifacts
from t21_engine.types import FloatArray


def compute_ecg_sqi(ecg: FloatArray, sample_rate_hz: float) -> float:
    samples = np.asarray(ecg, dtype=np.float64)
    artifacts = summarize_artifacts(samples)
    beats = detect_r_peaks(samples, sample_rate_hz)
    duration = samples.size / sample_rate_hz if sample_rate_hz > 0 else 0.0
    expected_minimum = max(1.0, duration * 0.4)
    count_score = min(1.0, beats.indices.size / expected_minimum)
    artifact_penalty = (
        0.45 * artifacts.missing_fraction
        + 0.25 * min(1.0, artifacts.flatline_fraction * 3.0)
        + 0.15 * min(1.0, artifacts.clipping_fraction * 5.0)
        + 0.15 * min(1.0, artifacts.abrupt_change_fraction * 10.0)
    )
    score = 0.65 * beats.confidence + 0.35 * count_score
    return float(np.clip(score * (1.0 - artifact_penalty), 0.0, 1.0))
