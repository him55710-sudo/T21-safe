from __future__ import annotations

import numpy as np
import pytest
from t21_engine.beats.pulse_peak import detect_pulse_peaks
from t21_engine.beats.rpeak import detect_r_peaks
from t21_engine.config import QualityConfig
from t21_engine.preprocessing.filters import bandpass_filter, preprocess_abp
from t21_engine.preprocessing.resampling import resample_signal
from t21_engine.quality.abp_sqi import compute_abp_sqi
from t21_engine.quality.ecg_sqi import compute_ecg_sqi
from t21_engine.quality.ppg_sqi import compute_ppg_sqi
from t21_engine.streaming.shadow_capture import build_shadow_capture
from t21_engine.types import FeatureSet, ShadowSafetyControls


def test_ecg_bandpass_preserves_passband_and_does_not_mutate() -> None:
    fs = 100.0
    timestamps = np.arange(0.0, 10.0, 1.0 / fs)
    passband = np.sin(2.0 * np.pi * 2.0 * timestamps)
    high_frequency = 0.8 * np.sin(2.0 * np.pi * 40.0 * timestamps)
    raw = (passband + high_frequency).astype(np.float64)
    before = raw.copy()

    filtered = bandpass_filter(raw, fs, 0.5, 20.0)

    assert np.array_equal(raw, before)
    assert np.corrcoef(filtered, passband)[0, 1] > 0.95
    assert np.std(filtered - passband) < np.std(raw - passband)


def test_r_peak_detection_finds_regular_spikes() -> None:
    fs = 100.0
    ecg = np.zeros(10 * int(fs), dtype=np.float64)
    expected = np.arange(50, ecg.size, 100)
    ecg[expected] = 1.0
    ecg += 0.01 * np.sin(np.arange(ecg.size) / 5.0)

    beats = detect_r_peaks(ecg, fs)

    assert abs(beats.indices.size - expected.size) <= 1
    assert beats.confidence > 0.6


def test_ppg_peak_detection_finds_pulses() -> None:
    fs = 100.0
    timestamps = np.arange(0.0, 10.0, 1.0 / fs)
    phase = np.mod(timestamps, 1.0)
    ppg = np.exp(-5.0 * phase) * (1.0 - np.exp(-35.0 * phase))

    beats = detect_pulse_peaks(ppg.astype(np.float64), fs)

    assert 8 <= beats.indices.size <= 11
    assert beats.confidence > 0.6


def test_sqi_penalizes_flatline_and_signal_loss() -> None:
    fs = 100.0
    timestamps = np.arange(0.0, 12.0, 1.0 / fs)
    phase = np.mod(timestamps, 1.0)
    clean_ecg = 1.2 * np.exp(-0.5 * ((phase - 0.1) / 0.02) ** 2)
    clean_ppg = np.exp(-5.0 * phase) * (1.0 - np.exp(-35.0 * phase))
    lost_ppg = clean_ppg.copy()
    lost_ppg[200:] = np.nan

    assert compute_ecg_sqi(clean_ecg.astype(np.float64), fs) > compute_ecg_sqi(
        np.zeros_like(clean_ecg), fs
    )
    assert compute_ppg_sqi(clean_ppg.astype(np.float64), fs) > compute_ppg_sqi(
        lost_ppg.astype(np.float64), fs
    )


def test_abp_sqi_penalizes_implausible_flatline() -> None:
    fs = 100.0
    timestamps = np.arange(0.0, 10.0, 1.0 / fs)
    phase = np.mod(timestamps, 1.0)
    pulse = np.exp(-5.0 * phase) * (1.0 - np.exp(-35.0 * phase))
    clean_abp = 70.0 + 45.0 * pulse
    implausible = np.full_like(clean_abp, 400.0)

    assert compute_abp_sqi(clean_abp.astype(np.float64), fs) > compute_abp_sqi(
        implausible.astype(np.float64), fs
    )


def test_abp_preprocessing_preserves_pressure_baseline_and_reduces_noise() -> None:
    fs = 100.0
    timestamps = np.arange(0.0, 10.0, 1.0 / fs)
    pulse = 15.0 * np.sin(2.0 * np.pi * 1.2 * timestamps)
    high_frequency_noise = 3.0 * np.sin(2.0 * np.pi * 35.0 * timestamps)
    raw = (82.0 + pulse + high_frequency_noise).astype(np.float64)
    before = raw.copy()

    filtered = preprocess_abp(raw, fs)

    assert np.array_equal(raw, before)
    assert np.nanmedian(filtered) == pytest.approx(82.0, abs=1.0)
    assert np.std(filtered - (82.0 + pulse)) < np.std(high_frequency_noise)


def test_resampling_keeps_latest_duplicate_and_preserves_missing_tails() -> None:
    timestamps = np.asarray([0.0, 1.0, 1.0, 2.0, 3.0], dtype=np.float64)
    values = np.asarray([np.nan, 1.0, 2.0, 3.0, np.nan], dtype=np.float64)

    target, resampled = resample_signal(timestamps, values, 1.0)

    assert np.array_equal(target, np.asarray([0.0, 1.0, 2.0, 3.0]))
    assert np.isnan(resampled[0])
    assert resampled[1] == 2.0
    assert resampled[2] == 3.0
    assert np.isnan(resampled[3])


def test_shadow_capture_reuses_quality_artifacts_and_dual_reports_changes() -> None:
    features = FeatureSet(
        values={
            "delta_hr_bpm": -6.0,
            "delta_hr_pct": -8.0,
            "delta_map_mm_hg": -5.0,
            "delta_map_pct": -6.0,
            "ppg_amplitude_delta": -0.2,
            "ppg_amp_delta_pct": -10.0,
            "rmssd_ms": 20.0,
            "sdnn_ms": 30.0,
            "lf_power": None,
            "hf_power": None,
            "lf_hf_ratio": None,
        },
        window_seconds=30,
        valid_beat_count=12,
    )
    capture = build_shadow_capture(
        session_id="shadow-synthetic-001",
        event_id="shadow-synthetic-001-1000",
        subject_id="synthetic-001",
        is_synthetic=True,
        baseline_calibrated=True,
        quality_config=QualityConfig(minimum_sqi=0.0),
        feature_windows={30: features},
        signals={"ecg_ii": np.asarray([0.0, 1.0, 0.0], dtype=np.float64)},
        sample_rates_hz={"ecg_ii": 1.0},
    )

    assert capture["controls"] == {
        "actuation": False,
        "dosing": False,
        "closed_loop": False,
        "drug_advice": False,
        "emr_write": False,
    }
    assert capture["session"]["synthetic_label"] == "SYNTHETIC_DATA"
    assert capture["quality_gate"]["ecg_sqi"] is not None
    assert capture["quality_gate"]["ppg_sqi"] is None
    assert capture["quality_gate"]["abp_sqi"] is None
    assert capture["quality_gate"]["unavailable_signals"] == ["ppg", "abp"]
    assert capture["quality_gate"]["gap_fraction"] == 0.0
    assert capture["quality_gate"]["timestamp_synchronized"] is True
    assert capture["quality_gate"]["baseline_bypass"] is False
    assert (
        capture["quality_gate"]["threshold_status"]
        == "ENGINEERING_HYPOTHESIS_OR_PI_TO_DEFINE"
    )
    assert set(capture["quality_gate"]["artifacts"]["ecg_ii"]) == {
        "missing_fraction",
        "flatline_fraction",
        "clipping_fraction",
        "abrupt_change_fraction",
        "implausible_fraction",
    }
    window = capture["feature_windows"][0]
    assert window["absolute_change"]["hr_bpm"] == -6.0
    assert window["relative_change_pct"]["hr"] == -8.0
    assert window["evidence_status"] == "RESEARCH_HYPOTHESIS"
    assert window["clinical_decision_thresholds"] == "PI_TO_DEFINE"
    assert any("limited utility" in item for item in window["limitations"])


def test_shadow_controls_reject_action_capabilities() -> None:
    with pytest.raises(ValueError, match="rejects actuation"):
        ShadowSafetyControls(actuation=True)


def test_shadow_capture_withholds_baseline_changes_without_calibration() -> None:
    features = FeatureSet(
        values={"delta_hr_bpm": -6.0, "delta_hr_pct": -8.0},
        window_seconds=30,
        valid_beat_count=12,
    )
    capture = build_shadow_capture(
        session_id="shadow-synthetic-001",
        event_id="shadow-synthetic-001-1000",
        subject_id="synthetic-001",
        is_synthetic=True,
        baseline_calibrated=False,
        quality_config=QualityConfig(minimum_sqi=0.0),
        feature_windows={30: features},
        signals={"ecg_ii": np.asarray([0.0, 1.0, 0.0], dtype=np.float64)},
        sample_rates_hz={"ecg_ii": 1.0},
    )

    assert capture["quality_gate"]["usable"] is False
    assert capture["feature_windows"][0]["absolute_change"]["hr_bpm"] is None
    assert capture["feature_windows"][0]["relative_change_pct"]["hr"] is None
