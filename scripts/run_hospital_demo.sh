#!/usr/bin/env bash
# CODEX-079/084: One-command synthetic hospital Path B demo (showable / partner-safe).
# RUO · Shadow · clinical_validation=false · PHI-false · public/synthetic only.
# No VitalDB · no dosing/alerts/closed-loop · PROXY benches not required for this run.
# Optional multi-seed matrix: --seeds 1,2,3 (CODEX-084).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT_DIR="/tmp/t21-hospital-demo"
SEEDS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --seeds)
      SEEDS="${2:-}"
      shift 2
      ;;
    --seeds=*)
      SEEDS="${1#*=}"
      shift
      ;;
    -h|--help)
      echo "Usage: bash scripts/run_hospital_demo.sh [OUT_DIR] [--seeds S1,S2,...]"
      echo "  Default OUT_DIR=/tmp/t21-hospital-demo"
      echo "  Without --seeds: single default demo seed"
      echo "  With --seeds: fail-closed matrix + multi-seed-report.json"
      exit 0
      ;;
    *)
      OUT_DIR="$1"
      shift
      ;;
  esac
done

export PYTHONPATH="${ROOT}/services/engine/src${PYTHONPATH:+:${PYTHONPATH}}"

echo "=== T21 Path B hospital demo (RUO / clinical_validation=false) ==="
echo "synthetic hospital case · observe-only shadow · no PHI cloud"
echo "output: ${OUT_DIR}"

mkdir -p "${OUT_DIR}"

echo "[1/3] Ensure engine importable"
python -c "import t21_engine.demo" 2>/dev/null || python -m pip install -e "services/engine[dev]" -q

run_one_seed() {
  local seed_out="$1"
  local seed_arg=()
  if [[ -n "${2:-}" ]]; then
    seed_arg=(--seed "$2")
    echo "  seed=${2} -> ${seed_out}"
  fi
  mkdir -p "${seed_out}"
  python -m t21_engine.demo --output-dir "${seed_out}" "${seed_arg[@]}" | tee "${seed_out}/hospital-demo-report.json"
  python - <<PY
import json
from pathlib import Path

out = Path("${seed_out}")
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
}

if [[ -z "${SEEDS}" ]]; then
  echo "[2/3] Run synthetic hospital demo with local ExportManifest"
  run_one_seed "${OUT_DIR}"
  echo "[3/3] Gate check done"
  echo "=== HOSPITAL DEMO PASS ==="
  exit 0
fi

echo "[2/3] Multi-seed matrix (${SEEDS})"
IFS=',' read -r -a SEED_ARR <<< "${SEEDS}"
SUMMARY_ROWS=()
for seed in "${SEED_ARR[@]}"; do
  seed="$(echo "${seed}" | tr -d '[:space:]')"
  [[ -n "${seed}" ]] || continue
  seed_out="${OUT_DIR}/seed-${seed}"
  run_one_seed "${seed_out}" "${seed}"
  SUMMARY_ROWS+=("${seed}|${seed_out}/hospital-demo-report.json")
done

echo "[3/3] Write multi-seed-report.json"
python - <<PY
import json
from pathlib import Path

out = Path("${OUT_DIR}")
rows_raw = """${SUMMARY_ROWS[*]}""".split()
rows = []
for item in rows_raw:
    seed, path = item.split("|", 1)
    report = json.loads(Path(path).read_text(encoding="utf-8"))
    if report.get("status") != "PASS":
        raise SystemExit(f"seed {seed} failed: {report!r}")
    if report.get("clinical_validation") is not False:
        raise SystemExit(f"seed {seed} clinical_validation gate failed")
    if report.get("contains_phi") is not False:
        raise SystemExit(f"seed {seed} PHI gate failed")
    replay = report.get("replay_qc") or {}
    rows.append(
        {
            "seed": int(seed),
            "status": report.get("status"),
            "clinical_validation": report.get("clinical_validation"),
            "contains_phi": report.get("contains_phi"),
            "synthetic_only": report.get("synthetic_only"),
            "events_processed": replay.get("events_processed"),
            "quality_usable": replay.get("quality_usable"),
            "report_path": path,
        }
    )

summary = {
    "schema_version": "hospital-demo-multi-seed/1.0",
    "clinical_validation": False,
    "contains_phi": False,
    "synthetic_only": True,
    "status": "PASS",
    "seeds": [row["seed"] for row in rows],
    "rows": rows,
}
(out / "multi-seed-report.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print("seed | status | events | quality_usable")
print("---- | ------ | ------ | --------------")
for row in rows:
    print(f"{row['seed']} | {row['status']} | {row['events_processed']} | {row['quality_usable']}")
print(f"multi-seed report: {out / 'multi-seed-report.json'}")
PY

echo "=== HOSPITAL DEMO MULTI-SEED PASS ==="
