#!/usr/bin/env bash
# CODEX-079: One-command synthetic hospital Path B demo (showable / partner-safe).
# RUO · Shadow · clinical_validation=false · PHI-false · public/synthetic only.
# No VitalDB · no dosing/alerts/closed-loop · PROXY benches not required for this run.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT_DIR="${1:-/tmp/t21-hospital-demo}"
REPORT_JSON="${OUT_DIR}/hospital-demo-report.json"

export PYTHONPATH="${ROOT}/services/engine/src${PYTHONPATH:+:${PYTHONPATH}}"

echo "=== T21 Path B hospital demo (RUO / clinical_validation=false) ==="
echo "synthetic hospital case · observe-only shadow · no PHI cloud"
echo "output: ${OUT_DIR}"

mkdir -p "${OUT_DIR}"

echo "[1/3] Ensure engine importable"
python -c "import t21_engine.demo" 2>/dev/null || python -m pip install -e "services/engine[dev]" -q

echo "[2/3] Run synthetic hospital demo with local ExportManifest"
python -m t21_engine.demo --output-dir "${OUT_DIR}" | tee "${REPORT_JSON}"

echo "[3/3] Gate check (PHI-false / RUO)"
python - <<PY
import json
from pathlib import Path

out = Path("${OUT_DIR}")
report = json.loads((out / "hospital-demo-report.json").read_text(encoding="utf-8"))
assert report.get("status") == "PASS", report
assert report.get("clinical_validation") is False, report
assert report.get("contains_phi") is False, report
assert report.get("synthetic_only") is True, report
assert report.get("mode") == "OBSERVE_ONLY_SHADOW", report
export = report.get("local_export") or {}
assert export.get("includes_phi") is False, export
assert export.get("includes_waveforms") is False, export
jsonl = Path(export["jsonl_path"])
assert jsonl.is_file(), jsonl
lines = [ln for ln in jsonl.read_text(encoding="utf-8").splitlines() if ln.strip()]
assert lines, "empty shadow JSONL"
manifest = json.loads(lines[-1])
assert manifest.get("schema_version") == "export-manifest/1.0", manifest
assert manifest.get("includes_phi") is False, manifest
assert manifest.get("includes_waveforms") is False, manifest
assert manifest.get("clinical_validation") is False, manifest
assert manifest.get("is_synthetic") is True, manifest
print("PASS · clinical_validation=false · includes_phi=false · synthetic_only")
print(f"report: {out / 'hospital-demo-report.json'}")
print(f"shadow: {jsonl}")
PY

echo "=== HOSPITAL DEMO PASS ==="
