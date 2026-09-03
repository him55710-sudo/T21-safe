from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from t21_engine.research_node_mcp import handlers
from t21_engine.research_node_mcp.handlers import (
    export_shadow_summary,
    list_demo_presets,
    list_local_shadow_exports,
    run_bidmc_align_resp_bench,
    run_mitbih_beat_bench,
    run_synthetic_demo,
    run_time_align_qc,
)
from t21_engine.research_node_mcp.server import handle_request


def _assert_gates(payload: dict[str, object]) -> None:
    assert payload["clinical_validation"] is False
    assert payload["synthetic_only"] is True
    assert payload["contains_phi"] is False
    assert payload["mode"] == "OBSERVE_ONLY_SHADOW"
    assert payload["fantasia_required"] is False
    assert payload["vitaldb_allowed"] is False
    controls = payload["controls"]
    assert isinstance(controls, dict)
    assert controls["dosing"] is False
    assert controls["alerts"] is False


def test_time_align_qc_happy_path_includes_safety_gates() -> None:
    payload = run_time_align_qc()

    assert payload["status"] == "PASS"
    assert payload["mission"] == "CODEX-021"
    assert payload["alignment_qc"]["status"] == "PASS"
    _assert_gates(payload)


@pytest.mark.parametrize(
    ("output_dir", "reason"),
    [
        ("s3://research-bucket/export", "NON_LOCAL_URI_REJECTED"),
        ("https://example.invalid/export", "NON_LOCAL_URI_REJECTED"),
        ("file:///tmp/export", "NON_LOCAL_URI_REJECTED"),
        ("//server/share/export", "NON_LOCAL_URI_REJECTED"),
        ("/tmp/phi-export", "PHI_PATH_REJECTED"),
        ("/tmp/patient_data/export", "PHI_PATH_REJECTED"),
    ],
)
def test_demo_fails_closed_on_cloud_network_and_phi_paths(
    output_dir: str, reason: str
) -> None:
    payload = run_synthetic_demo(output_dir=output_dir)

    assert payload["status"] == "REJECTED"
    assert payload["failure_reason_code"] == reason
    _assert_gates(payload)


def test_demo_reuses_local_shadow_jsonl_and_export_manifest(tmp_path: Path) -> None:
    payload = run_synthetic_demo(output_dir=tmp_path)

    assert payload["status"] == "PASS"
    assert payload["mission"] == "CODEX-021"
    records = [
        json.loads(line)
        for line in (tmp_path / "shadow-capture.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert records[-1]["content_scope"] == "SHADOW_CAPTURE_METADATA_ONLY"
    assert records[-1]["includes_phi"] is False
    assert records[-1]["includes_waveforms"] is False
    _assert_gates(payload)

    listed = list_local_shadow_exports(directory=str(tmp_path))
    assert listed["status"] == "PASS"
    assert listed["exports"] == [
        {
            "filename": "shadow-capture.jsonl",
            "size_bytes": (tmp_path / "shadow-capture.jsonl").stat().st_size,
            "summarizable": True,
        }
    ]
    summary = export_shadow_summary(path=str(tmp_path / "shadow-capture.jsonl"))
    assert summary["status"] == "PASS"
    assert summary["record_count"] == summary["capture_count"] + 1
    assert summary["manifest_count"] == 1
    assert summary["capture_schema_version"] == "shadow-capture/1.0"
    _assert_gates(summary)


@pytest.mark.parametrize(
    ("tool", "argument"),
    [
        (list_local_shadow_exports, {"directory": "s3://bucket/exports"}),
        (export_shadow_summary, {"path": "https://example.invalid/export.jsonl"}),
    ],
)
def test_shadow_export_read_tools_reject_cloud_uris(
    tool: Callable[..., dict[str, object]], argument: dict[str, str]
) -> None:
    payload = tool(**argument)
    assert payload["status"] == "REJECTED"
    assert payload["failure_reason_code"] == "NON_LOCAL_URI_REJECTED"
    _assert_gates(payload)


def test_shadow_summary_fails_closed_on_unversioned_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "legacy.jsonl"
    path.write_text('{"mode":"OBSERVE_ONLY_SHADOW"}\n', encoding="utf-8")
    payload = export_shadow_summary(path=str(path))
    assert payload["status"] == "FAIL_CLOSED"
    assert payload["failure_reason_code"] == "INVALID_SHADOW_JSONL"
    _assert_gates(payload)


def test_stdio_handler_wraps_happy_payload() -> None:
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 21,
            "method": "tools/call",
            "params": {"name": "run_time_align_qc", "arguments": {}},
        }
    )

    assert response is not None
    assert response["id"] == 21
    result = response["result"]
    assert result["isError"] is False
    _assert_gates(json.loads(result["content"][0]["text"]))


@pytest.mark.parametrize(
    ("runner", "evaluation_name", "scope", "schema_version"),
    [
        (
            run_mitbih_beat_bench,
            "evaluate_mitbih_beat_bench",
            "MITBIH_BEAT_PROXY",
            "mitbih-beat-bench/1.0",
        ),
        (
            run_bidmc_align_resp_bench,
            "evaluate_bidmc_align_resp_bench",
            "BIDMC_ALIGN_RESP_PROXY",
            "bidmc-align-resp-bench/1.0",
        ),
    ],
)
def test_public_proxy_handlers_reuse_existing_benches_and_add_banners(
    monkeypatch: pytest.MonkeyPatch,
    runner: Callable[..., dict[str, object]],
    evaluation_name: str,
    scope: str,
    schema_version: str,
) -> None:
    expected = {
        "schema_version": schema_version,
        "status": "PASS",
        "clinical_validation": False,
        "dataset": {"master_verified_proxy": True},
        "records": [{"annotation_source": "SYNTHETIC_JSON_EQUIVALENT"}],
        "aggregate": {"records_evaluated": 1},
    }
    monkeypatch.setattr(handlers, evaluation_name, lambda **_kwargs: expected)

    payload = runner()

    assert payload["status"] == "PASS"
    assert payload["scope"] == scope
    assert payload["mission"] == "CODEX-026"
    assert payload["read_only"] is True
    assert payload["clinical_validation"] is False
    assert payload["dataset"] == {"master_verified_proxy": True}
    assert payload["master_verified_proxy"] is True
    assert "PROXY / ENGINEERING ONLY" in str(payload["proxy_banner"])
    assert "no DS or clinical claims" in str(payload["proxy_banner"])
    assert payload["network_required"] is False
    assert payload["vitaldb_allowed"] is False


def test_mitbih_proxy_handler_fails_closed_on_invalid_match_window() -> None:
    payload = run_mitbih_beat_bench(match_window_ms=float("nan"))

    assert payload["status"] == "FAIL_CLOSED"
    assert payload["failure_reason_code"] == "INVALID_PARAMETERS"
    assert payload["clinical_validation"] is False
    assert "PROXY" in str(payload["proxy_banner"])


@pytest.mark.parametrize(
    ("runner_name", "evaluation_name", "schema_version", "extra"),
    [
        (
            "run_sqi_missingness_impact",
            "evaluate_sqi_missingness_impact",
            "sqi-missingness-impact/1.0",
            {"clinical_threshold_interpretation": "PI_TO_DEFINE"},
        ),
        (
            "run_baseline_window_sensitivity",
            "evaluate_baseline_window_sensitivity",
            "baseline-window-sensitivity/1.0",
            {"clinical_window_choice": "PI_TO_DEFINE", "windows_seconds": [180, 300]},
        ),
    ],
)
def test_evaluation_handlers_reuse_modules_and_add_gates(
    monkeypatch: pytest.MonkeyPatch,
    runner_name: str,
    evaluation_name: str,
    schema_version: str,
    extra: dict[str, object],
) -> None:
    expected = {
        "schema_version": schema_version,
        "status": "PASS",
        "synthetic_only": True,
        "clinical_validation": False,
        "rows": [{"engineering_value": 1.0}],
        **extra,
    }
    monkeypatch.setattr(handlers, evaluation_name, lambda **_kwargs: expected)

    payload = getattr(handlers, runner_name)()

    assert payload["rows"] == expected["rows"]
    assert payload["mission"] == "CODEX-023"
    assert "PI_TO_DEFINE" in payload["pi_to_define_banner"]
    _assert_gates(payload)


@pytest.mark.parametrize(
    ("name", "arguments"),
    [
        ("run_sqi_missingness_impact", {"gap_fractions": ["invalid"]}),
        ("run_sqi_missingness_impact", {"noise_std": []}),
        ("run_baseline_window_sensitivity", {"sample_rate_hz": 0}),
        ("run_baseline_window_sensitivity", {"seed": True}),
    ],
)
def test_evaluation_tools_fail_closed_on_invalid_parameters(
    name: str, arguments: dict[str, object]
) -> None:
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 23,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
    )

    assert response is not None
    result = response["result"]
    payload = json.loads(result["content"][0]["text"])
    assert result["isError"] is True
    assert payload["status"] in {"FAIL", "FAIL_CLOSED"}
    assert payload["failure_reason_code"] == "INVALID_PARAMETERS"
    assert payload["rows"] == []
    assert "PI_TO_DEFINE" in payload["pi_to_define_banner"]
    _assert_gates(payload)


def test_list_demo_presets_read_only_defaults() -> None:
    payload = list_demo_presets()
    assert payload["status"] == "PASS"
    assert payload["mission"] == "CODEX-042"
    assert payload["schema_version"] == "demo-presets/1.0"
    assert payload["clinical_validation"] is False
    presets = payload["presets"]
    assert isinstance(presets, list) and presets
    default = presets[0]
    assert default["id"] == "default"
    assert default["duration_seconds"] == 12.0
    assert default["baseline_seconds"] == 3
    assert default["seed"] == 20250321
    assert default["clinical_validation"] is False
    _assert_gates(payload)
