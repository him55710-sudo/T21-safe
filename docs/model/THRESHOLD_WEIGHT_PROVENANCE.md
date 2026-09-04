# Threshold / Weight Provenance

**Date:** 2026-09-04 (KST)  
**Sources (READ ONLY — values not changed):**  
- `services/engine/src/t21_engine/config.py`  
- `services/engine/src/t21_engine/risk/deterministic_index.py`  
**Eng tip HEAD:** `edff0f1`  
**Path:** B / RUO / Shadow / `clinical_validation=false`

> This inventory traces engineering defaults. It does **not** confer clinical validation.  
> Classifications: `ENGINEERING_FIXTURE` | `UI_RESEARCH_BIN` | `LABEL_CANDIDATE` | `QUALITY_RESEARCH_GATE` | `PIPELINE_CONTROL` | `PI_REQUIRED` | `UNKNOWN`.  
> Do not invent literature citations; if a value looks clinically meaningful but has no in-repo citation, mark `PI_REQUIRED` or `UNKNOWN`.

---

## Classification legend

| Class | Meaning |
| --- | --- |
| `ENGINEERING_FIXTURE` | Chosen for deterministic pipeline research; not clinically validated |
| `UI_RESEARCH_BIN` | Non-clinical RII display/status boundary; not an alarm/action threshold |
| `LABEL_CANDIDATE` | Candidate research label input; unusable as a clinical definition before PI/protocol approval |
| `QUALITY_RESEARCH_GATE` | Research signal-quality/index-withholding control; not clinical eligibility |
| `PIPELINE_CONTROL` | Sampling, window, buffering, or reproducibility control |
| `PI_REQUIRED` | Clinically consequential decision; options live in the Clinical Research Lock |
| `UNKNOWN` | Origin unclear from these files alone |

Required M0 semantic classes are applied as a second dimension:

| M0 class | Applies to |
| --- | --- |
| `ENGINEERING_FIXTURE` | RII weights, scale/clipping values, formula constants, filter defaults; an engineering default is not clinical evidence |
| `UI_RESEARCH_BIN` | `watch_threshold`, `elevated_threshold`, `high_threshold`, and the hardcoded BASELINE/STABLE boundary |
| `LABEL_CANDIDATE` | `hypotension_map_mm_hg`, `hypotension_duration_seconds`, `relative_hr_decline_pct`, `relative_map_decline_pct` |
| `QUALITY_RESEARCH_GATE` | all `QualityConfig` values and `baseline_minimum_fraction` |
| `PIPELINE_CONTROL` | sample rate, update/baseline/window/buffer durations, and deterministic seed |

Any clinical use of these classes remains `PI_REQUIRED`; the 2–3 decision options are canonical in `docs/research/CLINICAL_RESEARCH_LOCK_V0.md`. This classification records present engineering use and does not approve the values.

---

## A. `FilterConfig` (`config.py`)

| Symbol | Default | file:line | Class | Notes |
| --- | --- | --- | --- | --- |
| `ecg_low_hz` | `0.5` | config.py:11 | `ENGINEERING_DEFAULT` | Bandpass; not clinical endpoint |
| `ecg_high_hz` | `35.0` | config.py:12 | `ENGINEERING_DEFAULT` | |
| `ppg_low_hz` | `0.4` | config.py:13 | `ENGINEERING_DEFAULT` | |
| `ppg_high_hz` | `8.0` | config.py:14 | `ENGINEERING_DEFAULT` | |
| `abp_low_hz` | `0.3` | config.py:15 | `ENGINEERING_DEFAULT` | |
| `abp_high_hz` | `12.0` | config.py:16 | `ENGINEERING_DEFAULT` | |
| `order` | `3` | config.py:17 | `ENGINEERING_DEFAULT` | Filter order |
| `mains_hz` | `None` | config.py:18 | `ENGINEERING_DEFAULT` | Optional notch |

---

## B. `QualityConfig` (`config.py`)

| Symbol | Default | file:line | Class | Notes |
| --- | --- | --- | --- | --- |
| `minimum_sqi` | `0.55` | config.py:39 | `QUALITY_RESEARCH_GATE` | Affects index withhold; clinical SQI policy is CRL-09 `PI_REQUIRED` |
| `maximum_gap_fraction` | `0.15` | config.py:40 | `QUALITY_RESEARCH_GATE` | |
| `maximum_flatline_fraction` | `0.2` | config.py:41 | `QUALITY_RESEARCH_GATE` | |
| `minimum_valid_beats` | `4` | config.py:42 | `QUALITY_RESEARCH_GATE` | |
| `synchronization_tolerance_ms` | `100.0` | config.py:43 | `QUALITY_RESEARCH_GATE` | |
| `maximum_source_latency_ms` | `1000.0` | config.py:44 | `QUALITY_RESEARCH_GATE` | |

---

## C. `RiskConfig` (`config.py`) — RII weights, scales, bins

| Symbol | Default | file:line | Class | Notes |
| --- | --- | --- | --- | --- |
| `model_version` | `"rii-v0.1"` | config.py:67 | `ENGINEERING_FIXTURE` | Label only |
| `observation_context_seconds` | `120` | config.py:68 | `PIPELINE_CONTROL` | Clinical windowing is CRL-08 `PI_REQUIRED` |
| `relative_hr_decline_weight` | `25.0` | config.py:69 | `ENGINEERING_FIXTURE` | Part of weight sum=100; no in-file citation |
| `relative_map_decline_weight` | `35.0` | config.py:70 | `ENGINEERING_FIXTURE` | |
| `relative_ppg_amplitude_decline_weight` | `15.0` | config.py:71 | `ENGINEERING_FIXTURE` | |
| `hr_slope_weight` | `5.0` | config.py:72 | `ENGINEERING_FIXTURE` | |
| `map_slope_weight` | `10.0` | config.py:73 | `ENGINEERING_FIXTURE` | |
| `low_spo2_weight` | `10.0` | config.py:74 | `ENGINEERING_FIXTURE` | SpO2/Airway still do-not-run clinically |
| `relative_hr_decline_full_scale_pct` | `35.0` | config.py:75 | `ENGINEERING_FIXTURE` | Full-scale for clip to weight |
| `relative_map_decline_full_scale_pct` | `35.0` | config.py:76 | `ENGINEERING_FIXTURE` | |
| `relative_ppg_amplitude_decline_full_scale_pct` | `60.0` | config.py:77 | `ENGINEERING_FIXTURE` | |
| `hr_slope_full_scale_bpm_min` | `12.0` | config.py:78 | `ENGINEERING_FIXTURE` | |
| `map_slope_full_scale_mm_hg_min` | `15.0` | config.py:79 | `ENGINEERING_FIXTURE` | |
| `spo2_reference_pct` | `94.0` | config.py:80 | `ENGINEERING_FIXTURE` | No in-file clinical citation |
| `spo2_full_scale_decline_pct` | `10.0` | config.py:81 | `ENGINEERING_FIXTURE` | |
| `watch_threshold` | `25.0` | config.py:82 | `UI_RESEARCH_BIN` | Research bin only — not alarm |
| `elevated_threshold` | `50.0` | config.py:83 | `UI_RESEARCH_BIN` | Research bin only |
| `high_threshold` | `75.0` | config.py:84 | `UI_RESEARCH_BIN` | Research bin only |
| `hypotension_map_mm_hg` | `65.0` | config.py:85 | `LABEL_CANDIDATE` | No in-file clinical citation; clinical definition is `PI_REQUIRED` |
| `hypotension_duration_seconds` | `60.0` | config.py:86 | `LABEL_CANDIDATE` | Not directly consumed by deterministic index |
| `relative_hr_decline_pct` | `-20.0` | config.py:87 | `LABEL_CANDIDATE` | Not directly consumed by deterministic index |
| `relative_map_decline_pct` | `-20.0` | config.py:88 | `LABEL_CANDIDATE` | Not directly consumed by deterministic index |

Weight sum constraint enforced in `__post_init__` (config.py:109–110): must equal `100.0`.

---

## D. `PipelineConfig` (`config.py`)

| Symbol | Default | file:line | Class | Notes |
| --- | --- | --- | --- | --- |
| `config_version` | `"pipeline-v0.2"` | config.py:141 | `ENGINEERING_FIXTURE` | |
| `waveform_sample_rate_hz` | `100.0` | config.py:142 | `PIPELINE_CONTROL` | |
| `feature_update_seconds` | `1.0` | config.py:143 | `PIPELINE_CONTROL` | |
| `baseline_seconds` | `180` | config.py:144 | `PIPELINE_CONTROL` | Clinical baseline definition is CRL-08 `PI_REQUIRED` |
| `baseline_minimum_fraction` | `0.8` | config.py:145 | `QUALITY_RESEARCH_GATE` | Affects baseline establishment |
| `feature_windows_seconds` | `(30, 60, 180)` | config.py:146 | `PIPELINE_CONTROL` | Clinical windowing is `PI_REQUIRED` |
| `buffer_seconds` | `240` | config.py:147 | `PIPELINE_CONTROL` | |
| `deterministic_seed` | `20250321` | config.py:148 | `PIPELINE_CONTROL` | Reproducibility pin |

Nested: `filters`, `quality`, `risk` default factories (config.py:149–151).

---

## E. `deterministic_index.py` — logic constants & uses

| Symbol / behavior | Value | file:line | Class | Notes |
| --- | --- | --- | --- | --- |
| Module intent | RII v0.1 transparent weighted index | deterministic_index.py:1–4 | n/a | Explicit: **not** calibrated probability / clinical alarm |
| `_decline_component` | clips `-value/full_scale` to `[0,1]` × weight | :23–26 | `ENGINEERING_DEFAULT` | Formula |
| `_level` HIGH | `score >= risk.high_threshold` | :30–31 | uses `PI_REQUIRED` config | |
| `_level` ELEVATED | `score >= risk.elevated_threshold` | :32–33 | uses `PI_REQUIRED` config | |
| `_level` WATCH | `score >= risk.watch_threshold` | :34–35 | uses `PI_REQUIRED` config | |
| `_level` BASELINE cutoff | `score < 10.0` | :36–37 | `ENGINEERING_DEFAULT` / `UNKNOWN` | **Hardcoded `10.0`** not in `RiskConfig` |
| `_level` else | `STABLE` | :38 | `ENGINEERING_DEFAULT` | |
| Score assembly | HR/MAP/PPG decline + HR/MAP slopes + SpO2 | :70–105 | uses `RiskConfig` | |
| Final score clip | `[0.0, 100.0]` | :106 | `ENGINEERING_DEFAULT` | Dimensionless research score |
| Confidence | `baseline × median(SQI) × beat × uncertainty` | :108–121 | `ENGINEERING_DEFAULT` | Not a clinical probability |

No `LITERATURE_CITED` constants appear inside `deterministic_index.py`.

---

## F. Freeze rule

Until the canonical refocus decision is amended ([`docs/founder/T21_REFOCUS_DECISION_KR.md`](../founder/T21_REFOCUS_DECISION_KR.md)):

1. **Do not change** any numeric default in these files.  
2. Provenance updates are docs-only.  
3. Promoting any engineering/research class to a locked clinical value requires Clinical Research Lock amendment + PI — still no silent code edit in M0.

## G. Gaps for PI session

- Hardcoded `10.0` BASELINE boundary (deterministic_index.py:36) should be confirmed: move to config vs leave.  
- MAP 65 / SpO2 94 / relative −20% look “clinical” but lack in-file citations → remain `PI_REQUIRED`.  
- Absolute bradycardia thresholds: **not present** in these two files; still `PI_TO_DEFINE` in Lock table.

## H. REPO_FACT

- `REPO_FACT` (`edff0f1`): `RiskConfig`, `QualityConfig`, and `PipelineConfig` are defined in `services/engine/src/t21_engine/config.py`.
- `REPO_FACT` (`edff0f1`): `services/engine/src/t21_engine/risk/deterministic_index.py` consumes `PipelineConfig.risk` for score assembly and status bins, and `PipelineConfig.quality` for uncertainty/index withholding.
- `REPO_FACT` (`edff0f1`): no value in either source file was changed by this inventory.

## H. REPO_FACT

- `REPO_FACT` (`edff0f1`): definitions are in `services/engine/src/t21_engine/config.py`; score assembly and research-level mapping are in `services/engine/src/t21_engine/risk/deterministic_index.py`.
- `REPO_FACT` (`edff0f1`): invalid uncertainty returns `score=None` and `RiskLevel.INVALID`; weights, bins, and candidate label values were not changed by this inventory.
