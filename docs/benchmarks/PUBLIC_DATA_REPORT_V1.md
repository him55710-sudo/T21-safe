# Public Data Report v1 — PROXY engine smoke

**Freeze version:** `v2.6-meeting-pack-mcp`

**Freeze date:** `2026-09-04 UTC` (prior hospital-demo tip stamped `2026-09-03 UTC`; prior PROXY benches tip `v2.1-proxy-hyp-benches`)

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

The `v1.6-eng-ci` bump records engineering CI coverage after `v1.5-mcp-verify`
(PROXY/Fantasia/public_data benches, replay + research-node demo smokes,
baseline/SQI sensitivity CI, ReplayPipeline empty-batch fail-closed). CI/docs
and fail-closed hardening only; no new datasets or clinical claims.

| Delivery | Shipped eng CI / fail-closed artifact | Commit |
| --- | --- | --- |
| CODEX-069 | Fantasia HRV/age PROXY bench CI (proxy-bench-smoke) | `ae1a59b` |
| CODEX-070 | Replay pipeline integration CI | `48feac4` |
| CODEX-071 | Research node demo + hospital integration CI | `85ed55f` |
| CODEX-072 | Baseline-window + SQI/missingness CI | `6e0d4c2` |
| CODEX-073 | `public_data_bench` harness CI (proxy-bench-smoke) | `f7dd376` |
| CODEX-074 | ReplayPipeline empty signal batch fail-closed | `8b1ba66` |

No VitalDB download or implementation, and no CapnoBase or PulseDB benchmark, is part
of `v1.6-eng-ci` (superseding `v1.5-mcp-verify` for eng CI packaging). All entries remain research
engineering artifacts with
`clinical_validation=false`; none supports a DS-specific or other clinical claim.

The `v1.7-hospital-demo` bump records Founder/partner showable hospital demo
packaging after `v1.6-eng-ci` (one-command runner, KR onboarding, ExportManifest
PHI-false partner pack, show-card, multi-seed matrix, partner zip, CI extension).
Documentation/DX and local demo tooling only; no new datasets or clinical claims.

| Delivery | Shipped hospital-demo artifact | Commit |
| --- | --- | --- |
| CODEX-079 | `scripts/run_hospital_demo.sh` | `75fbf65` |
| CODEX-080 | Hospital demo KR onboarding + ARTIFACTS | `8ace65f` |
| CODEX-081 | ExportManifest PHI-false partner pack docs | `366811c` |
| CODEX-082 | Hospital demo CI smoke | `d3d995d` |
| CODEX-083 | PHI-false Markdown show-card generator | `835706d` |
| CODEX-084 | Multi-seed hospital demo matrix | `99f9bac` |
| CODEX-085 | Partner pack zip (no shadow JSONL) | `3a92306` |
| CODEX-086 | CI extends showcard + partner pack | `73a5cf1` |
| CODEX-087 | ARTIFACTS_INDEX hospital-demo refresh | `7f01768` |

No VitalDB download or implementation, and no CapnoBase or PulseDB benchmark, is part
of `v1.7-hospital-demo` (superseding `v1.6-eng-ci` for hospital-demo packaging). All entries remain research
engineering artifacts with
`clinical_validation=false`; none supports a DS-specific or other clinical claim.

The `v1.8-hospital-demo-html` bump records browser-openable hospital demo packaging
after `v1.7-hospital-demo` (HTML show-card, demo→HTML→zip chain, KR runbook, CI/pack
HTML defaults). Documentation/DX and local demo tooling only; no new datasets or
clinical claims.

| Delivery | Shipped hospital-demo HTML artifact | Commit |
| --- | --- | --- |
| CODEX-089 | HTML browser show-card generator | `b1a5597` |
| CODEX-090 | Demo → HTML → partner zip chain | `001a008` |
| CODEX-091 | HOSPITAL_DEMO_RUNBOOK_KR + ARTIFACTS | `abbac57` |
| CODEX-092 | CI wire HTML showcard + chain units | `12f01c7` |
| CODEX-093 | Partner pack includes HTML showcard | `abca64c` |

No VitalDB download or implementation, and no CapnoBase or PulseDB benchmark, is part
of `v1.8-hospital-demo-html` (superseding `v1.7-hospital-demo` for HTML demo packaging). All entries remain research
engineering artifacts with
`clinical_validation=false`; none supports a DS-specific or other clinical claim.

The `v1.9-hospital-demo-pack` bump records partner-pack depth after
`v1.8-hospital-demo-html` (business 1-pagers in zip, print-friendly HTML show-card,
ARTIFACTS/runbook refresh). Documentation/DX packaging only; no new datasets or
clinical claims.

| Delivery | Shipped partner-pack artifact | Commit |
| --- | --- | --- |
| CODEX-095 | Partner pack business 1-pagers (as available) | `d5aa785` |
| CODEX-096 | Print-friendly HTML show-card + quiet RUO banner | `b9862e3` |
| CODEX-097 | ARTIFACTS + RUNBOOK + freeze tip | `e14ae3b` |

No VitalDB download or implementation, and no CapnoBase or PulseDB benchmark, is part
of `v1.9-hospital-demo-pack` (superseding `v1.8-hospital-demo-html` for partner-pack packaging). All entries remain research
engineering artifacts with
`clinical_validation=false`; none supports a DS-specific or other clinical claim.

The `v2.0-hospital-demo-ready` bump records Founder-ready hospital demo packaging after
`v1.9-hospital-demo-pack` (fail-closed partner zip CI, Makefile wrappers, ARTIFACTS
refresh). Documentation/DX packaging only; no new datasets or clinical claims.

| Delivery | Shipped ready artifact | Commit |
| --- | --- | --- |
| CODEX-098 | Partner zip fail-closed contents CI/unit | `a46aa74` |
| CODEX-099 | Makefile `hospital-demo` / `hospital-demo-pack` | `5f68050` |
| CODEX-100 | ARTIFACTS + freeze tip | `3659fc3` |

No VitalDB download or implementation, and no CapnoBase or PulseDB benchmark, is part
of `v2.0-hospital-demo-ready` (superseding `v1.9-hospital-demo-pack` for Founder-ready packaging). All entries remain research
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

## PROXY Analysis Plan freeze (CODEX-101–109)

Tip freeze `v2.1-proxy-hyp-benches` records Founder-approved PROXY HYP-01/03/07
benches, one-command runner, partner zip, METHODS_CRITIQUE docs, and read-only MCP.

| Delivery | Artifact | Commit |
| --- | --- | --- |
| CODEX-101 | HYP-01 MIT-BIH brady-def sensitivity | `af98247` |
| CODEX-102 | HYP-03 Fantasia short-window HRV/LF-HF | `6318771` |
| CODEX-103 | HYP-07 Fantasia age-band HRV stability | `f0f7692` |
| CODEX-104 | One-command PROXY HYP runner | `d0b3988` |
| CODEX-105 | PROXY HYP runner CI smoke | `385b812` |
| CODEX-106 | ARTIFACTS_INDEX + founder KR pack | `b710db6` |
| CODEX-107 | METHODS_CRITIQUE prominence | `628911e` |
| CODEX-108 | PROXY HYP partner zip (docs/JSON/MD only) | `3025cca` |
| CODEX-109 | PROXY HYP MCP list/run + stdio smoke | `e2c3d6d` |

`clinical_validation=false` · PROXY≠DS · PI_TO_DEFINE · RQ-004 HYPOTHESIS · LF/HF not primary · no BIDMC/Airway/PHI waveforms in partner pack · no pooled instability score.

The prior tip `v2.0-hospital-demo-ready` remains the hospital-demo packaging freeze;
this tip adds the PROXY Analysis Plan engineering track without expanding clinical claims.

## PROXY hyp guards freeze (CODEX-111–114)

Tip freeze `v2.2-proxy-hyp-guards` records Auditor DUAL-GATE wording + runner stamps +
fail-closed doc pins + hospital-demo founder cross-links. No new HYP benches.

| Delivery | Artifact | Commit |
| --- | --- | --- |
| CODEX-111 | Founder-pack Auditor DSCS wording | `9e7dce8` (tip `e374856`) |
| CODEX-112 | Runner JSON/MD Auditor DUAL-GATE stamps (schema 1.1) | `666bc98` |
| CODEX-113 | Fail-closed string pins in PROXY_HYP_RESULTS_KR + ARTIFACTS_INDEX | `0f2b649` |
| CODEX-114 | Hospital-demo founder docs → v2.1 + 111 labels | `870d4b8` |

`clinical_validation=false` · HYP-01 PARTIALLY_SUPPORTED · HYP-03/07 STRETCH/neg-control-QA · Airway+BIDMC do-not-run · PI_TO_DEFINE · no clinical FACT.

Prior tip `v2.1-proxy-hyp-benches` remains the benches/runner/pack/MCP packaging freeze (101–109).

## Meeting one-pager freeze (CODEX-116–118)

Tip freeze `v2.3-meeting-onepager` records the Founder meeting one-pager, its
ARTIFACTS pointer, and its inclusion in the PROXY HYP partner pack. No new HYP benches.

| Delivery | Artifact | Commit |
| --- | --- | --- |
| CODEX-116 | Founder meeting one-pager — PROXY v0.1 (KR) | `e57fd2b` |
| CODEX-117 | ARTIFACTS_INDEX pointer to meeting one-pager | `8ebf510` |
| CODEX-118 | Partner pack includes meeting one-pager | `360db7d` |

`clinical_validation=false` · Auditor DUAL-GATE labels retained · no FACT · no BIDMC/Airway expansion · Path B / RUO / Shadow Mode.

Prior tip `v2.2-proxy-hyp-guards` remains the DUAL-GATE guards freeze (111–114); pack body starts at `e57fd2b` and the post-include tip is `360db7d`.

## Meeting / hospital-demo links freeze (CODEX-122–124)

Tip freeze `v2.4-meeting-demo-links` records hospital-demo Founder links to the
meeting one-pager, the UNIFIED_MCP claim-guard mention, and fail-closed hospital-demo
pack CI/unit assertions. No new HYP benches.

| Delivery | Artifact | Commit |
| --- | --- | --- |
| CODEX-122 | Hospital-demo Founder docs link `MEETING_ONEPAGER_PROXY_v0.1_KR.md` | `eb1f5e5` |
| CODEX-123 | UNIFIED_MCP meeting one-pager + claim-guard mention | `46a6b62` |
| CODEX-124 | Hospital-demo pack CI/unit asserts meeting one-pager staging | `c6806e1` |

`clinical_validation=false` · Auditor DUAL-GATE retained · no FACT · no new HYP benches · no BIDMC/Airway · Path B / RUO / Shadow Mode.

Prior tip `v2.3-meeting-onepager` remains the meeting one-pager freeze (116–118); the `v2.4-meeting-demo-links` tip SHA is `c6806e1`.

## Meeting demo harness freeze (CODEX-125–127)

Tip freeze `v2.5-meeting-demo-harness` records the prior freeze documentation, a
portable hospital-demo unit harness, and direct demo/founder meeting-one-pager links.
No new HYP benches.

| Delivery | Artifact | Commit |
| --- | --- | --- |
| CODEX-125 | Record `v2.4-meeting-demo-links` freeze | `877f582` |
| CODEX-126 | Hospital-demo unit harness prefers engine venv Python when needed | `3ae0026` |
| CODEX-127 | `DEMO.md` + founder README meeting-one-pager cross-links | `c601b11` |

`clinical_validation=false` · Auditor DUAL-GATE retained · no FACT · no new HYP benches · no BIDMC/Airway · Path B / RUO / Shadow Mode.

Prior tip `v2.4-meeting-demo-links` covers 122–124; the `v2.5-meeting-demo-harness` tip SHA after CODEX-127 is `c601b11`.

## Meeting pack / MCP freeze (CODEX-128–132)

Tip freeze `v2.6-meeting-pack-mcp` records meeting-one-pager pack visibility and
documentation pins on base `3a5589f`, plus the visible in-tree Path B / RUO / Silent
Shadow business-document refresh. No new HYP, BIDMC, or Airway work.

| Delivery | Artifact | Commit / state |
| --- | --- | --- |
| CODEX-128 | PROXY HYP pack README notes the meeting one-pager | `38f2cea` |
| CODEX-129 | Unit pin for hospital-demo Founder-document meeting-one-pager links | `a66ac5d` |
| CODEX-130 | Record `v2.5-meeting-demo-harness` freeze | `3a5589f` |
| CODEX-131 | Path B / RUO / Silent Shadow v0.2 business refresh, versioned copies, and pack help text | in-tree |
| CODEX-132 | PROXY HYP MCP tool help pins the meeting one-pager and claim guards, with unit/stdio pins | in-tree |

`clinical_validation=false` · Auditor DUAL-GATE retained · no FACT · no new HYP/BIDMC/Airway · Path B / RUO / Shadow Mode.

Freeze base is `3a5589f`; CODEX-131/132 are recorded as visible in-tree edits and are not assigned invented commit SHAs.

## Meeting pack / MCP follow-up freeze (CODEX-134–135)

Tip freeze `v2.7-meeting-pack-mcp-followup` records the visible in-tree follow-up on
committed base `76779ec` (the CODEX-131–133 tip). No new HYP, BIDMC, or Airway work.

| Delivery | Artifact | Commit / state |
| --- | --- | --- |
| CODEX-134 | PROXY HYP runner appends the guarded meeting-one-pager pointer to its Markdown output | in-tree |
| CODEX-135 | PROXY HYP / hospital-demo smoke workflows include meeting-one-pager claim/link checks and document triggers | in-tree |

`clinical_validation=false` · Auditor DUAL-GATE retained · no FACT · no new HYP/BIDMC/Airway · Path B / RUO / Shadow Mode.

Freeze base is `76779ec`; CODEX-134/135 are visible in-tree edits and are not assigned invented commit SHAs.

## Meeting tip sync freeze (CODEX-137–138)

Tip freeze `v2.8-meeting-tip-sync` records the visible in-tree Path B / RUO /
Silent Shadow business-document sync on committed base `a0aa6dd` (the
CODEX-134–136 tip). No new HYP, BIDMC, or Airway work.

| Delivery | Artifact | Commit / state |
| --- | --- | --- |
| CODEX-137 | Meeting/founder/MCP/partner-pack references sync to `v2.7-meeting-pack-mcp-followup` (`a0aa6dd`) | in-tree |
| CODEX-138 | Path B / RUO / Silent Shadow v0.2 Founder/PI business-document refresh and versioned copies | in-tree |

`clinical_validation=false` · Auditor DUAL-GATE retained · no FACT · no new HYP/BIDMC/Airway · Path B / RUO / Shadow Mode.

Freeze base is `a0aa6dd`; CODEX-137/138 are visible in-tree edits and are not assigned invented commit SHAs.
