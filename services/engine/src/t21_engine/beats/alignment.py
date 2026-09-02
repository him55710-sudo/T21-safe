"""Cross-modal beat timing helpers."""

from __future__ import annotations

import numpy as np

from t21_engine.types import BeatSeries


def pulse_arrival_time_ms(
    r_peaks: BeatSeries,
    pulse_peaks: BeatSeries,
    *,
    minimum_seconds: float = 0.05,
    maximum_seconds: float = 0.5,
) -> tuple[float | None, float]:
    arrivals: list[float] = []
    for r_time in r_peaks.times_s:
        candidates = pulse_peaks.times_s[pulse_peaks.times_s > r_time]
        if not candidates.size:
            continue
        delay = float(candidates[0] - r_time)
        if minimum_seconds <= delay <= maximum_seconds:
            arrivals.append(delay)
    if not arrivals:
        return None, 0.0
    paired_fraction = len(arrivals) / max(1, r_peaks.times_s.size)
    confidence = float(
        np.clip(
            paired_fraction * min(r_peaks.confidence, pulse_peaks.confidence),
            0.0,
            1.0,
        )
    )
    return float(np.median(arrivals) * 1000.0), confidence
