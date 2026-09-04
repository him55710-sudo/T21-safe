# 병원 Aggregate Feasibility Query (KR) — M0-B

**상태:** DRAFT · Founder 발송용 초안 · PI/기관 검토 전 · 지금은 자동 발송하지 않음<br>
**범위:** Path B / Research Use Only / Shadow / `clinical_validation=false`<br>
**Tip freeze:** `edff0f1` ([`FREEZE_DECLARATION_M0.md`](../governance/FREEZE_DECLARATION_M0.md))<br>
**관련:** [`PI_DECISION_PACK_KR.md`](../founder/PI_DECISION_PACK_KR.md) · [`HOSPITAL_DATA_REQUEST_SPEC.md`](../research/HOSPITAL_DATA_REQUEST_SPEC.md) §11 · [`SCHEMA_CLOCK_PILOT_ACCEPTANCE.md`](../research/SCHEMA_CLOCK_PILOT_ACCEPTANCE.md) · [`hospital-aggregate-query-1p.md`](hospital-aggregate-query-1p.md) (prior 1p; SUPERSEDE candidate for tip/send authority)

---

## 발송·연락 규칙 (하드)

| 주체 | 허용 | 금지 |
| --- | --- | --- |
| **Founder** | 병원/PI에게 본 질의표를 **수동** 전달·회신 수령 | PHI·환자 목록을 채팅/에이전트 도구에 붙여넣기 |
| **에이전트(Grok/Cursor 등)** | 문서 초안·체크리스트만 작성 | 병원·PI·IRB에 **이메일/메시지 발송**, 자동 팔로업, 연락처 수집 |

에이전트는 병원·PI에게 직접 연락하지 않는다. 발송·일정·회신 확인은 Founder만 한다.

---

## 1. 요청 목적

기관이 보유한 마취·진정 연구자료가 후속 프로토콜 설계에 적합한지 판단하기 위해 **최소한의 집계(count)** 만 확인한다. 이 질의는 전체 데이터 추출, 모델 학습, 임상 성능 주장, FACT 승격, 또는 환자별 판단을 승인하지 않는다.

---

## 2. 기관에 요청할 집계표

가능한 경우 기관의 기존 범주와 small-cell suppression 정책을 그대로 사용한다 (`SITE_REQUIRED`). 범주 정의가 다르면 억지로 변환하지 말고 정의 또는 `UNKNOWN`을 함께 회신한다. **환자 단위 행은 요청하지 않는다.**

| ID | 요청 집계 | 권장 회신 | 확인 목적 | 확정 |
| --- | --- | --- | --- | --- |
| F-01 | 연도별 고유 DS 환자 수와 마취·진정 사례 수 | `year`, `n_patients`, `n_cases` | cohort 규모와 연도 편중 | 기간=`PI_TO_DEFINE` · 산출=`SITE_REQUIRED` |
| F-02 | 환자별 반복 사례 분포 | 1회/2회/3회 이상 환자 수 | patient-level split 가능성 | `SITE_REQUIRED` |
| F-03 | 연령대 × 시술군 × 마취·진정 방식별 사례 수 | 기관 범주의 교차표 | intended population 후보 | 범주=`SITE_REQUIRED` · 범위=`PI_TO_DEFINE` |
| F-04 | DS 확인 근거 범주별 사례 수 | 임상 확인/승인 코드/기타/불명 | case ascertainment 검토 | `PI_TO_DEFINE` |
| F-05 | ECG, PPG, BP, SpO2, EtCO2 등 source별 보유 수와 교집합 | waveform/numeric 구분 count 또는 % | 동시 signal 가용성 | `SITE_REQUIRED` |
| F-06 | 약물, 기도 처치, PACU event의 source timestamp 보유 수 | source별 Y/N 및 count 또는 % | timeline linkage 가능성 | `SITE_REQUIRED` |
| F-07 | 동일 기간·유사 시술의 잠재적 비-DS 비교군 수 | 후보 pool과 범주 overlap | 비교 설계 가능성 | matching=`PI_TO_DEFINE` |
| F-08 | source system/device/firmware/schema 변경 연도별 사례 수 | 변경점별 count | 추출·분포 변화 위험 | `SITE_REQUIRED` |
| F-09 | 보존기간, 예상 추출량, 담당 부서, 비용과 소요시간 | 범위 또는 `UNKNOWN` | 후속 pilot 계획 | `SITE_REQUIRED` |

CHD, OSA, 마취력 등 환자 맥락은 기관에 이미 존재하는 승인된 구조화 필드의 집계만 받을 수 있다. 파형으로 이를 추론하지 않는다. DS 확인 기준, 기간, 연령대, 시술 범위는 PI가 정하기 전 `PI_REQUIRED` / `PI_TO_DEFINE`로 유지한다. **본 문서에 임상 cutoff를 만들지 않는다.**

---

## 3. 회신 형식과 privacy gate

- 한 개의 CSV/XLSX 집계표 또는 PDF 표를 권장한다.
- 환자·사례 식별자, MRN, 정확한 생년월일, 시술일, 주소, 연락처, 자유서술 기록은 포함하지 않는다.
- 기관 정책에 따른 small cell(예: n<5 또는 n<10 — **여기서 수치를 확정하지 않음**, `SITE_REQUIRED`)은 `SUPPRESSED`로 표기하며 역산 가능한 주변 합계도 함께 조정한다.
- 개인별 행이나 날짜가 도착하면 열람·재배포하지 않고 기관 data steward와 안전한 반송/삭제 절차를 협의한다.
- 연락·회신 창구: **Founder만** (이메일은 `PI_TO_DEFINE` / 기관 정책).
- 이 집계는 대외 사례 수 홍보, DS-specific 성능 주장, `clinical_validation=true`, 또는 임상 활성화의 근거가 아니다.

---

## 4. Feasibility 판정 기록

집계 회신 후 다음 항목만 문서화한다. 수치 합격선은 이 문서에서 만들지 않는다.

| 항목 | 기록값 |
| --- | --- |
| Population/setting 질문에 답할 수 있는가 | `YES / PARTIAL / NO / PI_REQUIRED` |
| 필요한 source의 교집합을 계산할 수 있는가 | `YES / PARTIAL / NO` |
| 반복 사례를 분리할 수 있는가 | `YES / PARTIAL / NO` |
| source timestamp와 schema 변경 이력을 확인할 수 있는가 | `YES / PARTIAL / NO` |
| IRB/DUA/security 검토 전 허용되는 다음 단계 | `NONE / SYNTHETIC SAMPLE / DEIDENTIFIED PILOT` |
| 미해결 질문, owner, 검토일 | 자유서술(식별정보 금지) |

`NO` 또는 `PARTIAL`은 실패한 기관이나 낮은 품질의 환자를 뜻하지 않는다. 후속 연구 질문과 추출 범위를 좁히기 위한 기록이다.

---

## 5. 다음 단계 gate · PI Decision Pack

집계 회신만으로 전체 extract를 요청하지 않는다. PI가 연구 질문을 검토하고 IRB/DUA, 기관 보안·반출 승인, data steward 책임이 확인된 경우에만 1–3건의 synthetic 또는 허용된 비식별 schema/clock pilot을 제안한다. Pilot acceptance는 [`SCHEMA_CLOCK_PILOT_ACCEPTANCE.md`](../research/SCHEMA_CLOCK_PILOT_ACCEPTANCE.md)를 사용한다.

합계 회신은 PI 회의 자료로만 쓴다. 인구·endpoint·window 결정은 [`PI_DECISION_PACK_KR.md`](../founder/PI_DECISION_PACK_KR.md)와 [`CLINICAL_RESEARCH_LOCK_V0.md`](../research/CLINICAL_RESEARCH_LOCK_V0.md)에서 `PI_REQUIRED`로 유지한다. 본 질의 회신만으로 Lock을 채우거나 RII/PROXY/threshold 코드를 바꾸지 않는다.

상세 source/data 요청 후보는 [`HOSPITAL_DATA_REQUEST_SPEC.md`](../research/HOSPITAL_DATA_REQUEST_SPEC.md)를 따른다.
