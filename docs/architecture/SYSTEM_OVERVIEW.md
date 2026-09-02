# System overview

Audit date: 2026-09-02. Status: Research Use Only (RUO), local-first, silent/shadow-mode prototype. It is not a medical device and must not be used for diagnosis, treatment, dosing, alarms, patient monitoring, procedural clearance, or autonomous action.

## What the system does

T21 Safe replays synthetic, local fixture, or explicitly enabled public waveform data; calculates deterministic signal-quality measures and exploratory physiological features; establishes a patient-specific baseline; and displays a bounded Research Instability Index with reasons and limitations. The index is an engineering hypothesis, not a probability or outcome forecast.

```text
Patient / Replay Data
→ Local Data Adapter
→ Signal Preprocessing
→ Signal Quality Gate
→ Patient Baseline Calibration
→ Feature Extraction
→ Research Instability Engine
→ Explanation Engine
→ FastAPI
→ Local Web Dashboard
```

All production-path processing occurs on one local machine or a hospital-controlled LAN. `OFFLINE_MODE=true` is the default. There is no LLM, hosted model, cloud database, telemetry service, or external analytics service in the inference path.

## Component map

| Stage | Implementation | Safety boundary |
|---|---|---|
| Data adapters | `services/engine/src/t21_engine/adapters` | Synthetic/local by default; network-backed public adapters hidden and blocked offline |
| Buffer/preprocessing | `streaming/ring_buffer.py`, `preprocessing` | Bounded memory; raw arrays retained separately from processed provenance |
| Quality gate | `quality`, `risk/uncertainty.py` | Flatline, clipping, rough motion, missingness, dropout, latency, timestamp, beat, and pressure checks |
| Baseline | `baseline/calibration.py` | First 180 seconds by default; no bypass; unstable or incomplete baseline withholds index |
| Features | `features` | Versioned, unit-documented exploratory features; no diagnosis inferred |
| Index/explanation | `risk/deterministic_index.py`, `risk/explanations.py` | Transparent fixed weights; invalid input yields `score=null`, `level=INVALID` |
| API | `services/api` | In-memory sessions, strict schemas, no request persistence, local CORS allowlist |
| Dashboard | `apps/web` | Raw waveforms and quality remain visible; explicit RUO disclaimer and evidence view |

## What it does not do

- It does not prevent complications or predict cardiac arrest, bradycardia, hypotension, or any clinical outcome.
- It does not diagnose Down syndrome or infer DS status from waveforms.
- It does not optimize anesthetic dose or recommend propofol, atropine, ephedrine, phenylephrine, or any treatment.
- It does not replace an approved monitor, alarm, anesthesiologist, institutional escalation pathway, or prospective study protocol.
- Public adult/non-DS data do not establish pediatric or DS-specific performance.

## Evidence state

Software behavior and fail-safe paths are technically testable. No fitted model is registered; performance metrics remain `NOT_EVALUATED`. DS-specific literature supports research questions and candidate mechanisms only. A hospital DS cohort, adjudicated endpoints, patient-level splits, external validation, and approved prospective governance are still required.
