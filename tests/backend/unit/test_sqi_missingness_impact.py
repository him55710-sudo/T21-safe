from __future__ import annotations

import pytest
from t21_engine.evaluation.sqi_missingness_impact import run_sqi_missingness_impact


def test_clean_synthetic_baseline_has_usable_windows() -> None:
    report = run_sqi_missingness_impact(gap_fractions=(0.0,), noise_std=(0.0,))

    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["clinical_threshold_interpretation"] == "PI_TO_DEFINE"
    assert report["minimum_sqi_source"] == "QualityConfig.minimum_sqi"
    row = report["rows"][0]
    assert row["scenario"] == "clean"
    assert row["candidate_windows"] == 4
    assert row["available_analysis_windows"] == 4
    assert row["qc_pass_rate"] == 1.0


def test_controlled_gaps_lower_usable_window_count() -> None:
    report = run_sqi_missingness_impact(gap_fractions=(0.0, 0.25), noise_std=(0.0,))

    clean, gapped = report["rows"]
    assert gapped["available_analysis_windows"] < clean["available_analysis_windows"]
    assert gapped["qc_pass_rate"] < clean["qc_pass_rate"]
    assert gapped["mean_ecg_sqi"] < clean["mean_ecg_sqi"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"gap_fractions": (-0.1,)},
        {"gap_fractions": (1.1,)},
        {"noise_std": (float("nan"),)},
        {"window_seconds": 0.0},
    ],
)
def test_invalid_parameters_fail_closed(kwargs: dict[str, object]) -> None:
    report = run_sqi_missingness_impact(**kwargs)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "INVALID_PARAMETERS"
    assert report["rows"] == []
    assert report["clinical_validation"] is False
