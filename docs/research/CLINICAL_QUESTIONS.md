# Clinical Questions

문서 상태: 임상의 검토 전 연구 질문 초안<br>
마지막 검토일: 2026-09-02

## 의사결정 질문

T21 Safe의 현재 목적은 “어떤 처치를 해야 하는가?”에 답하는 것이 아니다. 다음에 답할 수 있는 근거가 존재하는지 단계적으로 확인하는 것이다.

1. 공개 non-DS 데이터로 다중 생체신호 ingestion, 시간 동기화, signal-quality gate와 feature 계산을 재현 가능하게 구현할 수 있는가?
2. DS 마취·진정 사례에서 baseline 대비 HR, BP, SpO2, PPG, respiration/EtCO2와 HRV feature의 시간적 궤적은 어떠한가?
3. 같은 기관·시기·절차의 matched non-DS control과 비교했을 때 궤적과 사전 정의 사건 분포가 다른가?
4. 사건 이후 정보를 사용하지 않는 고정 deterministic pipeline과 검증 가능한 통계·ML 모델이 prospective silent mode에서 adjudicated event 전 변화를 포착하는가?
5. signal quality와 설명 가능한 구성요소가 의료진의 연구 검토에 충분하며 불필요한 alarm-like 행동을 유발하지 않는가?

## 질문·단계·estimand 매핑

| ID | 단계 | 질문 | 주요 estimand/산출물 | 판정 전제 |
| --- | --- | --- | --- | --- |
| CQ-00A | Phase 0 | 다양한 공개 파형을 동일 계약으로 읽고 단위·시간축·결측을 추적할 수 있는가? | 파일/track 성공률, 단위 검증률, 동기화 오류, missingness | 임상 유효성 질문이 아님 |
| CQ-00B | Phase 0 | ECG R-peak, PPG pulse, SQI, HRV/PTT feature가 공개 annotation 또는 reference 구현과 일치하는가? | detection sensitivity/PPV, timing error, feature agreement | DS 성능 주장 금지 |
| CQ-01A | Phase 1 | DS 사례에서 유도·진정·시술·회복 단계별 생리 궤적은 무엇인가? | 환자별 baseline 대비 변화의 분포, event-aligned trajectory | 단일군 characterization |
| CQ-01B | Phase 1 | artifact, ventilation, 약물·자극·airway intervention과 변화가 어떻게 시간적으로 겹치는가? | 시간 정렬 audit, mixed-effects exploratory coefficients | 인과효과로 해석 금지 |
| CQ-02A | Phase 2 | DS와 matched control의 사전 정의 event 발생 및 궤적이 다른가? | adjusted risk difference/ratio 또는 trajectory contrast | matching/adjustment와 overlap 확인 |
| CQ-02B | Phase 2 | CHD, 연령, sedation/anesthesia context에 따라 차이가 달라지는가? | 사전 정의 interaction 및 subgroup CI | 검정력 부족 시 기술통계만 |
| CQ-03A | Phase 3 | frozen RII가 silent validation에서 후보 사건을 얼마나 구분하는가? | AUROC, AUPRC, fixed-FAR sensitivity, false alarms/hour | threshold는 test에서 조정 금지 |
| CQ-03B | Phase 3 | 사건 전 사용 가능한 lead time과 calibration은 어떠한가? | median/IQR lead time, calibration intercept/slope, Brier score | 임상 확률 주장은 별도 검증 전 금지 |
| CQ-04A | Phase 4 | 연구 화면이 올바른 signal-quality/원인 구성요소 이해를 돕는가? | comprehension, task completion, misuse/overreliance, workload | 실제 치료 의사결정에 사용하지 않음 |
| CQ-05A | Phase 5 | advisory clinical trial을 검토할 충분한 기술·임상·규제 근거가 축적됐는가? | go/no-go evidence package | 별도 규제·IRB·안전 승인 필요 |

## 후보 endpoint 질문

아래는 **후보**이며 최종 endpoint가 아니다. 정의와 임계값은 마취과·소아마취/치과마취·통계·IRB 검토 후 protocol/label version으로 고정한다.

- significant relative HR decline
- age-appropriate bradycardia event
- hypotension event
- vasopressor administration
- anticholinergic administration
- airway intervention
- desaturation
- procedure interruption
- PACU escalation

약물·airway·PACU 항목은 생리적 ground truth가 아니라 임상 행동/경과 표지자다. 현장 practice, indication, documentation latency의 영향을 받으므로 별도 outcome family로 분석한다.

## 기전 질문

- M-01: DS군의 사건 전 변화가 sympathetic failure 관련 feature와 동반되는가?
- M-02: respiratory/ventilation context를 고려한 후 RMSSD·SD1 변화가 남는가?
- M-03: baroreflex proxy 또는 BP-HR coupling이 control과 다른가?
- M-04: resting baseline feature보다 provoked/time-varying feature가 더 재현 가능한가?

모든 기전 질문은 `RESEARCH_HYPOTHESIS`다. feature는 실제 sympathetic/vagal activity 또는 baroreflex를 직접 측정하는 것으로 명명하지 않는다.

## 명시적 비질문

- 어떤 약물·용량·수액·처치가 최적인가?
- atropine 또는 특정 약물에 대한 DS 특이 반응을 어떻게 치료해야 하는가?
- 펌프 또는 ventilator를 자동 제어할 수 있는가?
- T21 Safe가 사고를 예방하거나 임상 outcome을 개선하는가?
- 어느 병원이 DS 마취를 수행해야 하는가?

이 질문들은 현재 Path B 범위에 없고, 본 연구의 관찰 자료로 답하지 않는다.

## 근거 연결

임상 질문의 배경과 정량 근거는 [`EVIDENCE_LEDGER.csv`](EVIDENCE_LEDGER.csv) CLN-001~011, HRV-001~006 및 [`EVIDENCE_SUMMARY.md`](EVIDENCE_SUMMARY.md)를 따른다.
