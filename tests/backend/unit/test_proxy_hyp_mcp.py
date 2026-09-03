"""CODEX-109: PROXY HYP MCP handlers."""

from __future__ import annotations

from pathlib import Path

from t21_engine.proxy_hyp_mcp.handlers import (
    list_proxy_hyp_benches,
    run_proxy_hyp_benches_tool,
)


def test_list_proxy_hyp_benches_gates() -> None:
    payload = list_proxy_hyp_benches()
    assert payload["status"] == "PASS"
    assert payload["clinical_validation"] is False
    assert payload["lf_hf_primary"] is False
    assert payload["rq004_status"] == "HYPOTHESIS"
    assert "BIDMC" in payload["prohibited"]
    assert len(payload["benches"]) == 3
    ids = {row["hypothesis_id"] for row in payload["benches"]}
    assert ids == {"HYP-01", "HYP-03", "HYP-07"}


def test_run_proxy_hyp_benches_fixture_only(tmp_path: Path) -> None:
    out = tmp_path / "out"
    payload = run_proxy_hyp_benches_tool(output_dir=str(out))
    assert payload["status"] == "PASS"
    assert payload["clinical_validation"] is False
    assert payload["network_required"] is False
    assert payload.get("full_reports_omitted") is True
    assert "reports" not in payload
    assert (out / "proxy-hyp-bench-report.json").is_file()


def test_run_rejects_non_local_uri() -> None:
    payload = run_proxy_hyp_benches_tool(mitbih_root="https://example.com/data")
    assert payload["status"] == "REJECTED"
    assert payload["failure_reason_code"] == "NON_LOCAL_URI_REJECTED"
