from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from t21_engine.evaluation.fantasia_short_window_hrv_lfhf import (
    run_fantasia_short_window_hrv_lfhf,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "wfdb_fantasia_synthetic"


def _record() -> SimpleNamespace:
    fs = 100.0
    ecg = np.zeros(6000)
    peak = 50
    index = 0
    intervals = (90, 100, 110, 100)
    while peak < ecg.size:
        ecg[peak] = 10.0
        peak += intervals[index % len(intervals)]
        index += 1
    return SimpleNamespace(fs=fs, p_signal=ecg[:, None])


def test_short_window_negative_control_layers(monkeypatch) -> None:
    monkeypatch.setitem(
        sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: _record())
    )

    report = run_fantasia_short_window_hrv_lfhf(FIXTURE)

    assert report["schema_version"] == "fantasia-short-window-hrv-lfhf/1.0"
    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["lf_hf_primary"] is False
    assert report["neg_control_qa"] is True
    assert report["role_tag"] == "PROXY_HRV_AGE_STABILITY"
    assert report["hypothesis_id"] == "HYP-03"
    assert report["hypothesis"]["rq004_status"] == "HYPOTHESIS"
    assert report["hypothesis"]["human_review_required"] is True
    fact = report["fact"]
    assert fact["layer"] == "FACT"
    assert fact["lf_hf_task_force_gate_full"]["withheld"] is True
    assert fact["lf_hf_task_force_gate_full"]["primary"] is False
    assert fact["reference_5min_window"]["status"] == "UNAVAILABLE"
    assert len(fact["ultra_short_windows"]) >= 1
    for window in fact["ultra_short_windows"]:
        assert window["lf_hf_task_force_gate"]["withheld"] is True
        assert window["lf_hf_task_force_gate"]["primary"] is False
    interpretation = report["interpretation"]
    assert interpretation["layer"] == "INTERPRETATION"
    assert interpretation["engineering_probe_only"] is True
    assert interpretation["lf_hf_primary"] is False
    assert interpretation["neg_control_qa"] is True
    assert "RQ004_as_FACT" in report["prohibited_claims"]
    json.dumps(report)


def test_checksum_mismatch_fails_closed(tmp_path: Path) -> None:
    for source in FIXTURE.iterdir():
        if source.name != "generate_fixture.py":
            (tmp_path / source.name).write_bytes(source.read_bytes())
    (tmp_path / "f1o01.dat").write_bytes(b"changed")

    report = run_fantasia_short_window_hrv_lfhf(tmp_path)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "SHA256_MISMATCH"
    assert report["clinical_validation"] is False
    assert report["lf_hf_primary"] is False
    assert report["neg_control_qa"] is True
    assert report["fact"] is None


def test_insufficient_rr_fails_closed(monkeypatch) -> None:
    short = SimpleNamespace(fs=100.0, p_signal=np.zeros((100, 1)))
    monkeypatch.setitem(
        sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: short)
    )

    report = run_fantasia_short_window_hrv_lfhf(FIXTURE)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "INSUFFICIENT_RR_INTERVALS"
    assert report["clinical_validation"] is False
    assert report["lf_hf_primary"] is False
    assert report["neg_control_qa"] is True
