# Signal engine handoff

## Implemented

- VitalDB public live FHIR, optional WFDB, local CSV, and nine deterministic synthetic
  scenarios.
- Timestamp-aware bounded ring buffer, configurable filtering, artifact candidates,
  ECG/PPG/ABP SQI, beat/pulse detection, first-window baseline, feature extraction,
  OOD/uncertainty gate, transparent `rii-v0.1`, and SSE payload generation.
- FastAPI health/cases/replay/stream/analyze/evidence routes with Pydantic v2 contracts.
- Offline local fixture and mocked VitalDB failure fallback.
- Unit/integration tests covering required safety and transport paths.

## Safety invariants

- Invalid output is `score=null`, `level=INVALID`; no last-known score is reused.
- Public cases are `unknown_or_non_ds` and `clinical_use_allowed=false`.
- Synthetic outputs identify their synthetic origin.
- DS hypothesis mode reduces confidence and declares lack of DS validation.
- No PHI persistence, LLM inference, dosing, treatment, or control path exists.

## Next validation work

Obtain an approved, versioned dataset and protocol before fitting any statistical model.
Run patient/case-level splits, validate preprocessing and labels independently, report
class balance and invalid-rate metrics, and leave all unsupported metrics
`NOT_EVALUATED`. Clinical or DS claims require an entirely separate governed study.
