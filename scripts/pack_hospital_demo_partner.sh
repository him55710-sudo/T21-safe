#!/usr/bin/env bash
# CODEX-085: Pack partner-safe hospital demo bundle (no waveforms / no PHI).
# Includes report JSON, MD+HTML show-cards, EN/KR ExportManifest 1-pagers, onboarding.
# Docs only — never copy shadow JSONL (waveforms/PHI excluded by design;
# partner pack is docs + summary reports only).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DEMO_DIR="${1:-/tmp/t21-hospital-demo}"
PACK_DIR="${2:-/tmp/t21-hospital-demo-partner-pack}"
STAGING="${PACK_DIR}/staging"
ZIP_OUT="${PACK_DIR}/t21-hospital-demo-partner-pack.zip"

export PYTHONPATH="${ROOT}/services/engine/src${PYTHONPATH:+:${PYTHONPATH}}"

echo "=== Pack hospital demo partner bundle (PHI-false) ==="
mkdir -p "${STAGING}/docs" "${STAGING}/reports"

if [[ ! -f "${DEMO_DIR}/hospital-demo-report.json" ]]; then
  echo "demo report missing; running hospital demo into ${DEMO_DIR}"
  bash scripts/run_hospital_demo.sh "${DEMO_DIR}"
fi

cp "${DEMO_DIR}/hospital-demo-report.json" "${STAGING}/reports/"
if [[ -f "${DEMO_DIR}/multi-seed-report.json" ]]; then
  cp "${DEMO_DIR}/multi-seed-report.json" "${STAGING}/reports/"
fi

python3 scripts/generate_hospital_demo_showcard.py \
  "${DEMO_DIR}/hospital-demo-report.json" \
  -o "${STAGING}/reports/showcard.md"
python3 scripts/generate_hospital_demo_showcard_html.py \
  "${DEMO_DIR}/hospital-demo-report.json" \
  -o "${STAGING}/reports/showcard.html"

cp docs/business/export-manifest-phi-false-1p.md "${STAGING}/docs/"
cp docs/founder/EXPORT_MANIFEST_PHI_FALSE_KR.md "${STAGING}/docs/"
cp docs/founder/HOSPITAL_DEMO_ONBOARDING_KR.md "${STAGING}/docs/"
cp docs/founder/hospital-demo-showcard.example.md "${STAGING}/docs/"
if [[ -f docs/founder/hospital-demo-showcard.example.html ]]; then
  cp docs/founder/hospital-demo-showcard.example.html "${STAGING}/docs/"
fi

# CODEX-095: partner business 1-pagers (copy only if present; PHI-false / RUO docs)
for biz in \
  docs/business/research-node-one-pager.md \
  docs/business/research-overview-2p.md \
  docs/business/safety-local-first-1p.md \
  docs/business/export-manifest-phi-false-1p.md \
  docs/business/HOSPITAL_POC_ONEPAGER.md
do
  if [[ -f "${biz}" ]]; then
    cp "${biz}" "${STAGING}/docs/"
  fi
done

cat > "${STAGING}/README.md" << 'README'
# T21 Path B Hospital Demo — Partner Pack

RUO / Shadow · `clinical_validation=false` · PHI-false · synthetic only.

## Contents

- `reports/hospital-demo-report.json` — demo gates + QC summary
- `reports/showcard.md` — PHI-false Markdown show card
- `reports/showcard.html` — browser-openable PHI-false HTML show card
- `docs/` — EN/KR ExportManifest PHI-false story + hospital demo onboarding

## Not included

- Raw waveforms or PHI
- Shadow JSONL event stream (metadata stays local on the demo host)
- VitalDB / CapnoBase / PulseDB / MIMIC
- Dosing, alerts, closed-loop, or clinical claims

Re-run locally:

```bash
bash scripts/run_hospital_demo.sh /tmp/t21-hospital-demo
bash scripts/pack_hospital_demo_partner.sh /tmp/t21-hospital-demo
```
README

python - <<PY
import json
from pathlib import Path
report = json.loads(Path("${DEMO_DIR}/hospital-demo-report.json").read_text(encoding="utf-8"))
assert report.get("clinical_validation") is False
assert report.get("contains_phi") is False
export = report.get("local_export") or {}
assert export.get("includes_phi") is False
assert export.get("includes_waveforms") is False
print("pack gates OK")
PY

rm -f "${ZIP_OUT}"
python - <<PY
from pathlib import Path
import zipfile

staging = Path("${STAGING}")
zip_out = Path("${ZIP_OUT}")
with zipfile.ZipFile(zip_out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(staging.rglob("*")):
        if path.is_file():
            zf.write(path, path.relative_to(staging).as_posix())
print(f"wrote {zip_out} ({zip_out.stat().st_size} bytes)")
PY
echo "partner pack: ${ZIP_OUT}"
echo "=== PARTNER PACK PASS ==="
