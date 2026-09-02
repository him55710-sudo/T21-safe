# FDA Clinical Decision Support 분석

문서 상태: 비법률·비규제 자문 초안<br>
기준일: 2026-09-02<br>
적용 문서: FDA *Clinical Decision Support Software*, Final Guidance, 2026-01-29

## 결론 요약

장래 T21 Safe가 ECG, PPG, 혈압, SpO2 등 연속 또는 준연속 생체신호의 패턴을 분석해 환자별 출력을 임상의에게 제공한다면, FD&C Act 520(o)(1)(E)의 비기기 CDS 제외를 충족하기 어렵다. FDA 최종 지침상 네 기준을 **모두** 충족해야 하며, 첫 번째 기준은 의료영상, IVD 신호, 또는 신호획득시스템의 패턴·신호를 획득·처리·분석하지 않을 것을 요구한다. T21 Safe의 핵심 기능은 이 조건과 직접 충돌한다.

따라서 독립적 검토를 돕는 설명을 충분히 제공하더라도 그것만으로 비기기 CDS가 되지는 않는다. 장래 임상 기능은 device software function일 가능성을 전제로 FDA와 사전논의해야 한다. 정확한 분류, product code, 510(k)·De Novo 등 제출경로는 본 분석으로 확정할 수 없다.

분류: `VERIFIED_OFFICIAL_INFORMATION`(지침 내용), `PRODUCT_ASSUMPTION`(T21 Safe에 대한 잠정 적용)

## 현재 연구 프로토타입과 장래 임상 기능

| 항목 | 현재 RUO / silent shadow | 장래 임상 가설 |
|---|---|---|
| 출력 수신자 | 승인된 연구자 | 적격 의료진 가능성 |
| 치료 전 노출 | 없음 | 실시간/준실시간 가능성 |
| 주장 | 기술·임상 성능 연구 | 불안정 패턴 보조표시 가능성 |
| 환자별 판단 영향 | 금지 | 미확정 |
| 신호 분석 | 있음 | 있음 |
| 규제 결론 | RUO 문구만으로 결정 불가 | device 가능성을 전제로 협의 |

제품의 실제 기능, 배포, 표시·홍보와 사용 맥락이 규제 판단에 중요하다. `For Research Use Only` 표시는 임상적 의도와 사용을 자동으로 면제하지 않는다.

분류: `VERIFIED_OFFICIAL_INFORMATION`

## 520(o)(1)(E) 네 기준별 검토

### 기준 1 — 신호 또는 패턴을 획득·처리·분석하지 않는가?

FDA는 연속·준연속·스트리밍 생리측정과 ECG 파형, QRS complex, baseline variation 분석을 신호/패턴 분석의 예로 제시한다. T21 Safe는 ECG/심박, PPG/SpO2, 혈압 등의 시계열을 전처리하고 특징을 계산하므로 장래 임상 기능은 이 기준을 충족하지 못할 가능성이 높다.

판정: **불충족 가능성 높음**<br>
분류: `VERIFIED_OFFICIAL_INFORMATION` + `PRODUCT_ASSUMPTION`

### 기준 2 — 의료정보를 표시·분석하는가?

입력에는 환자 생체신호와 제한된 임상 공변량이 포함된다. 그러나 기준 1의 신호분석 문제를 기준 2의 의료정보 분석으로 대체 해석할 수 없다.

판정: 기능은 의료정보를 분석하지만, 전체 제외요건을 구제하지 않음<br>
분류: `PRODUCT_ASSUMPTION`

### 기준 3 — 의료전문가에게 권고를 제공하는가?

현재 RUO 버전은 의료진에게 환자별 권고를 제공하지 않는다. 장래 UI가 위험도, 우선순위 또는 조치 필요성을 표시하면 의료전문가 대상 recommendation으로 평가될 수 있다. 단순 정보인지 권고인지 정확한 문구·표현·워크플로를 FDA와 확인해야 한다.

판정: 현재 해당 없음; 장래 기능 미정<br>
분류: `PRODUCT_ASSUMPTION`

### 기준 4 — 의료전문가가 근거를 독립적으로 검토할 수 있는가?

FDA 지침은 적어도 intended use, 사용자·대상, 요구 입력과 데이터 품질, 알고리즘·개발자료·검증 결과, 환자별 알려진 정보와 알려지지 않은 정보를 제공해 사용자가 권고 근거를 독립 검토할 수 있어야 한다고 설명한다. T21 Safe는 이를 설계 목표로 삼아야 하지만 아직 사용자 검증과 임상 검증이 없다.

판정: 설계 가능하나 현재 입증되지 않음<br>
분류: `VERIFIED_OFFICIAL_INFORMATION`(요건), `LIMITED_EVIDENCE`(제품 입증)

## 시간 민감성과 자동화 편향

2026 최종 지침의 개정이력에는 13–14쪽에서 time-critical decision-making 언급을 정렬 목적으로 삭제한 경미한 수정이 기록되어 있다. 따라서 “시간 민감하다”는 표현 하나만으로 결론을 내리지 않는다. 다만 사용자가 정보를 독립 검토할 실질적 기회, automation bias, 출력의 명확성은 여전히 중요한 설계·위험관리 쟁점이다. T21 Safe는 기준 1의 생체신호 분석만으로도 비기기 CDS 제외가 어려우므로 시간 민감성 논쟁에 의존할 필요가 없다.

분류: `VERIFIED_OFFICIAL_INFORMATION`

## MDDS 검토

FDA의 MDDS 정책은 의료기기 데이터의 전송·저장·형식변환·표시와 같은 기능을 다룬다. T21 Safe는 신호를 해석해 새로운 특징량과 환자별 연구 점수를 생성하므로 단순 MDDS 기능으로만 보기 어렵다. 연결 게이트웨이의 순수 전송 기능과 분석 기능은 아키텍처·표시·위험관리에서 분리해야 한다.

분류: `VERIFIED_OFFICIAL_INFORMATION`(정책 범위), `PRODUCT_ASSUMPTION`(제품 적용)

## 권고되는 FDA 상호작용

1. 현재와 장래 intended use, 데이터 흐름, 신호 처리, UI mock-up, 임상 워크플로를 하나의 기능 설명서로 고정한다.
2. 미국 임상·배포 전 규제전문가와 device status, product code, predicate 가능성 및 제출경로를 검토한다.
3. Q-Submission/Pre-Sub에서 임상 사건정의, 독립검증, 소아·다운증후군 자료 충분성, 경보 성능, human factors와 사이버보안을 질문한다.
4. 필요한 경우 513(g) 절차의 적합성을 규제전문가와 검토한다.
5. 모델을 locked version으로 시작하고, 변경이 계획되면 PCCP 적용 가능성과 제출 범위를 별도 검토한다.
6. 임상 사용·상업적 배포·임상의 노출 전에 FDA 결론을 문서화한다.

분류: `PRODUCT_ASSUMPTION`

## 독립검토를 위한 최소 투명성 패키지

- 정확한 사용 목적, 대상 환자·환경·사용자와 제외조건
- 입력 채널, 단위, 샘플링, 시간동기, 품질·결측 기준
- 전처리·특징량·모델·임계값의 버전과 변경이력
- 개발·내부시험·외부시험 자료의 출처, 대표성, 분할 및 누출 통제
- 환자 단위 판별·보정·경보부담·리드타임과 95% 신뢰구간
- 하위군·결측·센서·기관별 성능과 알려진 실패모드
- 현재 환자 입력 중 사용된 정보, 미사용·불확실 정보와 신호 지연
- 원신호·기존 모니터 확인 경로와 `insufficient_signal` 상태

이는 비기기 CDS 제외를 보장하는 체크리스트가 아니라, 안전한 설계와 FDA 논의를 위한 최소자료다.

## 공식 근거

- FDA, [Clinical Decision Support Software — Final Guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software), 2026-01-29; [PDF](https://www.fda.gov/media/109618/download).
- FDA, [Clinical Decision Support Software FAQs](https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software-frequently-asked-questions-faqs).
- FDA, [Digital Health Policy Navigator — Step 6](https://www.fda.gov/medical-devices/digital-health-center-excellence/step-6-software-function-intended-provide-clinical-decision-support).
- FDA, [Policy for Device Software Functions and Mobile Medical Applications](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/policy-device-software-functions-and-mobile-medical-applications), 2022-09.
- FDA, [Medical Device Data Systems policy](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/medical-device-data-systems-medical-image-storage-devices-and-medical-image-communications-devices).
- FDA, [Predetermined Change Control Plan for AI-Enabled Device Software Functions](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence), 2025-08.

공식 지침 요약은 `VERIFIED_OFFICIAL_INFORMATION`이다. 최종 제품 지위와 제출경로는 `PRODUCT_ASSUMPTION`이며 FDA 결정 또는 자격 있는 규제 자문이 필요하다.
