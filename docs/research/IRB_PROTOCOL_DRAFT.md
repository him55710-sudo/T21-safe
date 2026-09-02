# IRB Protocol Draft

문서 상태: 기관별 양식 이전의 연구계획 초안<br>
protocol version: `0.1.0`<br>
마지막 검토일: 2026-09-02

> 이 문서는 IRB 승인서가 아니다. 기관 연구책임자, 마취과·치과마취 임상의, 통계가, 개인정보/정보보안 담당자와 IRB가 수정·승인해야 한다.

## 1. 행정 정보

- 연구명: Down syndrome 환자의 마취·진정 중 다중 생체신호 변화에 관한 단계적 관찰연구
- 영문명: Staged Observational Study of Multimodal Physiological Changes During Anesthesia or Sedation in Individuals with Down Syndrome
- 연구책임자(PI): `TBD_HOSPITAL`
- 의학책임자: `TBD_ANESTHESIOLOGIST`
- 통계책임자: `TBD_BIOSTATISTICIAN`
- 수행기관/부서: `TBD_SITE`
- 연구기간: IRB 승인일 이후 기관·연구책임자·통계가가 데이터 가용성과 단계별 중지규칙을 검토해 확정
- 자금/이해상충: `TBD_DISCLOSURE`
- 연구등록: prospective 단계 전 공개등록 필요성 검토

## 2. 배경과 근거

소아 DS의 sevoflurane 흡입 유도에서 비교군보다 서맥이 더 자주 관찰되었다(PMID 40376277, 21109130, 20736433). procedural sedation 연구에서는 DS 소아·젊은 성인의 혈압 감소가 비교군보다 컸으나 임상적 의미는 불확실하다고 보고되었다(PMID 40704557). 반면 DS 소아 비심장 마취의 단일기관 후향 코호트는 1,713건 중 51건(2.98%)의 합병증을 보고했고 내부 non-DS 비교군이 없었다(PMID 40363932; DOI `10.3390/jcm14092900`). 이 근거는 모든 DS 마취가 위험하다는 결론이 아니라, 맥락별 생리 궤적과 데이터 품질을 체계적으로 연구할 필요를 지지한다.

공개 VitalDB/PhysioNet 데이터는 generic signal processing에는 유용하지만 충분한 DS 마취 사례를 확인할 수 없다. 실제 DS validation은 기관 승인 자료가 필요하다.

## 3. 연구 목적

### Primary — 단계별

- Phase 1: DS 마취·진정 사례에서 ECG/HR, PPG/SpO2, BP, EtCO2/respiration의 단계별·event-aligned 궤적과 데이터 품질을 기술한다.
- Phase 2: 사전 정의한 matched non-DS control과 후보 사건 및 궤적의 adjusted association을 추정한다.
- Phase 3: frozen Research Instability Index(RII)를 prospective silent/shadow mode에서 adjudicated candidate event에 대해 검증한다.

### Secondary

- CHD, 연령층, procedure/anesthesia context, airway/respiratory context별 이질성을 탐색한다.
- signal-quality failure, missingness, time-alignment 오류를 정량화한다.
- candidate label의 reviewer agreement와 feasibility를 평가한다.

### 연구 범위 밖

치료 효과, 약물/용량 최적화, 사고 예방, 임상 alarm 대체 또는 펌프/ventilator 제어를 평가하지 않는다.

## 4. 연구 설계

### Module R — Retrospective observational study

- 기존 마취/진정 사례의 deidentified waveform, monitor numeric, anesthesia record, MAR, procedure/PACU 기록을 연결한다.
- DS 단일군 characterization 후 별도 protocol-defined matched comparison을 수행한다.
- 임상 진료에 접촉·개입하지 않는다.

### Module P — Prospective silent observational study

- Module R에서 freeze된 pipeline을 read-only 복제 stream에 실행한다.
- patient-specific RII/output은 임상팀과 환자에게 표시하지 않는다.
- 기존 monitor와 진료 workflow는 변경하지 않는다.
- 사후 blinded clinician adjudication과 pre-specified SAP 분석만 수행한다.

Module P는 별도 amendment/IRB 승인, 동의 전략, 정보보안 및 device/regulatory 검토 후 시작한다.

## 5. 연구 대상

### Inclusion 후보

- 기관 기록에서 clinician-confirmed Down syndrome 진단이 확인된 환자
- 연구기간 내 마취 또는 진정 하 시술/검사를 받은 사례
- 필요한 최소 timeline과 연구 변수의 합법적 linkage가 가능한 사례

### Control 후보

- 동일 기관·시기·comparable procedure/anesthesia context의 non-DS 환자
- age, sex, ASA status, CHD/주요 comorbidity, procedure family, site/time에 대한 overlap이 있는 사례

### Exclusion/flag 후보

- 동의 철회/opt-out 또는 법적·IRB 범위 밖 자료
- DS status를 추정해야 하는 사례
- patient/case linkage 또는 clock alignment를 신뢰할 수 없는 사례
- 사전 정의한 별도 생리 regime(예: 심폐소생/체외순환) — 무조건 제외 대신 별도 cohort 여부 검토

최종 criteria는 outcome을 보기 전 고정한다.

## 6. 취약한 연구대상자 보호

DS 환자와 소아는 의사결정능력·동의권·부당한 영향·프라이버시를 특별히 보호한다.

- prospective 참여에는 법정대리인 동의와 가능한 범위의 대상자 assent 절차를 기관 규정에 따라 마련한다.
- 의사결정능력은 진단명만으로 일괄 판단하지 않는다.
- 참여 거절/철회가 진료에 영향을 주지 않음을 명시한다.
- recruitment는 treating clinician의 부당한 영향이 없도록 분리한다.
- 연구 결과를 개인 임상 위험으로 반환하지 않는다.

Retrospective 동의 면제는 최소위험, practicability, 권리·복지 영향, 개인정보 보호 등 해당 법/기관 기준을 PI와 IRB가 판단하며 본 초안이 면제를 단정하지 않는다.

## 7. 표본 크기

고정값은 아직 선언하지 않는다. 기관 feasibility query로 다음을 추정한 뒤 [`STATISTICAL_ANALYSIS_PLAN.md`](STATISTICAL_ANALYSIS_PLAN.md)의 식과 simulation을 사용한다.

- unique DS patients와 cases/year
- 후보 event prevalence와 95% CI
- waveform/SQI evaluable fraction
- repeated cases per patient 및 site clustering
- candidate model parameter 수와 보수적 예상 fit
- 목표 sensitivity/calibration precision

필요 표본을 달성하지 못하면 model development 대신 characterization/feasibility 연구로 제한한다.

## 8. 연구 절차

1. IRB/DUA/보안 승인과 data minimization 확정.
2. source inventory 및 small deidentified pilot extract로 schema/clock/units 검증.
3. approved honest-broker가 patient/case key를 연구 key로 치환.
4. waveform/numeric/clinical event를 secure enclave로 전송.
5. versioned deterministic pipeline으로 SQI/features/RII 생성.
6. output에 blinded된 임상의 2인이 candidate event를 독립 검토하고 필요 시 제3자가 adjudicate.
7. patient-level split과 사전 고정 SAP 분석.
8. aggregate 결과와 uncertainty, missingness, negative result를 보고.

## 9. 수집 변수

최소필요 목록과 형식은 [`HOSPITAL_DATA_REQUEST_SPEC.md`](HOSPITAL_DATA_REQUEST_SPEC.md)를 따른다. 직접식별자, 불필요한 free text, facial image/audio는 수집하지 않는다. 유전 원자료는 DS confirmation에 필요하지 않으며 요구하지 않는다.

## 10. RII와 임상 격리

- RII는 검증되지 않은 연구 score이며 확률이 아니다.
- 임상 monitor/alarm/order/pump에 연결하지 않는다.
- 실시간 inference에는 LLM을 사용하지 않는다.
- shadow service 장애가 기존 monitor와 진료에 영향을 주지 않는 architecture를 시험한다.
- 우발적 노출 또는 연구 output에 따른 임상 action은 protocol deviation으로 기록·조사한다.

## 11. 잠재적 위험과 완화

| 위험 | 수준/설명 | 완화 |
| --- | --- | --- |
| 개인정보 재식별 | 희귀질환+상세 timeline 결합 | 최소수집, pseudonymization, date shifting/relative time, access control, cell suppression |
| 데이터 breach | waveform/clinical record 유출 | 승인 enclave, encryption, audit log, retention/deletion, incident response |
| 연구 output 오용 | RII를 임상 alarm처럼 해석 | output 비노출, persistent RUO label, training, access separation |
| 편향/낙인 | DS 위험 과장 또는 접근 제한 | neutral language, control/context, subgroup uncertainty, no eligibility decision use |
| 부당한 동의 영향 | 취약 대상자 | independent consent, accessible materials, assent/capacity process |
| prospective system interference | latency/부하/연결 오류 | read-only mirror, network isolation, failure-independence test, no control path |

prospective module의 위험 수준은 기관 IRB와 규제/안전 담당자가 최종 판단한다.

## 12. 직접 이익과 사회적 가치

참여자에게 직접 임상 이익을 기대하거나 약속하지 않는다. 가능한 사회적 가치는 DS 마취·진정 생리 데이터의 품질·공백·연구 가능성을 더 정확히 이해하는 것이다.

## 13. 개인정보·데이터 관리

- PI 책임 하 data management plan, data flow diagram, role-based access.
- 연구키와 re-identification key는 honest broker가 분리 보관.
- encryption in transit/at rest, MFA, immutable access/audit log.
- source별 IRB/DUA/retention/secondary-use 제한을 metadata로 강제.
- Git에는 코드·synthetic fixture·비식별 문서만 저장; raw patient data 금지.
- export는 aggregate 또는 승인된 deidentified data만; small-cell suppression 기준은 기관 검토 후 고정.
- 보존기간 종료/철회/incident 시 삭제 또는 접근폐기 절차와 증적 유지.

## 14. 안전 모니터링과 incident

관찰·silent 연구라도 privacy/security incident, unexpected clinical exposure, system interference, protocol deviation을 추적한다. serious/unanticipated problem 보고 기준과 기한은 기관 IRB 정책을 따른다. clinical adverse event는 기존 care pathway로 관리하며 연구팀은 치료를 지시하지 않는다. 독립 medical monitor/DSMB 필요성은 prospective 규모와 위험에 따라 IRB가 결정한다.

## 15. 통계 분석

[`STATISTICAL_ANALYSIS_PLAN.md`](STATISTICAL_ANALYSIS_PLAN.md)를 사전 등록하고 version freeze한다. patient-level split, temporal/external validation, test threshold 비조정, calibration과 alarm burden, missingness/SQI를 포함한다. 관찰연구 association을 인과효과로 표현하지 않는다.

## 16. 결과 공유

- aggregate 결과, protocol/SAP deviations, uncertainty와 null/negative results를 보고한다.
- 정량 주장에는 PMID/DOI 또는 연구 protocol/registry ID를 연결한다.
- 개인 participant risk score는 반환하지 않는다.
- 데이터/코드 공개는 IRB/DUA/license와 재식별 위험 검토 후 가능한 범위만 수행한다.
- 논문 저자권과 community/participant communication은 사전 정책을 마련한다.

## 17. 중단 기준

- IRB/DUA/보안 범위 위반
- DS status·timeline·label을 신뢰성 있게 확인할 수 없음
- 연구 시스템이 임상 workflow에 간섭
- patient-specific output의 무단 임상 사용
- 심각한 재식별/보안 위험 또는 incident
- 사전 정의 데이터 품질/정밀도/futility 기준 미달
- 규제 검토에서 추가 승인 전 진행 금지 판정

## 18. IRB/PI가 확정할 항목

- 정확한 대상 연령·procedure·study period
- consent/assent/waiver/opt-out 전략
- control cohort와 matching 변수
- endpoint와 threshold source
- sample-size assumptions와 primary estimand
- data retention, cross-border/cloud use, third-party processor
- incidental finding와 individual result non-return policy
- compensation/recruitment materials
- prospective shadow architecture와 medical-device determination
