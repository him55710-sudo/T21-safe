# Prohibited claims

These statements and reasonable paraphrases are prohibited in product UI, README/taglines, demonstrations, exports, marketing, API descriptions, and research recruitment material.

## Absolute denylist

- T21 Safe prevents complications in patients with Down syndrome.
- T21 Safe predicts cardiac arrest.
- T21 Safe accurately predicts bradycardia or hypotension.
- T21 Safe optimizes anesthetic or propofol dose.
- T21 Safe recommends atropine, ephedrine, phenylephrine, propofol, or any medication/action.
- A procedure is safe to proceed because of a T21 Safe output.
- A general hospital can safely anesthetize a patient with Down syndrome by relying on this system.
- Public non-DS, adult, ICU, perioperative, ambulatory, or healthy-volunteer data validate DS-specific or pediatric performance.
- The Research Instability Index is a probability, diagnosis, prognosis, alarm, treatment threshold, or validated forecast.
- `DS_HYPOTHESIS_MODE` is DS-specific activation, calibration, or validation.

## Required wording patterns

Use bounded language such as:

- “Research-only replay of physiological signal features.”
- “Candidate association for future validation.”
- “Generic technical validation on the named source population.”
- “No DS-specific calibration or clinical validation has been performed.”
- “Index withheld because input quality is insufficient.”
- “Review the raw waveform, signal quality, source context, and complete study protocol.”

Do not convert a prohibited claim into an implication through color, urgency, labels, icons, animations, or workflow placement. `WATCH`, `ELEVATED`, and `HIGH` are research bins only and must remain accompanied by the index name, quality state, explanation, and RUO boundary.

## Drug and action boundary

Medication events may be displayed as read-only retrospective research metadata after provenance and leakage review. Drug names, timing, or doses must not produce a score contribution, recommendation, “what-if” simulation, procedural clearance, or automated action. Post-index treatments are forbidden as predictors.

## Enforcement

`apps/web/scripts/check-forbidden.mjs` scans the production bundle for representative prohibited language. Automated scanning is only a backstop; a clinical-safety reviewer must review new user-facing copy and contextual implications.
