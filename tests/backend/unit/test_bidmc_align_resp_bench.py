from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from t21_engine.evaluation.bidmc_align_resp_bench import run_bidmc_align_resp_bench

FIXTURE = Path(__file__).parents[1] / "fixtures" / "wfdb_bidmc_synthetic"


def _synthetic_record(*, names: list[str] | None = None) -> SimpleNamespace:
    fs = 25.0
    size = 1500
    sample = np.arange(size)
    ecg = np.zeros(size)
    ppg = np.zeros(size)
    for peak in range(12, size, 25):
        ecg[peak] = 10.0
        ppg[peak + 5] = 8.0
    resp = np.sin(2.0 * np.pi * sample / 125.0)
    return SimpleNamespace(
        fs=fs,
        p_signal=np.column_stack((ecg, ppg, resp)),
        sig_name=names or ["II", "PLETH", "RESP"],
        skew=[0, 0, 0],
    )


@pytest.fixture
def mock_wfdb(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(
        sys.modules,
        "wfdb",
        SimpleNamespace(rdrecord=lambda _name: _synthetic_record()),
    )


def test_fixture_reports_alignment_and_respiration_rate_error(mock_wfdb: None) -> None:
    report = run_bidmc_align_resp_bench(FIXTURE)

    assert report["schema_version"] == "bidmc-align-resp-bench/1.0"
    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["proxy_multisignal_only"] is True
    assert report["network_required"] is False
    row = report["records"][0]
    assert row["alignment"]["channels"] == ["ecg", "ppg", "resp"]
    assert row["alignment"]["max_start_skew_ms"] == 0.0
    assert row["alignment"]["max_end_skew_ms"] == 0.0
    assert row["alignment"]["ecg_ppg_median_pulse_arrival_ms"] == pytest.approx(200.0)
    assert row["respiration_rate"]["reference_source"] == "SYNTHETIC_JSON_EQUIVALENT"
    assert row["respiration_rate"]["reference_rate_bpm"] == 12.0
    assert row["respiration_rate"]["detected_rate_bpm"] == 12.0
    assert row["respiration_rate"]["absolute_error_bpm"] == 0.0
    json.dumps(report)


def test_missing_required_channel_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    record = _synthetic_record(names=["II", "PLETH", "unknown"])
    monkeypatch.setitem(sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: record))

    report = run_bidmc_align_resp_bench(FIXTURE)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "MISSING_REQUIRED_CHANNEL"
    assert report["aggregate"] is None


def test_declared_wfdb_channel_skew_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    record = _synthetic_record()
    record.skew = [0, 2, 0]
    monkeypatch.setitem(sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: record))

    report = run_bidmc_align_resp_bench(FIXTURE)

    alignment = report["records"][0]["alignment"]
    assert alignment["declared_channel_offset_ms"] == {
        "ecg": 0.0,
        "ppg": 80.0,
        "resp": 0.0,
    }
    assert alignment["max_start_skew_ms"] == 80.0


def test_missing_respiration_reference_fails_before_waveform_load(tmp_path: Path) -> None:
    (tmp_path / "bidmc01.hea").write_text("synthetic placeholder", encoding="utf-8")

    report = run_bidmc_align_resp_bench(tmp_path)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "MISSING_RESP_REFERENCE"
    assert report["aggregate"] is None


def test_unlabeled_synthetic_reference_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "bidmc01.hea").write_text("synthetic placeholder", encoding="utf-8")
    (tmp_path / "bidmc01.synthetic-resp-reference.json").write_text(
        json.dumps({"breath_samples": [1, 2]}), encoding="utf-8"
    )

    report = run_bidmc_align_resp_bench(tmp_path)

    assert report["status"] == "FAIL"
    assert report["failure_reason_code"] == "RESP_REFERENCE_LOAD_FAILURE"
