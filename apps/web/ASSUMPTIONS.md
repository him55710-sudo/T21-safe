# Product UI assumptions

Last updated: 2026-09-02. These assumptions allow the product-ui branch to progress without inventing clinical behavior. They must be revisited with the signal-engine and research-data owners before any study use.

## Contract and integration

- The canonical browser contract is the Zod schema in `lib/contracts.ts`. Optional fields (`events`, per-signal quality, baseline values) extend the required core event without changing its required names or semantics.
- `NEXT_PUBLIC_DEMO_MODE=true` means the browser uses a deterministic local generator and never requires a backend. `false` means cases, replay creation, evidence, and SSE frames come from `NEXT_PUBLIC_API_URL`.
- The integrated repository uses `services/api` as the only Docker API target. `apps/web/lib/api.ts` validates and normalizes that versioned backend contract into the UI contract; no alternate shim is part of the runtime.
- Browser replay speed accelerates source time. A 180-second baseline remains a 180-second source interval even when displayed faster.
- EventSource reconnect uses bounded exponential backoff. A connection interruption changes the connection label but does not itself fabricate a risk state.

## Risk and quality behavior

- A research index is visible only when `baseline.calibrated`, `quality.usable`, `risk.valid`, and a numeric `risk.score` are all true.
- `BASELINE` is a workflow state with no numeric score. `INVALID` is an explicit suppression state, not a high or low risk level.
- Demo thresholds and reason ordering are deterministic fixture behavior only. API mode uses versioned output from `services/engine`; neither path defines clinical thresholds.
- Confidence describes model/input support for the current research output, not certainty about a patient outcome.
- Sustained movement is emphasized using recent-window trend direction; no UI alert is generated from one short spike.
- Default audio state is off and no audible alarm implementation is included.

## Down syndrome presentation

- A structured context value of “confirmed by clinical record” selects `DS_HYPOTHESIS_MODE`; it does not activate DS weights or claim validation.
- Public and synthetic cases are never described as verified DS cases.
- DS context is entered manually from an authorized study record. The interface does not infer DS, congenital heart disease, OSA, or anesthesia history from waveforms.

## Human factors and privacy

- The 1920×1080 layout is the primary design target; responsive layouts support review and testing but do not imply bedside-device certification.
- Color is redundant with text, icons, patterns, and level names.
- Manual acknowledgment is deliberately named “research annotation”; it never records that a patient-care action occurred.
- Medication events are read-only timeline metadata. No dose editing, simulation, or action language is present.
- Study subject IDs are assumed to be pseudonymous. Names, medical-record numbers, dates of birth, contact details, free-text patient histories, and other direct identifiers must not be entered or exported.
- Export is browser-local and contains the pseudonymous research context, frames, and annotations. Production research storage, retention, access control, and audit requirements remain outside this prototype.
