# Implementation assumptions

This file records assumptions made so implementation can proceed without silently
inventing clinical claims.

1. The prototype is Research Use Only and runs in shadow mode. No output is suitable
   for diagnosis, treatment, dosing, alarm replacement, or patient monitoring.
2. Public VitalDB cases are adult perioperative data unless their public metadata says
   otherwise. They are treated as `unknown_or_non_ds`; no Down syndrome or pediatric
   performance is inferred.
3. `GENERIC_VALIDATION_MODE` validates signal processing and generic research-event
   plumbing. `DS_HYPOTHESIS_MODE` uses the same deterministic pipeline only to visualize
   within-person change; it never emits a DS clinical probability.
4. Waveforms are resampled to 100 Hz for this 24-hour prototype. Raw inputs are retained
   separately and provenance records each transform.
5. Baseline defaults to the first 180 seconds. Tests may explicitly shorten it to keep
   the test suite fast; this does not change the production default.
6. ECG is the preferred beat source. PPG may support degraded operation when ECG is
   unavailable, but low quality or too few beats always withholds the index.
7. MAP may come from an ABP waveform or a numeric trend. Missing optional modalities
   reduce confidence; missing all hemodynamic trend information invalidates the index.
8. The adult generic hypotension candidate (`MAP < 65 mmHg` for at least 60 seconds) is
   a research label v0, not a DS or pediatric clinical endpoint.
9. The deterministic weighted index is intentionally transparent and uncalibrated. Its
   thresholds are engineering hypotheses pinned in configuration, not learned clinical
   cut points.
10. The VitalDB adapter uses public, read-only endpoints and preserves CC BY 4.0
    attribution. Network, package, or track failures fall back to an explicitly labeled
    synthetic local fixture when requested; fallback data is never represented as
    remotely loaded or as a real patient record.
11. Drug events or infusion rates, when present, are metadata only and never become a
    dosing recommendation or a control signal.
12. No PHI is accepted or persisted. Replay sessions are in-memory and are cleaned up
   after completion or cancellation.
