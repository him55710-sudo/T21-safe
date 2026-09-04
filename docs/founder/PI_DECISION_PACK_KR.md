# PI 의사결정 팩 — Evidence-First M0-A

**상태:** 회의용 초안 · 결정 전

**범위:** Path B / Research Use Only / Shadow / `clinical_validation=false`
**고정 원칙:** 이 문서는 임상 정의, RII/PROXY 로직, threshold, weight를 바꾸거나 승인하지 않는다.

## 1. 이번 회의의 목표

PI가 코드 값을 고르는 회의가 아니라, 다음 연구 프로토콜에 들어갈 질문과 선택지, 필요한 근거, 결정권자를 좁히는 회의다. 공개 non-DS PROXY 결과나 synthetic fixture PASS는 DS 임상 검증이 아니다.

## 2. PI 결정 요청표

| ID | PI가 결정/지정할 항목 | 회의 전 제시할 자료 | 기록할 결과 | 코드 영향 |
| --- | --- | --- | --- | --- |
| PI-01 | intended population과 setting의 연구 정의 | PICOTS, inclusion/exclusion 후보, 데이터 가용성 | 선택안, 제외안, 근거, 미해결 질문 | 없음 |
| PI-02 | primary/secondary endpoint와 ground-truth 절차 | Clinical Research Lock, labeling protocol, adjudication 옵션 | endpoint 문구, 판정자/불일치 처리, blindness | 없음 |
| PI-03 | 관찰 window와 baseline 연구 질문 | 문헌/데이터 gap, sensitivity 계획 | 비교할 옵션과 사전분석 순서 | M0 값 변경 금지 |
| PI-04 | signal/channel 및 SQI 실패 처리 | 외적 타당성 계획, acquisition 제약 | 필수/선택 signal, unusable 정의의 연구 과제 | M0 값 변경 금지 |
| PI-05 | subgroup/confounder/missingness 계획 | 수집 가능한 변수, bias 위험 | 사전지정 그룹, 금지 inference, 결측 처리 원칙 | 없음 |
| PI-06 | external cohort 및 validation design | site/device 분포, DUA/IRB 상태 | 독립성, split/holdout, 성공/중단 기준 초안 | 없음 |
| PI-07 | clinician comprehension의 critical items | HF protocol, display 옵션 | 사용자 역할, critical error, retest gate | display 연구만 |
| PI-08 | 임상/통계 자문 및 sign-off RACI | 현재 owner와 gap | PI, statistician, adjudicator, security/data owner | 없음 |

## 3. 회의에서 결정하지 않는 것

- RII 숫자, status boundary, feature weight 또는 모델 선택
- PROXY 결과를 DS-specific 성능으로 승격하는 것
- diagnosis, arrest/outcome prediction, dosing, anesthetic 변경, procedure clearance
- `clinical_validation=true`, FACT 승격 또는 patient-care deployment
- 근거 없이 waveform에서 DS, CHD, OSA, anesthesia history를 추론하는 것

해당 제안이 나오면 **Parking lot — Founder unfreeze 이후 별도 change control**로 이동한다.

## 4. 60분 진행안

| 시간 | 내용 | 산출물 |
| --- | --- | --- |
| 0–5분 | RUO/Shadow, freeze, PROXY 경계 확인 | 공통 전제 |
| 5–20분 | population/setting/endpoint | PI-01, PI-02 |
| 20–35분 | baseline/window/signal-quality 연구 질문 | PI-03, PI-04 |
| 35–45분 | subgroup, missingness, external design | PI-05, PI-06 |
| 45–55분 | HF critical comprehension | PI-07 |
| 55–60분 | RACI와 unresolved items | PI-08, action log |

## 5. 의사결정 기록 양식

각 항목마다 다음을 남긴다.

```text
Decision ID:
Status: DECIDED | NARROWED | DEFERRED | REJECTED
Selected option / wording:
Alternatives rejected and why:
Evidence reviewed (document/version):
Assumptions and evidence gaps:
Owner / due date:
PI name / review date:
Founder disposition:
Does this request an unfreeze? NO by default
```

회의 메모에 PHI, free-text patient history, credential을 넣지 않는다. 개인 환자 사례가 논의되면 저장 문서에는 비식별·집계된 연구 질문만 남긴다.

## 6. 회의 종료 gate

회의가 끝나도 자동 unfreeze는 없다. 다음 조건이 충족되어야 후속 단계 제안이 가능하다.

1. `CLINICAL_RESEARCH_LOCK_V0.md`에 PI 검토 결과와 미결 항목을 문서 PR로 반영한다.
2. endpoint, population, labeling/adjudication, 분석 책임자가 명시된다.
3. 외부 데이터 권한과 보안 stage가 확인된다.
4. 통계분석계획과 HF protocol의 수치 기준은 unblinding 전에 승인된다.
5. Founder가 허용 범위와 새 기준 SHA를 별도로 서면 승인한다.

미결 항목은 억지로 채우지 않고 `PI_REQUIRED`로 유지한다.

## 7. 읽을 문서

- [Founder Refocus 결정](T21_REFOCUS_DECISION_KR.md)
- [Clinical Research Lock](../research/CLINICAL_RESEARCH_LOCK_V0.md)
- [Signal External Validity Plan](../research/SIGNAL_EXTERNAL_VALIDITY_PLAN.md)
- [Clinician Comprehension Protocol](../product/CLINICIAN_COMPREHENSION_PROTOCOL.md)
- [RII Display HF Options](../model/RII_DISPLAY_HF_OPTIONS.md)
