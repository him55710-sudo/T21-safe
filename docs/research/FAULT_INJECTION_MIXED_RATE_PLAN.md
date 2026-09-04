# Fault Injection Plan — Mixed-Rate / Clock Skew / Missing Samples

**Status:** PLAN only (no production harness in this PR)<br>
**Mode:** Path B / RUO / Shadow / `clinical_validation=false`<br>
**Tip freeze:** `edff0f1` — no RII / PROXY / threshold / MCP feature expansion<br>
**Related:** [`SCHEMA_CLOCK_PILOT_ACCEPTANCE.md`](SCHEMA_CLOCK_PILOT_ACCEPTANCE.md) · [`HOSPITAL_DATA_REQUEST_SPEC.md`](HOSPITAL_DATA_REQUEST_SPEC.md) · [`SIGNAL_EXTERNAL_VALIDITY_PLAN.md`](SIGNAL_EXTERNAL_VALIDITY_PLAN.md) · [`../safety/PROHIBITED_CLAIMS.md`](../safety/PROHIBITED_CLAIMS.md)

---

## 1. Purpose

Define a **pre-implementation** engineering plan for injecting controlled time-domain faults into multi-stream physiological research replays:

1. **Mixed-rate streams** (e.g. ECG @ 250–500 Hz vs SpO2/MAP @ 1 Hz vs events @ irregular cadence)
2. **Clock skew** between modality clocks or export clocks (fixed offset, drift, step change)
3. **Missing samples** (gaps, dropouts, NaN tails, sparse event lanes)

This plan supports schema/clock pilot readiness and future silent Shadow QC. It does **not** authorize clinical validation, FACT elevation, dosing/closed-loop behavior, or DS performance claims.

**Agents do not email sites or PIs.** Founder/site own any real extract under DUA/IRB.

---

## 2. Non-goals (explicit)

| Out of scope | Why |
| --- | --- |
| Changing `RiskConfig` / RII weights or bins | Freeze tip `edff0f1` |
| New PROXY HYP benches claiming clinical meaning | PROXY ≠ DS validation |
| MCP tool/surface expansion | Freeze |
| Alarm UX, procedural clearance, medication advice | Permanent Path B prohibition |
| Inventing PI Lock thresholds | See [`CLINICAL_RESEARCH_LOCK_V0.md`](CLINICAL_RESEARCH_LOCK_V0.md) |

---

## 3. Fault classes (engineering)

### 3.1 Mixed-rate streams

| Scenario ID | Description | Acceptance idea (eng) |
| --- | --- | --- |
| MR-01 | Master timeline at rate R; secondary stream at R/k | Nearest-previous (or documented) alignment maps each master tick to ≤1 secondary sample |
| MR-02 | Irregular event lane (med/airway markers as metadata only) | Events attach by timestamp without becoming score inputs |
| MR-03 | Resample-to-grid then align | Document grid Hz; preserve missing-tail semantics |

### 3.2 Clock skew

| Scenario ID | Description | Acceptance idea (eng) |
| --- | --- | --- |
| CS-01 | Constant offset Δt between ECG and PPG clocks | QC reports measured Δt; fail-closed if abs(Δt) exceeds site policy (SITE_REQUIRED) |
| CS-02 | Linear drift (ppm) over case duration | Drift estimate logged; no silent “correction” that invents samples |
| CS-03 | Step discontinuity (device reconnect) | Segment boundary flagged; no cross-boundary baseline reuse without provenance |

### 3.3 Missing samples

| Scenario ID | Description | Acceptance idea (eng) |
| --- | --- | --- |
| MS-01 | Contiguous gap fraction g in one modality | SQI / withhold path remains fail-closed (`score=null` / INVALID when applicable) |
| MS-02 | Sparse NaNs at stream end (missing tail) | No extrapolation past last finite sample |
| MS-03 | Whole-modality absent | `available_modalities` / provenance reflect absence; no imputed clinical value |

---

## 4. Proposed harness shape (future; not built here)

1. **Deterministic seed** + fixture manifest (synthetic or deidentified schema sample only).
2. **Fault recipe YAML/JSON** listing scenario IDs, parameters, expected QC codes.
3. **Pure alignment helper** under unit test (nearest-previous / max-skew reject) with **no new runtime deps**.
4. **Report artifact** (JSON): scenario, input rates, measured skew, gap fractions, pass/fail eng codes.
5. Wire into an optional smoke job later — **not** as a freeze-breaking required PROXY bench.

Unit coverage landed with this plan: [`tests/backend/unit/test_mixed_rate_time_alignment.py`](../../tests/backend/unit/test_mixed_rate_time_alignment.py) (pure-Python nearest-previous aligner stub used only by tests).

---

## 5. Gate ownership

| Class | Owner |
| --- | --- |
| Engineering pass/fail for alignment/QC codes | Maintainer |
| Timezone / NTP / export clock policy | `SITE_REQUIRED` |
| Whether skew/gap envelopes are acceptable for Lock questions | `PI_REQUIRED` |

Engineering PASS ≠ PI Lock complete ≠ clinical validation.

---

## 6. Claim boundary

Allowed language: research replay, candidate association, technical alignment QC, Path B / RUO.

Forbidden: predicting arrest, optimizing anesthetic dose, procedural “clear to proceed,” medication advice, DS-calibrated performance from public non-DS data, FACT elevation from fixture PASS.

See [`../safety/PROHIBITED_CLAIMS.md`](../safety/PROHIBITED_CLAIMS.md).
