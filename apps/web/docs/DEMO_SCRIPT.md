# Demo script

## Setup

Use a 1920×1080 browser and `NEXT_PUBLIC_DEMO_MODE=true`. Confirm the research banner is visible and sound is off.

## Seven-minute flow

1. On Research Start, select **Progressive instability**. Point out the `SYNTHETIC` label, no-patient-data attribution, backend/mock status, and permanent research disclaimer.
2. Open dataset information. State that public data, when selected, are not verified DS cases and are only for demonstrating signal processing.
3. Start replay. On Patient Context, show explicit `unknown` values and available-signal controls. Explain that the prototype never infers DS or heart disease from waveforms.
4. Begin baseline. Emphasize that source time is 180 seconds even though demo replay is accelerated, and that there is no baseline bypass. The index remains hidden.
5. On Monitor, identify ECG, PPG, ABP, numeric units, per-signal SQI, event timeline, and sound-off state. Wait for WATCH and ELEVATED; describe this as sustained synthetic movement, not an alarm or patient-care recommendation.
6. Open Structured Explanation. Compare current, baseline, delta, quality, direction, and plain-language feature statements across the three groups.
7. Open Evidence. Show model/feature version, non-DS source population, DS data limitation, evidence ID, license, and known limitations.
8. Open Case Review. Show synchronized index/timeline, candidate event, research annotation (optional), and anonymized JSON export.
9. If time allows, restart with **ECG motion artifact** or **Missing PPG signal**. Demonstrate that `INVALID` replaces the number and gives a reason.

## Closing statement

“T21 Safe currently demonstrates a transparent, quality-gated research workflow. It has no DS-specific calibration and is not intended for patient-care decisions.”
