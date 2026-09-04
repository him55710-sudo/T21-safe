# Schema/Clock Pilot Acceptance

**Status:** DRAFT · pre-extract research gate  
**Scope:** 1–3 synthetic or IRB/DUA-authorized deidentified cases  
**Boundary:** This gate evaluates extract mechanics and time semantics only. It does not validate a clinical definition, model, score, threshold, weight, or DS-specific performance.

## 1. Purpose

Use a deliberately small pilot before accepting a hospital-scale extract. The pilot must show that records can be interpreted, linked, time-aligned, audited, and reproduced without direct identifiers. A pilot `PASS` authorizes only a recommendation to continue governance review for a larger extract; it does not authorize that extract by itself.

## 2. Preconditions

- The PI or delegated protocol owner has documented the research question and minimum sources needed.
- The institution has confirmed whether the sample is synthetic or deidentified and what IRB/DUA/security terms apply.
- A data steward, technical contact, reviewer, and decision owner are named.
- Transfer location, access list, retention period, and deletion/return procedure are approved.
- The sample contains no direct identifiers or unnecessary free text. Dates use an approved transformation while preserving documented within-case intervals when required.

If any precondition is missing, record `HOLD`; do not compensate by requesting more cases.

## 3. Required pilot package

| Package item | Minimum evidence |
| --- | --- |
| Data dictionary | Field name, type, unit, null/sentinel meaning, source, version |
| Schema examples | Valid record per supplied table/file type; relation keys described |
| Source inventory | System, device, channel, software/firmware/schema version where available |
| Time semantics | timezone or relative origin, timestamp type, precision, source clock, date-shift behavior |
| Clock evidence | synchronization method, known offset/drift/outage, correction history, uncertainty |
| Case linkage | pseudonymous patient/case/source keys and repeated-case rule |
| Extract provenance | query/spec version, extraction time, responsible system, file checksum |
| Governance manifest | synthetic/deidentified status, authorization reference, permitted use, retention |

## 4. Acceptance checks

Each check receives `PASS`, `FAIL`, `HOLD`, or `NOT_APPLICABLE`, with evidence location and reviewer. Do not replace missing evidence with assumptions.

| ID | Check | Acceptance evidence | Fail-closed response |
| --- | --- | --- | --- |
| SC-01 | Files match the declared schema and version | deterministic parse; required fields/types reported | stop ingestion; request corrected sample/schema |
| SC-02 | Units and sentinel/null meanings are explicit | dictionary-to-record comparison; unmapped values listed | quarantine affected fields; do not impute |
| SC-03 | Patient, case, and source relations are unambiguous | key cardinality and duplicate report | stop linkage; resolve merge/split rules |
| SC-04 | Sample counts and waveform headers agree | expected vs observed rows/samples/rates | quarantine mismatch; preserve original |
| SC-05 | Source/schema changes are represented | version/change-point inventory | stratify or request provenance; no silent pooling |
| CL-01 | Every timestamp has documented semantics | UTC offset/timezone or relative origin and precision | withhold cross-source ordering |
| CL-02 | Source clocks can be compared | offset, sync method, uncertainty and correction status | mark alignment unusable |
| CL-03 | Drift, resets, outages, and discontinuities are detectable | known-event log or deterministic continuity report | segment or exclude affected interval from pilot use |
| CL-04 | Cross-source ordering is reproducible | rerun produces the same aligned order and audit output | stop; correct transform/versioning |
| CL-05 | Deidentification preserves only authorized intervals | method note and interval spot-check without exact dates | stop transfer/use; escalate to data steward |
| GV-01 | Direct identifiers and unnecessary free text are absent | automated inventory plus human spot-check | restrict access; follow approved return/deletion process |
| GV-02 | Provenance and checksums reproduce | manifest verification on an independent rerun | reject package until corrected |

No universal clock tolerance or clinical plausibility cutoff is defined here. Any numeric tolerance must come from the approved protocol and source-specific evidence, be versioned, and be reviewed before use.

## 5. Decision rule

- `PASS`: every applicable check passes and no privacy/governance hold remains.
- `CONDITIONAL`: only explicitly documented, non-critical metadata gaps remain; owner and due date are recorded, and affected fields stay quarantined.
- `FAIL`: any schema ambiguity, irreproducible transform, unusable required clock relationship, direct identifier exposure, or authorization conflict remains.
- `HOLD`: governance authority or required evidence is pending.

`CONDITIONAL` and `PASS` do not authorize clinical interpretation. A larger extract requires a separate PI, IRB/DUA, security, and data-owner disposition.

## 6. Acceptance record

```text
Pilot ID (pseudonymous):
Sample type: SYNTHETIC | DEIDENTIFIED
Institution/source:
Authorization reference (no credentials/PHI):
Schema and extract version:
Manifest/checksum location:
Checks SC-01..GV-02:
Decision: PASS | CONDITIONAL | FAIL | HOLD
Open gaps and quarantined fields:
Reviewer(s) / role / date:
PI disposition:
Data steward disposition:
Permitted next step:
Retention/deletion date or rule:
```

Related documents: [Hospital Aggregate Feasibility Query](../business/HOSPITAL_AGGREGATE_FEASIBILITY_QUERY_KR.md), [Hospital Data Request Spec](HOSPITAL_DATA_REQUEST_SPEC.md), [Labeling Protocol](LABELING_PROTOCOL.md), and [PI Decision Pack](../founder/PI_DECISION_PACK_KR.md).
