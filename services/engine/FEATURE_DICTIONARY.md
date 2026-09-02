# Feature dictionary

All features are research variables. None is a diagnosis, treatment instruction, or
validated DS risk factor.

Baseline state also stores labeled minimum, quartile, median, and maximum summaries for
heart rate and available signal-quality indices; these are calibration diagnostics, not
population reference ranges.

| Feature | Unit | Window / minimum | Meaning and limitation |
|---|---:|---|---|
| `current_hr_bpm` | bpm | 5 s current summary | Numeric HR or plausible RR-derived HR |
| `delta_hr_bpm`, `delta_hr_pct` | bpm, % | 30/60/180 s | Change from individual baseline |
| `hr_slope_bpm_min` | bpm/min | >=2 valid points | Least-squares trend; artifact-sensitive |
| `hr_acceleration_bpm_sample`, `hr_deceleration_bpm_sample` | bpm/sample | >=2 points | Exploratory adjacent change |
| `rr_mean_ms` | ms | >=2 plausible RR | RR restricted to 300-2000 ms |
| `rmssd_ms`, `sdnn_ms` | ms | >=2 plausible RR | Short-window HRV; interpret cautiously |
| `poincare_sd1_ms`, `poincare_sd2_ms` | ms | >=3 RR preferred | Poincaré dispersion |
| `sample_entropy` | unitless | >=5 RR | Withheld when matching counts are invalid |
| `lf_power`, `hf_power`, `lf_hf_ratio` | s², ratio | >=180 s and 20 beats | Optional; respiratory confounding; not core |
| `ppg_amplitude` | source units | valid pulses | Peak minus preceding trough |
| `ppg_amp_delta_pct` | % | baseline required | Within-person amplitude change |
| `ppg_pulse_width_s`, `ppg_rise_time_s` | s | valid pulse | Median pulse morphology |
| `ppg_pulse_area` | source-unit·s | valid pulse | Area above local trough |
| `ppg_amplitude_variability` | source units | >=2 pulses | Beat-to-beat amplitude variation |
| `ppg_peak_confidence` | 0-1 | >=2 s | Pulse timing confidence |
| `current_sbp_mm_hg`, `current_dbp_mm_hg`, `current_map_mm_hg` | mmHg | current | Numeric trend; ABP median proxy when MAP absent |
| `delta_map_mm_hg`, `delta_map_pct` | mmHg, % | baseline required | Change from individual MAP baseline |
| `map_slope_mm_hg_min` | mmHg/min | >=2 points | MAP/ABP trend |
| `map_duration_below_threshold_s` | s | current window | Adult generic candidate only; not DS/pediatric |
| `pressure_variability` | mmHg | >=2 points | Window dispersion |
| `ptt_ms` | ms | aligned ECG and PPG | Pulse-arrival/transit proxy, not true PTT validation |
| `ecg_ppg_alignment_confidence` | 0-1 | paired beats | Fraction and quality of plausible pairs |
| `hr_ppg_divergence`, `hr_map_divergence` | percentage points | paired trends | Exploratory cross-modal divergence |
| `combined_trend_consistency` | 0/1 | HR and MAP | Whether both relative trends decline |
| `current_spo2_pct`, `spo2_slope_pct_min` | %, %/min | available | Optional saturation trend |
| `current_etco2_mm_hg`, `etco2_slope_mm_hg_min` | mmHg, mmHg/min | available | Optional capnography trend |
| `respiratory_rate_bpm` | breaths/min | available | Numeric respiratory trend |
| `resp_waveform_irregularity` | coefficient of variation | >=2 plausible breaths | Exploratory interval variability; not a respiratory diagnosis |
| `resp_missing_breath_candidate` | 0/1 candidate | usable respiratory waveform | Prolonged inter-peak interval candidate; not an apnea diagnosis |
| `available_modalities` | count | current window | Used to reduce uncertainty when sparse |
