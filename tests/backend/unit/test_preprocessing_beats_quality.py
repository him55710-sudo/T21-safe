from __future__ import annotations

import numpy as np
import pytest
from t21_engine.beats.pulse_peak import detect_pulse_peaks
from t21_engine.beats.rpeak import detect_r_peaks
from t21_engine.preprocessing.filters import bandpass_filter, preprocess_abp
from t21_engine.preprocessing.resampling import resample_signal
from t21_engine.quality.abp_sqi import compute_abp_sqi
from t21_engine.quality.ecg_sqi import compute_ecg_sqi
from t21_engine.quality.ppg_sqi import compute_ppg_sqi


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
