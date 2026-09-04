"""CODEX-101: HYP-01 MIT-BIH abs/rel bradycardia-definition sensitivity scaffold."""

from __future__ import annotations

from pathlib import Path

from t21_engine.evaluation.mitbih_brady_def_sensitivity import (
    run_mitbih_brady_def_sensitivity,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "wfdb_mitdb_synthetic"


def test_hyp01_defaults_to_pi_to_define_without_clinical_cutoffs() -> None:
    report = run_mitbih_brady_def_sensitivity(FIXTURE)
    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["sqi_fail_reason"] is None
    assert report["role_tag"] == "PROXY_ECG_BENCHMARK"
    assert report["hypothesis_id"] == "HYP-01"
    assert report["thresholds"] == {
        "status": "UNAVAILABLE",
        "reason": "PI_TO_DEFINE",
        "absolute_hr_bpm": {"value": "PI_TO_DEFINE", "unit": "bpm"},
        "relative_drop_fraction": {"value": "PI_TO_DEFINE", "unit": "fraction"},
        "note": "No clinical cutoffs hardcoded; sensitivity waits on PI_TO_DEFINE.",
    }
    assert report["fact"]["layer"] == "FACT"
    assert report["interpretation"]["status"] == "UNAVAILABLE"
    assert report["interpretation"]["reason"] == "PI_TO_DEFINE"
    assert report["interpretation"]["abs_vs_rel_concordance"] == {
        "status": "UNAVAILABLE",
        "reason": "PI_TO_DEFINE",
        "value": "PI_TO_DEFINE",
    }
    assert report["hypothesis"]["status"] == "HYPOTHESIS"
    assert report["hypothesis"]["human_review_required"] is True
    assert "pooled_instability_score" not in report


def test_hyp01_engineering_probe_path_marks_non_clinical() -> None:
    report = run_mitbih_brady_def_sensitivity(
        FIXTURE, absolute_hr_bpm=200.0, relative_drop_fraction=0.05
    )
    assert report["status"] == "PASS"
    assert report["interpretation"]["engineering_probe_only"] is True
    assert report["interpretation"]["clinical_cutoff"] == "PI_TO_DEFINE"
    assert report["clinical_validation"] is False


def test_hyp01_missing_sample_fails_closed(tmp_path: Path) -> None:
    report = run_mitbih_brady_def_sensitivity(tmp_path)
    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "MISSING_SAMPLE"


def test_hyp01_propagates_structured_sqi_fail_reason() -> None:
    sqi_fail_reason = {
        "code": "ECG_SQI_UNUSABLE",
        "reason": "Synthetic proxy ECG did not pass its configured SQI gate.",
    }
    report = run_mitbih_brady_def_sensitivity(
        FIXTURE,
        sqi_fail_reason=sqi_fail_reason,
    )

    assert report["sqi_fail_reason"] == sqi_fail_reason
    assert report["clinical_validation"] is False
