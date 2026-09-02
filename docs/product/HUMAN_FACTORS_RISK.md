# Human factors risk

| Hazard | Likely mechanism | Existing control | Residual risk / required evidence |
|---|---|---|---|
| Automation bias toward index | Large number/status color looks authoritative | Raw waveforms, SQI, reasons, limitations, RUO banner | Moderated clinician study; measure decisions with/without index |
| Research bins interpreted as alarms | Terms WATCH/ELEVATED/HIGH resemble escalation | Sound off; no treatment text; “Research Instability Index” name | Test comprehension; consider neutral research coding in future protocol |
| Signal artifact interpreted as physiology | Motion/flush/loss changes trends | Raw-window SQI; invalid withholding; modality badges | Device-specific artifact validation and disconnect simulations |
| False reassurance from low score | Valid numeric score may hide unmeasured risk | Not probability; complete-context reminders | Test that users continue standard monitoring; never display procedural clearance |
| Baseline anchoring | Bad initial 180 s becomes reference | Stability/quality gate; no bypass | Validate induction-stage baseline protocol and restart rules |
| Public case mistaken for DS patient | Product research context centers DS | `verified_ds=false`; source/attribution; synthetic/local/public labels | Repeated disclosure in exports and study training |
| Color-only interpretation | Red/amber/green carries meaning | Text status and numeric/quality labels | Accessibility/contrast and color-vision testing |
| Alarm fatigue/alert chasing | Frequent state changes | No sound; sustained-trend UI; replay context | Measure transition frequency and false research events/hour |
| Patient context overcollection | Form encourages identifiers | Pseudonymous ID and coarse groups only; no API transmission | Institutional data dictionary and export review |
| Stale/reconnected stream | Old score could appear current | Stream connection state; delayed/dropout gates; explicit end event | Verify UI clears/marks stale frame on network interruption |
| Explanation overconfidence | Feature rationale mistaken for cause | Candidate/limitation wording | Clinician comprehension and causal-language review |
| Export reused as patient-care report | HTML/CSV looks durable | “research summary—not patient-care report” disclaimer | Watermark, access control, retention policy, recipient training |

## Acceptance criteria before clinician review

- 100% of invalid signal, baseline, and transport fixtures withhold the index or visibly reduce confidence.
- No participant interprets the index as a probability, diagnosis, treatment instruction, or validated forecast in comprehension testing.
- Public/synthetic/local source type, DS verification status, license, and model limitation remain visible in replay and export.
- Workflow does not delay or replace approved monitoring/escalation in a simulated study.

Prospective shadow use requires a formal usability engineering plan, representative users/tasks/environments, use-error analysis, training materials, and signed clinical-safety review.
