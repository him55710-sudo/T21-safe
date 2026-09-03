# ExportManifest — PHI-false partner one-pager

**Status:** Path B / RUO / Shadow · `clinical_validation=false`  
**Audience:** hospital IT / research partners reviewing local export controls  
**Not:** clinical monitor · dosing/alerts · cloud PHI store · VitalDB/CapnoBase/PulseDB

Korean companion: [`docs/founder/EXPORT_MANIFEST_PHI_FALSE_KR.md`](../founder/EXPORT_MANIFEST_PHI_FALSE_KR.md)

---

## What partners get

A **local-only** metadata export after the synthetic hospital demo:

```bash
bash scripts/run_hospital_demo.sh /tmp/t21-hospital-demo
```

The JSONL ends with an `export-manifest/1.0` object. Schema pin: `contracts/export-manifest.schema.json`.

## Hard guarantees (fail-closed)

| Field | Value | Meaning |
| --- | --- | --- |
| `includes_phi` | `false` (const in schema) | No PHI payload in export |
| `includes_waveforms` | `false` | No raw waveforms |
| `clinical_validation` | `false` | RUO; not a validated clinical device claim |
| `is_synthetic` / `synthetic_only` | `true` on demo path | Synthetic hospital fixture only |
| `storage_scope` | local research | No cloud URI write path |
| Controls | actuation/dosing/closed_loop/drug_advice/emr_write = off | Observe-only |

Cloud schemes (`s3://`, `gs://`, remote URLs) are **rejected** before write. Partners keep the directory on approved local disk.

## What it is not

- Not a DS clinical validation package  
- Not BIDMC/MIT-BIH/Fantasia **PROXY** bench output (those are labeled **PROXY** separately)  
- Not permission to move PHI off-prem  

## Engineering pointers

- Builder: `services/engine/src/t21_engine/streaming/export_manifest.py`  
- Types/schema: `ExportManifest` + `contracts/export-manifest.schema.json`  
- Hospital IT checklist: [`docs/security/HOSPITAL_DEPLOYMENT_CHECKLIST.md`](../security/HOSPITAL_DEPLOYMENT_CHECKLIST.md)
