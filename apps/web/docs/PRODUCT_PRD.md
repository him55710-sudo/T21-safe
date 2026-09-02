# T21 Safe product requirements

## Product intent

T21 Safe is a research-only shadow-mode interface for investigating whether patient-specific perioperative signal trends can be organized safely for physiologically vulnerable cohorts, starting with Down syndrome research workflows.

The product helps a clinician-researcher answer four questions quickly:

1. Are the required signals present and usable?
2. Is the current physiology near or moving away from the subject-specific baseline?
3. Which measured feature changes moved the research index?
4. What evidence and population limitations constrain interpretation?

It does not direct patient care, infer diagnoses from waveforms, recommend medication changes, clear a procedure, or use an LLM in the risk path.

## Users and contexts

- Primary: anesthesiologist or perioperative clinician participating in an approved observational study.
- Secondary: clinical researcher reviewing an anonymized session.
- Technical: signal-engine investigator validating contract, quality gating, and deterministic replay.
- Environment: 1920×1080 research workstation or shadow display; not a certified bedside monitor.

## Product states

1. Research start: choose VitalDB public demonstration, synthetic scenario, or local fixture; inspect attribution and limitations.
2. Patient context: enter pseudonymous and record-derived context; unknown remains unknown.
3. Baseline: collect 180 source seconds; show progress, available signals, SQI, stability, values, and confidence; no bypass.
4. Live monitor: display Canvas waveforms and numeric vitals beside a quality-gated index, trend, reasons, confidence, baseline deltas, and limitations.
5. Structured explanation: group current/baseline/delta/quality/direction by rhythm/autonomic, perfusion/hemodynamics, and respiration/oxygenation.
6. Case review: synchronize trends, events, quality, and annotations; export an anonymized research-session artifact.
7. Evidence and data: expose versions, source population, DS data availability, evidence ID, license, model card, and protocol links.

## Safety requirements

- Every screen contains the research disclaimer through the persistent shell.
- Score display requires calibrated baseline, usable quality, valid risk, and numeric score.
- Invalid quality has higher visual priority than a previous score.
- State vocabulary is limited to BASELINE, STABLE, WATCH, ELEVATED, HIGH, and INVALID.
- Status uses text plus an icon or shape plus color.
- Sound is disabled and no sound-generation code exists.
- Medication events are metadata only.
- Public data are not represented as DS patient data.
- `DS_HYPOTHESIS_MODE` always exposes the no-DS-calibration statement.
- No LLM output can enter the stream-frame contract or calculate the index.

## Non-functional requirements

- Strict TypeScript and runtime Zod validation.
- Smooth Canvas waveform updates without thousands of DOM elements.
- SSE reconnect with bounded backoff.
- Browser-only mock operation.
- Production standalone build and non-root container.
- Keyboard-visible focus, semantic labels, 1920×1080 primary layout, and responsive fallback.
- No PHI in fixtures, logs, source, or exports.

## Acceptance

Acceptance is the repository Definition of Done: build, unit/integration tests, Playwright flow, invalid-state suppression, public/DS disclaimers, Docker composition, documentation alignment, and no prohibited action language in production output.
