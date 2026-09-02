# Validation Roadmap

문서 상태: 단계별 연구·안전 gate 초안<br>
마지막 검토일: 2026-09-02

## 원칙

- 공개 데이터는 generic pipeline을 검증하고 실제 DS 임상 성능을 대신하지 않는다.
- 각 단계는 독립적인 질문과 freeze artifact를 가진다.
- 한 단계의 실패를 문구 변경이나 test set threshold tuning으로 숨기지 않는다.
- LLM은 비실시간 연구 정리/코드 검토에만 허용하며 inference path에는 포함하지 않는다.
- Phase 3까지 patient-specific output은 임상팀에 비노출이다.

## 단계 개요

| Phase | 목적 | 핵심 데이터 | 필수 산출물 | 진입 gate | 종료/진행 gate |
| --- | --- | --- | --- | --- | --- |
| 0 | 기술 pipeline 검증 | 공개 non-DS bounded samples | signal contract, SQI/detector validation, reproducibility report | registry/license 검증 | reference agreement·failure handling·manifest 통과 |
| 1 | DS 후향 characterization | 병원 DS waveform + timeline | cohort flow, missingness/SQI, phase/event trajectories | IRB/DUA, DS 확인, clock linkage | 데이터 완전성·label feasibility·bias audit |
| 2 | Matched comparison | DS + matched non-DS | comparison SAP, balance/overlap, adjusted associations | endpoint/adjudication freeze | estimability, uncertainty, subgroup/bias review |
| 3 | Prospective silent validation | 순차 prospective DS ± controls | locked model card, prospective report, deviations | full freeze + shadow isolation | prespecified performance/calibration/burden/futility gate |
| 4 | Human factors/alarm utility research | replay/simulation 우선 | use specification, formative/summative study, misuse analysis | stable outputs, regulatory review | comprehension·workload·overreliance acceptance |
| 5 | Advisory trial 검토 | 별도 승인 임상 연구 | new intended use, clinical investigation plan, safety monitoring | MFDS/FDA strategy, QMS, IRB/regulatory approval | 사전 정의 clinical utility/safety criteria |

## Phase 0 — Public non-DS technical validation

### Work packages

1. VitalDB bounded cases: intraoperative ingestion, track alignment, numeric/waveform gaps.
2. BIDMC PPG: ECG/PPG/respiration alignment과 manual breath reference.
3. PTT PPG: synchronized ECG/PPG timing, motion/attachment-force sensitivity.
4. MIT-BIH/VitalDB Arrhythmia: R-peak/beat/rhythm detector reference.
5. Fantasia/propofol dynamics: HRV feature implementation and controlled state transitions.
6. MIMIC waveform samples: device/ICU distribution-shift stress tests.

### Freeze artifacts

- input schema and unit contract
- resampling/filter version and causal/noncausal designation
- SQI reason codes
- detector/feature reference tests
- dataset/version/license/checksum manifests
- supported/unsupported modality matrix

### Gate

필수 channel의 corrupted/missing/unit mismatch가 명시적 실패 상태를 내고, 동일 input+version에서 deterministic output이 재현되어야 한다. 숫자 기준은 benchmark pilot와 independent reviewer 승인 후 고정한다. Phase 0 결과로 DS 임상 성능을 주장하면 FAIL이다.

## Phase 1 — Retrospective DS waveform characterization

### 선행조건

- IRB 승인 또는 면제 판정과 데이터 처리 근거
- clinician-confirmed DS inclusion logic
- patient-level linkage, clock audit, source inventory
- label manual과 blinded adjudication pilot
- 원시 자료가 Git/비승인 장비에 저장되지 않는지 확인

### 분석

- eligible/evaluable flow와 repeated cases
- signal availability, missingness, SQI failure by phase/device
- baseline 및 phase-aligned trajectories
- candidate event frequency와 annotation agreement
- CHD/age/context별 기술통계
- public-to-hospital feature distribution shift

### Stop

DS status를 추정해야 하거나, event timestamp를 신뢰성 있게 복원하지 못하거나, 핵심 signal의 선택적 availability가 분석을 심각하게 왜곡하면 prediction development로 진행하지 않는다.

## Phase 2 — Matched control comparison

### 설계

- 동일 site/time과 comparable procedure context에서 control source를 정한다.
- outcome을 보기 전에 matching/weighting 변수와 estimand를 고정한다.
- patient clustering, temporal drift, monitor type, anesthesia/sedation protocol을 보존한다.
- overlap 부족 strata는 결과를 생성하지 않는다.

### Gate

- standardized balance와 positivity 검토 통과
- label adjudication agreement와 missingness 차이 수용 가능
- 관찰 association을 인과 또는 제품 효과로 과장하지 않음
- sample-size/precision scenario가 연구 질문을 지지함

## Phase 3 — Prospective silent/shadow validation

### Freeze 이전

- code commit, container/dependency lock, feature schema
- model equation/weights, calibration, thresholds, refractory/episode rules
- eligible population, endpoint, horizon, SAP, missingness/SQI rule
- model card, dataset lineage, hazard controls
- 변경 금지 날짜와 승인자

### 운영

- clinical monitor에서 read-only 복제
- 임상팀에게 output 비노출
- real-time available data만 inference에 사용
- outage, latency, clock drift, missingness, protocol deviations 기록
- 사후 blinded endpoint adjudication

### 보고

AUROC/AUPRC뿐 아니라 fixed-FAR sensitivity, false alarms/hour, missed-event rate, lead time, calibration intercept/slope, Brier, subgroup 성능, SQI failure를 CI와 함께 보고한다. test set에서 threshold를 바꾸지 않는다.

## Phase 4 — Human factors and alarm utility

- IEC 62366-1 기반 use-related risk analysis와 critical task 선정.
- replay/synthetic cases로 연구 score, data unavailable, quality limitation, disclaimer 이해를 시험.
- outcome: task success, time, comprehension, trust calibration, workload, alarm fatigue/overreliance, prohibited action 시도.
- 실제 patient care에 영향을 주는 실시간 시험은 별도 승인 전 금지.
- “no action”과 기존 monitor 우선 원칙을 이해하지 못하면 UI progression을 중단한다.

## Phase 5 — Advisory clinical trial consideration

Phase 5는 자동 진입이 아니다. 다음을 모두 충족한 뒤 steering committee가 별도 go/no-go를 결정한다.

- intended use와 device status/등급 경로의 MFDS 사전상담 및 필요 FDA 전략
- ISO 14971 risk management와 IEC 62304 lifecycle evidence
- IEC 62366-1 summative plan, cybersecurity plan, clinical evaluation plan
- prospective external validation과 subgroup calibration
- clinical equipoise, endpoint, sample size, DSMB/medical monitor 필요성
- liability, training, site readiness, post-market/monitoring 구상

## Cross-phase artifacts

모든 phase에서 다음을 보존한다.

- data manifest와 registry version
- protocol/SAP/label version
- code/model/container hash
- approval, deviation, issue, corrective action log
- eligible/excluded/evaluable flow
- negative/null/failed results
- reviewer sign-off와 unresolved questions

## 독립 검토

- Clinical: endpoint, age/context, CHD/airway/medication confounding
- Dataset: access, license, DS identification, linkage, distribution shift
- Biostatistics: estimand, leakage, split, precision, calibration
- Regulatory/Safety: intended use, UI claim, device path, hazards

판정 형식은 [`RESEARCH_REVIEW_BOARD.md`](RESEARCH_REVIEW_BOARD.md)를 사용한다.
