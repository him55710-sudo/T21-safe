#!/usr/bin/env bash
# CODEX-108: Pack partner-safe PROXY HYP-01/03/07 bundle (JSON/MD/KR docs only).
# No waveforms · no PHI · no BIDMC · METHODS_CRITIQUE near top of README.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BENCH_DIR="${1:-/tmp/t21-proxy-hyp-benches}"
PACK_DIR="${2:-/tmp/t21-proxy-hyp-partner-pack}"
STAGING="${PACK_DIR}/staging"
ZIP_OUT="${PACK_DIR}/t21-proxy-hyp-partner-pack.zip"

export PYTHONPATH="${ROOT}/services/engine/src${PYTHONPATH:+:${PYTHONPATH}}"

if [[ -x "${ROOT}/services/engine/.venv/bin/python" ]]; then
  PYTHON="${ROOT}/services/engine/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

echo "=== Pack PROXY HYP partner bundle (PHI-false / docs+tables only) ==="
mkdir -p "${STAGING}/docs" "${STAGING}/reports"

if [[ ! -f "${BENCH_DIR}/proxy-hyp-bench-report.json" ]]; then
  echo "bench report missing; running proxy hyp benches into ${BENCH_DIR}"
  bash scripts/run_proxy_hyp_benches.sh "${BENCH_DIR}"
fi

cp "${BENCH_DIR}/proxy-hyp-bench-report.json" "${STAGING}/reports/"
cp "${BENCH_DIR}/proxy-hyp-bench-results.md" "${STAGING}/reports/"

cp docs/founder/PROXY_HYP_RESULTS_KR.md "${STAGING}/docs/"
cp docs/founder/MEETING_ONEPAGER_PROXY_v0.1_KR.md "${STAGING}/docs/"
cp docs/benchmarks/ARTIFACTS_INDEX.md "${STAGING}/docs/"
# Optional safety one-pager if present (RUO); never waveforms.
if [[ -f docs/business/safety-local-first-1p.md ]]; then
  cp docs/business/safety-local-first-1p.md "${STAGING}/docs/"
fi

cat > "${STAGING}/README.md" << 'README'
# T21 PROXY HYP-01/03/07 — Partner Pack

Meeting-pack follow-up freeze tip: `v2.7-meeting-pack-mcp-followup`; `docs/founder/MEETING_ONEPAGER_PROXY_v0.1_KR.md` is staged in this pack.

## Auditor DSCS + METHODS_CRITIQUE (read first)

| Label | Status |
| --- | --- |
| HYP-01 | **PARTIALLY_SUPPORTED** (HR-event/SQI) — not clinical FACT |
| HYP-03 / HYP-07 | **STRETCH if positive PROXY** / **OK as neg-control-QA** |
| RQ-004 | **HYPOTHESIS** (never FACT) |
| LF/HF | **Not primary**; **&lt;180s withheld** |
| Age metadata | **UNAVAILABLE** / PI_TO_DEFINE |
| v0.1 claims | Collapsed to **ECG HR-event / SQI** only |
| Airway + BIDMC | **do-not-run** |
| `clinical_validation` | **`false`** |
| PROXY ≠ DS | **Required** |
| Pooled instability score | **None** |

Forbidden: 06b / BIDMC / Airway / Driver-map / PHI / dosing / closed-loop / DS peri-op performance claims / positive HRV PROXY stretch-as-FACT.

See `docs/PROXY_HYP_RESULTS_KR.md` (Auditor DSCS + METHODS_CRITIQUE at top).

## Contents

- `reports/proxy-hyp-bench-report.json` — HYP-01/03/07 FACT/INTERPRETATION/HYPOTHESIS
- `reports/proxy-hyp-bench-results.md` — summary table
- `docs/PROXY_HYP_RESULTS_KR.md` — founder KR pack + critique
- `docs/founder/MEETING_ONEPAGER_PROXY_v0.1_KR.md` — also staged by the hospital-demo partner pack (cross-pack consistency; docs-only; no PHI)
- `docs/ARTIFACTS_INDEX.md` — engineering artifact index (PROXY section)
- `docs/safety-local-first-1p.md` — optional RUO one-pager (if present)

## Not included

- Raw waveforms or PHI
- Shadow JSONL / WFDB `.dat` bytes
- BIDMC / Airway / Driver-map / VitalDB
- Dosing, alerts, closed-loop, or clinical claims

Re-run locally:

```bash
bash scripts/run_proxy_hyp_benches.sh /tmp/t21-proxy-hyp-benches
bash scripts/pack_proxy_hyp_partner.sh /tmp/t21-proxy-hyp-benches /tmp/t21-proxy-hyp-partner-pack
```
README

"${PYTHON}" - <<PY
import json
from pathlib import Path

report = json.loads(Path("${BENCH_DIR}/proxy-hyp-bench-report.json").read_text(encoding="utf-8"))
assert report.get("clinical_validation") is False, report
assert report.get("network_required") is False, report
assert report.get("pooled_instability_score") is None, report
assert "BIDMC" in (report.get("prohibited") or []), report
assert report.get("status") == "PASS", report
readme = Path("${STAGING}/README.md").read_text(encoding="utf-8")
assert "METHODS_CRITIQUE" in readme or "Auditor DSCS" in readme
assert "PARTIALLY_SUPPORTED" in readme
assert "clinical_validation" in readme
assert "waveforms" in readme.lower() or "Waveforms" in readme
kr = Path("${STAGING}/docs/PROXY_HYP_RESULTS_KR.md").read_text(encoding="utf-8")
assert min(kr.index("METHODS_CRITIQUE"), kr.index("Auditor DSCS")) < kr.index("랜딩 SHA")
assert "PARTIALLY_SUPPORTED" in kr
print("pack gates OK")
PY

# Fail-closed: no waveform / fixture bytes in staging
"${PYTHON}" - <<PY
from pathlib import Path
staging = Path("${STAGING}")
forbidden_suffixes = {".dat", ".hea", ".atr", ".jsonl", ".edf", ".wav"}
bad = [p for p in staging.rglob("*") if p.is_file() and p.suffix.lower() in forbidden_suffixes]
assert not bad, f"waveform/fixture bytes leaked into pack: {bad}"
# Also reject obvious waveform dirs
for name in ("wfdb", "fantasia", "mitdb", "bidmc"):
    hits = [p for p in staging.rglob("*") if name in p.name.lower() and p.suffix.lower() in {".dat", ".hea"}]
    assert not hits, hits
print("no-waveform gate OK")
PY

rm -f "${ZIP_OUT}"
"${PYTHON}" - <<PY
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
echo "=== PROXY HYP PARTNER PACK PASS ==="
