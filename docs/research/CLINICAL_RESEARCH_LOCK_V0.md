# Clinical Research Lock v0

**Status:** Draft lock table — clinical cells are `PI_REQUIRED` / `PI_TO_DEFINE`  
**Date:** 2026-09-04 (KST)  
**Path:** B / RUO / Shadow / `clinical_validation=false`  
**Eng tip HEAD:** `edff0f1`  
**Rule:** Do **not** invent clinical fills. Options listed for PI; code thresholds stay ENGINEERING_DEFAULT until Founder/PI unfreezes.

> Research Use Only. No dosing, closed-loop, FACT elevation, or DS performance claims from PROXY.

Related: [`RESEARCH_PRD.md`](RESEARCH_PRD.md), [`PICOTS.md`](PICOTS.md), [`CLINICAL_QUESTIONS.md`](CLINICAL_QUESTIONS.md), [`../safety/PROHIBITED_CLAIMS.md`](../safety/PROHIBITED_CLAIMS.md), [`../founder/T21_REFOCUS_DECISION_KR.md`](../founder/T21_REFOCUS_DECISION_KR.md).

---

## Decision table

| Decision | Status | Options (PI_REQUIRED) | Notes |
| --- | --- | --- | --- |
| Primary endpoint family | `PI_REQUIRED` | (A) Absolute bradycardia event rate (pre-defined abs HR); (B) Relative HR decline from patient baseline; (C) Composite hemodynamic instability (HR+MAP±SpO2) with pre-specified hierarchy; (D) Time-to-first adjudicated event under Shadow | Do not pick from PROXY HYP-01 PASS. Concordance null until thresholds locked. |
| Study population | `PI_REQUIRED` | (A) Pediatric DS anesthesia/sedation only; (B) DS + matched non-DS same site/era; (C) Age-stratified pediatric vs young adult DS separate analyses; (D) Phase-0 public non-DS technical cohort only (no clinical estimand) | PROXY PhysioNet ≠ OR DS. Phase 0 remains technical. |
| Windowing / observation context | `PI_REQUIRED` | (A) Align to eng defaults: feature windows 30/60/180s, baseline 180s, observation_context 120s (`PipelineConfig` / `RiskConfig`); (B) Protocol-first windows (e.g. 60/120/300s) then re-pin eng; (C) Metric-specific minima (HRV ≥180s separate from RII update 1s) | Eng values are ENGINEERING_DEFAULT, not clinical lock. Recalibration after events forbidden. |
| Bradycardia — absolute threshold | `PI_REQUIRED` | (A) Age-band absolute HR cutoffs (PI table TBD); (B) Single absolute cutoff for defined age band only; (C) Absolute + duration (e.g. HR < X for ≥ T s); (D) Defer absolute; relative-only primary | Meeting one-pager: abs/rel = `PI_TO_DEFINE`; concordance=null. |
| Bradycardia — relative threshold | `PI_REQUIRED` | (A) Keep eng probe `-20%` (`RiskConfig.relative_hr_decline_pct`) as research flag only; (B) PI-chosen relative decline % + duration; (C) Percentile vs patient baseline distribution; (D) Dual abs+rel with OR/AND rule | Eng `-20%` is not clinical validation. |
| HRV role | `PI_REQUIRED` | (A) Exploratory / neg-control QA only (`lf_hf_primary=false`); (B) Secondary endpoint family after length/SQI gates; (C) Exclude from primary RII and claims; (D) Time-domain only short windows; withhold LF/HF if <180s | PROHIBITED: HRV as peri-op instability biomarker from PROXY. HYP-03 STRETCH if claimed positive. |
| SpO2 / Airway context | `PI_REQUIRED` | (A) SpO2 as RII context weight only (eng `spo2_reference_pct=94`, weight 10) — research bin; (B) Separate airway/desaturation endpoint with PI defs; (C) Do-not-run until BIDMC/usability gate; (D) Require EtCO2/airway event lane before SpO2 endpoint | Meeting: Airway/SpO2/BIDMC = do-not-run until usability evaluated. |
| BIDMC (and similar public PPG/resp sets) | `PI_REQUIRED` | (A) Usability gate first (license, annotation quality, alignment); (B) Technical SQI/alignment only after gate; (C) Explicit exclude from current Path B tip; (D) Schedule post-M0 Phase 0 work package | No clinical claim from BIDMC. |
| FACT elevation | `PI_REQUIRED` | (A) Remain false indefinitely under Path B until prospective silent gate; (B) Define Master FACT checklist (data, SAP, adjudication, lock) then Founder+PI sign-off; (C) Never elevate from PROXY fixture PASS | Fixture PASS ≠ Master FACT. `clinical_validation=false` stays. |
| Hypotension MAP / duration (eng present) | `PI_REQUIRED` | (A) Review eng `hypotension_map_mm_hg=65`, `duration_seconds=60` as literature-inspired defaults needing PI confirm; (B) Age/procedure-specific MAP; (C) Relative MAP decline primary (`-20%` eng probe) | Classify in provenance as ENGINEERING_DEFAULT / PI_REQUIRED — do not tune in code during freeze. |
| RII watch/elevated/high bins | `PI_REQUIRED` | (A) Keep 25/50/75 as research bins only with RUO labeling; (B) Freeze bins + forbid retune until Phase 3 SAP; (C) Replace numeric bins with ordinal research states without urgency UX | Not probability, alarm, or treatment threshold (`PROHIBITED_CLAIMS.md`). |
| DS_HYPOTHESIS_MODE / PROXY labeling | Lock reminder | N/A — already constrained | Must not be read as DS-specific activation or validation. |

---

## Freeze interaction

Until Founder unfreezes (`FREEZE_DECLARATION_M0.md`):

- No edits to `config.py` / `deterministic_index.py` values.
- No new PROXY benches or FACT language.
- PI meetings only narrow **Options** columns; acceptance recorded as amendment to this table (version bump `v0.1` …).

## Version

| Field | Value |
| --- | --- |
| Lock doc version | `v0` |
| Next | PI session → `v0.1` with narrowed options only (still no invented fills) |
