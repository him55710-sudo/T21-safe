#!/usr/bin/env bash
# CODEX-104: One-command local PROXY runner for HYP-01 / HYP-03 / HYP-07 (CODEX-101–103).
# RUO · clinical_validation=false · MIT-BIH+Fantasia fixtures only · no network.
# No BIDMC · no Airway · no Driver-map · no PHI · no pooled instability score.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT_DIR="/tmp/t21-proxy-hyp-benches"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      echo "Usage: bash scripts/run_proxy_hyp_benches.sh [OUT_DIR]"
      echo "  Default OUT_DIR=/tmp/t21-proxy-hyp-benches"
      echo "  Emits proxy-hyp-bench-report.json + proxy-hyp-bench-results.md"
      exit 0
      ;;
    *)
      OUT_DIR="$1"
      shift
      ;;
  esac
done

export PYTHONPATH="${ROOT}/services/engine/src${PYTHONPATH:+:${PYTHONPATH}}"

# Prefer engine .venv when present (CI / local install); else PATH python3.
if [[ -x "${ROOT}/services/engine/.venv/bin/python" ]]; then
  PYTHON="${ROOT}/services/engine/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

echo "=== T21 PROXY HYP-01/03/07 benches (RUO / clinical_validation=false) ==="
echo "fixtures: MIT-BIH + Fantasia local only · no BIDMC/Airway/Driver-map/PHI"
echo "output: ${OUT_DIR}"
echo "python: ${PYTHON}"

mkdir -p "${OUT_DIR}"

echo "[1/2] Engine importable"
"${PYTHON}" -c "import t21_engine.evaluation.proxy_hyp_bench_runner" \
  || { echo "FAIL: cannot import proxy_hyp_bench_runner (install services/engine[dev])" >&2; exit 1; }

echo "[2/2] Run HYP-01 → HYP-03 → HYP-07"
"${PYTHON}" -m t21_engine.evaluation.proxy_hyp_bench_runner --output-dir "${OUT_DIR}"

JSON="${OUT_DIR}/proxy-hyp-bench-report.json"
MD="${OUT_DIR}/proxy-hyp-bench-results.md"
[[ -f "${JSON}" ]] || { echo "FAIL: missing ${JSON}" >&2; exit 1; }
[[ -f "${MD}" ]] || { echo "FAIL: missing ${MD}" >&2; exit 1; }

"${PYTHON}" - <<PY
import json
from pathlib import Path

out = Path("${OUT_DIR}")
report = json.loads((out / "proxy-hyp-bench-report.json").read_text(encoding="utf-8"))
assert report.get("schema_version") == "proxy-hyp-bench-runner/1.1", report
assert report.get("clinical_fact") is False, report
assert (report.get("auditor_dual_gate") or {}).get("hypotheses", {}).get("HYP-01", {}).get("auditor_label") == "PARTIALLY_SUPPORTED", report
assert report.get("status") == "PASS", report
assert report.get("clinical_validation") is False, report
assert report.get("network_required") is False, report
assert report.get("pooled_instability_score") is None, report
assert "BIDMC" in (report.get("prohibited") or []), report
rows = report.get("summary_rows") or []
assert len(rows) == 3, rows
for row in rows:
    assert row.get("clinical_validation") is False, row
    assert row.get("status") == "PASS", row
    assert row.get("human_review_required") is True, row
md = (out / "proxy-hyp-bench-results.md").read_text(encoding="utf-8")
assert "clinical_validation" in md
assert "HYP-01" in md and "HYP-03" in md and "HYP-07" in md
print("gate checks PASS")
PY

echo "=== DONE ==="
echo "JSON: ${JSON}"
echo "MD:   ${MD}"
