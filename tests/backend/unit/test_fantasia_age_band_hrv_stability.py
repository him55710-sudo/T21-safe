from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from t21_engine.evaluation.fantasia_age_band_hrv_stability import (
    run_fantasia_age_band_hrv_stability,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "wfdb_fantasia_synthetic"


def _record(seed: int = 0) -> SimpleNamespace:
    fs = 100.0
    ecg = np.zeros(6000)
    peak = 50 + seed
    index = 0
    intervals = (90 + seed % 3, 100, 110, 100)
    while peak < ecg.size:
        ecg[peak] = 10.0
        peak += intervals[index % len(intervals)]
        index += 1
    return SimpleNamespace(fs=fs, p_signal=ecg[:, None])


def test_multi_record_engine_qa_layers(monkeypatch) -> None:
    waves = {
        "f1o01": _record(0),
        "synthetic02": _record(1),
        "synthetic03": _record(2),
    }

    def _rdrecord(name: str):
        key = Path(name).name
        return waves[key]

    monkeypatch.setitem(sys.modules, "wfdb", SimpleNamespace(rdrecord=_rdrecord))

    report = run_fantasia_age_band_hrv_stability(FIXTURE)

    assert report["schema_version"] == "fantasia-age-band-hrv-stability/1.0"
    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["age_unavailable"] is True
    assert report["lf_hf_as_balance_index"] is False
    assert report["role_tag"] == "PROXY_HRV_AGE_STABILITY"
    assert report["hypothesis_id"] == "HYP-07"
    assert report["hypothesis"]["human_review_required"] is True
    assert "RQ003_causation" in report["prohibited_claims"]
    assert report["fact"]["layer"] == "FACT"
    assert report["fact"]["records_evaluated"] == 3
    assert report["fact"]["preferred_feature_domain"] == "time_domain"
    assert len(report["records"]) == 3
    assert all(row["status"] == "PASS" for row in report["records"])
    assert all(row["deterministic_recompute_exact"] for row in report["records"])
    interp = report["interpretation"]
    assert interp["engineering_probe_only"] is True
    assert interp["engine_qa"]["all_deterministic_recompute_exact"] is True
    assert interp["age_stability"]["status"] == "UNAVAILABLE"
    assert interp["age_stability"]["reason"] == "PI_TO_DEFINE"
    json.dumps(report)


def test_checksum_mismatch_fails_closed(tmp_path: Path) -> None:
    for source in FIXTURE.iterdir():
        if source.name != "generate_fixture.py":
            (tmp_path / source.name).write_bytes(source.read_bytes())
    (tmp_path / "f1o01.dat").write_bytes(b"changed")

    report = run_fantasia_age_band_hrv_stability(tmp_path)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "SHA256_MISMATCH"
    assert report["clinical_validation"] is False
    assert report["age_unavailable"] is True
    assert report["fact"] is None


def test_insufficient_rr_fails_closed(monkeypatch) -> None:
    short = SimpleNamespace(fs=100.0, p_signal=np.zeros((100, 1)))
    monkeypatch.setitem(
        sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: short)
    )

    report = run_fantasia_age_band_hrv_stability(FIXTURE)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "INSUFFICIENT_RR_INTERVALS"
    assert report["clinical_validation"] is False
    assert report["age_unavailable"] is True
