# Feature traceability matrix

All rows are research variables. “Technical validation” means repository synthetic tests or a suitable future dataset role; it does not mean clinical or DS validation. No feature has DS-specific performance evidence.

| Feature(s) | Unit | Physiological/technical rationale | Source/calculation | Runtime window | Literature/data support | Known confounders | Failure/withhold condition |
|---|---|---|---|---|---|---|---|
| `current_hr_bpm` | bpm | Current cardiac rate summary | Numeric HR median over last 5 s, else plausible RR | 5 s | Synthetic tests; future MIT-BIH/VitalDB technical checks | Ectopy, pacing, detector error, drug/surgical context | Missing HR and unusable beat detection |
| `delta_hr_bpm`, `delta_hr_pct` | bpm, % | Within-person change | Current HR minus/divided by baseline median | Current vs 180 s baseline | Engineering rationale; no DS feature validation | Unstable baseline, age, anesthetic stage | Baseline absent/zero or HR OOD |
| `hr_slope_bpm_min` | bpm/min | Direction/rate of change | Least-squares slope | Up to 60 s | Synthetic decline test; future perioperative validation | Irregular sampling, artifact, transient events | Fewer than two finite points |
| `hr_acceleration_bpm_sample`, `hr_deceleration_bpm_sample` | bpm/sample | Exploratory adjacent change | Extremes of adjacent HR differences | Up to 60 s | Implementation only | Sample rate, noise, ectopy | Fewer than two finite HR values |
| `beat_detection_confidence` | 0–1 | Reliability of beat-derived features | ECG R-peak or PPG pulse detector confidence | Up to 60 s | Synthetic/flatline/noise tests; future MIT-BIH/BIDMC | Rhythm, motion, low perfusion | Too few beats makes index invalid |
| `rr_mean_ms` | ms | Mean accepted RR interval | RR intervals restricted to 300–2000 ms | Up to 60 s | Standard signal method; future MIT-BIH | Ectopy, pacing, short windows | Fewer than two accepted beats |
| `rmssd_ms`, `sdnn_ms` | ms | Short-window HRV summaries | Time-domain statistics of accepted RR | Up to 60 s; baseline stored | Generic HRV methods; future Fantasia/propofol checks | Breathing, drugs, age, ectopy, window length | Insufficient accepted RR intervals |
| `poincare_sd1_ms`, `poincare_sd2_ms` | ms | RR dispersion geometry | Poincaré transforms | Up to 60 s | Generic method only | Same as HRV; nonstationarity | Prefer at least three RR intervals |
| `sample_entropy` | unitless | Exploratory RR irregularity | Tolerance-based pattern counts | Up to 60 s | Generic method only | Very short series, ectopy, parameter choice | Invalid/zero match counts |
| `lf_power`, `hf_power`, `lf_hf_ratio` | s², ratio | Exploratory spectral HRV | Interpolated RR spectral power | At least 180 s/20 beats | HRV literature; future Fantasia only | Respiration, nonstationarity, drugs | Withheld below duration/beat minimum; not core index |
| `ppg_amplitude` | source units | Peripheral pulse morphology proxy | Pulse peak minus preceding trough | Up to 60 s | Synthetic/BIDMC/PTT technical role | Sensor contact, gain, site, motion, vasomotor state | Missing/low-quality PPG or no pulses |
| `ppg_amplitude_delta`, `ppg_amp_delta_pct` | source units, % | Within-person peripheral pulse change | Current amplitude vs baseline median | Current vs 180 s baseline | Synthetic amplitude-decline test | Gain changes, contact force, motion, drugs | Missing baseline/current amplitude |
| `ppg_pulse_width_s`, `ppg_rise_time_s` | s | Pulse morphology | Half-height width; trough-to-peak time | Up to 60 s | Future BIDMC/PTT checks | Filtering, reflection, perfusion, motion | No valid finite pulses |
| `ppg_pulse_area` | source-unit·s | Exploratory pulse area | Integral above local trough | Up to 60 s | Implementation only | Gain/contact/site/filtering | No valid finite pulses |
| `ppg_amplitude_variability` | source units | Beat-to-beat amplitude spread | SD of pulse amplitudes | Up to 60 s | Future motion/PPG validation | Motion, respiration, arrhythmia | Fewer than two amplitudes |
| `ppg_peak_confidence` | 0–1 | Pulse timing reliability | Pulse detector confidence | Up to 60 s | Synthetic artifact tests; future BIDMC | Motion, clipping, low perfusion | No/insufficient pulses |
| `perfusion_trend_proxy` | source units | Exploratory alias of median PPG amplitude | Median pulse amplitude | Up to 60 s | Hypothesis only | Not a calibrated perfusion measure | Same as PPG amplitude |
| `current_sbp_mm_hg`, `current_dbp_mm_hg`, `current_map_mm_hg` | mmHg | Current pressure summaries | Last numeric median; ABP proxy when MAP absent | Current/last 100 samples | Synthetic ABP tests; future VitalDB | Transducer leveling, damping, flush, cuff/device differences | Missing/implausible pressure source |
| `delta_map_mm_hg`, `delta_map_pct` | mmHg, % | Within-person pressure change | Current MAP vs baseline | Current vs 180 s baseline | Synthetic MAP decline test | Baseline stage, transducer artifact, drugs | Missing baseline/current MAP |
| `map_slope_mm_hg_min` | mmHg/min | Direction/rate of MAP change | Least-squares slope | Up to 60 s | Synthetic decline test | Gaps, flush, interventions | Fewer than two finite points |
| `map_duration_below_threshold_s` | s | Generic adult candidate label/feature | Time MAP is below configured 65 mmHg | Up to 60 s | Generic adult research only | Age/context; arterial vs cuff semantics | Not valid for pediatric/DS interpretation |
| `pressure_variability` | mmHg | Window pressure dispersion | Sample SD | Up to 60 s | Implementation only | Artifact, flush, damping, surgery | Fewer than two finite values |
| `ptt_ms` | ms | ECG-to-PPG pulse-arrival proxy | Aligned R/pulse peak delay | Up to 60 s | Future PTT-PPG technical validation | Pre-ejection period, clocks, sensor site | Missing modalities or implausible alignment |
| `ecg_ppg_alignment_confidence` | 0–1 | Cross-modal timing reliability | Plausible pair fraction/quality | Up to 60 s | Synthetic desynchronization tests; future PTT-PPG | Clock drift, dropped packets, ectopy | Synchronization failure withholds index |
| `hr_ppg_divergence`, `hr_map_divergence` | percentage points | Exploratory cross-modal disagreement | Differences between relative trends | Up to 60 s | Hypothesis only | Modality-specific artifact and lag | Missing component feature |
| `combined_trend_consistency` | 0/1 | Whether HR and MAP both decline | Sign agreement | Up to 60 s | Engineering hypothesis | Independent physiology/artifact | Missing HR or MAP delta |
| `current_spo2_pct`, `spo2_slope_pct_min` | %, %/min | Saturation level/trend | Last summary and least-squares slope | Up to 60 s | Synthetic desaturation; generic validation only | Probe motion, perfusion, delay | Missing/out-of-range saturation |
| `current_etco2_mm_hg`, `etco2_slope_mm_hg_min` | mmHg, mmHg/min | Ventilation trend context | Last summary and slope | Up to 60 s | Implementation only | Airway leak, sampling line, ventilation changes | Missing/out-of-range EtCO2 |
| `respiratory_rate_bpm` | breaths/min | Respiratory context | Numeric respiratory trend | Up to 60 s | Future BIDMC technical check | Ventilation mode, artifact, counting method | Missing/invalid respiratory source |
| `available_modalities` | count | Data completeness/uncertainty | Count of finite core/optional modalities | Up to 60 s | Engineering control | Redundant correlated signals | Fewer than three reduces confidence |

The evidence ledger and dataset registry define population applicability. None of the listed rationales establishes causality, treatment response, or DS-specific thresholds.
