# Public Data Report v1 — PROXY engine smoke

**Status:** Scaffold filled from CODEX-006 family · **PROXY only**  
**clinical_validation:** `false`  
**DS clinical claims:** none (public non-DS / synthetic-fixture data ≠ DS validation)  
**Path B:** observe-only · no PHI cloud · no clinical cutoffs/alerts

---

## Scope

| Dataset | Role in v1 | Notes |
| --- | --- | --- |
| BIDMC PPG and Respiration v1.0.0 | Master VERIFIED public path | Local-first sample root `data/public/bidmc/1.0.0/` or CI fixture-equivalent + `sha256-manifest.json` |
| MIT-BIH Arrhythmia v1.0.0 (catalog `wfdb:mitdb-100`) | Master VERIFIED **PROXY** public path, unlocked in CODEX-006b | Local-first root `data/public/mitdb/1.0.0/` or clearly labeled synthetic CI fixture-equivalent; `clinical_validation=false`; **no DS validation claim** |

Harness: `t21_engine.evaluation.public_data_bench` — seeded, fail-closed, machine-readable PASS/FAIL.

---

## Commits / engineering trail (facts only)

| Item | Ref |
| --- | --- |
| CODEX-006 initial harness (MIT-BIH + BIDMC catalog + offline bench) | `f4b36f5` |
| BIDMC-first local sha256 / wfdb I/O refine | `44ed44c` |
| BIDMC `data/public/...` resolution + tracked manifest (006a) | `b816efa` |
| MIT-BIH promoted for local-first PROXY bench (CODEX-006b) | see commit for this slice |
| Related replay JSONL sink (pre-req path) | `25586c8` (CODEX-005 #3) |

Unit coverage at CODEX-006b landing: **12** `test_public_data_bench` cases passed (local CI; FastAPI adapter suite may be env-gated).

---

## Result semantics (not clinical metrics)

Reports include: `schema_version`, `status`, `seed`, dataset name/version/license notes, per-case `failure_reason_code`, `sha256` digests when local files present, `clinical_validation: false`, Path B `safety` block.

**No AUCs, sensitivity, specificity, or “risk score performance” are claimed in v1.**

---

## Failures section (expected fail-closed codes)

| Code | Meaning |
| --- | --- |
| `MISSING_SAMPLE` | No per-case local public-data root / fixture |
| `SHA256_MISMATCH` | Manifest digests ≠ files on disk |
| `WFDB_LOAD_FAILURE` | Local wfdb I/O failed |
| `MISSING_PUBLIC_METADATA` | Catalog metadata incomplete |
| `DATASET_NOT_PROMOTED` | Catalog exists but has not been Master-promoted |
| Smoke integrity | `NO_SUPPORTED_SIGNALS`, `INVALID_TIMESTAMPS`, `MISALIGNED_SIGNAL`, `NONFINITE_SIGNAL`, `MISSING_SOURCE_ATTRIBUTION` |

---

## Explicit non-claims

- Public PROXY pass ≠ hospital readiness  
- Public PROXY pass ≠ DS perioperative clinical validation  
- Synthetic CI fixture ≠ PhysioNet record bytes (fixture is labeled)

## Next

- Fill numeric engineering digests from recorded local public samples when an operator places them under the corresponding `data/public/...` roots
