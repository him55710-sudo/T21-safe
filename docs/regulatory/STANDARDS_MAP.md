# Standards Applicability Map

문서 상태: 계획 초안, 인증·적합 선언 아님<br>
기준일: 2026-09-02<br>
대상: 현재 RUO 프로토타입과 장래 의료기기 가설

표준 적용성은 최종 intended use, 제품 분류, 시스템 경계, 배포지역과 규제기관 협의에 따라 달라진다. 아래 `적용 예상`은 설계준비를 위한 판단이며 적합성 또는 인증을 주장하지 않는다.

## 핵심 매핑

| 표준/사양 | 확인한 판본 | 적용 예상 | T21 Safe 관련성 | 현재 증거 | 핵심 공백 | 책임자/시점 |
|---|---|---:|---|---|---|---|
| IEC 62304 | 2006+A1:2015, consolidated ed. 1.1; IEC 안정성 일자 2028 | 장래 의료기기: 높음 | 생명주기, 안전등급, 요구사항, 형상·변경·문제관리 | 버전 고정·테스트 원칙, 연구 PRD | 소프트웨어 안전등급, SDP, 요구-위험-시험 추적, 유지보수 절차 | SW/품질; 설계동결 전 |
| ISO 14971 | 2019 ed. 3; ISO가 2025 확인 | 장래 의료기기: 높음 | 위험관리 계획·분석·통제·잔여위험·생산후 정보 | 초기 위해분석·위험등록부 | 정식 위험관리파일, 통제 검증, 잔여위험 수용기준, PMS 피드백 | 안전/품질; 모든 단계 |
| IEC 62366-1 | 2015+A1:2020 consolidated | 장래 사용자표시: 높음 | 사용 오류, 위해 관련 시나리오, 형성·총괄 사용적합성 | intended-use/비의도 사용 초안 | 사용자·환경 분석, UI 명세, critical task, 총괄검증 | HF/임상; UI 동결 전 |
| IEC 81001-5-1 | 2021, IEC 정오·해석 반영판 확인 | 연결형 소프트웨어: 높음 | 보안 생명주기, 위협·취약점·업데이트·보안위험 | 연구망·접근통제 요구 | 보안개발계획, threat model, SBOM, 취약점/패치/공개정책 | 보안/SW; 아키텍처부터 |
| HL7 FHIR R4 | v4.0.1, permanent home, normative+STU 혼합 | 조건부/인터페이스 | 환자·관찰·시술·약물·장치 데이터 교환 | 병원 데이터 필드 명세 | 프로파일/용어/단위, Provenance, 구현가이드, 적합성시험 | 통합/데이터; 병원 연동 전 |
| ISO/IEEE 11073-10201 | 2020; ISO가 2025 확인 | 조건부/급성기 vital signs | 기기·관측값·단위·metric 모델의 의미 보존 | 입력 채널 후보 | 지원 장치 mapping, 단위·상태·시간 의미, conformance 범위 | 통합/임상공학; 연결 전 |

공식 판본 정보 분류: `VERIFIED_OFFICIAL_INFORMATION`<br>
제품 적용 판단 분류: `PRODUCT_ASSUMPTION`

## 추가 검토 표준

아래는 장래 의료기기 개발 단계에서 적용성·최신 판본·국가 채택을 규제기관/인증기관과 다시 확인한다.

| 표준 | 적용 조건 | 준비할 산출물 | 현재 상태 |
|---|---|---|---|
| ISO 13485 | 의료기기 QMS로 개발·제조할 때 | 설계관리, 공급자, CAPA, 문서·기록, 변경관리 | 미구축 |
| IEC 82304-1 | 독립형 health software product의 제품안전·정보 요구 적용 시 | 제품 요구, 검증, 동반문서, 유지보수 | 미평가 |
| ISO 14155 | 의료기기 임상조사로 수행할 때 | 임상조사계획, 모니터링, 데이터·안전·보고 | IRB 초안만 존재 |
| ISO 20417 | 제조자가 제공하는 의료기기 정보에 적용 시 | 표시사항, 경고, 사용자 정보, 추적 | RUO 문구 초안만 존재 |
| ISO 15223-1 | 의료기기 라벨 기호를 사용할 때 | 기호 선택·설명·라벨 검증 | 해당 없음/미평가 |
| IEC 60601-1 계열 | 자체 의료용 전기 하드웨어를 공급하거나 시스템 통합책임이 생길 때 | 기본안전·필수성능·EMC·시스템 시험 | 현재 자체 하드웨어 없음 |

분류: `PRODUCT_ASSUMPTION`. 구매·적용 전에 최신 판본, 정오표, 전환기간과 MFDS/FDA 인정 여부를 확인한다.

## 표준별 최소 추적성

```text
intended use / user needs
  -> system & software requirements
  -> hazards / hazardous situations / risk controls
  -> architecture & cybersecurity controls
  -> unit / integration / system / usability tests
  -> clinical performance evidence
  -> residual risk & labeling
  -> change / post-market feedback
```

모든 항목은 문서 ID, 버전, 승인자, 커밋/빌드 해시, 데이터·모델 버전과 양방향 링크를 가져야 한다. 임상 계산 빌드에는 잠금파일, 컨테이너 digest, 전처리·모델·임계값 해시를 포함한다.

## 상호운용성 최소 통제

- 환자·방문·장치 식별자 연결 규칙과 충돌 감지
- UTC 기준 시간, 원본 timezone, 장치 clock offset과 동기화 품질
- UCUM 등 단위 체계, 원 단위 보존, 변환식·범위·정밀도
- 관측값 상태(유효/무효/보정/수동입력), provenance와 원시 참조
- sampling rate, resampling, latency, packet loss, duplicate/out-of-order 처리
- 모니터 vendor·model·firmware·interface version 추적
- 연결 단절·stale data·환자 mismatch 시 fail-silent와 사용자 표시
- 합성/재생 데이터 기반 conformance 및 negative testing

분류: `PRODUCT_ASSUMPTION`

## 단계별 게이트

| 단계 | 표준 관련 완료조건 |
|---|---|
| RUO 후향 연구 | 데이터·코드·모델 추적, 최소 위험등록부, 보안 접근통제, 재현 가능한 시험 |
| 전향 silent validation | 임상연구 품질절차, 인터페이스 검증, 신호 지연·결측·mismatch 시험, 모니터링 계획 |
| 사용자 노출 전 | 정식 QMS·위험관리파일·SW 생명주기·사용적합성·사이버보안 증거와 규제기관 합의 |
| 제출/출시 전 | 적용 표준 목록·편차·검증보고서·임상평가·표시·PMS/업데이트 계획 승인 |

## 공식 출처

- IEC, [IEC 62304:2006+A1:2015](https://webstore.iec.ch/en/publication/22794).
- ISO, [ISO 14971:2019](https://www.iso.org/standard/72704.html).
- IEC, [IEC 62366-1:2015+A1:2020](https://webstore.iec.ch/en/publication/21863).
- IEC, [IEC 81001-5-1:2021](https://webstore.iec.ch/en/publication/63293).
- HL7, [FHIR Release 4 (v4.0.1)](https://hl7.org/fhir/R4/).
- ISO, [ISO/IEEE 11073-10201:2020](https://www.iso.org/standard/77339.html).
- IMDRF, [Good Machine Learning Practice for Medical Device Development](https://www.imdrf.org/documents/good-machine-learning-practice-medical-device-development-guiding-principles), N88 FINAL:2025.

공식 페이지의 판본·범위 요약은 `VERIFIED_OFFICIAL_INFORMATION`이다. 표준 원문은 저작권 자료이므로 실제 요구사항은 정식 사본과 품질·규제 전문가 검토를 기준으로 한다.
