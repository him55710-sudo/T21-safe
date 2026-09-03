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
    assert payload["records"] == [{"record": "f1o01", "sha256_verified": True}]
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
    monkeypatch.setitem(sys.modules, "wfdb", SimpleNamespace(rdrecord=lambda _name: _record()))

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
            "params": {"name": "list_records", "arguments": {"sample_root": str(FIXTURE)}},
        }
    )

    assert response is not None
    assert response["id"] == 7
    result = response["result"]
    assert result["isError"] is False
    decoded = json.loads(result["content"][0]["text"])
    _assert_gates(decoded)
