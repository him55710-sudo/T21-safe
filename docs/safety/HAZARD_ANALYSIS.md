# Preliminary Hazard Analysis

문서 상태: 초기 위험분석, ISO 14971 적합성 또는 잔여위험 수용 선언 아님<br>
기준일: 2026-09-02<br>
범위: RUO/shadow 연구 시스템과 장래 사용자 노출 가설

## 1. 안전 목표

현재 연구 단계의 최우선 통제는 **연구 출력이 환자 치료에 도달하지 않게 하는 것**이다. 장래 임상 기능을 검토할 때도 T21 Safe는 기존 모니터·임상판단을 대체하지 않고, 치료·투약·기기제어를 직접 수행하지 않으며, 신뢰할 수 없는 입력에서는 fail-silent 해야 한다.

분류: `PRODUCT_ASSUMPTION`

## 2. 분석 방법

위험 시나리오는 다음 사슬로 기록한다.

```text
hazardous source → foreseeable sequence of events → hazardous situation → harm
                    ↘ preventive/detective control → verification evidence
```

내부 우선순위 척도는 정식 위험수용 결정이 아니라 작업 순서를 정하기 위한 것이다.

### 심각도

| 등급 | 내부 정의 |
|---:|---|
| S5 | 사망 또는 생명위협 손상 가능 |
| S4 | 중대한 영구/장기 손상 또는 긴급 중재 가능 |
| S3 | 일시적 손상 또는 추가 처치·관찰 가능 |
| S2 | 경미한 불편, 지연 또는 비임상적 데이터 손실 |
| S1 | 임상 위해 없음, 연구/운영 영향만 |

### 발생가능성

| 등급 | 내부 정의 |
|---:|---|
| P5 | 빈번할 것으로 예상 |
| P4 | 개연성 있음 |
| P3 | 간헐적 |
| P2 | 드묾 |
| P1 | 극히 드묾/합리적으로 예상하기 어려움 |

정량 빈도 경계는 실제 사용시간·사건자료가 없어 정의하지 않았다. 심각도와 발생가능성은 임상안전 책임자 승인 전 잠정값이다. S4–S5 시나리오는 빈도가 낮아도 독립 검토와 통제 검증이 필요하다.

## 3. 시스템 경계와 안전상태

### 포함

- 병원 모니터/기록시스템에서 읽기 전용으로 들어오는 데이터
- 수집, 환자연결, 시간동기, 단위정규화, 품질평가, 전처리
- 버전 고정 통계·ML inference, 로그와 연구 결과 저장
- 연구자용 분석·평가 UI와 내보내기

### 제외되지만 인터페이스 위험은 관리

- 원 환자감시장치와 그 경보
- 마취기, 펌프, 인공호흡기와 치료행위
- 병원 EHR/데이터웨어하우스 자체 운영
- 문헌 정리용 LLM

### 안전상태

- RUO/shadow: 임상의에게 출력 비공개, 분석 중단, 연구자에게 오류 표시, 원자료 보존
- 장래 사용자 노출: 점수/권고 미표시(`insufficient_signal`/`unavailable`), 데이터 시각·지연 명시, 기존 모니터 사용 안내, 자동 제어 없음

## 4. 주요 위해 시나리오

| ID | 위험원/고장 | 예견 가능한 사건 사슬 | 위해 상황/가능한 위해 | 초기 우선순위 | 필수 통제 | 검증 게이트 |
|---|---|---|---|---|---|---|
| H-01 | 잘못된 환자 연결 | bed/device ID 재사용 → 다른 환자 신호 결합 → 잘못된 출력 | 부적절한 신뢰·지연·처치 가능 | S5/P2 | 다중 식별자 일치, encounter 시간검사, 불일치 fail-silent, 감사로그 | mismatch·bed-transfer 재생시험 |
| H-02 | stale/지연 데이터 | 네트워크 정체 → 과거값을 현재값으로 표시 | 변화 누락 또는 잘못된 안심 | S5/P3 | source/event/receive 시간, freshness TTL, 지연 표시, TTL 초과 무출력 | 지연·순서뒤바뀜 fault injection |
| H-03 | 단위/스케일 오류 | mmHg/kPa·%/fraction 혼동 → 비현실 값 통과 | 오출력·사건 누락 | S5/P2 | 원 단위 보존, 명시적 allowlist 변환, 생리범위·차원 검사 | 단위 permutation/경계시험 |
| H-04 | clock 불일치 | 장치별 시계 차이 → 약물·신호·사건 오정렬 | 잘못된 학습·리드타임·출력 | S4/P3 | UTC+원 timezone, clock offset, 동기 품질, 허용오차 초과 제외 | 알려진 offset 재생시험 |
| H-05 | 파형 artifact | motion/전극 이탈/관류저하 → 특징 왜곡 | 오경보·미탐·과신 | S4/P4 | 채널별 SQI, plausibility, 교차채널 확인, 품질 미달 무출력 | 합성 artifact·실제 불량구간 시험 |
| H-06 | 결측/채널 전환 | 센서 제거·vendor channel swap → 묵시적 대체/보간 | 거짓 안정성·오출력 | S4/P4 | 필수채널 명세, 제한 보간, provenance, 장시간 결측 무출력 | dropout/channel-swap 시험 |
| H-07 | 잘못된 resampling | aliasing·필터 경계 → 특징량 왜곡 | 연구 결론·출력 오류 | S4/P3 | 샘플링 메타데이터 검사, anti-alias, 고정 파라미터, golden signal | 주파수 응답·golden vector 시험 |
| H-08 | 데이터/라벨 누출 | 동일 환자 반복 사례가 train/test에 분산 | 과대평가된 성능으로 임상 전환 | S5/P3 | 환자단위 분할, site/time lockbox, feature cutoff, 독립감사 | split-ID·time leakage 자동검사 |
| H-09 | 참조라벨 오류 | 치료기록을 사건의 완전한 대리로 사용 → incorporation bias | 잘못된 모델/성능 주장 | S4/P3 | 사전정의 라벨, blinded adjudication, 불일치·불확실 라벨 보존 | 이중판정·κ/합의율 보고 |
| H-10 | 대표성 부족 | 단일기관/소수 DS 사례 → 하위군에서 성능저하 | 특정 환자군 미탐·오경보 | S5/P3 | 다기관·시간외 검증, 연령/CHD/마취법 하위군, 제한 표시 | 사전정의 하위군 CI·OOD 평가 |
| H-11 | 잘못된 임계값 최적화 | test set 반복 튜닝 → 낙관적 경보 성능 | 임상 경보부담·미탐 | S5/P3 | threshold development-only 고정, 독립시험 1회, 변경시 재검증 | 해시·결정로그·lockbox 감사 |
| H-12 | 보정 실패 | 점수를 확률처럼 해석하나 calibration 불량 | 위험 과대/과소평가 | S4/P3 | 현재 probability claim 금지, calibration plot/slope/intercept, UI 의미검증 | 외부·하위군 보정평가 |
| H-13 | OOD 입력 | 새 vendor/연령/환경에서 강제 점수 | 알려지지 않은 성능으로 과신 | S5/P3 | 지원범위 allowlist, OOD/품질 gate, 무출력, 배포제한 | 미지원 vendor/범위 negative test |
| H-14 | 과도한 경보 | 낮은 임계값·중복 알림 → alarm fatigue | 실제 문제 무시·업무방해 | S4/P4 | 현재 경보 없음, 향후 refractory/episode logic, false alerts/hour 한도 | 시뮬레이션·사용적합성·silent 성능 |
| H-15 | 미탐/거짓 안심 | 점수 낮음 → 기존 모니터 확인 감소 | 대응 지연 | S5/P3 | 대체 금지 표시, 원신호 병기, sensitivity/coverage, 교육·HF 검증 | 위험시나리오 총괄 사용성 시험 |
| H-16 | automation bias | 설명 없는 숫자·색상 → 과신 | 부적절한 우선순위·처치 가능 | S5/P3 | 행동지시 금지, 근거/제한/품질 표시, 독립검토 설계 | 임상의 critical-task 시험 |
| H-17 | shadow 출력 노출 | 연구 UI/알림이 임상팀에 우연히 공개 | 미검증 출력이 치료에 영향 | S5/P2 | 역할분리, 임상망 미표시, 알림 비활성, 접근로그, SOP | 권한·notification·workflow 검증 |
| H-18 | LLM 경로 유입 | 생성 모델이 특징·점수·임계값 결정 | 비결정적·검증불가 출력 | S5/P2 | inference dependency denylist, SBOM/정적검사, 아키텍처 게이트 | 빌드·의존성·네트워크 차단시험 |
| H-19 | 버전 혼선 | 모델/전처리/임계값 불일치 | 검증되지 않은 조합 배포 | S5/P3 | signed manifest, 호환성 matrix, 원자적 배포, hash 검증 | 잘못된 manifest 기동거부시험 |
| H-20 | 조용한 온라인 변경 | 자동 재학습/원격 config 변경 | 성능 변화 미검증 | S5/P2 | 온라인학습 금지, immutable config, 승인된 변경관리 | 변경시도 차단·감사로그 시험 |
| H-21 | 사이버 침해 | 데이터/모델/시간값 변조 또는 서비스거부 | 오출력·무출력·정보유출 | S5/P2 | 최소권한, 암호화, 서명, segmentation, SBOM, 취약점 대응 | threat-model 기반 보안시험 |
| H-22 | 개인정보 노출 | export/log에 직접식별자 포함 | 사생활·법적·사회적 손상 | S4/P3 | 최소수집, 가명화, export denylist, 보존·삭제, 접근감사 | DLP/권한/재식별 위험 검토 |
| H-23 | 로그/오류 은폐 | 무출력 원인이 기록되지 않음 | 결함 반복·안전감시 실패 | S3/P3 | 구조화 reason code, immutable audit, 모니터링·escalation | 각 실패모드 로그 완전성 시험 |
| H-24 | 경계 확장 | 연구점수를 임상 확률·치료추천으로 마케팅 | 검증·허가 없는 임상 사용 | S5/P2 | claims review, 배포게이트, 표시 통제, 규제 승인 | 릴리스 체크리스트·자료 감사 |

모든 우선순위와 통제는 `PRODUCT_ASSUMPTION`이다. 임상적 위해의 가능성은 보수적 시나리오 분석이며 제품이 실제 위해를 발생시켰다는 주장도, 통제로 위험이 수용되었다는 주장도 아니다.

## 5. 독립 안전 아키텍처 요구

1. **Data gate:** 환자연결, 시간, 단위, freshness, 채널과 품질을 모델보다 먼저 판정한다.
2. **Deterministic inference:** 고정된 입력계약과 artifact hash가 일치할 때만 실행한다.
3. **Output gate:** 지원범위·품질·결측·OOD 실패 시 점수 대신 명시적 무출력을 반환한다.
4. **Audit:** 원 데이터 참조, 입력/출력, 버전, 오류, 사용자 접근을 append-only 기록한다.
5. **Clinical separation:** 연구 서비스 계정·UI·notification channel을 임상 운영에서 분리한다.
6. **No control path:** 출력에서 펌프·마취기·모니터 제어 인터페이스로 향하는 쓰기 경로를 두지 않는다.
7. **Human verification:** 장래 기능에서도 원신호·기존 경보·환자상태를 확인할 수 있게 한다.

## 6. 검증 전 금지되는 결론

- 위험이 ALARP 또는 수용 가능하다는 결론
- 경보가 안전하거나 임상적으로 유용하다는 결론
- 공개 데이터 성능을 다운증후군 마취 성능으로 일반화
- AUROC 하나로 안전성 또는 유용성을 입증했다는 주장
- 문서 작성만으로 IEC/ISO 적합성을 달성했다는 주장

## 7. 위험관리 산출물 연결

- 위험 항목·소유자·상태: [Risk Register](RISK_REGISTER.md)
- 절대 경계와 단계별 금지사항: [Clinical Safety Boundaries](CLINICAL_SAFETY_BOUNDARIES.md)
- 사용 목적: [Intended Use Draft](../regulatory/INTENDED_USE_DRAFT.md)
- 성능·통계: [Statistical Analysis Plan](../research/STATISTICAL_ANALYSIS_PLAN.md)
- 검증 단계: [Validation Roadmap](../research/VALIDATION_ROADMAP.md)

## 공식 방법론 근거

- ISO, [ISO 14971:2019 — Medical devices — Application of risk management to medical devices](https://www.iso.org/standard/72704.html).
- IEC, [IEC 62366-1:2015+A1:2020 — Usability engineering](https://webstore.iec.ch/en/publication/21863).
- IEC, [IEC 81001-5-1:2021 — Security activities in the product life cycle](https://webstore.iec.ch/en/publication/63293).

표준의 범위·판본은 `VERIFIED_OFFICIAL_INFORMATION`이다. 본 문서는 표준 원문을 대체하지 않는다.
