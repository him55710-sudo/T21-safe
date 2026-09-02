# SQI and missingness impact — synthetic hospital cases

**Status:** deterministic engineering benchmark only  
**clinical_validation:** `false`  
**Clinical interpretation of thresholds:** `PI_TO_DEFINE`

`t21_engine.evaluation.sqi_missingness_impact` injects centered missing spans and
seeded additive noise into the ECG, PPG, and ABP channels from the synthetic hospital
case factory. It divides the case into complete, non-overlapping windows and reports
the QC pass rate and the number of windows available for analysis after applying
`evaluate_quality` with `QualityConfig.minimum_sqi`.

The default table includes a clean baseline, 10% and 25% missingness, and noise at
0.20 times each channel's within-window standard deviation. These are engineering
stress conditions, not clinical cutoffs. The report is withheld on invalid parameters,
non-synthetic/PHI-marked input, alignment failure, missing channels, or no complete
windows. It always reports `clinical_validation=false` and enables no alerts, dosing,
or clinical decisions.

The source is generated locally, contains no patient records, and uses neither
Fantasia nor VitalDB.
