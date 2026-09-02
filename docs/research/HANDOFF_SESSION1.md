# Session 1 Handoff — Research & Data

기준일: 2026-09-02<br>
브랜치: `agent/research-data`<br>
대상: Session 2 `agent/signal-engine`, Session 3 `agent/product-ui`, 병원 연구팀

## 1. 검증된 사실

- 소아 sevoflurane 유도 관찰연구에서 DS군의 서맥 또는 더 큰 심박수 감소가 보고됐다(PMID 40376277, 21109130, 20736433). 적용범위는 해당 연령·마취법·관찰창이다. `VERIFIED_CLINICAL_EVIDENCE`
- 2025 전향연구는 DS 소아 93명과 대조 102명에서 초기 300초를 관찰했고 서맥 54/93(58%) 대 22/102(22%)를 보고했다(PMID 40376277; DOI 10.4274/jpr.galenos.2024.87528). `VERIFIED_CLINICAL_EVIDENCE`
- DS resting HRV 체계적 문헌고찰/메타분석에서 RMSSD 차이가 보고됐지만, 마취 중 환자별 예측성을 입증하지 않는다(PMID 30005737; DOI 10.1016/j.autneu.2018.05.006). `VERIFIED_CLINICAL_EVIDENCE` + `LIMITED_EVIDENCE`
- 13개 공식 데이터셋을 30개 공통 필드로 등록했다. 공개자료는 generic pipeline/feature validation 용도이며 DS 임상성능 근거가 아니다. `VERIFIED_OFFICIAL_INFORMATION`
- VitalDB에서 DS label을 확인할 수 있다고 가정하지 않았다. INSPIRE 공식 설명의 diagnosis exclusion 때문에 DS 식별을 `NO`, MIMIC의 Q90와 waveform 연결은 `UNCERTAIN`으로 기록했다. `VERIFIED_OFFICIAL_INFORMATION`
- FDA 2026 CDS 지침상 연속 생체신호 패턴 분석은 비기기 CDS 제외의 첫 기준을 충족하기 어렵다. `VERIFIED_OFFICIAL_INFORMATION`

세부 근거와 식별자는 [Evidence Ledger](EVIDENCE_LEDGER.csv)와 [Evidence Summary](EVIDENCE_SUMMARY.md)를 기준으로 한다.

## 2. 아직 불확실한 사실

- 모든 마취제·연령·진정/수술 환경에서 위험이 같은지
- sympathetic failure가 개인별 사건의 인과적·충분한 예측기인지
- vagal excess, baroreflex impairment, resting/ultra-short HRV의 마취 중 예측 가치
- DS 병원 cohort의 실제 사건률, usable waveform 비율, 반복마취와 하위군 분포
- MIMIC Q90 환자의 실제 수와 matched waveform 존재
- 최종 사건정의, 임상적으로 의미 있는 lead time, 허용 false alerts/hour
- MFDS 제품 해당성·품목·등급·임상시험 절차와 FDA 제출경로

모두 `LIMITED_EVIDENCE`, `RESEARCH_HYPOTHESIS` 또는 `PRODUCT_ASSUMPTION`으로만 취급한다.

## 3. 제품에서 사용 금지할 주장

- “DS 환자의 마취 사고를 예방합니다.”
- “서맥을 정확히 예측합니다.”
- “마취제 용량을 최적화합니다.”
- “일반 병원도 안전하게 DS 마취를 할 수 있게 합니다.”
- “DS 환자는 모든 마취에서 항상 고위험입니다.”
- “atropine hypersensitivity가 입증됐습니다.”
- “특정 마취제를 특정 비율로 감량해야 합니다.”
- “공개 데이터로 DS 임상성능을 검증했습니다.”
- “RUO이므로 의료기기 규제를 받지 않습니다.”

분류: `UNSUPPORTED_OR_REJECTED` 또는 현재 intended-use 위반.

## 4. Session 2가 구현해도 되는 feature

Session 2 소유범위 안에서 아래 연구용 backend/engine 기능을 구현할 수 있다.

- 명시적 schema/version을 가진 읽기 전용 waveform/numeric ingestion
- patient/encounter binding, UTC timestamp, unit, provenance validation
- deterministic resampling/filtering 및 합성 golden-vector 회귀시험
- ECG R-peak detection, beat quality와 candidate HR/HRV feature 계산
- PPG quality/morphology와 PTT **연구 특징량** 계산
- age/reference threshold를 config로 분리한 candidate event-label 생성
- 각 채널 SQI, missingness, freshness, clock uncertainty, OOD gate
- patient-level split 및 patient ID overlap/leakage 자동검사
- version-locked preprocessing/model/threshold manifest와 checksum
- `no_score + reason_code`를 반환하는 fail-silent API contract
- 합성/공개 소형 fixture 기반 unit/integration/replay/fault-injection test
- 연구 결과 export에 입력·버전·품질·오류 provenance 포함

구현 기준은 [Labeling Protocol](LABELING_PROTOCOL.md), [SAP](STATISTICAL_ANALYSIS_PLAN.md), [Hospital Data Request](HOSPITAL_DATA_REQUEST_SPEC.md), [Safety Boundaries](../safety/CLINICAL_SAFETY_BOUNDARIES.md)다.

## 5. Session 2가 구현하면 안 되는 feature

- 임상 경보, 임상 확률 또는 “low/high risk” 진료용 endpoint
- 약물·용량·수액·기도·검사·치료 추천
- 펌프·마취기·인공호흡기·모니터 write/control path
- LLM/생성형 AI runtime dependency, fallback, 환자별 설명
- 품질 미달, stale, patient mismatch, unknown unit, unsupported input의 강제 점수
- 자동/온라인 재학습 또는 원격 임계값 변경
- test set 성능에 맞춘 threshold tuning
- 사례 단위 무작위분할로 동일 환자를 train/test에 중복
- post-index 처치·사건 변수를 prediction feature로 사용
- credential/DUA/IRB를 우회한 downloader 또는 raw patient data의 Git 저장

## 6. Session 3에서 반드시 표시할 disclaimer

연구자용 UI의 모든 환자별·집계 출력에 다음 의미가 지속적으로 보여야 한다.

> 연구용입니다. 임상적 유효성이 검증되지 않았습니다. 진단, 치료, 투약 또는 환자감시 목적으로 사용하지 마십시오. 출력은 임상 경보가 아니며 기존 모니터와 의료진 판단을 대체하지 않습니다.

추가 UI 요구:

- 데이터 시각과 freshness, source, model/pipeline version 표시
- 점수와 `unavailable/insufficient_signal` 상태를 시각·의미상 분리
- 품질·결측·지원범위·reason code 표시
- 확률, 치료행동, 안전/예방 효과를 암시하는 단어·색상·아이콘 금지
- shadow mode에서는 임상팀 계정·화면·notification route에 접근 불가
- 연구 export에도 동일 disclaimer와 provenance 포함

## 7. 병원 교수에게 검토받아야 할 질문

1. 대상 연령, 마취/진정 환경, baseline과 제외기준은 무엇인가?
2. 유도 시작·약물투여·기도확보·절개·회복의 기준 타임스탬프는 무엇인가?
3. 상대 HR 감소와 age-appropriate bradycardia의 임상적으로 의미 있는 정의는 무엇인가?
4. hypotension, desaturation, airway intervention, procedure interruption, PACU escalation을 어떻게 판정할 것인가?
5. vasopressor/anticholinergic 투여는 outcome, mediator, confounder 중 어떻게 취급할 것인가?
6. 판정자가 보아야 할 원자료와 blinded adjudication 절차는 무엇인가?
7. 임상적으로 유용한 최소 lead time과 허용 false alerts/hour는 얼마인가?
8. CHD, 갑상선질환, OSA, 연령, baseline HR, 마취법, 수술유형 하위군은 무엇인가?
9. 반복 마취를 포함할지, 환자내 상관과 prior anesthetic를 어떻게 처리할 것인가?
10. silent 연구의 중지·보고 기준과 우연히 발견된 원자료 이상 대응 SOP는 무엇인가?

## 8. 데이터 접근 선행조건

### 공개 OPEN 자료

- registry의 공식 source/version/license를 사용 직전 재확인
- `--sample`/`--limit`, host allowlist, byte cap과 checksum manifest 사용
- 다운로드 대상은 Git checkout 밖의 승인된 경로
- raw data·credential·DUA 문서를 Git에 저장하지 않음

### Credential-required 자료

- 개인 계정, 필수 교육(CITI 등), DUA/credential 승인 완료
- 기관·데이터셋별 허용 목적·보존·공유·파생물 조건 기록
- credential 우회, 토큰 공유, 원자료 재배포 금지

### 병원 자료

- IRB 및 필요한 임상시험/기관 승인
- 데이터 사용계약, 최소필요 필드, 가명화키 분리, 접근권한과 감사로그
- 저장 위치·암호화·보존·삭제·export·사고대응 계획
- source system/device/firmware, 단위, sampling, timezone/clock, 데이터 품질 문서
- 임상판정·SAP·split·중지규칙 사전확정
- shadow 결과의 치료팀 비노출을 E2E로 검증

## 9. 통합 시 확인할 계약

Session 2/3 통합 전에 다음 계약을 명시적 version으로 합의한다.

- input observation/waveform schema와 단위·시간 의미
- signal-quality와 `no_score` reason-code enum
- 연구 점수의 이름·범위·비확률 의미
- model/pipeline/threshold manifest와 호환성 규칙
- UI freshness·provenance·disclaimer 필드
- patient/encounter identity와 shadow-mode authorization
- audit event, export metadata와 삭제/보존 이벤트

## 10. 첫 다음 행동

1. 소아마취 전문의·생물통계가·데이터보호/임상공학 담당자 공동 프로토콜 검토
2. MFDS 사전상담으로 제품 해당성·등급·silent 임상연구 절차 확인
3. 병원 데이터 feasibility query로 DS 사례수·파형 coverage·사건률·장치 metadata 산출
4. Session 2는 합성/OPEN 소형 자료만으로 deterministic ingestion/SQI/reason-code contract 구현
5. Session 3는 치료팀과 분리된 연구 UI에서 disclaimer·freshness·무출력 상태부터 구현

전체 판정은 [Research Review Board](RESEARCH_REVIEW_BOARD.md)의 **CONDITIONAL PASS**다. 임상 사용 승인이 아니다.
