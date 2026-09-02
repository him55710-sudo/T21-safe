# T21 Safe Research Product Requirements Document

문서 상태: RUO / Shadow Mode 연구 요구사항<br>
PRD version: `0.1.0`<br>
마지막 검토일: 2026-09-02<br>
근거: [`EVIDENCE_SUMMARY.md`](EVIDENCE_SUMMARY.md), [`EVIDENCE_LEDGER.csv`](EVIDENCE_LEDGER.csv)

> **Research Use Only. 임상적 유효성은 검증되지 않음. 진단, 치료, 투약 또는 환자감시 목적으로 사용하지 않음.**

## 1. Clinical problem

소아 DS의 sevoflurane 흡입 유도에서는 비교군보다 서맥이 더 자주 관찰되었다(PMID 40376277, 21109130, 20736433). DS 소아·젊은 성인의 procedural sedation에서도 비교군보다 큰 혈압 감소가 관찰되었으나 임상적 의미는 아직 불확실하다(PMID 40704557). 동시에 단일기관 DS 소아 비심장 마취 코호트의 전체 합병증률은 낮게 보고되었고 내부 non-DS 대조군이 없었다(PMID 40363932). 따라서 문제는 “DS 마취는 항상 위험하다”가 아니라 다음 연구 격차다.

- 특정 상황에서 관찰된 변화를 환자별, 시간 정렬된 다중 신호로 재현할 수 있는가?
- artifact·환기·약물·airway/procedure event를 구분할 수 있는가?
- 공개 non-DS 자료로 기술 pipeline을 검증한 뒤 실제 DS 병원 자료에서 독립적으로 검증할 수 있는가?

## 2. Target users

- **Anesthesiologist:** 연구 protocol 설계, 사건 adjudication, replay 검토.
- **Dental anesthesiology team:** 장애인 구강진료 환경의 sedation/anesthesia data 수집과 단계 annotation.
- **Regional disability oral health center researcher:** cohort governance, IRB, 데이터 품질, 연구 export와 결과 해석.

개발자·통계가·규제/안전 담당자는 운영 이해관계자지만 patient-specific 임상 사용자는 아니다.

## 3. Initial intended environment

- 대학병원 또는 권역장애인구강진료센터의 승인된 연구망.
- monitor/anesthesia information system에서 복제된 연구용 stream 또는 retrospective export.
- 실제 bedside monitor, alarm, pump, ventilator, EHR order entry와 논리·물리적으로 분리.
- UTC 또는 검증된 relative time, device/source clock metadata, deidentified research key 사용.
- prospective 단계에서도 output은 연구 서버에 저장하고 치료팀 화면에는 표시하지 않는다.

## 4. Research-only intended use

T21 Safe는 마취·진정 연구에서 환자별 ECG, PPG, BP, SpO2, EtCO2/respiration 및 임상 event의 시간적 변화를 수집·품질검사·분석하고, 혈역학적 변화 전조를 탐색하기 위한 **Research Instability Index(RII)** 및 구성요소를 생성하는 소프트웨어다.

RII는 연구 지표이며 임상 위험 확률, 진단, 예후, 경고 또는 처치 권고가 아니다.

## 5. Explicit non-intended use

다음 용도는 금지한다.

- 실시간 환자감시, bedside alarm 대체 또는 alarm suppression
- 진단·triage·치료·투약·마취제 용량·수액·airway 처치 추천
- 펌프, ventilator, monitor, EHR order의 자동/반자동 제어
- 의료진 또는 기관의 DS 마취 수행 가능 여부 판단
- DS 외관/파형으로 진단 상태 추정
- 임상적으로 검증된 확률·예방효과·정확도·안전성 주장
- 보험, 접근 제한, 인력 평가 또는 환자/보호자에게 위험 수치 제공

## 6. Data inputs

### 필수 연구 입력

- patient/case/site pseudonymous keys
- ECG 또는 validated HR source
- PPG/SpO2와 sensor/perfusion quality context
- noninvasive BP 및 가능 시 invasive arterial pressure, 측정 source 포함
- procedure/anesthesia/sedation phase timestamps
- source clock, sample rate, units, device/channel metadata

### 권장 context

- EtCO2/capnogram, respiratory rate, airway pressure, ventilation mode
- age band, sex, height/weight, ASA status
- clinician-confirmed DS status; CHD, OSA/airway, thyroid/neurologic comorbidity
- medication administration time/class, airway intervention, procedure stimulus/interrupt, PACU disposition
- BIS/EEG 등은 가용 시 별도 exploratory input이며 RII 필수 입력이 아니다.

입력마다 `source`, `available_at`, `unit`, `clock`, `quality`, `missing_reason`, `transform_version`을 기록한다.

## 7. Patient baseline calibration

- 대상 단계 이전의 안정적이고 SQI를 통과한 구간을 이용해 환자별 median/robust variability를 계산한다.
- 목표 5분 baseline은 PRODUCT_ASSUMPTION이며 실제 workflow/availability audit와 임상의 승인을 거쳐 고정한다.
- baseline 안정성은 HR/BP/respiratory trend, intervention, movement/artifact, missingness로 판정한다.
- baseline이 없거나 불안정하면 baseline-dependent feature/RII를 `UNAVAILABLE`로 둔다. 다른 환자나 인구 평균으로 대신하지 않는다.
- recalibration 조건은 protocol version으로 고정하며 사건을 본 뒤 소급 변경하지 않는다.

## 8. Signal quality gate

각 modality는 `GOOD`, `LIMITED`, `UNUSABLE`, `MISSING` 상태와 reason code를 낸다.

- ECG: lead-off, saturation, powerline/noise, R-peak plausibility, ectopy burden.
- PPG/SpO2: sensor-off, motion, low perfusion, clipping, pulse agreement.
- BP: cuff cycle/failed measurement, arterial damping/flush/artifact, source switching.
- EtCO2/respiration: disconnected/sampling-line artifact, ventilation mode/context.
- multimodal consistency: ECG–PPG pulse timing, HR agreement, clock offset.

필수 signal이 `UNUSABLE/MISSING`이면 RII를 계산하지 않고 `insufficient signal quality`만 연구 로그에 기록한다. 품질 실패 자체를 환자 위험으로 해석하지 않는다.

## 9. Research Instability Index

### 설계

- `0–100`과 같은 범위를 쓰더라도 **확률이 아닌 dimensionless 연구 score**로 명시한다.
- 입력, preprocessing, feature, weights/coefficients, missingness rule, threshold, update cadence, checksum을 release manifest로 고정한다.
- 초기 후보 구성: baseline-relative HR/BP trajectory, signal-quality-weighted PPG morphology, oxygenation/respiratory context, 검증된 window의 metric-specific HRV, cross-signal consistency.
- RII 계산은 deterministic signal pipeline 및 versioned statistical/ML model만 사용한다.
- LLM, generative model, 온라인 self-learning, 환자별 자동 threshold 변경을 금지한다.

### 상태

- `AVAILABLE_RESEARCH_SCORE`
- `BASELINE_NOT_ESTABLISHED`
- `INSUFFICIENT_SIGNAL_QUALITY`
- `MODEL_NOT_APPLICABLE`
- `PIPELINE_ERROR`

오류/결측 상태에서 이전 score를 최신값처럼 유지하지 않는다.

## 10. Explainability outputs

연구 replay/export에 다음을 함께 제공한다.

- score timestamp와 사용한 lookback/horizon
- 현재/과거 signal-quality 상태와 exclusion reason
- top score components: 예) `baseline-relative HR change`, `BP trajectory unavailable`, `PPG quality limited`
- 각 component의 방향·크기·단위와 baseline reference
- data provenance와 algorithm/model version
- uncertainty/unsupported 상태

“sympathetic failure”, “vagal excess”, “baroreflex failure” 같은 기전을 feature만으로 확정 표시하지 않는다. LF/HF를 sympathovagal balance라고 부르지 않는다(PMID 23431279).

## 11. Event timeline

timeline은 raw/derived signal quality, phase, candidate physiology event, medication administration, airway intervention, procedure marker, model output을 서로 다른 lane으로 표시한다.

- raw source timestamp와 corrected timestamp를 추적한다.
- 임상 action을 model이 유발한 것처럼 표현하지 않는다.
- future-adjudicated label은 replay에서만 보이고 prospective score 계산에는 들어가지 않는다.
- medication dose 또는 처치 우선순위를 시각적으로 추천하지 않는다.
- event definition/schema version을 hover/export metadata에 포함한다.

## 12. Shadow Mode workflow

1. 연구대상/동의·IRB·data route eligibility 확인.
2. 임상 monitor는 기존 workflow대로 유지하고 T21 Safe는 read-only 복제 stream만 받는다.
3. ingestion → unit/clock checks → SQI → feature → frozen RII를 연구망에서 수행.
4. patient-specific output을 임상팀·환자·보호자에게 실시간 표시하지 않는다.
5. 기존 임상 기록과 별개로 immutable run manifest/log를 저장한다.
6. 시술 후 blinded clinician adjudication을 수행한다.
7. pre-specified analysis와 stop criteria를 적용한다.

T21 Safe 장애는 clinical monitoring에 영향을 주지 않아야 한다. 연구 소프트웨어가 끊겨도 현장 진료가 계속되는 구조를 검증한다.

## 13. Data export for research

- deidentified case-level Parquet/CSV 및 waveform reference manifest
- event/label table, feature table, SQI/missingness table, model run table
- data dictionary, units, timestamps, timezone/relative origin, provenance
- dataset/model/feature/label/SAP version과 SHA-256 checksum
- export approval, requester, purpose, scope, retention/expiry audit

free text·direct identifier·raw clinical keys는 기본 export에서 제외한다. 라이선스/DUA가 금지하는 재배포를 하지 않는다.

## 14. Human override and no-action policy

- 현재 Path B에는 clinician action 또는 override 대상이 되는 clinical recommendation이 없다.
- 연구 운영자는 ingestion을 중지하거나 case를 연구 분석에서 quarantine할 수 있다. 이 조치는 임상 진료를 변경하지 않는다.
- RII와 연구 event는 “no action required / not for clinical use” 상태를 항상 동반한다.
- 임상의가 우연히 output을 보더라도 기존 monitor와 임상 판단만 따르도록 protocol/training에 명시한다.
- clinical concern은 T21 Safe가 아니라 기존 hospital escalation pathway로 처리한다.

## 15. Known limitations

- 공개 데이터에서 충분한 DS 마취 사례와 DS-specific waveform linkage가 확인되지 않았다.
- 공개 자료는 주로 성인, ICU, 건강 자원자 또는 단일기관이며 소아 DS로 distribution shift가 크다.
- VitalDB는 DS label을 확인했다고 가정할 수 없고 INSPIRE는 관련 chromosomal diagnosis를 제거한다.
- HRV는 window, respiration, ventilation, nonstationarity, ectopy와 artifact에 민감하다.
- 임상 intervention label은 physiology의 완전한 ground truth가 아니며 practice variation이 있다.
- DS 연구 문헌은 주로 소아 sevoflurane 유도에 집중되어 약제·연령 일반화가 제한된다.
- RII의 calibration, lead time, false-alarm burden, clinical utility는 검증되지 않았다.
- rare event/subgroup 분석은 넓은 uncertainty와 selection bias를 가진다.

## 16. Clinical validation roadmap

- **Phase 0:** 공개 non-DS 데이터로 ingestion/SQI/detection/feature pipeline 검증.
- **Phase 1:** 병원 DS 후향 waveform characterization.
- **Phase 2:** DS와 matched control 비교.
- **Phase 3:** frozen prospective silent/shadow validation.
- **Phase 4:** replay/simulation 기반 human factors 및 alarm utility research.
- **Phase 5:** 충분한 gate 통과 후 advisory clinical trial 가능성 검토.

세부 gate와 산출물은 [`VALIDATION_ROADMAP.md`](VALIDATION_ROADMAP.md)를 따른다.

## 17. Product expansion hypotheses

아래는 `RESEARCH_HYPOTHESIS`이며 roadmap 약속이 아니다.

- 치과진정 workflow에 특화된 phase annotation과 replay.
- 다른 취약집단 또는 다른 procedure에서 동일 generic pipeline의 독립 검증.
- multimodal BP/PPG/ECG quality fusion.
- validated clinical research export를 이용한 site-to-site federated analysis.
- 규제·임상 근거 확보 후 clinician-facing advisory의 별도 제품 경로.

각 확장은 intended use, data representativeness, 규제 분류, risk management와 검증을 처음부터 다시 평가한다.

## 18. Success metrics

### 기술

- ingestion/units/clock validation 성공률
- reference annotation 대비 R-peak/PPG detection agreement
- deterministic rerun bitwise 또는 허용오차 내 재현성
- data provenance/manifest completeness
- missingness와 SQI failure rate

### 연구 성능

- AUROC, AUPRC
- fixed false-alarm rate에서 sensitivity
- false alarms/hour
- median lead time
- calibration slope/intercept, Brier score
- decision curve analysis(정당한 threshold가 있을 때만)
- subgroup performance와 uncertainty

### 운영·안전

- patient-level split/leakage audit 통과
- shadow isolation 및 failure-independence test 통과
- clinician comprehension/misuse rate
- data/privacy/security incident 0건 목표

목표 수치는 데이터 audit와 임상의·통계·human-factors review 후 protocol version에 고정한다.

## 19. Stop criteria

다음 중 하나면 해당 단계 진행 또는 model deployment를 중단한다.

- DS status, endpoint 또는 waveform timeline을 신뢰성 있게 확인할 수 없음
- 필수 SQI/clock/data provenance 기준 미달
- patient/site leakage 또는 future information 사용 발견
- prospective frozen 성능/precision/futility gate 미달
- subgroup에서 임상적으로 우려되는 큰 성능 격차
- 과도한 false-alarm burden 또는 automation bias/misuse
- 연구 output이 실제 임상 판단에 사용된 protocol deviation
- 개인정보·보안·DUA·IRB 위반 또는 serious incident
- 규제/안전 검토가 현재 intended use와 architecture를 지지하지 않음

중단은 조용히 threshold를 바꾸는 것으로 해결하지 않는다. 원인, 영향 범위, corrective action, 새 version과 재검증 필요성을 기록한다.

## 허용·금지 문구

허용:

- “환자별 생체신호 변화를 분석하는 연구용 도구”
- “혈역학적 변화 전조를 탐색하기 위한 연구 지표”
- “임상적 유효성은 검증되지 않음”
- “진단, 치료, 투약 또는 환자감시 목적으로 사용하지 않음”

금지:

- “DS 환자의 마취 사고를 예방합니다.”
- “서맥을 정확히 예측합니다.”
- “마취제 용량을 최적화합니다.”
- “일반 병원도 안전하게 DS 마취를 할 수 있게 합니다.”
