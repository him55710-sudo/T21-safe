# Clinical Safety Boundaries

문서 상태: 강제 경계 초안<br>
기준일: 2026-09-02<br>
적용 대상: T21 Safe 연구·개발·검토·데모·배포에 참여하는 모든 사람

## 한 줄 원칙

**T21 Safe는 현재 연구용 silent shadow 시스템이며, 환자 치료에 사용하지 않는다. LLM은 환자별 위험 계산 경로에 들어가지 않는다.**

## 절대 금지

현재 단계에서는 다음을 구현·활성화·홍보하지 않는다.

1. 환자별 출력의 임상의·환자·보호자 실시간 노출
2. 임상 경보, 진단, 예후, 임상적 확률 또는 “조기경고” 성능 주장
3. 약물·수액·기도관리·검사·치료의 선택, 용량 또는 시점 추천
4. 펌프·마취기·인공호흡기·모니터의 write/control path 또는 자동 폐루프
5. 기존 모니터 경보, 원 생체신호 또는 의료진 판단의 대체
6. LLM·생성형 AI의 전처리, 특징량, 점수, 임계값, 환자별 설명 생성 참여
7. 검증되지 않은 모델/임계값/전처리의 배포, 온라인 재학습, 암묵적 업데이트
8. 공개자료만으로 다운증후군 마취 임상성능이 입증됐다는 주장
9. `insufficient_signal`, stale, patient mismatch 또는 unsupported input에서 강제 점수 산출
10. IRB·데이터 사용계약·접근등급을 우회한 데이터 획득·재배포

이 경계는 `PRODUCT_ASSUMPTION`이 아니라 현재 프로젝트의 승인 조건이다.

## 허용되는 활동

- 공개·허가된 자료와 공식 문헌의 연구 정리 및 provenance 기록
- 라이선스·접근조건을 준수한 일반 생체신호 pipeline 기술시험
- IRB/DUA 범위 안의 후향 분석
- 치료팀에게 출력이 보이지 않는 전향 silent-mode 검증
- 합성 데이터·재생 데이터 기반 품질, 인터페이스, 실패모드 시험
- 버전 고정 deterministic pipeline 및 검증 가능한 통계·ML 모델 연구
- LLM을 이용한 문헌 정리, 문서 초안, 코드리뷰. 단, 사람이 출처·결론·변경을 검토해야 함

## 단계별 허용 경계

| 단계 | 출력 가시성 | 환자 치료 영향 | 허용 출력 | 진입 게이트 |
|---|---|---|---|---|
| 0. 합성/공개자료 | 연구자 | 없음 | 품질·특징량·기술 metric | 라이선스·manifest·재현성 |
| 1. 후향 병원자료 | 승인 연구자 | 없음 | 연구 점수·성능 리포트 | IRB/DUA·가명화·SAP |
| 2. 전향 silent | 분리된 연구팀; 치료팀 비공개 | 없음 | 잠긴 모델의 shadow 결과 | 기관 승인·E2E 안전·모니터링 |
| 3. 형성 사용성 연구 | 합성/재생 시나리오의 대표 사용자 | 실제 환자 치료 없음 | prototype UI | 위험분석·시나리오 승인 |
| 4. 임상 노출 | 현재 금지 | 잠재적 | 미정 | 규제·임상·품질·안전 승인과 별도 프로토콜 |
| 5. 치료/기기 제어 | 범위 밖 | 직접 | 없음 | 프로젝트 재정의 없이는 금지 |

## Shadow-mode 운영 요구

- 연구 서비스 계정, 저장소, UI와 notification route를 임상 운영에서 분리한다.
- 임상 화면, pager, 문자, 이메일, EHR inbox, 모니터 alarm channel로 출력하지 않는다.
- 연구자가 출력에 근거해 치료팀에 환자별 연락을 하지 않는다. 예외는 원 시스템에서 독립적으로 확인된 즉각적 데이터/보안 사고에 대해 기관 SOP가 요구하는 경우이며, 연구 점수 자체는 전달하지 않는다.
- 출력 조회와 export를 역할기반으로 제한하고 감사로그를 남긴다.
- 연구 장애는 환자감시나 치료기기의 기능에 영향을 주지 않아야 한다.
- 시스템 중단·입력 불량 시 연구 계산을 중지하고 원 데이터와 오류 원인을 보존한다.

## Inference safety contract

임상 계산 함수의 논리적 계약은 다음을 만족해야 한다.

```text
input contract valid
AND patient identity bound
AND timestamps fresh/aligned
AND units recognized
AND required channels present
AND signal quality sufficient
AND population/device within support
AND pipeline/model/threshold hashes compatible
  => deterministic research output + provenance
ELSE
  => no score + explicit reason code + audit event
```

허용 reason code 예: `PATIENT_MISMATCH`, `STALE_INPUT`, `CLOCK_UNCERTAIN`, `UNKNOWN_UNIT`, `MISSING_CHANNEL`, `LOW_SIGNAL_QUALITY`, `UNSUPPORTED_INPUT`, `VERSION_MISMATCH`, `SYSTEM_ERROR`.

## LLM 격리 규칙

### 허용

- 문헌 검색어·초안·요약 보조
- 비식별 개발문서와 코드에 대한 검토
- 합성 테스트 아이디어 생성

### 금지

- 환자 데이터 또는 환자별 출력의 외부 LLM 전송
- 환자별 특징·점수·임계값·경보·설명 산출
- runtime dependency, API fallback 또는 운영 장애 시 대체 추론
- LLM 생성 문장을 임상 근거·규제 결론으로 무검토 채택

### 기술 통제

- inference build dependency와 SBOM에서 생성형 AI SDK/endpoint denylist 검사
- 임상 계산 서비스의 외부 egress 기본 차단
- 빌드·컨테이너·모델 manifest 서명과 승인된 artifact allowlist
- LLM 사용 문서에 출처·검토자·승인기록 유지

## 임상의 노출 전 필수 증거

- 확정 intended use, 제품 상태/제출경로에 대한 규제기관 또는 자격 있는 전문가 결론
- 정식 위험관리계획·위험분석·통제검증·잔여위험 승인
- 환자연결·시간·단위·신호품질·결측·OOD·버전 mismatch E2E 시험
- 사전등록 SAP에 따른 독립 외부/시간외 및 전향 silent validation
- 환자 단위 95% CI, 보정, false alerts/hour, lead-time, coverage/무출력률, 하위군 결과
- 임상의의 원신호 확인·과신·무출력 이해를 포함한 사용적합성 검증
- 사이버보안 threat model, SBOM, 취약점·패치·복구 증거
- 필요한 IRB, DUA, 기관 정보보호, 임상안전, 품질 승인을 모두 문서화

이 증거 목록은 충분조건이나 허가 보장이 아니다. 분류: `PRODUCT_ASSUMPTION`.

## 중지 조건과 escalation

다음 사건이 발생하면 해당 연구 실행을 중지하고 입력·출력·버전·로그를 보존한다.

- shadow 출력이 치료팀 또는 환자에게 노출됨
- 연구 시스템이 원 모니터, EHR 또는 치료기기 동작에 영향
- 환자 mismatch, 단위 오류, 시간 오정렬 또는 stale 값인데 점수가 생성됨
- 승인되지 않은 데이터 접근·export·재식별 또는 보안침해 의심
- 모델·전처리·임계값 hash 불일치 또는 재현 불가
- 연구 점수가 실제 치료 결정에 사용되었다는 보고
- 사전 중지규칙을 넘는 성능·경보부담·data-quality 실패

통보 순서: 연구책임자 → 임상안전 책임자 → 데이터보호/보안 → 품질/규제 → IRB/기관이 요구하는 보고. 재개는 원인분석, CAPA, 통제 재검증과 필요한 승인 후에만 가능하다.

## 공개·발표 문구 규칙

### 허용 예

> 연구용 프로토타입에서 후보 신호 pipeline의 기술적 실행 가능성을 평가했다. 다운증후군 마취 환자의 임상 성능과 임상적 유용성은 아직 검증되지 않았다.

### 금지 예

- “다운증후군 마취 위험을 실시간 예측한다.”
- “서맥을 N분 전에 정확히 경고한다.”
- “안전성을 높인다/합병증을 예방한다.”
- “임상적으로 검증된 AI 경보이다.”

실제 결과를 보고할 때는 [Evidence Ledger](../research/EVIDENCE_LEDGER.csv)의 근거등급과 사전등록된 [Statistical Analysis Plan](../research/STATISTICAL_ANALYSIS_PLAN.md)을 함께 사용한다.

## 관련 문서

- [Intended Use Draft](../regulatory/INTENDED_USE_DRAFT.md)
- [FDA CDS Analysis](../regulatory/FDA_CDS_ANALYSIS.md)
- [Preliminary Hazard Analysis](HAZARD_ANALYSIS.md)
- [Risk Register](RISK_REGISTER.md)
- [IRB Protocol Draft](../research/IRB_PROTOCOL_DRAFT.md)

다운증후군 마취 관련 근거의 범위와 한계는 `VERIFIED_CLINICAL_EVIDENCE` 또는 `LIMITED_EVIDENCE`로 [Evidence Summary](../research/EVIDENCE_SUMMARY.md)에 구분되어 있으며, 이 문서는 새로운 임상 성능 주장을 추가하지 않는다.
