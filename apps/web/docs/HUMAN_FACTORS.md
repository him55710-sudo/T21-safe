# Human factors and alert design

## Design controls in this prototype

- Invalid-before-risk: a missing baseline, low SQI, absent composite input, or backend-invalid result removes the number and shows `INDEX HIDDEN` with reasons.
- Redundant encoding: levels use words, bounded shapes, direction symbols, patterns, and color. No interpretation depends on hue alone.
- Stable motion: no flashing, pulsing alert, or automatic zoom is used. Canvas lines update at replay cadence without animating layout.
- Trend over spike: the trend label summarizes a recent valid window and explicitly states that it is not based on one spike.
- Context near score: confidence, overall SQI, baseline deltas, top reasons, and population limitation remain in the same column.
- Action separation: manual notes are research annotations. Medication events are source metadata. Neither records a completed intervention.
- Audio default: sound is unavailable and visibly labeled off.

## Cognitive forcing functions

1. The user must select and inspect a data source.
2. Structured patient context precedes baseline.
3. Baseline has no unsafe override.
4. Low quality visually replaces, rather than merely annotates, a score.
5. The explanation screen changes the question from “what should I do?” to “which measured change moved this research output?”
6. Evidence and population limits are persistent navigation peers, not hidden settings.

## Automation-bias mitigations

- “Research Instability Index” is not named as a diagnosis or outcome prediction.
- Score is paired with raw waveforms and measured vitals.
- Confidence and limitations are always adjacent.
- Reason statements describe change from baseline, not a disease mechanism.
- `Review the complete patient context` is used instead of an action command.
- Public data and DS hypothesis mode carry explicit non-validation language.

## Accessibility

- Body and status text use high-luminance foregrounds on dark backgrounds; status text is never encoded by low-contrast color alone.
- Interactive controls have a 3px visible focus ring.
- Semantic headings, fieldsets, progressbar attributes, dialogs, table roles, and accessible Canvas labels are included.
- Monitor density is optimized for the requested 1920×1080 display; mobile fallback preserves content but is not a bedside-use target.

## Validation still required

- Formal WCAG contrast measurement on the production display profile.
- Simulated-use testing with anesthesiologists, including invalid-state recognition and explanation comprehension.
- Alarm philosophy review under the intended regulatory pathway.
- Response-time, workload, and fixation testing at representative OR lighting and viewing distance.
- Localization and abbreviation comprehension review.
