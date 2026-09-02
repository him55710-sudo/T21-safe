from __future__ import annotations

import numpy as np
import pytest
from t21_engine.adapters.synthetic_adapter import SyntheticAdapter
from t21_engine.baseline.calibration import calibrate_baseline
from t21_engine.beats.rpeak import detect_r_peaks
from t21_engine.config import PipelineConfig
from t21_engine.features import extract_features
from t21_engine.features.hrv import rr_intervals_ms, time_domain_hrv
from t21_engine.quality.quality_gate import evaluate_quality
from t21_engine.risk.deterministic_index import compute_research_instability_index
from t21_engine.risk.explanations import explain_features
from t21_engine.types import (
    BaselineState,
    FeatureSet,
    PipelineMode,
    QualityResult,
    RiskLevel,
)


@pytest.mark.asyncio
async def test_baseline_calibration_and_features_use_patient_baseline() -> None:
    config = PipelineConfig(baseline_seconds=5)
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    quality = evaluate_quality(batch.signals, batch.sample_rates_hz, config.quality)
    baseline = calibrate_baseline(
        batch.timestamps_s,
        batch.signals,
        100.0,
        quality,
        baseline_seconds=5,
    )
    features = extract_features(
        batch.timestamps_s, batch.signals, baseline, 100.0, window_seconds=5
    )

    assert baseline.calibrated
    assert baseline.median_hr == pytest.approx(72.0, abs=0.2)
    assert baseline.hr_distribution is not None
    assert baseline.quality_distribution is not None
    assert features.values["delta_hr_pct"] == pytest.approx(0.0, abs=0.5)
    assert features.valid_beat_count >= 4


@pytest.mark.asyncio
async def test_baseline_rejects_sparse_timestamp_coverage() -> None:
    config = PipelineConfig(baseline_seconds=5)
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=5
    )
    keep = (batch.timestamps_s < 1.0) | (batch.timestamps_s >= 4.0)
    timestamps = batch.timestamps_s[keep]
    signals = {name: values[keep] for name, values in batch.signals.items()}
    quality = evaluate_quality(signals, batch.sample_rates_hz, config.quality)

    baseline = calibrate_baseline(
        timestamps,
        signals,
        100.0,
        quality,
        baseline_seconds=5,
    )

    assert baseline.calibrated is False
    assert any("coverage" in reason for reason in baseline.reasons)


def test_hrv_time_domain_metrics() -> None:
    fs = 100.0
    timestamps = np.arange(0.0, 10.0, 1.0 / fs)
    phase = np.mod(timestamps, 1.0)
    ecg = np.exp(-0.5 * ((phase - 0.1) / 0.02) ** 2)
    beats = detect_r_peaks(ecg.astype(np.float64), fs)
    metrics = time_domain_hrv(rr_intervals_ms(beats))

    assert metrics["rr_mean_ms"] == pytest.approx(1000.0, abs=5.0)
    assert metrics["rmssd_ms"] == pytest.approx(0.0, abs=5.0)
    assert metrics["sdnn_ms"] == pytest.approx(0.0, abs=5.0)


def test_risk_is_withheld_when_baseline_or_quality_is_invalid() -> None:
    config = PipelineConfig()
    features = FeatureSet(
        values={"current_hr_bpm": 72.0, "available_modalities": 3.0},
        window_seconds=60,
        valid_beat_count=10,
    )
    quality = QualityResult(
        ecg_sqi=0.2,
        ppg_sqi=0.1,
        abp_sqi=0.2,
        usable=False,
        reasons=("Signal quality is insufficient.",),
    )
    baseline = BaselineState(False, 0.5, 0.0, reasons=("Baseline incomplete.",))

    result = compute_research_instability_index(
        features,
        quality,
        baseline,
        PipelineMode.GENERIC_VALIDATION_MODE,
        config,
        data_source="test",
    )

    assert result.valid is False
    assert result.score is None
    assert result.level is RiskLevel.INVALID


def test_baseline_out_of_distribution_withholds_risk() -> None:
    config = PipelineConfig()
    features = FeatureSet(
        values={
            "current_hr_bpm": 200.0,
            "current_map_mm_hg": 80.0,
            "beat_detection_confidence": 0.9,
            "available_modalities": 3.0,
        },
        window_seconds=60,
        valid_beat_count=10,
    )
    quality = QualityResult(0.9, 0.9, 0.9, True)
    baseline = BaselineState(
        True,
        1.0,
        0.9,
        median_hr=200.0,
        median_map=80.0,
    )

    result = compute_research_instability_index(
        features,
        quality,
        baseline,
        PipelineMode.GENERIC_VALIDATION_MODE,
        config,
        data_source="test",
    )

    assert result.valid is False
    assert result.score is None
    assert any("Baseline heart rate" in reason for reason in result.reasons)


def test_feature_out_of_distribution_withholds_risk() -> None:
    config = PipelineConfig()
    features = FeatureSet(
        values={
            "current_hr_bpm": 250.0,
            "current_map_mm_hg": 80.0,
            "beat_detection_confidence": 0.9,
            "available_modalities": 3.0,
        },
        window_seconds=60,
        valid_beat_count=10,
    )
    quality = QualityResult(0.9, 0.9, 0.9, True)
    baseline = BaselineState(
        True,
        1.0,
        0.9,
        median_hr=72.0,
        median_map=80.0,
    )

    result = compute_research_instability_index(
        features,
        quality,
        baseline,
        PipelineMode.GENERIC_VALIDATION_MODE,
        config,
        data_source="test",
    )

    assert result.valid is False
    assert result.score is None
    assert any("Feature current_hr_bpm" in reason for reason in result.reasons)


def test_insufficient_valid_beats_withholds_risk() -> None:
    config = PipelineConfig()
    features = FeatureSet(
        values={
            "current_hr_bpm": 72.0,
            "current_map_mm_hg": 80.0,
            "beat_detection_confidence": 0.0,
            "available_modalities": 3.0,
        },
        window_seconds=60,
        valid_beat_count=config.quality.minimum_valid_beats - 1,
    )
    quality = QualityResult(0.9, 0.9, 0.9, True)
    baseline = BaselineState(
        True,
        1.0,
        0.9,
        median_hr=72.0,
        median_map=80.0,
    )

    result = compute_research_instability_index(
        features,
        quality,
        baseline,
        PipelineMode.GENERIC_VALIDATION_MODE,
        config,
        data_source="test",
    )

    assert result.valid is False
    assert result.score is None
    assert any("too few valid beats" in reason for reason in result.reasons)


def test_ds_hypothesis_mode_uses_same_index_but_reduces_confidence() -> None:
    config = PipelineConfig()
    features = FeatureSet(
        values={
            "current_hr_bpm": 60.0,
            "current_map_mm_hg": 70.0,
            "delta_hr_pct": -15.0,
            "delta_map_pct": -12.0,
            "beat_detection_confidence": 0.9,
            "available_modalities": 3.0,
        },
        window_seconds=60,
        valid_beat_count=10,
    )
    quality = QualityResult(0.9, 0.9, 0.9, True)
    baseline = BaselineState(
        True,
        1.0,
        0.9,
        median_hr=72.0,
        median_map=82.0,
    )

    generic = compute_research_instability_index(
        features,
        quality,
        baseline,
        PipelineMode.GENERIC_VALIDATION_MODE,
        config,
        data_source="test",
    )
    ds_hypothesis = compute_research_instability_index(
        features,
        quality,
        baseline,
        PipelineMode.DS_HYPOTHESIS_MODE,
        config,
        data_source="test",
    )

    assert ds_hypothesis.score == generic.score
    assert ds_hypothesis.confidence == pytest.approx(generic.confidence * 0.5)
    assert any("Down syndrome" in reason for reason in ds_hypothesis.reasons)


def test_explanations_are_non_prescriptive() -> None:
    reasons = explain_features(
        {
            "delta_hr_pct": -22.0,
            "map_slope_mm_hg_min": -5.0,
            "delta_map_pct": -18.0,
            "ppg_amp_delta_pct": -30.0,
            "current_spo2_pct": 90.0,
        }
    )

    combined = " ".join(reasons).lower()
    assert "heart rate" in combined
    assert "map" in combined
    assert "ppg" in combined
    assert "dose" not in combined
    assert "administer" not in combined
