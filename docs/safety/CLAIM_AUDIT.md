# Claim audit

Audit date: 2026-09-02. Scope: every tracked source, UI string, HTML page, model card, README, and Markdown/CSV/YAML research artifact. Search terms included `prevent`, `predict`, `safe`, `optimize`, `diagnosis`, `treatment`, `dosing`, `recommendation`, `Down syndrome specific`, `DS-specific`, `bradycardia prediction`, `hypotension prediction`, `cardiac arrest`, `propofol`, `atropine`, `ephedrine`, and `phenylephrine`, including common inflections.

Classification applies to the sentence in context. Negated limitations, method names, literature summaries, and prohibited-copy test patterns are not product efficacy claims.

## Material claims

| Claim or claim family | Location | Classification | Audit disposition |
|---|---|---|---|
| The runtime index is deterministic, fixed-weight, local, and contains no LLM | `services/engine`, model card, root README | VERIFIED | Confirmed in executable path and registry |
| Invalid quality/baseline/timestamp/dropout/latency input withholds a score | engine quality, uncertainty, replay, synthetic safety tests | VERIFIED | Covered by backend tests; invalid means `score=null`, `level=INVALID` |
| API replay state is in-memory and request bodies are not persisted | `services/api` | VERIFIED | No database, file write, telemetry, or external inference client exists |
| VitalDB is an adult intraoperative public source suitable for generic adapter research | dataset registry and adapter | LIMITED_EVIDENCE | Source metadata verified; no T21 Safe clinical performance established |
| MIMIC/BIDMC data can support generic signal-processing checks | research docs | LIMITED_EVIDENCE | ICU/adult setting must remain explicit; prohibited for anesthesia or DS validation |
| Healthy-volunteer propofol/PTT/Fantasia data can support narrow feature implementation checks | research docs | LIMITED_EVIDENCE | Never use for clinical-event, pediatric, or DS performance claims |
| Candidate autonomic/hemodynamic patterns may warrant DS cohort research | evidence summary/ledger and PRD | RESEARCH_HYPOTHESIS | Retain only with explicit uncertainty and prospective validation plan |
| `DS_HYPOTHESIS_MODE` represents a DS-specific calibrated model | any implied reading of mode name | UNSUPPORTED | UI/model card explicitly state no DS calibration; mode only reduces confidence |
| “Patient-specific perioperative safety intelligence … starting with Down syndrome” | former root/UI tagline | PROHIBITED_PRODUCT_CLAIM | Removed; replaced with local-first physiological signal research wording |
| Current 0–100 index predicts a 120-second outcome | former `horizon_seconds` API field | UNSUPPORTED | Renamed `observation_context_seconds`; no target or forecast horizon exists |
| The system prevents complications, predicts arrest/bradycardia/hypotension, optimizes anesthetic dose, or recommends a drug | no approved product location | PROHIBITED_PRODUCT_CLAIM | Forbidden in UI, README, API, marketing, demo narration, and exports |
| Public non-DS adult data validate DS-specific performance | no approved product location | PROHIBITED_PRODUCT_CLAIM | Explicitly rejected throughout model/data/product documentation |

## Contextual term findings

- `prediction`/`predictor` in the statistical analysis and labeling protocols describes a possible future study design, leakage controls, or external competitor terminology. It is not a current product claim.
- Drug names in the evidence review and dataset descriptions document source contents or explicitly rejected treatment claims. No drug name affects the scoring code.
- `safety` in the brand name, safety-boundary headings, tests, and hazard controls describes governance. It must not be expanded into patient-benefit language.
- `diagnosis`, `treatment`, `dosing`, and `recommendation` occur predominantly in explicit negations and non-intended-use statements.
- Generic candidate label functions (`bradycardia_candidate`, `hypotension_candidate`) are research labeling utilities, not validated predictors and not used by the live deterministic index.

## Remediation completed

1. Removed the efficacy-adjacent root/UI “safety intelligence” tagline.
2. Replaced “monitoring prototype” wording with “signal-replay prototype” where it described the current product.
3. Replaced predictive `horizon_seconds` contract semantics with an observation context.
4. Bound online public adapters behind `OFFLINE_MODE=false` and retained source/population limitations.
5. Kept the research disclaimer literal across API, UI, SSE, exports, and static pages.

## Residual review rule

Any new user-facing copy matching the audit terms requires clinical-safety review. Research documents may use the terms only when the subject, evidence level, population, setting, and non-product status are explicit. See `PROHIBITED_CLAIMS.md` for the denylist.
