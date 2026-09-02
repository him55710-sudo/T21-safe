# 병원 Aggregate 합계질의 1쪽 (계획 §6-2)

**문서 상태:** DRAFT · Founder 검토용 · **지금은 발송하지 않음**  
**경로 제안:** `docs/business/hospital-aggregate-query-1p.md`  
**작성:** T21 제품·사업 분석가 · 2026-09-03 KST  
**정렬:** Business & Research Plan **§6-2** · `docs/research/HOSPITAL_DATA_REQUEST_SPEC.md` §11  
**원칙:** 합계(count)만 · PHI/파형/개별 차트 없음 · small-cell은 기관 정책에 따라 suppress

---

## 요청 목적 (한 문장)

협력기관에서 **진단 확인된 다운증후군(T21) 환자의 마취·진정 사례**에 대해, 후향 연구·IRB 설계에 필요한 **실현 가능성(feasibility)** 합계만 확인합니다. 전체 extract·예측 모델용 학습 데이터 요청이 아닙니다.

---

## 포함/제외 (초안 — 확정은 PI)

| 항목 | 초안 | 확정 |
| --- | --- | --- |
| DS 확인 | 임상의 진단 / 승인 구조화 코드 / 유전 확인 범주 — **원 유전자료 불필요** | `PI_TO_DEFINE` |
| 제외 | `UNCERTAIN` DS · ICD Q90만으로 waveform 사례 추정 금지 | |
| 기간 | 최근 5–10년 calendar year | `PI_TO_DEFINE` |
| 환경 | GA / procedural sedation / 치과마취 포함 여부 | `PI_TO_DEFINE` |

---

## §6-2 일곱 합계 항목

기관에 **아래 표만** 부탁드립니다. 환자·사례 식별자, 파형, 의무기록 원문은 요청하지 않습니다.

| # | 합계 항목 | 산출 예시 | 비고 |
| --- | --- | --- | --- |
| 1 | **연도별** 고유 DS 환자 수 · 마취·진정 **건수** | year × n_patients, n_cases | |
| 2 | 환자 1명이 **여러 번** 받은 사례 수 | n with ≥2 cases; max cases/patient | 반복 마취 비율 |
| 3 | **나이대 · 수술/시술 종류 · 마취·진정 방식** (가능하면 CHD 상태)별 건수 | crosstab counts | 범주는 기관 taxonomy |
| 4 | ECG · PPG · BP · SpO2 · 호흡(EtCO2 등) 자료가 **함께** 있는 비율 | modality ∩ counts / % | waveform 또는 numeric 명시 |
| 5 | 약물 · 기도 처치 · 회복실(PACU) 사건의 **시각 기록 가능 여부** | available Y/N + 대략 % | 시각 없으면 예측 연구 축소 |
| 6 | 비교군 가능한 **비 DS** 사례 수 (동일 기간·유사 시술) | n_control pool · overlap 가능 여부 | matching은 추후 |
| 7 | 자료 추출에 필요한 **병원 부서** · 예상 **비용·시간** · retention | IT/마취기록/연구지원 등 | extract 전 합의 |

**Small cell:** 기관 정책(예: n<5 또는 n<10)에 따라 `*` 처리. 이 합계로 **대외 DS 케이스 수 마케팅을 하지 않습니다.**

---

## 명시적 비요청 (이번 장)

- 개별 환자 목록 · MRN · 파형 파일 · free text 의무기록
- 펌프/EHR **쓰기** 권한 · 실시간 bedside 연동
- 클라우드 업로드 또는 병원 밖 반출 (별도 승인 전)

다음 단계(IRB/DUA 후): schema sample 1–3건(비식별) → acceptance test → 전체 extract.

---

## 회신 형식 (제안)

Excel/CSV 한 장 또는 PDF 표. 연락: **Founder만** (`PI_TO_DEFINE` 이메일). T21 팀은 PHI를 Grok/Notion에 올리지 않습니다.
