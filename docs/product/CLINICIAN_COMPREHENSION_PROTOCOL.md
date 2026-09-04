# Clinician Comprehension Protocol — M0-A

**Status:** Human-factors research protocol draft; PI/IRB review required before participants

**Mode:** RUO / Shadow. The interface is not a certified or validated patient monitor.

## Objective

Evaluate whether intended clinician participants correctly understand the display's research-only purpose, source-data limitations, signal-quality/invalid states, status vocabulary, uncertainty, and required reliance on complete clinical context. This protocol evaluates comprehension and foreseeable misuse; it does not test treatment efficacy or authorize patient-care decisions.

## Research questions

1. Do participants identify the display as observational research output rather than an alarm, diagnosis, prognosis, or treatment recommendation?
2. Do they withhold interpretation when baseline, signal quality, or backend output is invalid?
3. Can they distinguish measured change from a disease/outcome claim?
4. Do labels, trends, and explanations create anchoring, automation bias, or urgency beyond the evidence?
5. Which display option communicates uncertainty with the least hazardous misunderstanding?

## Participants and setting

The PI defines intended roles, experience bands, sample rationale, recruitment, consent, and compensation. Include relevant end users and, where appropriate, adjacent roles who may encounter the display. Use a simulated or non-care setting with synthetic, visibly labeled scenarios. No real patient records, care actions, or unapproved recording.

## Materials

- versioned prototype and build/commit identifier;
- randomized synthetic scenarios covering BASELINE, STABLE, WATCH, ELEVATED, HIGH, and INVALID;
- cases with missing baseline, unusable signal, backend invalidity, and recovery;
- neutral moderator guide, pre/post questions, observation form, and severity rubric;
- candidate display variants from [RII Display HF Options](../model/RII_DISPLAY_HF_OPTIONS.md).

Variants must use identical synthetic inputs. No variant changes the engine, clinical definition, weight, threshold, or status assignment.

## Session procedure

1. Obtain approved consent and collect only coarse, non-identifying role/experience data.
2. Give standardized orientation stating RUO/shadow limitations without teaching answers to test items.
3. Present counterbalanced scenarios and ask the participant to think aloud.
4. Ask for the perceived state, confidence, missing information, next information to review, and what the display does **not** establish.
5. Probe INVALID and transition cases: what caused withholding, what remains unknown, and whether the participant noticed recovery.
6. Test teach-back with open questions before recognition questions.
7. Debrief, clarify that no patient-care inference should be retained, and collect usability feedback.

Moderators must not invite medication, dosing, anesthesia changes, procedural clearance, diagnosis, or emergency prediction. If volunteered, record the misunderstanding neutrally and redirect to interpretation of the research display.

## Critical comprehension items

A participant must be able to state, in their own words, that:

- the display is RUO/shadow and does not replace source waveforms, the standard monitor, or clinical judgment;
- RII/status describes version-specific measured instability, not a diagnosis or predicted outcome;
- a visible status depends on adequate baseline, usable signal, and valid numeric backend output;
- INVALID/hidden output must not be treated as reassuring or stable;
- PROXY/public-fixture evidence is not DS-specific clinical validation;
- medication events and acknowledgments are research annotations, not proof of care or recommendations.

## Measures

| Measure | Definition |
| --- | --- |
| Critical-item comprehension | Correct teach-back for each item, with verbatim-safe coded rationale |
| Hazardous misunderstanding | Interpretation that could encourage unsupported diagnosis, prediction, treatment, clearance, or false reassurance |
| Invalid-state response | Correctly withholds index interpretation and seeks source/context review |
| Time to first correct interpretation | From scenario reveal to correct explanation; descriptive only |
| Confidence calibration | Confidence compared with correctness |
| Preference and workload | Secondary; never overrides safety comprehension |

Two trained reviewers independently code critical items and disagreements. Report item-level denominators, scenario/variant, role band, uncertainty, missing observations, and all critical misunderstandings. Do not rely on a single mean usability score.

## Decision rules

Numerical acceptance criteria and sample size are `PI_REQUIRED` and must be locked before data review. Regardless of aggregate score, any plausible high-severity misunderstanding triggers corrective design analysis and retest. Preference cannot compensate for failure to understand INVALID, RUO, or non-diagnostic meaning. Findings can select or revise display copy/layout; they cannot authorize model or threshold changes under M0.

## Data governance and outputs

Use participant codes, coarse demographics, approved recordings/transcripts, access controls, retention dates, and a deletion owner. Do not place participant or patient identifiers in the repository. The output packet contains protocol/version, approvals, recruitment accounting, scenario order, raw coded responses in approved storage, analysis script, deviations, findings, hazards, disposition, and sign-offs.

## Stop criteria

Pause the session or study for accidental PHI exposure, participant distress, protocol/consent failure, prototype behavior inconsistent with the frozen scenario, or repeated framing that could be mistaken for patient-care guidance.

Related: [Human Factors Risk](HUMAN_FACTORS_RISK.md), [Clinical Workflow Audit](CLINICAL_WORKFLOW_AUDIT.md), [Prohibited Claims](../safety/PROHIBITED_CLAIMS.md).
