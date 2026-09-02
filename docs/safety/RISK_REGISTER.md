# Risk Register

문서 상태: 활성 초안<br>
기준일: 2026-09-02<br>
범위: 현재 RUO/shadow 연구 및 장래 임상 가설

## 상태 규칙

- `OPEN`: 통제 또는 검증 증거가 미완료
- `CONTROL_DESIGNED`: 통제가 요구사항으로 정의됐으나 검증 미완료
- `VERIFIED_FOR_RUO`: 현재 연구 경계에서 통제가 시험·검토됨; 장래 임상 수용을 뜻하지 않음
- `ACCEPTED`: 지정된 사용 목적에서 잔여위험 승인 완료. **현재 사용 금지**
- `BLOCKED`: 필요한 데이터·결정·외부 승인이 없어 진행 불가

현재 모든 위험은 `OPEN` 또는 `CONTROL_DESIGNED`이다. 이 등록부 자체는 ISO 14971 적합성, 위험통제 유효성 또는 잔여위험 수용의 증거가 아니다.

## 등록부

| ID | 위험 | 단계 | S/P(잠정) | 통제/결정 | 검증 증거 요구 | 소유자 | 상태 |
|---|---|---|---|---|---|---|---|
| R-001 | 잘못된 환자 연결 | RUO+future | 5/2 | 다중 ID·encounter 일치, mismatch fail-silent | bed transfer·ID 재사용 replay | 통합/임상공학 | OPEN |
| R-002 | 데이터 지연·stale 값 | RUO+future | 5/3 | source/event/receive time, TTL, 지연 표시 | latency·out-of-order fault injection | 통합 | CONTROL_DESIGNED |
| R-003 | 단위·스케일 오류 | RUO+future | 5/2 | allowlist 변환, 원단위, 범위·차원 검사 | 단위 permutation·boundary test | 데이터 | CONTROL_DESIGNED |
| R-004 | 장치 clock 불일치 | RUO+future | 4/3 | UTC·offset·동기품질, 허용범위 밖 제외 | known-offset replay | 통합 | OPEN |
| R-005 | artifact가 유효신호로 처리 | RUO+future | 4/4 | 채널별 SQI, plausibility, 교차채널, 무출력 | 합성+실제 artifact test | 신호/임상 | OPEN |
| R-006 | 결측·채널전환 은폐 | RUO+future | 4/4 | 필수채널, 제한 보간, provenance | dropout·channel swap test | 신호 | OPEN |
| R-007 | resampling/filter 오류 | RUO+future | 4/3 | anti-alias, 고정 파라미터, golden vectors | 주파수응답·경계·회귀시험 | 신호 | OPEN |
| R-008 | train/test 환자 누출 | 연구 | 5/3 | 환자단위 분할, site/time lockbox | ID overlap·feature cutoff CI test | 통계/데이터 | CONTROL_DESIGNED |
| R-009 | 라벨 편향·오류 | 연구 | 4/3 | blinded 2인 판정, 불확실 라벨 보존 | 일치도·불일치 합의·감사표본 | 임상판정위 | OPEN |
| R-010 | DS 고해상도 자료 부족 | 연구 | 5/4 | 공개자료는 pipeline용; IRB 병원자료 확보 | 데이터 수·사건·coverage 보고 | PI/데이터 | BLOCKED |
| R-011 | 단일기관/하위군 성능저하 | 연구+future | 5/3 | 다기관·시간외·하위군 검증, 제한 표시 | site/age/CHD/anesthesia CI | 임상/통계 | BLOCKED |
| R-012 | test set로 임계값 튜닝 | 연구 | 5/3 | development-only 고정, 독립 lockbox | 결정로그·hash·재현성 감사 | 통계/품질 | CONTROL_DESIGNED |
| R-013 | 확률로 오해되는 미보정 점수 | future | 4/3 | probability claim 금지, 의미·불확실성 표시 | calibration+HF 검증 | 통계/HF | OPEN |
| R-014 | 지원 밖 입력 강제 산출 | RUO+future | 5/3 | 지원범위 allowlist, OOD/quality gate | 미지원 vendor·범위 negative test | ML/신호 | OPEN |
| R-015 | 과도한 경보·alarm fatigue | future | 4/4 | RUO 경보 없음; episode/refractory 설계 | false alerts/hour+silent+HF | 임상/HF | OPEN |
| R-016 | 미탐으로 거짓 안심 | future | 5/3 | 대체금지, 원신호, coverage·민감도 공개 | 임상성능+critical-task HF | 임상/HF | OPEN |
| R-017 | automation bias | future | 5/3 | 행동지시 금지, 근거·한계·품질 표시 | 총괄 사용적합성 검증 | HF/안전 | OPEN |
| R-018 | shadow 결과가 치료팀에 노출 | RUO | 5/2 | 연구계정/망/UI 분리, 알림 비활성 | 권한·route·notification E2E test | 연구운영/보안 | OPEN |
| R-019 | LLM이 inference 경로에 포함 | RUO+future | 5/2 | dependency denylist, SBOM, egress 차단 | 빌드 graph·정적·네트워크 시험 | 아키텍처/품질 | CONTROL_DESIGNED |
| R-020 | 모델·전처리·임계값 버전 혼선 | RUO+future | 5/3 | signed manifest, compatibility matrix, atomic deploy | 불일치 기동거부·rollback test | MLOps/품질 | OPEN |
| R-021 | 무승인 재학습/config 변경 | RUO+future | 5/2 | online learning 금지, immutable config, 승인 workflow | 변경차단·감사로그 시험 | MLOps/품질 | CONTROL_DESIGNED |
| R-022 | 사이버 변조·서비스거부 | RUO+future | 5/2 | 최소권한, 암호화, 서명, segmentation, SBOM | threat-model 보안시험·복구훈련 | 보안 | OPEN |
| R-023 | 개인정보 노출·재식별 | RUO | 4/3 | 최소수집, 가명화, export 제한, 보존·삭제 | 접근·DLP·재식별위험 검토 | DPO/보안 | OPEN |
| R-024 | 오류·무출력 로그 불완전 | RUO+future | 3/3 | reason code, append-only audit, escalation | 실패모드별 log completeness | 운영/품질 | OPEN |
| R-025 | 연구 주장 경계 확장 | RUO | 5/2 | claims review, 배포·자료 승인 게이트 | 릴리스/웹/발표자료 감사 | 규제/PI | CONTROL_DESIGNED |
| R-026 | 공개자료 라이선스/DUA 위반 | 연구 | 3/2 | registry access class, manual gate, manifest | 다운로드·사용·배포 감사 | 데이터거버넌스 | CONTROL_DESIGNED |
| R-027 | 치료·약물 데이터가 라벨/feature에 누출 | 연구 | 5/3 | prediction cutoff, post-index variable denylist | temporal provenance 검사 | 통계/임상 | OPEN |
| R-028 | 점수 미산출이 정상 저위험으로 표시 | future | 5/3 | 상태와 점수 분리, 명시적 `unavailable` | UI/API contract·HF 시험 | 제품/HF | OPEN |

## 릴리스 차단 기준

다음 중 하나라도 충족하면 임상의 노출 또는 임상 목적 릴리스를 차단한다.

- S5 위험의 통제·검증·잔여위험 승인이 미완료
- patient identity, timestamp, unit, freshness 또는 quality gate 실패 시 점수가 나옴
- 모델·전처리·임계값·입력계약 hash를 하나라도 재현하지 못함
- 독립 외부/시간외 검증이 없거나 목표 성능·경보부담을 사전 충족하지 못함
- 하위군 결과가 미보고되거나 필수 DS 자료가 없음
- LLM/생성형 AI, 자동 재학습 또는 의료기기 write/control path가 inference graph에 존재
- shadow 출력이 치료팀에게 노출될 가능성이 검증으로 배제되지 않음
- 규제·IRB·정보보호·임상안전 승인 중 필요한 하나가 없음

## 위험검토 회의 입력

- 새 이상사례, near miss, false alert, missed event, 무출력과 data-quality trend
- 모델·데이터·센서·vendor·interface·infrastructure 변경
- 사용자 피드백, use error, 업무우회(workaround)
- 취약점, SBOM 변경, 보안사건과 패치
- 새 임상근거·표준·규제지침
- 하위군·기관·시간에 따른 성능 또는 보정 drift

각 검토는 날짜, 참석 역할, 입력자료 버전, 위험 항목 변경, 결정·근거, 소유자와 기한을 기록한다.

## 연결 문서

- [Preliminary Hazard Analysis](HAZARD_ANALYSIS.md)
- [Clinical Safety Boundaries](CLINICAL_SAFETY_BOUNDARIES.md)
- [Standards Applicability Map](../regulatory/STANDARDS_MAP.md)
- [Validation Roadmap](../research/VALIDATION_ROADMAP.md)

모든 위험 추정과 통제 설계는 `PRODUCT_ASSUMPTION`이다. 검증이 끝나기 전 통제 효과는 `LIMITED_EVIDENCE`이며, 위험 수용권자는 연구·개발 담당자가 아니라 지정된 임상안전/품질 책임자다.
