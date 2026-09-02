from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from t21_engine.evaluation.mitbih_beat_bench import match_beats, run_mitbih_beat_bench

FIXTURE = Path(__file__).parents[1] / "fixtures" / "wfdb_mitdb_synthetic"


def test_match_beats_reports_matches_misses_false_and_nearest_timing() -> None:
    matches, missed, false = match_beats(
        np.asarray([100, 200, 300]), np.asarray([97, 207, 450]), tolerance_samples=10
    )

    assert matches == [(100, 97), (200, 207)]
    assert missed == [300]
    assert false == [450]


def test_fixture_bench_reports_machine_readable_counts_and_timing(monkeypatch) -> None:
    ecg = np.zeros(20, dtype=np.float64)
    ecg[[3, 8, 13, 18]] = 10.0

    def rdrecord(record_name: str) -> SimpleNamespace:
        assert Path(record_name).name == "100"
        return SimpleNamespace(fs=10.0, p_signal=ecg[:, None])

    monkeypatch.setitem(sys.modules, "wfdb", SimpleNamespace(rdrecord=rdrecord))
    report = run_mitbih_beat_bench(FIXTURE)

    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["proxy_ecg_only"] is True
    assert report["network_required"] is False
    assert report["dataset"] == {
        "catalog_case_id": "wfdb:mitdb-100",
        "dataset_name": "MIT-BIH Arrhythmia Database",
        "dataset_version": "1.0.0",
        "master_verified_proxy": True,
    }
    assert report["records"] == [
        {
            "record": "100",
            "status": "PASS",
            "failure_reason_code": None,
            "annotation_source": "SYNTHETIC_JSON_EQUIVALENT",
            "sample_rate_hz": 10.0,
            "annotated_beats": 3,
            "detected_beats": 4,
            "matched_beats": 3,
            "missed_beats_fn": 0,
            "false_beats_fp": 1,
            "mean_abs_error_ms": 33.333333333333336,
            "median_abs_error_ms": 0.0,
            "max_abs_error_ms": 100.0,
        }
    ]
    assert report["aggregate"]["missed_beats_fn"] == 0
    assert report["aggregate"]["false_beats_fp"] == 1
    json.dumps(report)


def test_missing_annotation_fails_closed_before_waveform_load(tmp_path: Path) -> None:
    (tmp_path / "100.hea").write_text("synthetic placeholder", encoding="utf-8")

    report = run_mitbih_beat_bench(tmp_path)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "MISSING_ANNOTATIONS"
    assert report["aggregate"] is None
    assert report["records"][0]["failure_reason_code"] == "MISSING_ANNOTATIONS"
