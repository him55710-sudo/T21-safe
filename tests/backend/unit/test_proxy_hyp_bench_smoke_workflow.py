"""CODEX-105: workflow pins for PROXY HYP runner smoke."""

from __future__ import annotations

from pathlib import Path

WORKFLOW = (
    Path(__file__).resolve().parents[3]
    / ".github"
    / "workflows"
    / "proxy-hyp-bench-smoke.yml"
)


def test_proxy_hyp_bench_smoke_workflow_exists_and_gates() -> None:
    assert WORKFLOW.is_file()
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "CODEX-105" in text
    assert "clinical_validation=false" in text or "clinical_validation" in text
    assert "no BIDMC" in text or "BIDMC" in text
    assert "run_proxy_hyp_benches.sh" in text
    assert "test_proxy_hyp_bench_runner.py" in text
    assert "wfdb_bidmc" not in text
