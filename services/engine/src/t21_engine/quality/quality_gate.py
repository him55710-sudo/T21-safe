"""Central quality gate that explicitly withholds unsafe index output."""

from __future__ import annotations

import numpy as np

from t21_engine.config import QualityConfig
from t21_engine.quality.abp_sqi import compute_abp_sqi
from t21_engine.quality.ecg_sqi import compute_ecg_sqi
from t21_engine.quality.ppg_sqi import compute_ppg_sqi
from t21_engine.types import QualityResult


def evaluate_quality(
    signals: dict[str, np.ndarray],
    sample_rates_hz: dict[str, float],
    config: QualityConfig,
    *,
    out_of_order_count: int = 0,
    timestamp_synchronized: bool = True,
    valid_beat_count: int | None = None,
) -> QualityResult:
    ecg_sqi = (
        compute_ecg_sqi(signals["ecg_ii"], sample_rates_hz["ecg_ii"])
        if "ecg_ii" in signals
        else None
    )
    ppg_sqi = compute_ppg_sqi(signals["ppg"], sample_rates_hz["ppg"]) if "ppg" in signals else None
    abp_sqi = compute_abp_sqi(signals["abp"], sample_rates_hz["abp"]) if "abp" in signals else None
    unavailable = tuple(name for name in ("ecg_ii", "ppg", "abp") if name not in signals)
    gap_fraction = max(
        (float(np.mean(~np.isfinite(values))) for values in signals.values() if values.size),
        default=1.0,
    )
    reasons: list[str] = []
    beat_source_usable = any(
        value is not None and value >= config.minimum_sqi for value in (ecg_sqi, ppg_sqi)
    )
    pressure_usable = (abp_sqi is not None and abp_sqi >= config.minimum_sqi) or (
        "map_mm_hg" in signals
        and float(np.mean(np.isfinite(signals["map_mm_hg"]))) >= 1.0 - config.maximum_gap_fraction
    )
    if not beat_source_usable:
        reasons.append("No ECG or PPG beat source meets the SQI threshold.")
    if not pressure_usable:
        reasons.append("No usable arterial pressure waveform or MAP trend is available.")
    if gap_fraction > config.maximum_gap_fraction:
        reasons.append("The feature window contains too much missing data.")
    if out_of_order_count > 0 or not timestamp_synchronized:
        reasons.append("Timestamp synchronization failed.")
    if valid_beat_count is not None and valid_beat_count < config.minimum_valid_beats:
        reasons.append("The feature window contains too few valid beats.")
    return QualityResult(
        ecg_sqi=ecg_sqi,
        ppg_sqi=ppg_sqi,
        abp_sqi=abp_sqi,
        usable=not reasons,
        unavailable_signals=unavailable,
        reasons=tuple(reasons),
        gap_fraction=gap_fraction,
        timestamp_synchronized=timestamp_synchronized and out_of_order_count == 0,
    )
