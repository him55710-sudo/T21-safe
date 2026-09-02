# Data lineage

The authoritative machine-readable inventory is `research/dataset_registry.yaml` (mirrored in CSV). Each row records source, version, license/access, population, age, setting, modalities, diagnosis/DS availability, intended role, bias, leakage risk, and verification date.

## Runtime lineage

| Runtime source | Adapter | Transformation | Output provenance |
|---|---|---|---|
| Local synthetic generator | `SyntheticAdapter` | Deterministic seed → ECG/PPG/ABP/numerics | `raw:synthetic:*`; no patient data |
| Bundled local fixture | `LocalFixtureAdapter` | CSV parse only | `raw:csv:local_waveform.csv`; development fixture |
| VitalDB public API | `VitalDBAdapter` | Public FHIR sample → canonical names/resampling | VitalDB URL/track metadata; online mode only |
| PhysioNet/local WFDB | `WFDBAdapter` | WFDB channels → canonical names | Dataset/record identifier; online mode/optional dependency |

Raw arrays are copied before filtering. Processed provenance records `pipeline-v0.2`. The API frame includes raw and processed provenance, source population metadata, model version, and explicit limitations. No runtime source is identified as a verified DS case.

## Dataset inventory

| Dataset ID | Version | Population/setting | DS identification | Permitted project role |
|---|---|---|---|---|
| `vitaldb-open` | PhysioNet 1.0.0; live API | Adult noncardiac intraoperative | Uncertain; do not infer | Live/public adapter demo; generic signal processing |
| `inspire` | 1.4.2 | Adults 18–90, perioperative/ward/ICU tables | No; relevant congenital/chromosomal codes excluded | Generic tabular event research/external validation only |
| `mimic-iv` | 3.1 | Adult ED/hospital/ICU | Unverified without approved query/linkage | Generic event-model methods only |
| `mimic-iv-waveform` | 0.1.0 | 200 records/198 critically ill adults | Unverified | Technical waveform preview/signal pretraining |
| `mimic-iii-waveform` | 1.0 | Adult/neonatal ICU | Unverified | Generic waveform engineering only |
| `mimic-iii-ext-ppg` | 1.1.0 | Predominantly adult ICU segments | Unverified | PPG/SQI feature validation with patient split |
| `propofol-autonomic-dynamics` | 1.0 | Nine healthy adult volunteers | No | Narrow autonomic feature implementation checks |
| `bidmc-ppg-resp` | 1.0.0 | 53 adult ICU recordings | No direct diagnosis | PPG/respiration technical validation |
| `ptt-ppg` | 1.1.0 | 22 healthy adults, activity protocol | No | Sensor alignment/motion/PTT proxy engineering |
| `mit-bih-arrhythmia` | 1.0.0 | 47 ambulatory subjects, enriched arrhythmias | Not identifiable | ECG beat-detector technical validation |
| `fantasia` | 1.0.0 | 40 healthy adults at rest | No | HRV implementation checks only |
| `multimodal-surgery-anesthesia` | 1.0 | 101 adult surgeries, derived indices | Unverified | Derived-feature/timeline research only |
| `vitaldb-arrhythmia` | 1.0.0 | 482 primarily adult surgical patients | Unverified | Intraoperative ECG beat/rhythm validation only |

## Training and validation state

No dataset has trained the registered Research Instability Index. The index is fixed and deterministic; all model metrics are `NOT_EVALUATED`. Dataset usage described above is planned or adapter-level unless a versioned run manifest and report are committed. There is no external clinical validation and no DS-specific validation.

## Leakage controls

- Split by patient/subject before case/window generation; repeated cases for one patient remain in one partition.
- Fit preprocessing, imputation, feature selection, model parameters, calibration, and thresholds on development data only.
- Do not use test data for threshold selection.
- Exclude future waveform, post-index medication/intervention, discharge outcome, retrospective diagnosis coding, and overlapping adjacent windows across partitions.
- Record source version, query, subject/case mapping, checksum, code revision, and exclusion counts in every run manifest.
