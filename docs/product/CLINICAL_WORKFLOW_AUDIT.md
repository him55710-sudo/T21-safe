# Clinical workflow audit

Perspective: anesthesiology research reviewer. Scope: start, context, calibration, live replay, explanation, review, evidence, and export flows. This is not a clinical-use validation.

| Question | Finding | Status/action |
|---|---|---|
| Is research-only use clear on first view? | Persistent top disclaimer and start-screen limitations are present | PASS for prototype copy; comprehension study still required |
| Do waveforms and signal quality remain visible? | Live view shows ECG/PPG/ABP, numerics, per-signal SQI, and overall quality | PASS; verify hierarchy with clinicians at target resolution |
| Does one number dominate? | A 0–100 index and status color remain prominent | PARTIAL; retained as required research output but accompanied by raw signals, quality, trend, reasons, and evidence |
| Is index rise explained? | Explanation view lists feature contributions and uncertainty reasons | PASS for transparency; feature labels need clinician usability testing |
| Can signal loss look like deterioration? | Invalid quality hides score and renders `INVALID`; missing-signal fixture exists | PASS in tests; add real device disconnect testing |
| Is alarm fatigue likely? | Sound is off and no patient-care alarm exists; WATCH/ELEVATED/HIGH could still be interpreted as alarm states | RISK; label as research bins and test overreliance |
| Does UI direct treatment? | No medication/dose/action recommendation is rendered; forbidden-copy scan/tests exist | PASS |
| Can a public demo be mistaken for DS data? | Cases expose `verified_ds=false`; UI distinguishes synthetic/public/local fixture and states no DS validation | PASS after integration label fix |
| Can baseline be bypassed? | No override; index hidden until calibration and quality gates pass | PASS |
| Does detailed patient context leave the browser? | API start request sends only case/mode/speed/baseline | PASS; local export still requires governance |
| Does real API integrate with UI? | Case/evidence/frame normalizers and custom SSE handlers added; Docker now uses actual engine API | PASS in contract tests; browser E2E required for final verification |

## Workflow assessment

The linear start → pseudonymous context → 180-second baseline flow is appropriate for research replay. The live screen keeps raw evidence near the derived index, and the explanation/evidence screens reduce opacity. The interface must remain shadow-only: no bedside alarm routing, order entry, pump control, procedural clearance, or implied response checklist may be added.

## Required clinician review tasks

1. Confirm that users understand `WATCH`, `ELEVATED`, and `HIGH` as unvalidated research bins.
2. Test whether color/size causes attention to leave waveforms and SQI.
3. Test missing signal, delayed packet, baseline failure, reconnect, and replay-complete states.
4. Confirm that public, local fixture, synthetic, and future hospital data are never confused.
5. Validate terminology, units, explanation usefulness, and export interpretation with anesthesiologists and research coordinators.
