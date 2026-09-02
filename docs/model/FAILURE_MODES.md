# Model and signal failure modes

| Failure | Detection | Runtime response | Residual risk / next control |
|---|---|---|---|
| ECG/PPG noise or rough motion | Raw-window roughness, abrupt change, beat confidence | Per-signal SQI falls; confidence reduced or index invalid | Validate across devices/electrocautery and annotated artifacts |
| Flatline/clipping | Flatline/extreme fractions | Low SQI; redundant modality may permit low-confidence output | UI must identify affected modality; test stuck-at plausible values |
| PPG loss/poor perfusion | Missingness/pulse confidence | Confidence reduced; invalid if no beat source | Validate delayed recovery and sensor reconnect |
| ABP flush/damping/flatline | Range, span, flatline, roughness | Low ABP SQI; MAP redundancy may permit low-confidence output | Add expert-labeled arterial-line artifact corpus |
| Excessive missing samples | Gap fraction | `INVALID`, score withheld | Distinguish source gaps from true physiologic plateaus |
| Source-reported dropout | Adapter transport flag | `INVALID`, score withheld | Device adapters must set flag consistently |
| Delayed packet/stale batch | Source latency >1000 ms | `INVALID`, score withheld | Configure validated latency per deployment; synchronize clocks |
| ECG/PPG desynchronization | Error >100 ms / sync flag | `INVALID`, score withheld | Validate multi-device clock drift and resampling |
| Out-of-order/duplicate timestamps | Ring buffer reversal count/sort | `INVALID`; duplicate retains newest value | Record upstream device sequence IDs |
| Unstable/incomplete baseline | Progress, quality, HR/MAP IQR | Baseline not calibrated; score withheld | No override; restart only under protocol |
| Unsupported age/DS mode | Metadata/mode | Confidence multiplier and reason | Not a substitute for pediatric/DS validation |
| Physiologic feature outside engineering range | OOD range checks | `INVALID` | Ranges are not clinical normal ranges; validate source units |
| Mixed sample rates | Current common-rate batch assumption | Potential misalignment/incorrect features | Add explicit per-signal resampling integration tests before device ingestion |
| Medication/surgical event confounding | Not inferable from waveform alone | Explanation cannot resolve causality | Review complete study context; never recommend treatment |
| Valid-looking artifact passes SQI | Residual possibility | May produce misleading non-null index | Expert artifact dataset, conservative invalidation, human factors testing |
| Deterministic weights/bins mistaken for probability | Metadata and copy controls | Model card says uncalibrated; no forecast field | Continue claim scans and clinician comprehension tests |
| Patient leakage in future training | Required patient IDs/split utility | Patient-level partitions | Verify manifests; site/external splits and repeated-procedure audit |
| Test-set tuning | Process control | Forbidden | Lock protocol/thresholds before test access; signed audit trail |

No failure response directs care. Existing approved clinical monitoring and escalation remain independent of T21 Safe.
