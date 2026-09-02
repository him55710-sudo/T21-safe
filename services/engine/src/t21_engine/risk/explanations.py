"""Deterministic, non-prescriptive feature explanations."""

from __future__ import annotations


def explain_features(features: dict[str, float | None]) -> tuple[str, ...]:
    reasons: list[str] = []
    delta_hr = features.get("delta_hr_pct")
    map_slope = features.get("map_slope_mm_hg_min")
    delta_map = features.get("delta_map_pct")
    ppg_delta = features.get("ppg_amp_delta_pct")
    spo2 = features.get("current_spo2_pct")
    if delta_hr is not None and delta_hr <= -10.0:
        reasons.append("Heart rate is declining from the patient-specific baseline.")
    if (map_slope is not None and map_slope <= -2.0) or (
        delta_map is not None and delta_map <= -10.0
    ):
        reasons.append("MAP trend is decreasing.")
    if ppg_delta is not None and ppg_delta <= -15.0:
        reasons.append("PPG amplitude is decreasing.")
    if spo2 is not None and spo2 < 92.0:
        reasons.append("The oxygen saturation trend is below the research threshold.")
    if not reasons:
        reasons.append("Signals remain near the patient-specific research baseline.")
    return tuple(reasons)
