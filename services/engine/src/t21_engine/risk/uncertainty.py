"""Minimal uncertainty and out-of-distribution gate."""

from __future__ import annotations

from dataclasses import dataclass

from t21_engine.config import QualityConfig
from t21_engine.types import BaselineState, FeatureSet, PipelineMode, QualityResult


@dataclass(frozen=True, slots=True)
class UncertaintyDecision:
    valid: bool
    confidence_multiplier: float
    reasons: tuple[str, ...]


def assess_uncertainty(
    quality: QualityResult,
    baseline: BaselineState,
    features: FeatureSet,
    mode: PipelineMode,
    quality_config: QualityConfig,
    *,
    age_group: str = "unknown",
) -> UncertaintyDecision:
    invalid_reasons: list[str] = []
    caution_reasons: list[str] = []
    multiplier = 1.0
    if not quality.usable:
        invalid_reasons.extend(quality.reasons or ("Signal quality is insufficient.",))
    if not baseline.calibrated:
        invalid_reasons.extend(baseline.reasons or ("Baseline calibration is incomplete.",))
    if baseline.median_hr is not None and not 35.0 <= baseline.median_hr <= 180.0:
        invalid_reasons.append("Baseline heart rate is outside the supported research range.")
    if baseline.median_map is not None and not 40.0 <= baseline.median_map <= 140.0:
        invalid_reasons.append("Baseline MAP is outside the supported research range.")
    if features.valid_beat_count < quality_config.minimum_valid_beats:
        invalid_reasons.append("The feature window contains too few valid beats.")

    ranges = {
        "current_hr_bpm": (20.0, 220.0),
        "current_map_mm_hg": (20.0, 200.0),
        "current_spo2_pct": (50.0, 100.0),
        "delta_hr_pct": (-80.0, 100.0),
        "delta_map_pct": (-80.0, 100.0),
    }
    for name, (minimum, maximum) in ranges.items():
        value = features.values.get(name)
        if value is not None and not minimum <= value <= maximum:
            invalid_reasons.append(f"Feature {name} is outside the supported research range.")
    modalities = features.values.get("available_modalities")
    if modalities is not None and modalities < 3:
        multiplier *= 0.75
        caution_reasons.append("Fewer than three modalities are available; confidence is reduced.")
    if age_group not in {"adult", "unknown"}:
        multiplier *= 0.6
        caution_reasons.append(
            "This age group is not supported by the generic adult validation data."
        )
    if mode is PipelineMode.DS_HYPOTHESIS_MODE:
        multiplier *= 0.5
        caution_reasons.append("Down syndrome population performance has not been validated.")
    reasons = tuple(dict.fromkeys([*invalid_reasons, *caution_reasons]))
    return UncertaintyDecision(not invalid_reasons, multiplier, reasons)
