# Public Data Report v1 — PROXY engine smoke

**Freeze version:** `v1.5-mcp-verify`

**Freeze date:** `2026-09-03 UTC`

**Status:** Scaffold filled from CODEX-006 family · **PROXY only**  
**clinical_validation:** `false`  
**DS clinical claims:** none (public non-DS / synthetic-fixture data ≠ DS validation)  
**Fantasia Master Notion:** `VERIFIED PROXY` (`operational_proxy_ok`; page `3d09631d743b81efae8fe2731113b4f6`)

**Not included in this freeze:** VitalDB, CapnoBase, PulseDB

**Path B:** observe-only · no PHI cloud · no clinical cutoffs/alerts

---

## Freeze changelog

This version freezes the public-data report before any VitalDB work. It records the
following shipped **PROXY** engineering benchmarks and synthetic support artifacts:

| Delivery | Shipped artifact | Commit |
| --- | --- | --- |
| CODEX-011 | BIDMC synchronization / respiration benchmark | `869b996` |
| CODEX-009 | MIT-BIH beat benchmark | `0606d62` |
| CODEX-016 | Fantasia HRV / age-stability benchmark; `operational_proxy_ok`; Fantasia Master now `VERIFIED PROXY` | `f290223` |
| CODEX-008 | Synthetic hospital case factory with time-alignment QC | `2648af7` |
| CODEX-010 | Deterministic synthetic Research Node demo | `020dd79` |
| CODEX-012 | Synthetic baseline-window comparison (180 / 300 seconds) | `a7d8ebd` |
| CODEX-013 | Synthetic SQI / missingness impact table | `aec1d37` |
| CODEX-014 | `ARTIFACTS_INDEX.md` reproducibility pointers | `cce9194` |
| CODEX-015 | Clean-environment install smoke | `631e74c` |

The `v1.1-mcp-pre-VitalDB` bump also records the engineering-only MCP track. These
local, bounded interfaces organize existing PROXY and synthetic research workflows;
they do not add clinical validation or expand the datasets in this freeze.

| Delivery | Shipped MCP engineering artifact | Commit |
| --- | --- | --- |
| CODEX-018 | Fantasia local-first PROXY HRV MCP | `38e749d` |
| CODEX-019 | Fantasia MCP client configuration and stdio CI smoke | `41211ce` |
| CODEX-020 | Fantasia multi-record synthetic fixture matrix | `7c69ff8` |
| CODEX-021 | Research Node synthetic demo, QC, and shadow MCP | `9c5d4d9` |
| CODEX-022 | Unified Fantasia + Research Node MCP configuration and CI smoke | `66c792a` |
| CODEX-023 | Research Node MCP read-only SQI and baseline tools | `3cd2dab` |

The `v1.2-mcp-dx` bump records Founder/DX packaging after the MCP tool surface stabilized.
These are documentation and onboarding artifacts only; they do not expand datasets or
clinical claims.

| Delivery | Shipped DX / packaging artifact | Commit |
| --- | --- | --- |
| CODEX-025 | Founder dual-MCP setup checklist + `scripts/smoke_dual_mcp.py` | `e6514fc` |
| CODEX-027 | Shadow JSONL schema versions + local MCP list/export tools | `ed13e47` |
| CODEX-026 | BIDMC/MIT-BIH PROXY benches as Research Node MCP read-only tools | `03468f1` |
| CODEX-028 | Founder KR MCP onboarding one-pager (`docs/founder/`) | `fa9b152` |

No VitalDB download or implementation, and no CapnoBase or PulseDB benchmark, is part
of `v1.2-mcp-dx` (superseding `v1.1-mcp-pre-VitalDB` for DX packaging). All entries, including the MCP and DX track, remain research
engineering artifacts with
`clinical_validation=false`; none supports a DS-specific or other clinical claim.

The `v1.3-mcp-dx2` bump records MCP DX follow-ons after `v1.2-mcp-dx` (tool catalog,
CI path filters, shadow JSONL pin, list_demo_presets, Fantasia age PI_TO_DEFINE asserts,
catalog regen). Documentation/test packaging only; no new datasets or clinical claims.

| Delivery | Shipped MCP DX2 artifact | Commit |
| --- | --- | --- |
| CODEX-039 | MCP tool catalog auto-gen (`docs/mcp/TOOL_CATALOG.md`) | `2b890ac` |
| CODEX-040 | mcp-stdio-smoke GHA path filters + server matrix | `da75ff1` |
| CODEX-041 | Research Node MCP `list_demo_presets` read-only tool | `0fbaf5d` |
| CODEX-042 | Shadow JSONL schema/version pin unit tests | `79e977b` |
| CODEX-043 | Fantasia MCP age stays `PI_TO_DEFINE` / non-clinical asserts | `43f1859` |
| CODEX-044 | TOOL_CATALOG regen including `list_demo_presets` | `1acb911` |

No VitalDB download or implementation, and no CapnoBase or PulseDB benchmark, is part
of `v1.3-mcp-dx2` (superseding `v1.2-mcp-dx` for MCP DX2 packaging). All entries remain research
engineering artifacts with
`clinical_validation=false`; none supports a DS-specific or other clinical claim.

The `v1.4-path-b-verify` bump records Path B Founder DX verify packaging after
`v1.3-mcp-dx2` (schema/unit pin CI, local verify script, CI wire-up, thin unit,
UNIFIED_MCP pointer). Documentation/CI packaging only; no new datasets or clinical claims.

| Delivery | Shipped Path B verify artifact | Commit |
| --- | --- | --- |
| CODEX-051 | MCP schema/unit pins CI workflow | `d599f68` |
| CODEX-052 | `scripts/verify_path_b_mcp.sh` one-command DX verify | `3701b2e` |
| CODEX-053 | Path-filtered CI for verify script | `87680a1` |
| CODEX-054 | Thin unit for verify script | `e498967` |
| CODEX-055 | UNIFIED_MCP one-line pointer to verify script | `9dd49cd` |

No VitalDB download or implementation, and no CapnoBase or PulseDB benchmark, is part
of `v1.4-path-b-verify` (superseding `v1.3-mcp-dx2` for Path B verify packaging). All entries remain research
engineering artifacts with
`clinical_validation=false`; none supports a DS-specific or other clinical claim.

The `v1.5-mcp-verify` bump records Path B / MCP verify hardening after
`v1.4-path-b-verify` (schema/export/shadow roundtrips, catalog fail-closed,
CI wires for verify + public PROXY benches + synthetic hospital QC). Documentation/CI
packaging and regression hooks only; no new datasets or clinical claims.

| Delivery | Shipped verify / CI artifact | Commit |
| --- | --- | --- |
| CODEX-059 | Schema pins CI includes shadow/export roundtrip | `af5e869` |
| CODEX-060 | `export_shadow_summary` fixture roundtrip unit | `8c99037` |
| CODEX-061 | Catalog drift fail-closed unit | `9d788c1` |
| CODEX-062 | SKIP — ExportManifest already pinned | — |
| CODEX-063 | Wire `test_verify_path_b_mcp` into Path B / schema-pins CI | `4cdb61c` |
| CODEX-064 | Research Node `list_local_shadow_exports` tmp JSONL roundtrip | `048336b` |
| CODEX-065 | Fantasia `list_records` sha256 fixture assert | `09fa324` |
| CODEX-066 | Public PROXY bench thin CI (BIDMC + MIT-BIH units) | `f0d661d` |
| CODEX-067 | Synthetic hospital time-align/QC CI hook | `904cc9e` |

No VitalDB download or implementation, and no CapnoBase or PulseDB benchmark, is part
of `v1.5-mcp-verify` (superseding `v1.4-path-b-verify` for MCP verify packaging). All entries remain research
engineering artifacts with
`clinical_validation=false`; none supports a DS-specific or other clinical claim.

---

## Scope

| Dataset | Role in v1 | Notes |
| --- | --- | --- |
| BIDMC PPG and Respiration v1.0.0 | Master VERIFIED public path | Local-first sample root `data/public/bidmc/1.0.0/` or CI fixture-equivalent + `sha256-manifest.json` |
| MIT-BIH Arrhythmia v1.0.0 (catalog `wfdb:mitdb-100`) | Master VERIFIED **PROXY** public path, unlocked in CODEX-006b | Local-first root `data/public/mitdb/1.0.0/` or clearly labeled synthetic CI fixture-equivalent; `clinical_validation=false`; **no DS validation claim** |
| Fantasia v1.0.0 (catalog `wfdb:fantasia-f1o01`) | `operational_proxy_ok`; Fantasia Master `VERIFIED PROXY` | Local-first root `data/public/fantasia/1.0.0/` or synthetic fixture-equivalent + SHA-256 manifest; `clinical_validation=false`; PROXY status is not clinical verification |

Harness: `t21_engine.evaluation.public_data_bench` — seeded, fail-closed, machine-readable PASS/FAIL.

### MIT-BIH-style beat detection table (CODEX-009)

`t21_engine.evaluation.mitbih_beat_bench` compares `detect_r_peaks` output with a
local `*.atr` annotation when present. Offline CI instead uses the explicitly labeled
`100.synthetic-annotations.json`; it contains no real MIT-BIH annotation bytes. Missing
annotations fail closed with `MISSING_ANNOTATIONS`.

| Record/source | Annotated | Detected | Matched | Missed (FN) | False (FP) | Mean / median / max absolute timing error (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `100` synthetic fixture-equivalent | 3 | 4 | 3 | 0 | 1 | 33.33 / 0 / 100 |

These are deterministic engineering counts from the synthetic fixture test at a 150 ms
match window. They are not sensitivity, specificity, clinical performance, or results on
the public MIT-BIH waveform bytes. The JSON report schema is
`mitbih-beat-bench/1.0`, with per-record and aggregate count/timing fields,
`clinical_validation=false`, `proxy_ecg_only=true`, and `network_required=false`.

### BIDMC alignment / respiration-rate table (CODEX-011)

`t21_engine.evaluation.bidmc_align_resp_bench` requires ECG, PPG, RESP, and a
breath reference. It fails closed when any is unavailable. WFDB multiplexed channels
share one sample clock, so clock-skew fields summarize their common timebase; the
physiological ECG-to-PPG pulse-arrival value is reported separately and is not treated
as clock error.

| Record/source | Start / end sync error (ms) | ECG–PPG median pulse arrival (ms) | Reference / detected RR (breaths/min) | Absolute RR error (breaths/min) |
| --- | ---: | ---: | ---: | ---: |
| `bidmc01` synthetic fixture-equivalent | 0 / 0 | 200 | 12 / 12 | 0 |

These deterministic values exercise the offline fixture only; the fixture contains no
real BIDMC bytes or patient data. They are engineering **PROXY** results, with
`clinical_validation=false`, and make no DS or clinical-performance claim. The report
schema is `bidmc-align-resp-bench/1.0`.

### Fantasia HRV / age-stability PROXY (CODEX-016)

`t21_engine.evaluation.fantasia_hrv_age_bench` applies `time_domain_hrv` to a
local Fantasia record, compares non-overlapping split-window summaries, and repeats the
full calculation to expose deterministic reproducibility. It verifies the synthetic
fixture manifest before loading the waveform and fails closed on missing data,
provenance, checksums, WFDB loading, or insufficient RR intervals.

| Record/source | RR intervals | Deterministic recompute | Age metadata | Age-stability result |
| --- | ---: | --- | --- | --- |
| `f1o01` synthetic fixture-equivalent | fixture/test dependent | exact | unavailable | `PI_TO_DEFINE` / unavailable |

No age is assigned to the CI fixture, so no age comparison, association, or clinical age
claim is calculated. Split-window absolute deltas are engineering diagnostics, not
acceptance thresholds or clinical performance. Authorization is explicitly
`operational_proxy_ok`; the Fantasia Master is `VERIFIED PROXY`, and
`clinical_validation=false`. This is not DS/anesthesia validation and makes no PTT/PPG
claim. Schema: `fantasia-hrv-age-bench/1.0`.

### Baseline window sensitivity (CODEX-012, synthetic)

See `docs/benchmarks/BASELINE_WINDOW_SENSITIVITY.md`. Module
`t21_engine.evaluation.baseline_window_sensitivity` compares 180s vs 300s
pre-induction windows on synthetic hospital cases only (`clinical_validation=false`,
`clinical_window_choice=PI_TO_DEFINE`). Not a public-data claim.

### SQI / missingness impact (CODEX-013, synthetic)

See `docs/benchmarks/SQI_MISSINGNESS_IMPACT.md`. Module
`t21_engine.evaluation.sqi_missingness_impact` applies deterministic gaps/noise to
synthetic hospital channels and reports QC pass rate plus usable analysis-window
counts. `clinical_validation=false`; clinical threshold interpretation is
`PI_TO_DEFINE`. Not a public-data or clinical-performance claim.

---

## Commits / engineering trail (facts only)

| Item | Ref |
| --- | --- |
| CODEX-006 initial harness (MIT-BIH + BIDMC catalog + offline bench) | `f4b36f5` |
| BIDMC-first local sha256 / wfdb I/O refine | `44ed44c` |
| BIDMC `data/public/...` resolution + tracked manifest (006a) | `b816efa` |
| MIT-BIH promoted for local-first PROXY bench (CODEX-006b) | `ba514e5` |
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
| `MISSING_ANNOTATIONS` | Beat benchmark found neither a local `.atr` nor the labeled synthetic annotation equivalent |
| `ANNOTATION_LOAD_FAILURE` | Beat annotations exist but cannot be parsed or do not meet the fixture provenance schema |
| `MISSING_REQUIRED_CHANNEL` | BIDMC alignment bench lacks ECG, PPG, or RESP |
| `MISSING_RESP_REFERENCE` | Neither `.breath` annotations nor the labeled synthetic respiration reference is present |
| `RESP_REFERENCE_LOAD_FAILURE` | Respiration reference exists but cannot be parsed or lacks required provenance |
| `RESP_REFERENCE_OUT_OF_RANGE` | A breath reference sample falls outside the waveform |
| `INSUFFICIENT_DETECTIONS` | Beat/pulse/breath detections cannot produce the required engineering metrics |
| `MISSING_MANIFEST` | Fantasia fixture has no SHA-256 manifest |
| `INVALID_FIXTURE_PROVENANCE` | Fantasia fixture provenance or manifest is invalid |
| `INSUFFICIENT_RR_INTERVALS` | Fantasia record has too few accepted RR intervals for split-window HRV |
| Smoke integrity | `NO_SUPPORTED_SIGNALS`, `INVALID_TIMESTAMPS`, `MISALIGNED_SIGNAL`, `NONFINITE_SIGNAL`, `MISSING_SOURCE_ATTRIBUTION` |

---

## Explicit non-claims

- Public PROXY pass ≠ hospital readiness  
- Public PROXY pass ≠ DS perioperative clinical validation  
- Synthetic CI fixture ≠ PhysioNet record bytes (fixture is labeled)

## Next

- Fill numeric engineering digests from recorded local public samples when an operator places them under the corresponding `data/public/...` roots
