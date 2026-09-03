"""Read-only handlers for PROXY HYP-01/03/07 MCP tools."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from t21_engine.evaluation.proxy_hyp_bench_runner import (
    BENCH_COMMITS,
    SCHEMA_VERSION,
    run_proxy_hyp_benches,
)

_URI_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")

BENCH_CATALOG = (
    {
        "codex_id": "CODEX-101",
        "hypothesis_id": "HYP-01",
        "role_tag": "PROXY_ECG_BENCHMARK",
        "module": "t21_engine.evaluation.mitbih_brady_def_sensitivity",
        "landing_commit": BENCH_COMMITS["CODEX-101"],
    },
    {
        "codex_id": "CODEX-102",
        "hypothesis_id": "HYP-03",
        "role_tag": "PROXY_HRV_AGE_STABILITY",
        "module": "t21_engine.evaluation.fantasia_short_window_hrv_lfhf",
        "landing_commit": BENCH_COMMITS["CODEX-102"],
        "lf_hf_primary": False,
        "rq004_status": "HYPOTHESIS",
    },
    {
        "codex_id": "CODEX-103",
        "hypothesis_id": "HYP-07",
        "role_tag": "PROXY_HRV_AGE_STABILITY",
        "module": "t21_engine.evaluation.fantasia_age_band_hrv_stability",
        "landing_commit": BENCH_COMMITS["CODEX-103"],
    },
)


def _gates() -> dict[str, Any]:
    return {
        "clinical_validation": False,
        "research_use_only": True,
        "network_required": False,
        "proxy_not_ds": True,
        "lf_hf_primary": False,
        "rq004_status": "HYPOTHESIS",
        "pooled_instability_score": None,
        "prohibited": [
            "BIDMC",
            "Airway",
            "Driver-map",
            "HYP-06b",
            "PHI",
            "dosing",
            "closed_loop",
            "waveforms_in_mcp_export",
        ],
    }


def _result(status: str, **payload: Any) -> dict[str, Any]:
    return {"status": status, **_gates(), **payload}


def _reject_non_local(path: str | None) -> dict[str, Any] | None:
    if path is None:
        return None
    raw = str(path)
    if _URI_PATTERN.match(raw) or raw.startswith(("//", "\\\\")):
        return _result(
            "REJECTED",
            failure_reason_code="NON_LOCAL_URI_REJECTED",
            message="Only local filesystem paths are accepted.",
        )
    return None


def list_proxy_hyp_benches() -> dict[str, Any]:
    """List locked PROXY HYP benches (read-only catalog; no network)."""
    return _result(
        "PASS",
        schema_version=SCHEMA_VERSION,
        benches=list(BENCH_CATALOG),
        methods_critique_pointer="docs/founder/PROXY_HYP_RESULTS_KR.md",
        note="Fixture-only MIT-BIH+Fantasia; thresholds PI_TO_DEFINE; HUMAN_REVIEW_REQUIRED labels.",
    )


def run_proxy_hyp_benches_tool(
    mitbih_root: str | None = None,
    fantasia_root: str | None = None,
    output_dir: str | None = None,
) -> dict[str, Any]:
    """Run HYP-01/03/07 local benches; optional local output_dir for JSON/MD tables."""
    for candidate in (mitbih_root, fantasia_root, output_dir):
        rejected = _reject_non_local(candidate)
        if rejected is not None:
            return rejected
    if output_dir is not None:
        try:
            out = Path(output_dir).expanduser().resolve()
            out.mkdir(parents=True, exist_ok=True)
        except (OSError, RuntimeError):
            return _result("FAIL", failure_reason_code="INVALID_OUTPUT_DIR")
    else:
        out = None
    report = run_proxy_hyp_benches(
        mitbih_root=mitbih_root,
        fantasia_root=fantasia_root,
        output_dir=out,
    )
    # Strip bulky nested reports for MCP default payload; keep summary + gates.
    slim = {k: v for k, v in report.items() if k != "reports"}
    slim["full_reports_omitted"] = True
    slim["note"] = (
        "Nested per-bench reports omitted from MCP payload; write output_dir for full JSON."
    )
    return slim


__all__ = ["list_proxy_hyp_benches", "run_proxy_hyp_benches_tool", "BENCH_CATALOG"]
