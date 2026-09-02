from __future__ import annotations

from dataclasses import replace

from t21_engine.adapters.synthetic_hospital_case import build_synthetic_hospital_case
from t21_engine.evaluation.baseline_window_sensitivity import (
    run_baseline_window_sensitivity,
)


def test_reports_both_synthetic_preinduction_windows_and_deltas() -> None:
    report = run_baseline_window_sensitivity()

    assert report["status"] == "PASS"
    assert report["failure_reason_code"] is None
    assert report["windows_seconds"] == [180, 300]
    assert report["clinical_validation"] is False
    assert report["synthetic_only"] is True
    assert report["clinical_window_choice"] == "PI_TO_DEFINE"
    assert report["safety"] == {
        "dosing": False,
        "alerts": False,
        "clinical_decision": False,
    }
    assert {row["metric"] for row in report["rows"]} == {
        "hr_bpm",
        "map_or_abp",
        "spo2_pct",
    }
    for row in report["rows"]:
        assert row["window_180_value"] is not None
        assert row["window_300_value"] is not None
        assert row["absolute_delta_300_minus_180"] is not None
        assert row["relative_delta_pct_300_minus_180"] is not None


def test_fails_closed_when_preinduction_window_is_too_short() -> None:
    case = build_synthetic_hospital_case(duration_s=1000.0)

    report = run_baseline_window_sensitivity(case)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "INSUFFICIENT_PREINDUCTION_WINDOW"
    assert report["rows"] == []
    assert report["clinical_validation"] is False


def test_fails_closed_when_required_channel_is_missing() -> None:
    case = build_synthetic_hospital_case(duration_s=2000.0)
    channels = dict(case.channels)
    del channels["spo2_pct"]

    report = run_baseline_window_sensitivity(replace(case, channels=channels))

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "MISSING_REQUIRED_CHANNEL"
    assert report["rows"] == []
