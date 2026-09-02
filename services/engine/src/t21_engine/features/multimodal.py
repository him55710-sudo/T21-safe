"""Features that require two or more synchronized modalities."""

from __future__ import annotations

from t21_engine.beats.alignment import pulse_arrival_time_ms
from t21_engine.types import BeatSeries


def extract_multimodal_features(
    r_peaks: BeatSeries,
    pulse_peaks: BeatSeries,
    *,
    current_hr: float | None,
    current_map: float | None,
    ppg_amplitude_delta_pct: float | None,
    delta_hr_pct: float | None,
    delta_map_pct: float | None,
    available_modalities: int,
) -> dict[str, float | None]:
    ptt_ms, alignment_confidence = pulse_arrival_time_ms(r_peaks, pulse_peaks)
    return {
        "ptt_ms": ptt_ms,
        "ecg_ppg_alignment_confidence": alignment_confidence,
        "hr_ppg_divergence": (
            delta_hr_pct - ppg_amplitude_delta_pct
            if delta_hr_pct is not None and ppg_amplitude_delta_pct is not None
            else None
        ),
        "hr_map_divergence": (
            delta_hr_pct - delta_map_pct
            if delta_hr_pct is not None and delta_map_pct is not None
            else None
        ),
        "combined_trend_consistency": (
            1.0
            if delta_hr_pct is not None
            and delta_map_pct is not None
            and delta_hr_pct < 0.0
            and delta_map_pct < 0.0
            else 0.0
            if delta_hr_pct is not None and delta_map_pct is not None
            else None
        ),
        "available_modalities": float(available_modalities),
        "current_hr_bpm_for_alignment": current_hr,
        "current_map_mm_hg_for_alignment": current_map,
    }
