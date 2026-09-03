#!/usr/bin/env python3
"""CODEX-089/096: Browser-openable PHI-false HTML show-card from hospital-demo-report.json.

RUO / Shadow · clinical_validation=false · synthetic/local only.
Never embeds waveforms, patient identifiers, or cloud URIs.
Print-friendly layout with a quiet RUO banner (no clinical claim language).
Reuses gate checks from the Markdown show-card generator.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

_MD_SCRIPT = Path(__file__).resolve().parent / "generate_hospital_demo_showcard.py"


def _load_md_gates():
    spec = importlib.util.spec_from_file_location("hospital_demo_showcard_md", _MD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {_MD_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render_showcard_html(report: dict[str, Any]) -> str:
    md = _load_md_gates()
    md._require_gates(report)
    safe = {k: report[k] for k in md.ALLOWED_TOP_KEYS if k in report}
    alignment = safe.get("alignment_qc") or {}
    replay = safe.get("replay_qc") or {}
    export = safe.get("local_export") or {}

    def cell(value: Any) -> str:
        return html.escape(str(value))

    channels = ", ".join(alignment.get("checked_channels") or [])
    rows = [
        ("status", safe.get("status")),
        ("path", safe.get("path")),
        ("mode", safe.get("mode")),
        ("intended_use", safe.get("intended_use")),
        ("clinical_validation", safe.get("clinical_validation")),
        ("contains_phi", safe.get("contains_phi")),
        ("synthetic_only", safe.get("synthetic_only")),
        ("case_id", safe.get("case_id")),
        ("seed", safe.get("seed")),
        ("duration_seconds", safe.get("duration_seconds")),
    ]
    gate_rows = "\n".join(
        f"<tr><th>{cell(k)}</th><td><code>{cell(v)}</code></td></tr>" for k, v in rows
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>T21 Path B Hospital Demo — Show Card</title>
  <style>
    :root {{
      --ink: #1a1f2b;
      --muted: #5b6472;
      --line: #e4e7ee;
      --paper: #ffffff;
      --wash: #f5f6f8;
      --accent: #2f5d8a;
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      color: var(--ink);
      background: var(--wash);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      max-width: 48rem;
      margin: 1.5rem auto 2.5rem;
      padding: 0 1rem;
    }}
    .card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 1.35rem 1.5rem 1.6rem;
    }}
    .ruo {{
      display: inline-block;
      margin: 0 0 0.85rem;
      padding: 0.28rem 0.55rem;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: var(--wash);
      color: var(--muted);
      font-size: 0.78rem;
      letter-spacing: 0.02em;
    }}
    h1 {{
      font-size: 1.4rem;
      font-weight: 650;
      margin: 0 0 0.25rem;
      color: var(--ink);
    }}
    .sub {{
      margin: 0 0 1.1rem;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    h2 {{
      font-size: 0.95rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--accent);
      margin: 1.15rem 0 0.45rem;
      border-bottom: 1px solid var(--line);
      padding-bottom: 0.25rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 0.35rem 0 0.5rem;
    }}
    th, td {{
      text-align: left;
      padding: 0.42rem 0.3rem;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
      font-size: 0.95rem;
    }}
    th {{ width: 40%; color: var(--muted); font-weight: 600; }}
    code {{ font-size: 0.9em; }}
    ul {{ margin: 0.35rem 0 0.2rem; padding-left: 1.15rem; }}
    li {{ margin: 0.2rem 0; }}
    .foot {{
      margin-top: 1.25rem;
      color: var(--muted);
      font-size: 0.8rem;
    }}
    @media print {{
      :root {{ background: #fff; }}
      body {{ margin: 0; max-width: none; padding: 0; }}
      .card {{
        border: none;
        border-radius: 0;
        box-shadow: none;
        padding: 0;
      }}
      .ruo {{
        border: 1px solid #bbb;
        background: #fff;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }}
      h2 {{ break-after: avoid; }}
      table, ul {{ break-inside: avoid; }}
      a {{ color: inherit; text-decoration: none; }}
    }}
  </style>
</head>
<body>
  <article class="card">
    <div class="ruo">Research Use Only · observe-only shadow · not a clinical device</div>
    <h1>T21 Path B Hospital Demo</h1>
    <p class="sub">Synthetic local run summary · <code>clinical_validation=false</code> · PHI-false</p>
    <h2>Gates</h2>
    <table>
      <tbody>
{gate_rows}
      </tbody>
    </table>
    <h2>Alignment / QC</h2>
    <ul>
      <li>alignment status: <code>{cell(alignment.get("status"))}</code></li>
      <li>channels: <code>{cell(channels)}</code></li>
      <li>events_processed: <code>{cell(replay.get("events_processed"))}</code></li>
      <li>quality_usable: <code>{cell(replay.get("quality_usable"))}</code></li>
      <li>baseline_calibrated: <code>{cell(replay.get("baseline_calibrated"))}</code></li>
      <li>timestamp_synchronized: <code>{cell(replay.get("timestamp_synchronized"))}</code></li>
    </ul>
    <h2>Local export (metadata only)</h2>
    <ul>
      <li>includes_phi: <code>{cell(export.get("includes_phi"))}</code></li>
      <li>includes_waveforms: <code>{cell(export.get("includes_waveforms"))}</code></li>
      <li>content_scope: <code>{cell(export.get("content_scope"))}</code></li>
      <li>jsonl_path: <code>{cell(export.get("jsonl_path"))}</code></li>
    </ul>
    <h2>Out of scope</h2>
    <ul>
      <li>VitalDB / CapnoBase / PulseDB / MIMIC</li>
      <li>Raw waveforms or PHI</li>
      <li>Dosing, alerts, closed-loop actuation, or treatment advice</li>
      <li>PROXY public benches (BIDMC / MIT-BIH / Fantasia) — labeled <strong>PROXY</strong> separately</li>
    </ul>
    <p class="foot">Generated by <code>scripts/generate_hospital_demo_showcard_html.py</code> · open locally in a browser · print via the browser print dialog.</p>
  </article>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a PHI-false hospital demo HTML show-card (browser-openable)."
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
        help="HTML output path (default: <report_dir>/showcard.html)",
    )
    args = parser.parse_args(argv)
    report = json.loads(args.report_json.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise SystemExit("report JSON must be an object")
    try:
        card = render_showcard_html(report)
    except ValueError as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "error": str(exc)}), file=sys.stderr)
        return 2
    # Soft assert: avoid clinical claim phrasing in the template itself.
    lowered = card.lower()
    for banned in ("diagnos", "treat patient", "clinical validation=true", "cleared device"):
        if banned in lowered:
            print(json.dumps({"status": "FAIL_CLOSED", "error": f"banned phrasing: {banned}"}), file=sys.stderr)
            return 2
    out = args.output
    if out is None:
        out = args.report_json.resolve().parent / "showcard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(card, encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
