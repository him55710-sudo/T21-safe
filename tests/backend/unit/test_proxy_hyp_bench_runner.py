"""CODEX-104: PROXY HYP-01/03/07 one-command runner."""

from __future__ import annotations

import json
from pathlib import Path

from t21_engine.evaluation.proxy_hyp_bench_runner import (
    SCHEMA_VERSION,
    run_proxy_hyp_benches,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def test_run_proxy_hyp_benches_emits_layers_and_artifacts(tmp_path: Path) -> None:
    out = tmp_path / "out"
    report = run_proxy_hyp_benches(output_dir=out)

    assert report["schema_version"] == SCHEMA_VERSION
    assert report["clinical_fact"] is False
    assert (
        report["auditor_dual_gate"]["hypotheses"]["HYP-01"]["auditor_label"]
        == "PARTIALLY_SUPPORTED"
    )
    assert (
        report["auditor_dual_gate"]["hypotheses"]["HYP-01"]["claim_label"]
        == "PARTIALLY_SUPPORTED"
    )
    assert report["auditor_dual_gate"]["airway_bidmc_do_not_run"] is True
    assert all(row.get("auditor_label") for row in report["summary_rows"])
    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["network_required"] is False
    assert report["pooled_instability_score"] is None
    assert "BIDMC" in report["prohibited"]
    assert len(report["summary_rows"]) == 3
    assert {
        row["hypothesis_id"]: row["claim_label"] for row in report["summary_rows"]
    } == {
        "HYP-01": "PARTIALLY_SUPPORTED",
        "HYP-03": "STRETCH/QA",
        "HYP-07": "STRETCH/QA",
    }
    for row in report["summary_rows"]:
        assert row["status"] == "PASS"
        assert row["clinical_validation"] is False
        assert row["human_review_required"] is True
        assert row["fact_layer"] == "FACT"
        assert row["hypothesis_status"] == "HYPOTHESIS"
        assert "sqi_fail_reason" in row
    assert (out / "proxy-hyp-bench-report.json").is_file()
    md = (out / "proxy-hyp-bench-results.md").read_text(encoding="utf-8")
    assert "HYP-01" in md and "HYP-03" in md and "HYP-07" in md
    assert "clinical_validation" in md
    assert "PI_TO_DEFINE" in md
    assert "claim_label" in md
    assert "SQI fail reason" in md
    assert "PARTIALLY_SUPPORTED" in md
    assert "STRETCH/QA" in md
    loaded = json.loads(
        (out / "proxy-hyp-bench-report.json").read_text(encoding="utf-8")
    )
    assert loaded["schema_version"] == "proxy-hyp-bench-runner/1.2"
    assert loaded["status"] == "PASS"
    assert all(
        {"claim_label", "sqi_fail_reason"} <= row.keys()
        for row in loaded["summary_rows"]
    )
    assert {
        row["hypothesis_id"]: row["claim_label"]
        for row in loaded["summary_rows"]
    } == {
        "HYP-01": "PARTIALLY_SUPPORTED",
        "HYP-03": "STRETCH/QA",
        "HYP-07": "STRETCH/QA",
    }


def test_default_fixture_roots_are_local() -> None:
    report = run_proxy_hyp_benches()
    roots = report["fixture_roots"]
    assert "wfdb_mitdb_synthetic" in roots["mitbih"]
    assert "wfdb_fantasia_synthetic" in roots["fantasia"]
    assert "bidmc" not in roots["mitbih"].lower()
    assert "bidmc" not in roots["fantasia"].lower()
