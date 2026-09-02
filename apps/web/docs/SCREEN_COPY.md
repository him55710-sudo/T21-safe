# Screen copy inventory

## Persistent

- `Research prototype. Not for diagnosis, treatment, dosing, or clinical monitoring.`
- Product: `T21 Safe`
- Tagline: `Patient-specific perioperative safety intelligence for physiologically vulnerable patients, starting with Down syndrome.`

## Start

- `See the signal. Understand the change.`
- `This case is not a verified Down syndrome case.`
- `Used only to demonstrate signal processing.`
- `SYNTHETIC SCENARIO — No patient data. No claim of population validity.`

## Context

- `Use structured record-derived context only. Unknown values must remain unknown.`
- `Entered context is authoritative.`
- `Waveforms are not used to infer Down syndrome or structural heart disease.`

## Baseline

- `Establishing a stable reference`
- `Risk output remains hidden until signal availability, quality, and baseline stability requirements are met.`
- Failure: `Calibration could not be established` / `Index unavailable`

## Monitor

- Index name: `Research Instability Index`
- Trend: `INCREASING`, `DECREASING`, `STABLE`
- Invalid: `INDEX HIDDEN — Signal or baseline requirements are not met.`
- Allowed reasons: `Heart rate is declining from baseline.`, `MAP trend is declining.`, `PPG amplitude is reduced.`, `Signal quality is insufficient.`
- Context reminder: `The index must be interpreted with complete patient context.`

## DS hypothesis mode

- `Candidate physiological features selected for future validation in patients with Down syndrome. No DS-specific calibration has been completed.`

## Explanation

- `What changed the research index?`
- `This view describes feature movement. It does not determine why a patient is at risk or prescribe a response.`

## Review and export

- `Research session summary`
- `Research summary — not a patient-care report`
- `Export anonymized JSON`, `Export CSV`, `Export research summary`
