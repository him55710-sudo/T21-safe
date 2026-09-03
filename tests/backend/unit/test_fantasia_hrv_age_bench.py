from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from t21_engine.evaluation.fantasia_hrv_age_bench import run_fantasia_hrv_age_bench

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


def test_fixture_reports_reproducibility_and_withholds_age_claims(monkeypatch) -> None:
    monkeypatch.setitem(
        sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: _record())
    )

    report = run_fantasia_hrv_age_bench(FIXTURE)

    assert report["schema_version"] == "fantasia-hrv-age-bench/1.0"
    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["operational_proxy_ok"] is True
    assert report["dataset"]["catalog_case_id"] == "wfdb:fantasia-f1o01"
    row = report["records"][0]
    assert row["rr_interval_count"] >= 12
    assert row["deterministic_recompute_exact"] is True
    assert row["split_window_absolute_delta"]["rmssd_ms"] is not None
    assert row["age_stability"] == {
        "status": "UNAVAILABLE",
        "reason": "PI_TO_DEFINE",
        "age_metadata_available": False,
        "age_stability_metrics": None,
    }
    json.dumps(report)


def test_checksum_mismatch_fails_closed(tmp_path: Path) -> None:
    for source in FIXTURE.iterdir():
        if source.name != "generate_fixture.py":
            (tmp_path / source.name).write_bytes(source.read_bytes())
    (tmp_path / "f1o01.dat").write_bytes(b"changed")

    report = run_fantasia_hrv_age_bench(tmp_path)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "SHA256_MISMATCH"
    assert report["aggregate"] is None


def test_insufficient_rr_intervals_fails_closed(monkeypatch) -> None:
    short = SimpleNamespace(fs=100.0, p_signal=np.zeros((100, 1)))
    monkeypatch.setitem(
        sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: short)
    )

    report = run_fantasia_hrv_age_bench(FIXTURE)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "INSUFFICIENT_RR_INTERVALS"


def test_catalog_labels_operational_proxy() -> None:
    from t21_engine.adapters.wfdb_adapter import WFDB_CATALOG

    entry = WFDB_CATALOG["wfdb:fantasia-f1o01"]
    assert entry.public_bench_enabled is True
    assert "Open Data Commons Attribution" in entry.license_notes


def test_fixture_matrix_withholds_all_age_metadata() -> None:
    manifest = json.loads(
        (FIXTURE / "sha256-manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["records"] == ["f1o01", "synthetic02", "synthetic03"]
    for record in manifest["records"]:
        metadata = json.loads(
            (FIXTURE / f"{record}.synthetic-metadata.json").read_text(encoding="utf-8")
        )
        assert metadata["synthetic"] is True
        assert metadata["age_metadata_available"] is False
        assert metadata["age_band"] == "PI_TO_DEFINE"
        assert metadata["age_group"] == "PI_TO_DEFINE"


@pytest.mark.parametrize("record", ["synthetic02", "synthetic03"])
def test_benchmark_handles_each_additional_synthetic_record(
    monkeypatch, record: str
) -> None:
    monkeypatch.setitem(
        sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: _record())
    )

    report = run_fantasia_hrv_age_bench(FIXTURE, record=record)

    assert report["status"] == "PASS"
    assert report["records"][0]["record"] == record
    assert report["records"][0]["age_stability"]["reason"] == "PI_TO_DEFINE"
