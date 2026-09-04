# Schema / Clock Pilot Acceptance — M0-B

**Status:** DRAFT · pre-extract research gate · checklist for 1–3 deidentified (or synthetic) schema/clock samples  
**Mode:** Path B / RUO / Shadow / `clinical_validation=false`  
**Tip freeze:** `edff0f1` — no RII/PROXY/threshold/MCP/feature code changes authorized  
**Related:** [`HOSPITAL_DATA_REQUEST_SPEC.md`](HOSPITAL_DATA_REQUEST_SPEC.md) §13 · [`HOSPITAL_AGGREGATE_FEASIBILITY_QUERY_KR.md`](../business/HOSPITAL_AGGREGATE_FEASIBILITY_QUERY_KR.md) · [`SIGNAL_EXTERNAL_VALIDITY_PLAN.md`](SIGNAL_EXTERNAL_VALIDITY_PLAN.md) · [`PI_DECISION_PACK_KR.md`](../founder/PI_DECISION_PACK_KR.md)

---

## 1. Purpose

Use a deliberately small pilot (1–3 cases) before accepting a hospital-scale extract. The pilot must show that records can be interpreted, linked, time-aligned, audited, and reproduced without direct identifiers.

A pilot engineering **PASS** authorizes only a recommendation to continue governance review. It does **not** mean clinical validation, FACT elevation, Lock completion, or extract approval.

**Agents never email the hospital or PI.** Founder sends/receives samples manually under site DUA/IRB.

---

## 2. Gate classes (do not mix)

| Class | Who decides | Examples |
| --- | --- | --- |
| **Engineering pass/fail** | Maintainer against §4 checks | Dictionary present, parse succeeds, no direct identifiers, clocks documented |
| **SITE_REQUIRED** | Site IT / honest broker / data steward | Timezone/NTP policy, export path, de-id method, device inventory, small-cell rules |
| **PI_REQUIRED** | PI (research science) | Whether modalities support Lock questions; authorization to propose larger extract |

**Rule:** Engineering PASS ≠ PI_REQUIRED satisfied. PI_REQUIRED OPEN ≠ automatic engineering FAIL if the site delivered a complete deidentified contract sample.

---

## 3. Preconditions

- [ ] Aggregate feasibility path acknowledged (or Founder+site written waiver)
- [ ] PI or delegated protocol owner documented research question and minimum sources (`PI_REQUIRED` if incomplete)
- [ ] Institution confirmed synthetic vs deidentified and IRB/DUA/security terms (`SITE_REQUIRED`)
- [ ] Data steward, technical contact, reviewer, decision owner named
- [ ] Transfer location, access list, retention, deletion/return approved (`SITE_REQUIRED`)
- [ ] Sample has no direct identifiers / unnecessary free text
- [ ] Tip freeze `edff0f1` still cited; no retune of RII/thresholds from this sample

If any precondition is missing, record `HOLD`; do not compensate by requesting more cases.

---

## 4. Required pilot package

| Package item | Minimum evidence | Owner class |
| --- | --- | --- |
| Data dictionary | Field name, type, unit, null/sentinel, source, version | Engineering / SITE |
| Schema examples | Valid record per table/file type; relation keys | Engineering |
| Source inventory | System, device, channel, software/firmware/schema version | SITE_REQUIRED |
| Time semantics | timezone or relative origin, timestamp type, precision, source clock, date-shift behavior | SITE_REQUIRED |
| Clock evidence | sync method, known offset/drift/outage, correction history, uncertainty | SITE_REQUIRED — **no invented drift cutoff** |
| Case linkage | pseudonymous patient/case/source keys; repeated-case rule | Engineering / SITE |
| Extract provenance | query/spec version, extraction time, responsible system, checksum | Engineering |
| Governance manifest | synthetic/deidentified status, authorization reference, permitted use, retention | SITE_REQUIRED |

---

## 5. Engineering acceptance checks (pass/fail)

Each check: `PASS` / `FAIL` / `HOLD` / `NOT_APPLICABLE` + evidence location. Do not invent numeric clinical or Hz cutoffs here.

| ID | Check | Fail-closed response |
| --- | --- | --- |
| SC-01 | Files match declared schema/version; deterministic parse | stop ingestion; request corrected sample |
| SC-02 | Units and sentinel/null meanings explicit | quarantine fields; do not impute |
| SC-03 | Patient/case/source relations unambiguous | stop linkage; resolve merge/split rules |
| SC-04 | Sample counts and waveform headers agree (or N/A schema-only) | quarantine mismatch; preserve original |
| SC-05 | Source/schema changes represented | stratify or request provenance; no silent pooling |
| CL-01 | Every timestamp has documented semantics | withhold cross-source ordering |
| CL-02 | Source clocks can be compared (method/uncertainty stated) | mark alignment unusable — **do not invent tolerance** |
| CL-03 | Drift/resets/outages detectable or explicitly unknown | segment/exclude; no invented threshold |
| CL-04 | Cross-source ordering reproducible on rerun | stop; correct transform/versioning |
| CL-05 | Deidentification preserves only authorized intervals | stop; escalate to data steward |
| GV-01 | Direct identifiers / unnecessary free text absent | restrict access; return/delete |
| GV-02 | Provenance and checksums reproduce | reject until corrected |

Any numeric clock tolerance must come from approved protocol / source-specific evidence (`SITE_REQUIRED` or `PI_TO_DEFINE`), be versioned, and be reviewed before use — **not invented in this checklist**.

---

## 6. SITE_REQUIRED gates (separate)

| Gate | Status | Site owner / date |
| --- | --- | --- |
| Export format and transfer path approved | OPEN | |
| Timezone / DST / device clock policy written | OPEN | |
| De-id / date-shift method preserves within-case alignment | OPEN | |
| Device/firmware inventory for sampled rooms | OPEN | |
| Small-cell / residual-risk policy for future aggregates | OPEN | |

---

## 7. PI_REQUIRED gates (separate from engineering)

| Gate | Status | PI / date |
| --- | --- | --- |
| Sample modalities sufficient to discuss Lock population/endpoint options | OPEN | |
| Missing phase anchors block intended feasibility questions? | OPEN | |
| Control/comparator relevance of non-DS fields if present | OPEN / N/A | |
| Authorization to propose larger extract after engineering PASS | OPEN | |

Do not mark these COMPLETE from agent judgment. Record options only via PI pack / Clinical Research Lock after PI review.

---

## 8. Decision rule

| Outcome | Meaning | Next step |
| --- | --- | --- |
| **PASS** | Applicable engineering checks pass; no privacy hold | Still need SITE/PI clearance for extract proposal |
| **CONDITIONAL** | Non-critical metadata gaps only; quarantines + owners/dates recorded | Do not expand extract scope silently |
| **FAIL** | Schema/clock/PHI/governance conflict | Site revises sample; no full extract |
| **HOLD** | Authority or evidence pending | Wait; agents do not chase hospital/PI by email |

Public non-DS PROXY benches and synthetic fixtures **do not** substitute for this pilot. PASS/CONDITIONAL do not authorize clinical interpretation or FACT.

---

## 9. Acceptance record

```text
Pilot ID (pseudonymous):
Sample type: SYNTHETIC | DEIDENTIFIED
Institution/source:
Authorization reference (no credentials/PHI):
Schema and extract version:
Manifest/checksum location:
Engineering checks SC-01..GV-02:
SITE_REQUIRED gates:
PI_REQUIRED gates:
Decision: PASS | CONDITIONAL | FAIL | HOLD
Open gaps and quarantined fields:
Reviewer(s) / role / date:
PI disposition:
Data steward disposition:
Permitted next step:
Retention/deletion date or rule:
Freeze tip cited: edff0f1
```

Related: [`HOSPITAL_AGGREGATE_FEASIBILITY_QUERY_KR.md`](../business/HOSPITAL_AGGREGATE_FEASIBILITY_QUERY_KR.md), [`HOSPITAL_DATA_REQUEST_SPEC.md`](HOSPITAL_DATA_REQUEST_SPEC.md), [`LABELING_PROTOCOL.md`](LABELING_PROTOCOL.md), [`PI_DECISION_PACK_KR.md`](../founder/PI_DECISION_PACK_KR.md), [`FREEZE_DECLARATION_M0.md`](../governance/FREEZE_DECLARATION_M0.md).
