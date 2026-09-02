"""Transparent weighted Research Instability Index v0.1.

This number is not a calibrated probability and is not a clinical alarm.
"""

from __future__ import annotations

import numpy as np

from t21_engine.config import PipelineConfig
from t21_engine.risk.explanations import explain_features
from t21_engine.risk.uncertainty import assess_uncertainty
from t21_engine.types import (
    BaselineState,
    FeatureSet,
    PipelineMode,
    QualityResult,
    RiskLevel,
    RiskResult,
)


def _decline_component(value: float | None, full_scale_decline_pct: float, weight: float) -> float:
    if value is None or value >= 0.0:
        return 0.0
    return weight * float(np.clip(-value / full_scale_decline_pct, 0.0, 1.0))


def _level(score: float, config: PipelineConfig) -> RiskLevel:
    if score >= config.risk.high_threshold:
        return RiskLevel.HIGH
    if score >= config.risk.elevated_threshold:
        return RiskLevel.ELEVATED
    if score >= config.risk.watch_threshold:
        return RiskLevel.WATCH
    if score < 10.0:
        return RiskLevel.BASELINE
    return RiskLevel.STABLE


def compute_research_instability_index(
    features: FeatureSet,
    quality: QualityResult,
    baseline: BaselineState,
    mode: PipelineMode,
    config: PipelineConfig,
    *,
    data_source: str,
    age_group: str = "unknown",
) -> RiskResult:
    uncertainty = assess_uncertainty(
        quality, baseline, features, mode, config.quality, age_group=age_group
    )
    if not uncertainty.valid:
        reasons = uncertainty.reasons or ("Signal quality is insufficient; index withheld.",)
        return RiskResult(
            score=None,
            level=RiskLevel.INVALID,
            valid=False,
            confidence=0.0,
            observation_context_seconds=config.risk.observation_context_seconds,
            reasons=reasons,
            model_version=config.risk.model_version,
            data_source=data_source,
        )

    values = features.values
    score = 0.0
    risk_config = config.risk
    score += _decline_component(
        values.get("delta_hr_pct"),
        risk_config.relative_hr_decline_full_scale_pct,
        risk_config.relative_hr_decline_weight,
    )
    score += _decline_component(
        values.get("delta_map_pct"),
        risk_config.relative_map_decline_full_scale_pct,
        risk_config.relative_map_decline_weight,
    )
    score += _decline_component(
        values.get("ppg_amp_delta_pct"),
        risk_config.relative_ppg_amplitude_decline_full_scale_pct,
        risk_config.relative_ppg_amplitude_decline_weight,
    )
    hr_slope = values.get("hr_slope_bpm_min")
    map_slope = values.get("map_slope_mm_hg_min")
    score += risk_config.hr_slope_weight * float(
        np.clip(-(hr_slope or 0.0) / risk_config.hr_slope_full_scale_bpm_min, 0.0, 1.0)
    )
    score += risk_config.map_slope_weight * float(
        np.clip(
            -(map_slope or 0.0) / risk_config.map_slope_full_scale_mm_hg_min,
            0.0,
            1.0,
        )
    )
    spo2 = values.get("current_spo2_pct")
    if spo2 is not None:
        score += risk_config.low_spo2_weight * float(
            np.clip(
                (risk_config.spo2_reference_pct - spo2) / risk_config.spo2_full_scale_decline_pct,
                0.0,
                1.0,
            )
        )
    score = float(np.clip(score, 0.0, 100.0))

    sqi_values = [
        value for value in (quality.ecg_sqi, quality.ppg_sqi, quality.abp_sqi) if value is not None
    ]
    sqi_confidence = float(np.median(sqi_values)) if sqi_values else 0.0
    beat_confidence = features.values.get("beat_detection_confidence") or 0.0
    confidence = float(
        np.clip(
            baseline.confidence
            * sqi_confidence
            * beat_confidence
            * uncertainty.confidence_multiplier,
            0.0,
            1.0,
        )
    )
    reasons = tuple(dict.fromkeys([*explain_features(values), *uncertainty.reasons]))
    return RiskResult(
        score=score,
        level=_level(score, config),
        valid=True,
        confidence=confidence,
        observation_context_seconds=config.risk.observation_context_seconds,
        reasons=reasons,
        model_version=config.risk.model_version,
        data_source=data_source,
    )
