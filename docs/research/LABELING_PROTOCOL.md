# Candidate Event Labeling Protocol

문서 상태: adjudication 운영 초안 — 임상의 승인 전 endpoint 미확정<br>
label schema version: `candidate-labels/0.1.0`<br>
마지막 검토일: 2026-09-02

## 1. 목적과 경계

이 프로토콜은 retrospective/prospective shadow 연구에서 생리 변화와 임상 기록을 일관되게 annotation하기 위한 것이다. label은 진단이나 치료 지시가 아니며, 모니터의 기존 임상 alarm을 대체하지 않는다. 후보 임계값은 마취과·소아마취/치과마취·통계·IRB 검토 전 확정하지 않는다.

## 2. Label family

| Family | 후보 label | 근거 source | 현재 상태 |
| --- | --- | --- | --- |
| PHYSIOLOGY | significant relative HR decline | ECG/validated HR numeric | 정의 검토 필요 |
| PHYSIOLOGY | age-appropriate bradycardia event | ECG/HR + age | 연령별 기준 출처 필요 |
| PHYSIOLOGY | hypotension event | invasive/noninvasive BP + age/context | 기준·지속시간 검토 필요 |
| PHYSIOLOGY | desaturation | SpO2 + SQI/perfusion | 임계값·지속시간 검토 필요 |
| INTERVENTION | vasopressor administration | MAR/pump record + chart | indication은 별도 adjudication |
| INTERVENTION | anticholinergic administration | MAR/pump record + chart | indication은 별도 adjudication |
| INTERVENTION | airway intervention | airway/device/event log + note | taxonomy 검토 필요 |
| WORKFLOW | procedure interruption | procedure/anesthesia record | 원인 adjudication 필요 |
| OUTCOME | PACU escalation | PACU disposition/transfer | 기관별 정의 harmonization 필요 |

한 family의 label을 다른 family의 생리 ground truth로 자동 간주하지 않는다. 예를 들어 vasopressor 투여는 저혈압의 완전한 proxy가 아니며 예방적/다른 적응증일 수 있다.

## 3. 공통 event schema

각 event는 다음 필드를 갖는다.

```text
patient_key, case_key, site_key
event_id, label_schema_version, label_family, label_name
event_start_utc_or_relative, event_end_utc_or_relative
source_system, source_record_id, source_timestamp
algorithmic_candidate, reviewer_1, reviewer_2, adjudicator
final_status {PRESENT, ABSENT, UNCERTAIN, NOT_ASSESSABLE}
confidence {HIGH, MODERATE, LOW}
reason_code, free_text_redacted
signal_availability, sqi_status, clock_alignment_status
```

Git에는 실제 patient/case key 또는 free text를 저장하지 않는다.

## 4. 후보 정의 절차

### 4.1 Relative HR decline

후보 산식은 `100 × (HR_baseline − HR_current) / HR_baseline`이다. 이 산식 자체는 임상 cutoff가 아니다.

- baseline은 사전 정의한 안정 구간의 artifact-free central tendency로 계산한다.
- baseline이 불충분하면 `NOT_ASSESSABLE`로 두고 집단값으로 대체하지 않는다.
- 지속시간, magnitude, 허용 gap과 recovery 기준은 blinded development set 및 임상의 review 후 고정한다.
- ECG-derived HR와 monitor numeric HR가 불일치하면 ECG/SQI audit flag를 남긴다.

### 4.2 Age-appropriate bradycardia

- 연령/맥락별 기준은 연구 프로토콜에 채택한 공식 임상 reference와 임상의 합의로 별도 versioning한다.
- 단일 성인 cutoff를 소아에 적용하지 않는다.
- artifact, ectopy, pacing, monitor dropout을 제외/flag한다.
- 기존 연구의 outcome 정의를 재현하는 analysis와 병원 protocol label을 구분한다.

### 4.3 Hypotension

- invasive ABP와 noninvasive cuff BP를 구분하고 측정부위·cuff cycle·damping/SQI를 기록한다.
- absolute, age-adjusted, baseline-relative 후보를 별도 label로 유지한다.
- threshold와 최소 지속시간은 확정 전 `TBD_CLINICIAN_REVIEW`다.
- vasopressor 이전 값을 future information 없이 label candidate로 만들되 투여 자체는 별도 intervention label로 둔다.

### 4.4 Desaturation / respiratory deterioration

- SpO2 임계값·지속시간·recovery gap은 임상의 승인 전 확정하지 않는다.
- low perfusion, motion, sensor-off와 실제 desaturation을 SQI/PPG/clinical record로 구분한다.
- EtCO2, respiratory rate, airway pressure, ventilation mode와 산소 투여를 context로 보존한다.

### 4.5 Intervention labels

- MAR 주문 시각이 아니라 실제 administration/pump start/bolus 시각을 우선한다.
- source별 chart delay와 clock offset을 추정·기록한다.
- 약명, route, class는 연구용으로 정규화하되 용량 권고·우열 판단을 하지 않는다.
- indication은 두 명의 blinded clinician이 `event-related`, `prophylactic`, `other`, `uncertain` 중 adjudicate한다.

### 4.6 Airway, interruption, PACU

- airway taxonomy 후보: reposition/jaw support, oral/nasal airway, supraglottic airway, intubation/reintubation, assisted ventilation, suction, other. 실제 정의는 기관 프로토콜과 임상의 검토가 필요하다.
- procedure interruption은 시작/종료와 임상 사유를 분리한다.
- PACU escalation은 planned disposition과 unplanned escalation을 구분한다.

## 5. Time alignment

1. source clock, timezone, deidentification shift와 relative-time origin을 inventory한다.
2. monitor marker, anesthesia start, medication pump event 등 공유 anchor로 offset을 계산한다.
3. 자동 정렬 결과를 표본 수동 audit한다.
4. 허용 오차를 넘으면 해당 source 연결 label을 `UNCERTAIN` 또는 `NOT_ASSESSABLE`로 둔다.
5. corrected timestamp와 raw timestamp를 모두 보존하고 correction version을 기록한다.

## 6. Adjudication

- reviewer 2인은 RII/model output과 서로의 판정을 보지 않은 상태로 독립 검토한다.
- 불일치는 제3의 senior anesthesiologist가 해결한다.
- `UNCERTAIN`을 억지로 PRESENT/ABSENT에 병합하지 않는다.
- inter-rater agreement는 label별 Cohen's kappa 또는 prevalence 영향을 고려한 agreement와 raw agreement를 함께 보고한다.
- 최소 10% 또는 사전 정한 표본을 중복 검토하되 실제 비율은 label prevalence와 workload pilot 후 결정한다.
- adjudication manual/version, reviewer training, 변경 이유와 영향 사례 수를 보존한다.

## 7. Leakage 방지

- prediction time 이후의 signal, medication, airway, note, discharge/PACU outcome은 predictor에 들어가지 않는다.
- event 정의에 사용한 동일 signal의 미래 구간을 feature로 사용하지 않는다.
- label이 medication administration이면 drug name/time 자체를 사전 predictor로 사용할 수 있는 범위를 causal timeline으로 제한한다.
- interpolation은 window 경계를 넘어 future sample을 가져오지 않는다.
- repeated cases/windows는 patient-level split을 따른다.
- annotator는 RII와 model score에 blinded된다.

## 8. Quality states

| 상태 | 의미 | 분석 처리 |
| --- | --- | --- |
| PRESENT | 정의와 source quality를 충족 | primary label 후보 |
| ABSENT | 충분한 관찰 구간에서 정의 불충족 | negative 후보 |
| UNCERTAIN | source 충돌/시간 오차/임상 판단 불일치 | primary에서 분리; sensitivity analysis |
| NOT_ASSESSABLE | 필요한 signal/record 부재 | missingness outcome으로 보고 |

## 9. Change control

label 정의 변경은 semantic version, 승인자, 근거, 변경 전후 prevalence, affected case count를 기록한다. test/external validation label은 결과를 본 뒤 변경하지 않는다. 변경이 필요하면 새 protocol version의 별도 분석으로 간주한다.
