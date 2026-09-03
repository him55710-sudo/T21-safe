# T21 Path B Hospital Demo — Show Card

**RUO / Shadow · `clinical_validation=false` · PHI-false · synthetic only**

| Gate | Value |
| --- | --- |
| status | `PASS` |
| path | `Path B` |
| mode | `OBSERVE_ONLY_SHADOW` |
| intended_use | `RESEARCH_USE_ONLY` |
| clinical_validation | `False` |
| contains_phi | `False` |
| synthetic_only | `True` |
| case_id | `synthetic:hospital-stable` |
| seed | `20250321` |
| duration_seconds | `12.0` |

## Alignment / QC

- alignment status: `PASS`
- channels: `abp, ecg_ii, ppg, resp, spo2_pct`
- events_processed: `12`
- quality_usable: `True`
- baseline_calibrated: `True`
- timestamp_synchronized: `True`

## Local export (metadata only)

- includes_phi: `False`
- includes_waveforms: `False`
- content_scope: `SHADOW_CAPTURE_METADATA_ONLY`
- jsonl_path: `/tmp/t21-hospital-demo-codex079/shadow-capture.jsonl`

## Not included

- VitalDB / CapnoBase / PulseDB / MIMIC
- Raw waveforms or PHI
- Dosing, alerts, closed-loop, or clinical claims
- PROXY public benches (BIDMC / MIT-BIH / Fantasia) — labeled **PROXY** separately
