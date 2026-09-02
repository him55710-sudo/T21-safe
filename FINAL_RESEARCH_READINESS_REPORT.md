# T21 Safe final research readiness report

Audit date: 2026-09-02

## Conclusion

**READY_FOR_TECHNICAL_DEMO**

The integrated repository can run a local synthetic or bounded public-waveform
technical demonstration with deterministic processing, explicit provenance, a
quality-gated index, and a local dashboard. It is not ready for clinician evaluation,
retrospective DS research, prospective shadow deployment, or any clinical use.

The decisive limitation is evidence, not software polish: no DS cohort has been
loaded, no patient outcome target has been defined, no model has been fitted, no
clinical probability has been calibrated, and no internal or external performance
study has been completed.

## Readiness scores

| Area | Score | Current state and evidence | Critical gap | Next action |
| --- | ---: | --- | --- | --- |
| Clinical evidence readiness | 2/10 | Structured evidence ledger, PICOTS, protocol, labeling plan, and explicit unsupported-claim boundaries exist. | No DS patient cohort, adjudicated outcome labels, clinical effect estimate, or clinician usability evidence. | Secure IRB/data governance review and perform blinded descriptive feasibility work before model development. |
| Dataset readiness | 6/10 | Registry tracks 13 sources across 30 provenance/license/use fields; bounded allowlisted downloads and SHA-256 manifests are tested. | No approved DS dataset; several sources are ICU, adult-only, healthy-volunteer, restricted, or lack DS-identifying variables. | Obtain an institution-approved perioperative DS cohort and freeze a patient-level manifest/data dictionary. |
| Signal pipeline readiness | 7/10 | Deterministic ECG/PPG/ABP preprocessing, raw-signal SQI, baseline gate, gap/latency/order/synchronization gates, and 14 required synthetic safety scenarios pass. | No reference-tool agreement study, device-specific bench testing, prospective latency characterization, or pediatric artifact validation. | Run version-frozen bench and retrospective waveform validation against independent reference implementations. |
| Model readiness | 3/10 | The index is transparent and versioned; feature lineage, units, confounders, OOD behavior, patient-level splits, and withheld-output behavior are documented/tested. | `rii-v0.1` is an unfitted engineering hypothesis with no target, horizon, calibration, discrimination, threshold, or external validation. | Predeclare target/horizon and analysis plan, then develop only on an approved patient-level development split. |
| Product readiness | 7/10 | Research status is prominent; waveforms/quality precede interpretation; reasons, provenance, invalid states, DS limitations, completion state, and local export are visible. Type/lint/unit/E2E/build and 1920×1080 browser checks pass. | No clinician simulated-use study, formal alarm/usability validation, responsive target-device qualification, or production authentication. | Conduct formative anesthesia-clinician review using synthetic cases only and close human-factors findings. |
| Local security readiness | 5/10 | Offline is default; remote adapters are hidden/blocked; no cloud/LLM/telemetry path exists; local CORS, non-root web, read-only API container, and retention/threat policies are documented. | No implemented RBAC, local TLS, session timeout, immutable audit sink, encrypted backup workflow, secrets governance, or penetration test. | Build the institution-owned security controls and threat-model verification before any patient-derived data. |
| Hospital PoC readiness | 3/10 | Native API/dashboard and offline synthetic workflow run locally; architecture supports one workstation or isolated LAN. | Docker runtime is unverified on this host and there is no hospital identity, DICOM/device gateway, deployment qualification, support procedure, or approved data path. | Verify signed containers on hospital-like hardware, complete security review, and define a non-clinical engineering PoC acceptance plan. |
| Regulatory documentation readiness | 5/10 | Intended-use draft, FDA CDS analysis, MFDS questions, standards map, hazards, risk register, and prohibited claims are present. | Documents are drafts without sponsor decisions, classification determination, traceable verification records, quality system, or regulator feedback. | Obtain regulatory counsel/RA review and convert drafts into controlled documents only after intended use is frozen. |

Overall unweighted readiness is **4.8/10**. A mean score is not a safety claim and
must not be used as a release gate; the lowest evidence and hospital-control domains
govern the allowed use.

## Answers to the ten repository questions

1. **What does it do?** It replays synthetic, local-fixture, or explicitly enabled
   public waveform data; preprocesses signals; evaluates quality; calibrates a
   180-second within-subject baseline; extracts physiological change features; and
   renders a bounded deterministic research index with reasons and provenance.
2. **What does it not do?** It does not diagnose, predict a clinical outcome, prevent
   a complication, optimize or recommend drugs/doses, replace alarms, control a
   device, or support patient-care decisions.
3. **What data built it?** No dataset trained the current index. Synthetic fixtures
   built and verify the executable path; public datasets are cataloged for bounded
   generic signal-processing work only.
4. **What may each dataset be used for?** The per-source boundaries are authoritative
   in `research/dataset_registry.yaml` and `docs/data/DATA_USAGE_BOUNDARIES.md`.
   Setting, population, access, and license restrictions are not interchangeable.
5. **What is DS-specific and validated?** Nothing in model performance. DS status can
   select a visibly limited hypothesis display mode; this is metadata handling, not
   validation.
6. **What remains a hypothesis?** All DS physiological rationale, feature relevance,
   weights, score meaning, event target, target horizon, threshold, and intervention
   value.
7. **How is the score produced?** Version-pinned weighted contributions use relative
   HR decline, relative MAP decline, relative PPG amplitude decline, adverse HR/MAP
   slopes, and low SpO2 after baseline/quality/OOD gates. It is not a probability.
8. **How does it fail safe?** Low SQI, missing required modalities, incomplete or
   unstable baseline, excessive gaps, reported dropout, source latency over 1,000 ms,
   synchronization error over 100 ms, out-of-order timestamps, insufficient beats,
   and OOD values withhold the numeric score or reduce confidence as specified.
9. **Does patient data leave the machine?** The supported offline path does not send
   waveforms or PHI externally. Public acquisition is an explicit separate online
   action. This prototype has no approved PHI storage path, so patient PHI must not be
   entered.
10. **Can a hospital researcher start a research PoC?** They can start a synthetic
    technical demo and inspect bounded public data. They cannot start a patient-data
    PoC until IRB/data governance, security controls, deployment qualification,
    container verification, identity/audit/retention controls, and study approvals
    are complete.

## Audit disposition

- Claims: unsupported positive product claims removed; prohibited claims centralized.
- Data: provenance/use/license matrix reconciled; propofol dataset terms corrected;
  patient-level split and no-test-tuning boundaries are explicit.
- Model: forecast-like `horizon_seconds` semantics removed in favor of observation
  context; no clinical probability language remains in the runtime contract.
- Signals: raw waveform artifacts, dropout, latency, order, synchronization, missing
  modality, and confidence gates were strengthened and tested.
- Integration: the temporary API shim was removed; Docker and browser now target the
  real versioned API; custom SSE events and response-shape normalization are tested.
- Security: offline operation is default and network adapters are unavailable in that
  mode; local hardening controls remain design requirements, not implemented claims.
- Reproducibility: native services, synthetic replay, public sample replay, manifests,
  tests, build, browser flow, accessibility scan, and export were exercised. Docker
  runtime remains explicitly unverified because Docker was unavailable.
