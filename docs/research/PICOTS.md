# PICOTS 정의

문서 상태: 임상의·통계가 검토 전 초안<br>
버전: 0.1.0<br>
마지막 검토일: 2026-09-02

## Phase 0 — 기술 pipeline 검증

| 요소 | 정의 |
| --- | --- |
| Population | VitalDB 등 공개 intraoperative 성인 사례, 공개 ICU ECG/PPG/BP, 건강 자원자 자료. DS cohort로 간주하지 않는다. |
| Index | 버전이 고정된 ingestion, resampling, time alignment, SQI, R-peak/pulse detection, HRV·PPG·PTT feature pipeline |
| Comparator | 공개 annotation, dataset reference code/metadata, 독립 reference implementation 또는 수동 검토 표본 |
| Outcomes | parsing 성공, 신호 검출 agreement, timing error, missingness/SQI failure, deterministic reproducibility |
| Timing | dataset가 제공하는 짧은 bounded sample. window 후보는 30/60/120/300초이나 metric별 최소길이 검증 전 확정하지 않는다. |
| Setting | 공개 연구 데이터의 원 setting; 실제 임상 적용 아님 |

Phase 0는 코드·신호 처리 검증이며 DS 임상 성능의 증거가 아니다.

## Phase 1–2 — 후향 DS characterization와 matched comparison

### Population

- 협력병원에서 마취 또는 진정 하에 시술을 받은 DS 환자.
- 연구 질문에 맞는 동일 기관·시기·연령대·procedure/anesthesia context의 non-DS control.
- 소아/성인은 분리 분석하고 통합 계수 하나로 일반화하지 않는다.
- 한 환자의 여러 시술은 환자 식별자로 묶는다.

후보 제외/flag 기준:

- 파형과 임상 timeline을 신뢰성 있게 연결할 수 없음
- 핵심 baseline 또는 대상 단계가 없음
- 심폐소생, 체외순환 등 사전 정의한 별도 생리 regime
- 데이터 권한 철회 또는 IRB/동의 범위를 벗어난 사례

제외는 outcome을 본 뒤 결정하지 않는다. 제외 수와 이유를 flow diagram으로 보고한다.

### Index/Exposure

- DS status는 임상 진단/유전학 정보의 승인된 구조화 자료로만 확인한다. 자연어 추정이나 phenotype inference를 사용하지 않는다.
- 환자 baseline 대비 ECG-derived HR/RR, RMSSD/SD1 후보, BP trajectory, PPG morphology/perfusion proxy, SpO2, EtCO2/respiration, signal quality와 time-varying RII 구성요소.
- 약물, airway intervention, surgical stimulus, phase annotation은 confounder/context 또는 별도 outcome이며 RII가 처치를 추천하지 않는다.

### Comparator

- Phase 1: 동일 DS 환자의 사전 정의 baseline 및 단계 간 비교.
- Phase 2: age, sex, procedure family, anesthesia/sedation context, ASA status, CHD/주요 comorbidity, site/time의 임상적으로 가능한 범위에서 matched/weighted non-DS control.
- positivity/overlap이 부족한 strata는 억지로 effect를 산출하지 않고 `not estimable`로 보고한다.

### Outcomes

후보 outcome은 [`LABELING_PROTOCOL.md`](LABELING_PROTOCOL.md)에 정의한다. 생리 event, 임상 intervention, procedure/PACU outcome을 한 복합 endpoint로 무분별하게 합치지 않는다.

### Timing

- baseline: induction/sedation 시작 전 안정 구간 후보. 목표 5분은 PRODUCT_ASSUMPTION이며 실제 안정성·가용성 audit 후 확정한다.
- 분석 단계: pre-induction/baseline, induction 또는 sedation onset, procedure/stimulus, maintenance, emergence/recovery.
- feature window 후보: 30, 60, 120, 300초. 모든 지표를 모든 window에서 허용하지 않는다.
- prediction horizon 후보: 1, 3, 5, 10분. 임상적 의미와 annotation resolution을 검토한 뒤 사전 고정한다.
- intervention 직전/직후 구간은 인과·label leakage audit에 별도 표시한다.

### Setting

- 초기 우선 setting: 대학병원/권역장애인구강진료센터의 마취·진정 연구 환경.
- monitor data export, anesthesia information system, MAR, procedure timeline과 PACU record의 합법적 연결이 가능한 기관.
- 실제 bedside 경고나 치료 workflow와 분리된 secure research environment.

## Phase 3 — Prospective silent/shadow validation

| 요소 | 정의 |
| --- | --- |
| Population | 사전 고정 eligibility를 충족하는 연속적 prospective DS 마취·진정 사례; 가능하면 matched/parallel control |
| Index | release hash, preprocessing, feature schema, model coefficients/weights, thresholds까지 frozen된 deterministic pipeline |
| Comparator | blinded clinician-adjudicated candidate endpoint와 raw/standard monitor timeline |
| Outcomes | AUROC/AUPRC, fixed false-alarm-rate sensitivity, false alarms/hour, median lead time, calibration intercept/slope, Brier score, missingness/SQI failure |
| Timing | 실행 시점에 이용 가능했던 데이터만 사용; delayed adjudication 및 record correction은 ground truth side에만 사용 |
| Setting | clinical display/decision pathway와 격리된 shadow service; clinician에게 patient-specific output 비노출 |

## Phase 4–5

- Phase 4는 synthetic 또는 replay case를 우선 사용해 comprehension, alert fatigue risk, automation bias, no-action 이해를 평가한다.
- Phase 5 advisory trial은 별도 intended use, 규제 경로, 위험관리, 성능 gate, IRB/동의와 DSMB 필요성을 재평가한 뒤에만 검토한다.

## Analysis unit

- 독립 단위는 기본적으로 **patient**다.
- procedure/case 및 time window는 환자 내 반복 측정이다.
- split, bootstrap, confidence interval 및 mixed-effects/cluster-robust analysis는 환자 clustering을 보존한다.

## 최종 확정에 필요한 사람 검토

- 소아·성인 연령층과 치과진정 대상 정의
- baseline 안정성 규칙
- age-appropriate HR/BP 기준 출처
- 임상적으로 의미 있는 prediction horizon
- CHD·OSA·airway·thyroid·antiepileptic 등 필수 교란변수
- composite endpoint 사용 여부
