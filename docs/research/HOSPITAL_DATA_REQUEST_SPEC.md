# Hospital Data Request Specification

문서 상태: 협력기관 feasibility/data extract 요청 초안<br>
schema version: `hospital-request/0.1.0`<br>
마지막 검토일: 2026-09-02

## 1. 요청 목적

DS 환자의 마취·진정 전후 다중 생체신호를 **후향적으로 characterization**하고, 이후 frozen pipeline의 prospective silent validation 가능성을 평가한다. 이 요청은 임상용 모델 학습, 치료 권고, 투약 최적화 또는 펌프 제어를 위한 것이 아니다.

먼저 aggregate feasibility count와 synthetic/deidentified 1–3 case schema sample을 요청한다. 데이터 적합성·IRB·DUA·보안 승인 전 전체 extract를 요구하지 않는다.

## 2. Cohort identification

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `research_patient_id` | Yes | 기관 honest broker가 생성; MRN 불가 |
| `research_case_id` | Yes | procedure/anesthesia encounter pseudonym |
| `site_id` | Yes | 연구용 site code |
| `ds_status` | Yes | `CONFIRMED`, `NOT_DS`, `UNCERTAIN`; UNCERTAIN은 DS cohort 제외 |
| `ds_confirmation_source` | Yes | clinician diagnosis/approved structured code/genetic confirmation category; 원 유전자료 불필요 |
| `age_at_case` 또는 age band | Yes | IRB 재식별 정책에 맞는 정밀도 |
| `sex_recorded` | Requested | source/unknown 포함 |
| `procedure_family` | Yes | 최소필요 범주; free text 최소화 |
| `anesthesia_or_sedation_type` | Yes | 기관 taxonomy와 mapping 제공 |
| `asa_physical_status` | Requested | source/time 포함 |
| `chd_status/type` | Requested | 구조화 범주; 수술/현재 상태 구분 가능 시 포함 |
| 주요 context | Requested | OSA/airway, thyroid, epilepsy/neurologic, pulmonary hypertension 등 clinician-approved list |

ICD Q90 존재만으로 waveform 사례 수를 추정하지 않고, 승인된 cohort query 후 unique patient/case 및 waveform 교집합을 별도 산출한다.

## 3. Phase/time anchors

- admission/procedure room in/out
- monitor connect/disconnect
- anesthesia/sedation start/end
- induction start와 airway secured(해당 시)
- procedure/incision/stimulus start/end 또는 치과 시술 단계
- emergence/recovery start
- PACU in/out 및 disposition

각 timestamp에 source system, raw precision, timezone 또는 relative-time origin, charted-vs-device time를 포함한다. deidentification shift는 동일 case 내 source alignment를 보존해야 한다.

## 4. Waveforms

| Modality | 우선순위 | 희망 기술 정보 |
| --- | --- | --- |
| ECG | Required if available | raw lead(s), native sample rate, gain/units, lead label, device/model, gap/lead-off |
| PPG | Required if available | raw pleth, native sample rate, wavelength/site if known, perfusion/SQI, device/model |
| Invasive arterial BP | High | raw waveform, transducer/site, sample rate, units, flush/damping markers |
| Capnogram | High | raw waveform, units, sample rate, sampling mode |
| Airway pressure/flow | Optional high value | raw waveform, circuit/ventilation context |
| EEG/BIS-related | Optional exploratory | raw/processed distinction, sensor/device, index/SQI; separate governance |

희망 engineering minimum은 ECG/PPG 100 Hz 이상, ECG R-peak reference에는 가능하면 250 Hz 이상이지만 이는 **수집 적합성 요청값**이지 임상 표준 주장이나 제외 기준 확정값이 아니다. native data를 우선하며 resampled 자료면 원 rate/filter를 제공한다.

## 5. Numeric time series

- HR/PR, RR interval 가능 시
- SpO2, perfusion index/SQI
- NIBP SYS/DIA/MAP와 cuff cycle/failure
- invasive SYS/DIA/MAP
- EtCO2, inspired CO2, respiratory rate
- airway pressure, tidal volume, minute ventilation, PEEP, ventilation mode
- inspired/expired anesthetic concentration, FiO2
- temperature
- BIS/processed EEG index/SQI(가용 시)

필드마다 units, native update cadence, device/source, valid range, sentinel/missing codes, preprocessing/averaging을 data dictionary에 적는다. 단위를 추정하지 않는다.

## 6. Medication and fluid context

- actual administration/bolus/infusion start-stop time
- normalized generic class와 local code; route
- dose/units는 연구 confounding/timeline 용도로만 수집하며 처방 권고에 사용하지 않는다.
- order time, chart time, device administration time을 구분한다.
- vasopressor, anticholinergic, anesthetic/sedative, analgesic, neuromuscular blocker, reversal, IV fluid/blood product의 institution-approved mapping.
- prophylactic/therapeutic indication은 자동 추정하지 않고 adjudication 가능성만 검토한다.

## 7. Airway, procedure, and postoperative events

- airway device, insertion/removal and intervention timestamp
- assisted ventilation, reposition/support, suction, intubation/reintubation 등 기관 taxonomy
- procedural stimulus/interrupt/abort와 reason category
- standard monitor alarm/event logs(가능 시; device rule/version 포함)
- PACU escalation, unplanned admission/transfer, planned disposition
- 사전 승인된 postoperative outcome window와 구조화 outcome

free text는 먼저 요구하지 않는다. 구조화 자료로 불충분하고 IRB가 허용할 때만 honest-broker redaction/NLP 비실시간 연구를 별도 검토한다. LLM이 실시간 label/inference를 만들지 않는다.

## 8. Candidate labels/adjudication support

[`LABELING_PROTOCOL.md`](LABELING_PROTOCOL.md)의 label family를 지원할 source record ID와 audit trail을 요청한다. 최종 threshold는 임상의와 통계가 승인 전 확정하지 않는다. reviewer에게 model/RII output을 보이지 않도록 source export와 model output을 분리한다.

## 9. Data format

선호 형식:

- waveforms: WFDB, HDF5 또는 lossless institution format + header/data dictionary
- tabular: Parquet 또는 RFC 4180 CSV + UTF-8
- timestamps: ISO 8601 UTC 또는 case-relative seconds + origin metadata
- event: one row per event; interval이면 start/end
- units: UCUM mapping 가능 시 제공, local raw unit 보존
- terminology: ICD/SNOMED/LOINC/RxNorm/ATC/local mapping은 사용한 version 포함
- provenance: FHIR R4 export를 사용하는 경우 resource/profile/version과 `Provenance`/device source 보존

point-of-care device 통합에 IEEE 11073를 사용한 경우 적용 profile과 vendor mapping을 제공한다. 표준 미사용 자체가 데이터 배제 이유는 아니며 변환 audit가 필요하다.

## 10. Data quality package

- source system/device inventory와 software version
- sample rate/update cadence, averaging/filtering
- unit dictionary와 valid/sentinel codes
- clock architecture/NTP/known drift와 outage
- channel availability by year/room/device
- duplicate/repeated cases, merge/split rules
- missingness summary와 extract logic
- known firmware/schema changes
- cohort query SQL 또는 재현 가능한 specification
- deidentification/date-shift method와 linkage preservation

## 11. Feasibility counts — aggregate first

기관에 먼저 다음 aggregate만 요청한다.

- year별 unique DS patients와 anesthesia/sedation cases
- age band, procedure family, anesthesia/sedation type, CHD status별 수
- ECG/PPG/BP/SpO2/EtCO2 waveform 또는 numeric 교집합
- medication/airway/PACU timestamp availability
- repeated cases per patient
- potential control pool과 overlap
- 예상 data volume, retention period, extract cost/time

small cell은 기관 정책에 따라 suppress한다. 이 count로 DS case count를 대외 주장하지 않는다.

## 12. Governance and transfer

- IRB protocol/waiver/consent scope
- DUA, controller/processor 역할, secondary use, publication, IP 조건
- on-prem/secure enclave 우선; cloud/cross-border 여부 별도 승인
- encryption, MFA, least privilege, audit, incident reporting
- retention/expiry/deletion certificate
- re-identification 금지와 linkage key의 honest-broker 분리
- raw data Git/개인 노트북/비승인 SaaS 업로드 금지

## 13. Acceptance tests

전체 extract 승인 전 small sample에서 다음을 확인한다.

1. schema/data dictionary completeness
2. units와 plausible range(값 수정 없이 flag)
3. case/source clock alignment와 drift
4. waveform sample count/sample-rate/header 일치
5. missing/sentinel/duplicate 처리
6. patient/case uniqueness와 repeated-case linkage
7. medication/event source timestamp 의미
8. deidentification과 direct identifier 부재
9. manifest: source, version, license/DUA, checksum
10. deterministic parser rerun 결과

실패 시 전체 extract를 계속 받지 않고 수정된 sample로 재검증한다.

## 14. 명시적 비요청

- 펌프 제어 API 또는 EHR order write access
- 실시간 bedside alarm suppression/control
- 얼굴·음성·불필요한 free text/direct identifier
- DS phenotype을 추론하기 위한 이미지·유전 원자료
- 규제/IRB/DUA를 우회한 공개 또는 사설 데이터
