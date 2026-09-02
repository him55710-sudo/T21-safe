# Data usage boundaries

## Allowed and prohibited uses

| Dataset group | Allowed | Prohibited |
|---|---|---|
| VitalDB / VitalDB Arrhythmia | Adult intraoperative adapter, waveform plumbing, generic SQI/beat checks, synthetic-style demonstration with attribution | DS identification, pediatric/DS validation, guaranteed anesthesia-event prediction, medication recommendation |
| INSPIRE | Adult perioperative tabular methods, operational label feasibility, external validation after credentialing | DS cohort construction (chromosomal/congenital codes removed), waveform validation, pediatric claims |
| MIMIC clinical/waveform | ICU/ED signal and generic event methods, approved linkage research | Treating ICU data as anesthesia data, assuming DS from waveform/metadata, cross-patient leakage, unrestricted redistribution |
| BIDMC / MIMIC-III-Ext-PPG | PPG, respiratory-rate, SQI, alignment, artifact engineering | Clinical instability prediction, DS/pediatric conclusions, random segment split across the same patient |
| MIT-BIH | ECG beat/rhythm detector checks | Perioperative outcome validation or DS inference |
| PTT-PPG / Fantasia | Motion, alignment, HRV, PTT-proxy implementation | Clinical event prediction, anesthesia claims, DS performance |
| Propofol autonomic dynamics | Reproduce narrow autonomic/behavioral feature calculations under its DUA | Dose optimization, treatment rules, clinical-event prediction, surgical/DS generalization |
| Multimodal surgery/anesthesia | Derived-index/timeline interoperability and exploratory feature work | Treating nociceptive stimulus as instability ground truth, raw-waveform claims, DS performance |
| Hospital DS cohort (future) | IRB/DUA-approved retrospective research and later approved silent shadow study | Care decisions, automatic alerts/actions, use outside protocol, external PHI transfer |

## Mandatory gates

1. Verify source/version/license and access authorization before download.
2. Generate a manifest and checksum outside the Git checkout.
3. Confirm population, setting, age, signal availability, event timing, and DS ascertainment from approved fields—not inference.
4. Define allowed role before analysis: demo, signal technical validation, generic event model, or DS cohort research.
5. Enforce subject-level partitions and temporal cutoffs before feature generation.
6. Keep test sets untouched until the analysis plan, thresholds, and calibration procedure are frozen.
7. Report source-population results without transferring them to DS, pediatric, anesthesia, or hospital settings.

## Detected error checks

| Failure pattern | Repository status |
|---|---|
| ICU data represented as anesthesia data | Controlled: setting recorded and prohibited above |
| Adult data represented as pediatric DS validation | Controlled: explicit prohibition/model limitations |
| Healthy-volunteer data used for clinical-event prediction | Controlled: feature implementation only |
| DS inferred without diagnosis availability | Controlled: `NO`/`UNCERTAIN`; runtime never marks verified DS |
| Multiple cases/windows leak across partitions | Method control exists; no training run to verify |
| Test set tunes thresholds | Prohibited in SAP and this boundary; no training run |
| Missing dataset version | Registry complete for all listed datasets |
| Missing license/attribution | One propofol license mismatch corrected during audit; runtime UI still needs manifest-driven license metadata before broader public replay |
