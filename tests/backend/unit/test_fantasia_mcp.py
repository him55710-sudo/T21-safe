from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from t21_engine.fantasia_mcp.handlers import (
    MASTER_NOTION_PAGE_ID,
    list_records,
    load_sample,
    run_hrv_proxy_bench,
)
from t21_engine.fantasia_mcp.server import handle_request

FIXTURE = Path(__file__).parents[1] / "fixtures" / "wfdb_fantasia_synthetic"


def _assert_gates(payload: dict[str, object]) -> None:
    assert payload["clinical_validation"] is False
    assert payload["scope"] == "PROXY_HRV_AGE_STABILITY"
    assert payload["not_ds_or_anesthesia"] is True
    assert payload["not_ptt_ppg"] is True
    assert payload["master_verified_proxy"] is True
    assert payload["master_verified_proxy_reference"] == {
        "system": "Notion",
        "page_id": MASTER_NOTION_PAGE_ID,
    }


def _record(sample_count: int = 6000) -> SimpleNamespace:
    ecg = np.zeros(sample_count)
    peak = 50
    index = 0
    intervals = (90, 100, 110, 100)
    while peak < ecg.size:
        ecg[peak] = 10.0
        peak += intervals[index % len(intervals)]
        index += 1
    return SimpleNamespace(fs=100.0, p_signal=ecg[:, None], sig_name=["ECG"])


def test_list_records_verifies_fixture_and_includes_gates() -> None:
    payload = list_records(FIXTURE)

    assert payload["status"] == "PASS"
    assert payload["records"] == [
        {"record": "f1o01", "sha256_verified": True},
        {"record": "synthetic02", "sha256_verified": True},
        {"record": "synthetic03", "sha256_verified": True},
    ]
    _assert_gates(payload)


def test_list_records_fails_closed_on_unmanifested_matrix_record(
    tmp_path: Path,
) -> None:
    for source in FIXTURE.iterdir():
        if source.name != "generate_fixture.py":
            (tmp_path / source.name).write_bytes(source.read_bytes())
    (tmp_path / "extra.hea").write_text(
        "extra 1 100 1\nextra.dat 16 1/mV 16 0 0 0 0 ECG\n"
    )
    (tmp_path / "extra.dat").write_bytes(b"\0\0")

    payload = list_records(tmp_path)

    assert payload["status"] == "FAIL"
    assert payload["failure_reason_code"] == "SHA256_MISMATCH"
    assert payload["record"] == "extra"
    _assert_gates(payload)


def test_list_records_fails_closed_on_missing_manifested_record_file(
    tmp_path: Path,
) -> None:
    for source in FIXTURE.iterdir():
        if source.name not in {"generate_fixture.py", "synthetic03.hea"}:
            (tmp_path / source.name).write_bytes(source.read_bytes())

    payload = list_records(tmp_path)

    assert payload["status"] == "FAIL"
    assert payload["failure_reason_code"] == "MISSING_SAMPLE"
    _assert_gates(payload)


def test_load_sample_is_bounded_and_verified(monkeypatch: pytest.MonkeyPatch) -> None:
    def rdrecord(_name: str, *, sampfrom: int, sampto: int) -> SimpleNamespace:
        assert sampfrom == 0
        return _record(sampto)

    monkeypatch.setitem(sys.modules, "wfdb", SimpleNamespace(rdrecord=rdrecord))

    payload = load_sample(FIXTURE, sample_count=8)

    assert payload["status"] == "PASS"
    assert payload["sample_count"] == 8
    assert payload["sha256_verified"] is True
    assert len(payload["samples"]) == 8
    _assert_gates(payload)


def test_run_bench_reuses_existing_benchmark(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(
        sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: _record())
    )

    payload = run_hrv_proxy_bench(FIXTURE)

    assert payload["status"] == "PASS"
    assert payload["schema_version"] == "fantasia-hrv-age-bench/1.0"
    _assert_gates(payload)


@pytest.mark.parametrize(
    "uri",
    [
        "s3://phi-bucket/fantasia",
        "gs://phi-bucket/fantasia",
        "https://storage.example/phi",
        "http://storage.example/phi",
        "file:///tmp/fantasia",
        "//server/share/fantasia",
    ],
)
def test_all_tools_reject_uri_and_network_paths(uri: str) -> None:
    payloads = [
        list_records(uri),
        load_sample(uri),
        run_hrv_proxy_bench(uri),
    ]

    for payload in payloads:
        assert payload["status"] == "REJECTED"
        assert payload["failure_reason_code"] == "NON_LOCAL_URI_REJECTED"
        _assert_gates(payload)


def test_stdio_tool_call_wraps_json_payload() -> None:
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "list_records",
                "arguments": {"sample_root": str(FIXTURE)},
            },
        }
    )

    assert response is not None
    assert response["id"] == 7
    result = response["result"]
    assert result["isError"] is False
    decoded = json.loads(result["content"][0]["text"])
    _assert_gates(decoded)


def test_hrv_proxy_bench_age_fields_stay_pi_to_define(monkeypatch: pytest.MonkeyPatch) -> None:
    """CODEX-043: age stays PI_TO_DEFINE; no clinical age claim in MCP payload."""
    monkeypatch.setitem(
        sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: _record())
    )

    payload = run_hrv_proxy_bench(FIXTURE)
    assert payload["status"] == "PASS"
    assert payload["clinical_validation"] is False
    assert "clinical_age_effect" in payload["prohibited_claims"]
    assert frozenset(payload["prohibited_claims"]) >= frozenset(
        {"DS", "anesthesia", "clinical_age_effect", "PTT_PPG"}
    )
    assert payload["aggregate"]["age_stability_status"] == "UNAVAILABLE"
    records = payload["records"]
    assert isinstance(records, list) and records
    age = records[0]["age_stability"]
    assert age["reason"] == "PI_TO_DEFINE"
    assert age["age_metadata_available"] is False
    assert age["age_stability_metrics"] is None
    blob = json.dumps(payload).lower()
    assert "years old" not in blob
    assert "clinical age" not in blob
    _assert_gates(payload)


def test_stdio_hrv_proxy_bench_age_pi_to_define(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(
        sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: _record())
    )
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 43,
            "method": "tools/call",
            "params": {
                "name": "run_hrv_proxy_bench",
                "arguments": {"sample_root": str(FIXTURE)},
            },
        }
    )
    assert response is not None
    decoded = json.loads(response["result"]["content"][0]["text"])
    assert decoded["clinical_validation"] is False
    assert decoded["records"][0]["age_stability"]["reason"] == "PI_TO_DEFINE"
    assert decoded["records"][0]["age_stability"]["age_metadata_available"] is False
    assert decoded["aggregate"]["age_stability_status"] == "UNAVAILABLE"
    _assert_gates(decoded)
