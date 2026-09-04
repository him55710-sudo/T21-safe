# RII Display Human-Factors Options — M0-A

**Status:** Design-research options; no option selected

**Invariant:** Options modify presentation only. They do not modify RII/PROXY logic, clinical definitions, thresholds, weights, or status assignment.

## Shared safety requirements

Every option must:

- display “Research Use Only / Shadow Mode” persistently;
- call the quantity **Research Instability Index** and avoid disease, diagnosis, outcome, urgency, or treatment claims;
- use only BASELINE, STABLE, WATCH, ELEVATED, HIGH, and INVALID;
- hide the index unless baseline is calibrated, signal quality is usable, and backend risk output is valid with a numeric score;
- show INVALID/hidden as unavailable, never as zero, normal, stable, or reassuring;
- retain source signal-quality and failure-reason visibility;
- identify version/provenance in research export or details;
- keep medication events and acknowledgment read-only research annotations.

No presentation is an alarm or substitute for the standard monitor and complete patient context.

## Candidate options

| Option | Primary presentation | Potential benefit | Foreseeable risk | Questions to test |
| --- | --- | --- | --- | --- |
| A — status first | Large status word; trend and numeric index behind details | May reduce false precision and focus on validity | Status words/colors may be read as alarm severity | Does the user retain non-diagnostic meaning and notice INVALID? |
| B — trend first | Time trend with status label; current number secondary | Emphasizes measured change and temporal context | Trend slope may be read as outcome prediction; chart may hide gaps | Can users explain gaps, baseline, and uncertainty? |
| C — context panel | Status and trend paired with baseline/SQI/validity panel | Makes prerequisites and failure reasons salient | Higher density and workload | Is invalidity noticed faster without obscuring source data? |
| D — qualitative only | Status and validity without current numeric value | Minimizes numeric anchoring | May encourage category boundary assumptions or conceal magnitude | Does removal reduce false precision without reducing comprehension? |

## Common state behavior

| State | Required behavior |
| --- | --- |
| Baseline incomplete | Hide number/status interpretation; show BASELINE and the missing prerequisite |
| Signal unusable | Hide number; show INVALID and signal-quality reason |
| Backend invalid/non-numeric | Hide number; show INVALID and processing-unavailable reason |
| Valid recovery | Restore display only after all prerequisites are valid; visually preserve the gap |
| Stale data | Do not present stale value as current; show timestamp/age and unavailable state per contract |

Color may reinforce but must not be the only carrier. Motion, sound, alarm icons, and directive wording are excluded in M0. Exact visual styling remains a prototype variable, not a clinical severity assertion.

## Evaluation matrix

Use the [Clinician Comprehension Protocol](../product/CLINICIAN_COMPREHENSION_PROTOCOL.md) with identical synthetic scenarios and counterbalanced order. Compare:

- RUO/non-diagnostic teach-back;
- correct withholding in BASELINE and INVALID;
- recognition of SQI/backend failure and data gaps;
- false reassurance, alarm interpretation, outcome prediction, or treatment inference;
- time to correct interpretation, confidence calibration, workload, and preference;
- accessibility under grayscale/color-vision variation, zoom, and common display conditions.

Numerical acceptance criteria and participant sample rationale are `PI_REQUIRED` before data review. A critical hazardous misunderstanding blocks selection regardless of preference.

## Selection record

The decision record must include prototype/version, participant roles, scenario set, randomized order, item-level results and uncertainty, critical errors, accessibility findings, deviations, chosen option/rationale, rejected alternatives, residual risks, required mitigations, owner, PI/HF reviewer, and Founder disposition.

Selection authorizes only a subsequent reviewed UI proposal. It does not authorize code changes during M0, clinical activation, or a claim of validated comprehension.

Related: [Human Factors Risk](../product/HUMAN_FACTORS_RISK.md), [Threshold/Weight Provenance](THRESHOLD_WEIGHT_PROVENANCE.md), [Prohibited Claims](../safety/PROHIBITED_CLAIMS.md).
