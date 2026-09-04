"""CODEX-104: one-command PROXY runner for HYP-01 / HYP-03 / HYP-07.

Local fixtures only (MIT-BIH + Fantasia). clinical_validation=false.
No BIDMC / Airway / Driver-map / PHI / pooled instability score.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from t21_engine.evaluation.fantasia_age_band_hrv_stability import (
    run_fantasia_age_band_hrv_stability,
)
from t21_engine.evaluation.fantasia_short_window_hrv_lfhf import (
    run_fantasia_short_window_hrv_lfhf,
)
from t21_engine.evaluation.mitbih_brady_def_sensitivity import (
    run_mitbih_brady_def_sensitivity,
)

SCHEMA_VERSION = "proxy-hyp-bench-runner/1.2"
BENCH_COMMITS = {
    "CODEX-101": "af98247",
    "CODEX-102": "6318771",
    "CODEX-103": "f0f7692",
}

# Auditor DUAL-GATE labels (CODEX-112) — stamped into JSON/MD; not clinical FACT.
AUDITOR_DUAL_GATE = {
    "clinical_validation": False,
    "clinical_fact": False,
    "pi_to_define": True,
    "airway_bidmc_do_not_run": True,
    "hypotheses": {
        "HYP-01": {
            "auditor_label": "PARTIALLY_SUPPORTED",
            "claim_label": "PARTIALLY_SUPPORTED",
            "scope": "HR-event/SQI",
            "note": "Partial support in ECG HR-event/SQI PROXY only — not clinical FACT.",
        },
        "HYP-03": {
            "auditor_label": "STRETCH_IF_POSITIVE_PROXY",
            "claim_label": "STRETCH/QA",
            "ok_as": "neg-control-QA",
            "lf_hf_primary": False,
            "note": "STRETCH if read as positive PROXY; OK as negative-control / methods QA.",
        },
        "HYP-07": {
            "auditor_label": "STRETCH_IF_POSITIVE_PROXY",
            "claim_label": "STRETCH/QA",
            "ok_as": "neg-control-QA",
            "note": "STRETCH if read as positive PROXY; OK as age-band engine QA only.",
        },
    },
    "prohibited_tracks": ["Airway", "BIDMC", "HYP-06b", "Driver-map"],
}


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _default_fixture_roots() -> dict[str, Path]:
    root = _repository_root()
    return {
        "mitbih": root / "tests" / "backend" / "fixtures" / "wfdb_mitdb_synthetic",
        "fantasia": root / "tests" / "backend" / "fixtures" / "wfdb_fantasia_synthetic",
    }


def _install_fixture_wfdb_shim_if_needed() -> str:
    """Use native wfdb when present; otherwise shim synthetic fixture .hea/.dat."""
    try:
        import wfdb  # noqa: F401

        return "native"
    except ImportError:
        pass

    class _Waveform:
        __slots__ = ("fs", "p_signal")

        def __init__(self, fs: float, p_signal: np.ndarray) -> None:
            self.fs = fs
            self.p_signal = p_signal

    def rdrecord(name: str) -> _Waveform:
        base = Path(str(name))
        if base.suffix:
            base = base.with_suffix("")
        hea_path = Path(f"{base}.hea")
        dat_path = Path(f"{base}.dat")
        if not hea_path.is_file() or not dat_path.is_file():
            raise FileNotFoundError(f"missing WFDB pair for {base}")
        first = next(
            (
                ln.strip()
                for ln in hea_path.read_text(encoding="utf-8", errors="replace").splitlines()
                if ln.strip() and not ln.startswith("#")
            ),
            "",
        )
        parts = first.split()
        if len(parts) < 4:
            raise ValueError(f"invalid WFDB header: {hea_path}")
        nsig = int(parts[1])
        fs = float(parts[2])
        nsamp = int(parts[3])
        raw = np.fromfile(dat_path, dtype="<i2")
        if raw.size < nsig * nsamp:
            raise ValueError(f"short .dat for {dat_path}")
        matrix = raw[: nsig * nsamp].reshape(nsamp, nsig).astype(np.float64)
        return _Waveform(fs, matrix)

    sys.modules["wfdb"] = SimpleNamespace(rdrecord=rdrecord)
    return "shim"


def _row_summary(codex_id: str, hyp_id: str, report: dict[str, Any]) -> dict[str, Any]:
    gate = AUDITOR_DUAL_GATE["hypotheses"].get(hyp_id, {})
    return {
        "codex_id": codex_id,
        "hypothesis_id": hyp_id,
        "status": report.get("status"),
        "failure_reason_code": report.get("failure_reason_code"),
        "sqi_fail_reason": report.get("sqi_fail_reason"),
        "clinical_validation": report.get("clinical_validation"),
        "role_tag": report.get("role_tag"),
        "schema_version": report.get("schema_version"),
        "landing_commit": BENCH_COMMITS.get(codex_id),
        "fact_layer": (report.get("fact") or {}).get("layer") if report.get("fact") else None,
        "interpretation_status": (report.get("interpretation") or {}).get("status"),
        "hypothesis_status": (report.get("hypothesis") or {}).get("status"),
        "human_review_required": (report.get("hypothesis") or {}).get("human_review_required"),
        "thresholds_note": (report.get("thresholds") or {}).get("note"),
        "auditor_label": gate.get("auditor_label"),
        "claim_label": gate.get("claim_label"),
        "auditor_ok_as": gate.get("ok_as"),
        "clinical_fact": False,
    }


def _markdown_table(rows: list[dict[str, Any]], aggregate: dict[str, Any]) -> str:
    dual = aggregate.get("auditor_dual_gate") or AUDITOR_DUAL_GATE
    lines = [
        "# PROXY HYP-01/03/07 bench results",
        "",
        "## Auditor DUAL-GATE (not clinical FACT)",
        "",
        f"- clinical_validation: `{aggregate['clinical_validation']}`",
        f"- clinical_fact: `{dual.get('clinical_fact', False)}`",
        f"- PI_TO_DEFINE: `{dual.get('pi_to_define', True)}`",
        f"- Airway+BIDMC: **do-not-run** (`{dual.get('airway_bidmc_do_not_run', True)}`)",
        "- HYP-01: **PARTIALLY_SUPPORTED** (HR-event/SQI)",
        "- HYP-03/07: **STRETCH if positive PROXY** / OK as **neg-control-QA**",
        "",
        f"- schema: `{SCHEMA_VERSION}`",
        f"- generated_at_utc: `{aggregate['generated_at_utc']}`",
        f"- network_required: `{aggregate['network_required']}`",
        f"- wfdb_backend: `{aggregate['wfdb_backend']}`",
        f"- pooled_instability_score: `{aggregate['pooled_instability_score']}`",
        "",
        "| CODEX | HYP | claim_label | SQI fail reason | status | role_tag | "
        "FACT | INTERPRETATION | HYPOTHESIS | landing |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            (
                "| {codex} | {hyp} | `{label}` | `{sqi_reason}` | {status} | `{role}` | "
                "{fact} | {interp} | {hyp_st} | `{sha}` |"
            ).format(
                codex=row["codex_id"],
                hyp=row["hypothesis_id"],
                label=row.get("claim_label") or "—",
                sqi_reason=row.get("sqi_fail_reason") or "—",
                status=row["status"],
                role=row.get("role_tag") or "",
                fact=row.get("fact_layer") or "—",
                interp=row.get("interpretation_status") or "—",
                hyp_st=row.get("hypothesis_status") or "—",
                sha=row.get("landing_commit") or "",
            )
        )
    lines.extend(
        [
            "",
            "## Gates",
            "",
            "- PROXY ≠ DS · RUO / Shadow Path B",
            "- Thresholds remain `PI_TO_DEFINE` (no clinical cutoffs hardcoded)",
            "- Airway+BIDMC **do-not-run** · no Driver-map / dosing / closed-loop / PHI",
            "- No clinical FACT from these benches; HUMAN_REVIEW_REQUIRED labels only",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def run_proxy_hyp_benches(
    *,
    mitbih_root: str | Path | None = None,
    fantasia_root: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Execute HYP-01/03/07 benches and optionally write JSON + Markdown tables."""
    fixtures = _default_fixture_roots()
    mit_root = Path(mitbih_root).resolve() if mitbih_root else fixtures["mitbih"]
    fan_root = Path(fantasia_root).resolve() if fantasia_root else fixtures["fantasia"]
    wfdb_backend = _install_fixture_wfdb_shim_if_needed()

    reports = {
        "CODEX-101": run_mitbih_brady_def_sensitivity(mit_root),
        "CODEX-102": run_fantasia_short_window_hrv_lfhf(fan_root),
        "CODEX-103": run_fantasia_age_band_hrv_stability(fan_root),
    }
    summaries = [
        _row_summary("CODEX-101", "HYP-01", reports["CODEX-101"]),
        _row_summary("CODEX-102", "HYP-03", reports["CODEX-102"]),
        _row_summary("CODEX-103", "HYP-07", reports["CODEX-103"]),
    ]
    overall = "PASS" if all(r["status"] == "PASS" for r in summaries) else "FAIL"
    aggregate: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": overall,
        "clinical_validation": False,
        "research_use_only": True,
        "network_required": False,
        "proxy_not_ds": True,
        "pooled_instability_score": None,
        "clinical_fact": False,
        "auditor_dual_gate": AUDITOR_DUAL_GATE,
        "wfdb_backend": wfdb_backend,
        "generated_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fixture_roots": {
            "mitbih": str(mit_root),
            "fantasia": str(fan_root),
        },
        "prohibited": [
            "BIDMC",
            "Airway",
            "Driver-map",
            "HYP-06b",
            "PHI",
            "dosing",
            "closed_loop",
            "pooled_instability_score",
        ],
        "bench_landing_commits": BENCH_COMMITS,
        "summary_rows": summaries,
        "reports": reports,
    }

    if output_dir is not None:
        out = Path(output_dir).resolve()
        out.mkdir(parents=True, exist_ok=True)
        json_path = out / "proxy-hyp-bench-report.json"
        md_path = out / "proxy-hyp-bench-results.md"
        json_path.write_text(
            json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        md_path.write_text(_markdown_table(summaries, aggregate), encoding="utf-8")
        aggregate["artifacts"] = {
            "json": str(json_path),
            "markdown": str(md_path),
        }
    return aggregate


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run PROXY HYP-01/03/07 local benches")
    parser.add_argument(
        "--output-dir",
        default="/tmp/t21-proxy-hyp-benches",
        help="Directory for JSON + Markdown result tables",
    )
    parser.add_argument("--mitbih-root", default=None)
    parser.add_argument("--fantasia-root", default=None)
    args = parser.parse_args(argv)
    result = run_proxy_hyp_benches(
        mitbih_root=args.mitbih_root,
        fantasia_root=args.fantasia_root,
        output_dir=args.output_dir,
    )
    printable = {k: result[k] for k in result if k != "reports"}
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["run_proxy_hyp_benches", "main", "SCHEMA_VERSION", "BENCH_COMMITS", "AUDITOR_DUAL_GATE"]
