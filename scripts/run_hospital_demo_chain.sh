#!/usr/bin/env bash
# CODEX-090: One-command chain — hospital demo → HTML showcard → partner zip.
# RUO / Shadow · clinical_validation=false · PHI-false · synthetic only · no VitalDB.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT_DIR="${1:-/tmp/t21-hospital-demo}"
PACK_DIR="${2:-/tmp/t21-hospital-demo-partner-pack}"

export PYTHONPATH="${ROOT}/services/engine/src${PYTHONPATH:+:${PYTHONPATH}}"

echo "=== T21 hospital demo chain (demo → HTML showcard → partner zip) ==="
echo "out=${OUT_DIR}"
echo "pack=${PACK_DIR}"

echo "[1/3] Hospital demo"
bash scripts/run_hospital_demo.sh "${OUT_DIR}"

REPORT="${OUT_DIR}/hospital-demo-report.json"
echo "[2/3] HTML show-card (browser-openable)"
python3 scripts/generate_hospital_demo_showcard_html.py "${REPORT}" -o "${OUT_DIR}/showcard.html"
python3 scripts/generate_hospital_demo_showcard.py "${REPORT}" -o "${OUT_DIR}/showcard.md"

echo "[3/3] Partner pack zip"
bash scripts/pack_hospital_demo_partner.sh "${OUT_DIR}" "${PACK_DIR}"

python - <<PY
from pathlib import Path
import zipfile

html = Path("${OUT_DIR}/showcard.html")
zip_path = Path("${PACK_DIR}/t21-hospital-demo-partner-pack.zip")
assert html.is_file(), html
assert zip_path.is_file(), zip_path
with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED) as zf:
    names = set(zf.namelist())
    arc = "reports/showcard.html"
    if arc not in names:
        zf.write(html, arc)
print(f"HTML showcard: {html}")
print(f"partner pack: {zip_path}")
print("open in browser:", html)
PY

echo "=== HOSPITAL DEMO CHAIN PASS ==="
