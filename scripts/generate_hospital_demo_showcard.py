#!/usr/bin/env python3
"""CODEX-083: Build a PHI-false Markdown show-card from hospital-demo-report.json.

RUO / Shadow · clinical_validation=false · synthetic/local only.
Never embeds waveforms, patient identifiers, or cloud URIs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ALLOWED_TOP_KEYS = frozenset(
    {
        "status",
        "path",
        "intended_use",
        "mode",
        "synthetic_only",
        "contains_phi",
        "clinical_validation",
        "case_id",
        "duration_seconds",
        "seed",
        "alignment_qc",
        "replay_qc",
        "local_export",
        "mission",
    }
)


def _require_gates(report: dict[str, Any]) -> None:
    if report.get("clinical_validation") is not False:
        raise ValueError("show-card requires clinical_validation=false")
    if report.get("contains_phi") is not False:
        raise ValueError("show-card requires contains_phi=false")
    if report.get("synthetic_only") is not True:
        raise ValueError("show-card requires synthetic_only=true")
    export = report.get("local_export") or {}
    if export and export.get("includes_phi") is not False:
        raise ValueError("show-card requires local_export.includes_phi=false")
    if export and export.get("includes_waveforms") is not False:
        raise ValueError("show-card requires local_export.includes_waveforms=false")


def render_showcard(report: dict[str, Any]) -> str:
    _require_gates(report)
    # Drop unexpected keys rather than echoing unknown fields.
    safe = {k: report[k] for k in ALLOWED_TOP_KEYS if k in report}
    alignment = safe.get("alignment_qc") or {}
    replay = safe.get("replay_qc") or {}
    export = safe.get("local_export") or {}
    lines = [
        "# T21 Path B Hospital Demo — Show Card",
        "",
        "**RUO / Shadow · `clinical_validation=false` · PHI-false · synthetic only**",
        "",
        "| Gate | Value |",
        "| --- | --- |",
        f"| status | `{safe.get('status')}` |",
        f"| path | `{safe.get('path')}` |",
        f"| mode | `{safe.get('mode')}` |",
        f"| intended_use | `{safe.get('intended_use')}` |",
        f"| clinical_validation | `{safe.get('clinical_validation')}` |",
        f"| contains_phi | `{safe.get('contains_phi')}` |",
        f"| synthetic_only | `{safe.get('synthetic_only')}` |",
        f"| case_id | `{safe.get('case_id')}` |",
        f"| seed | `{safe.get('seed')}` |",
        f"| duration_seconds | `{safe.get('duration_seconds')}` |",
        "",
        "## Alignment / QC",
        "",
        f"- alignment status: `{alignment.get('status')}`",
        f"- channels: `{', '.join(alignment.get('checked_channels') or [])}`",
        f"- events_processed: `{replay.get('events_processed')}`",
        f"- quality_usable: `{replay.get('quality_usable')}`",
        f"- baseline_calibrated: `{replay.get('baseline_calibrated')}`",
        f"- timestamp_synchronized: `{replay.get('timestamp_synchronized')}`",
        "",
        "## Local export (metadata only)",
        "",
        f"- includes_phi: `{export.get('includes_phi')}`",
        f"- includes_waveforms: `{export.get('includes_waveforms')}`",
        f"- content_scope: `{export.get('content_scope')}`",
        f"- jsonl_path: `{export.get('jsonl_path')}`",
        "",
        "## Not included",
        "",
        "- VitalDB / CapnoBase / PulseDB / MIMIC",
        "- Raw waveforms or PHI",
        "- Dosing, alerts, closed-loop, or clinical claims",
        "- PROXY public benches (BIDMC / MIT-BIH / Fantasia) — labeled **PROXY** separately",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a PHI-false hospital demo Markdown show-card."
    )
    parser.add_argument(
        "report_json",
        type=Path,
        help="Path to hospital-demo-report.json from scripts/run_hospital_demo.sh",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional Markdown output path (default: stdout)",
    )
    args = parser.parse_args(argv)
    report = json.loads(args.report_json.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise SystemExit("report JSON must be an object")
    try:
        card = render_showcard(report)
    except ValueError as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "error": str(exc)}), file=sys.stderr)
        return 2
    if args.output is None:
        print(card)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(card, encoding="utf-8")
        print(str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
