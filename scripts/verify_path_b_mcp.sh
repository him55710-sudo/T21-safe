#!/usr/bin/env bash
# CODEX-052: One-command local Founder DX verify (Path B / RUO).
# clinical_validation=false · no VitalDB · observe-only.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="${ROOT}/services/engine/src${PYTHONPATH:+:${PYTHONPATH}}"

echo "=== Path B MCP verify (RUO / clinical_validation=false) ==="

echo "[1/3] Research Node demo smoke"
python -m pip install -e "services/engine[dev,wfdb]" -q
python -m t21_engine.demo --help >/dev/null
python -m t21_engine.demo >/tmp/t21-path-b-demo.json
python - <<'PY'
import json
from pathlib import Path
report = json.loads(Path("/tmp/t21-path-b-demo.json").read_text(encoding="utf-8"))
assert report.get("clinical_validation") is False, report
assert report.get("status") == "PASS", report
print("demo PASS clinical_validation=false")
PY

echo "[2/3] Dual-MCP stdio smoke"
python scripts/smoke_dual_mcp.py

echo "[3/3] TOOL_CATALOG regen dry-diff"
python scripts/generate_mcp_tool_catalog.py >/tmp/t21-catalog-path.txt
if ! git diff --exit-code -- docs/mcp/TOOL_CATALOG.md; then
  echo "TOOL_CATALOG.md drifted from generator output" >&2
  echo "Re-run: PYTHONPATH=services/engine/src python scripts/generate_mcp_tool_catalog.py" >&2
  exit 1
fi
echo "TOOL_CATALOG.md matches generator (no diff)"

echo "=== ALL PASS ==="
