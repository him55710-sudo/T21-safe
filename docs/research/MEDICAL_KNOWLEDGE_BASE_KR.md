# T21 Safe 의학 지식 베이스 (연구용)

문서 상태: Path B RUO — paper-grade 지식 합성<br>
기준일: 2026-09-06<br>
원천: [`EVIDENCE_SUMMARY.md`](EVIDENCE_SUMMARY.md), [`EVIDENCE_LEDGER.csv`](EVIDENCE_LEDGER.csv)<br>
검색·검증 기준일(원천): 2026-09-02

> **경계:** 이 문서는 기존 근거 원장에 이미 기록된 PMID/claim만 인용한다. 새로운 임상 수치·비율·효과크기를 만들지 않는다. 공개 데이터셋 성능은 DS 임상 근거가 아니다. RII/PROXY feature 코드·임계값·가중치는 다루지 않는다.

## 1. 한 줄 요약

소아 Down syndrome(DS)에서 **sevoflurane 흡입 유도 중 서맥이 비교군보다 더 자주 관찰되었다**는 근거는 여러 관찰연구에서 일관된다. 그러나 이는 **특정 약제·소아·유도 단계**의 근거이며, 모든 연령·마취제·시술 단계의 보편 위험이나 개인 사건 예측·예방·치료 효과로 확장할 수 없다.

## 2. 판정 등급 정의

| 등급 | 의미 | 제품·논문에서의 사용 |
| --- | --- | --- |
| `VERIFIED_CLINICAL_EVIDENCE` | 원 논문/합의 표준에서 추적 가능한 관찰·방법론 결과 | 맥락(인구·약제·창)을 명시한 연구 설명에만 사용 |
| `LIMITED_EVIDENCE` | 소규모·비마취·초록 불일치·방법론 제한 | 가설·민감도 분석 입력; 임상 cutoff/진단 금지 |
| `UNSUPPORTED_OR_REJECTED` | 검토 seed에서 제품 주장에 쓸 비교 근거 없음 | UI·프로토콜·alert·마케팅에 금지 |
| `RESEARCH_HYPOTHESIS` | 연구 격차로 설명하는 제품 필요성 | RUO 문장만; 유효성·확률·경보 아님 |

## 3. VERIFIED — 맥락을 붙인 채 말할 수 있는 것

### 3.1 소아 sevoflurane 유도 서맥 (Q1)

| claim_id | 핵심 | PMID / DOI | 정량(원장만) |
| --- | --- | --- | --- |
| CLN-001 | 전향 관찰: 첫 300초 DS 서맥이 TD보다 많음 | PMID 40376277; DOI `10.4274/jpr.galenos.2024.87528` | DS 54/93 (58%); TD 22/102 (22%) |
| CLN-004 | 후향 matched: 서맥 빈도·HR 감소가 더 큼 | PMID 21109130; DOI `10.1016/j.jclinane.2010.05.002` | 초록에 exact rate 없음 — 원장대로 재인용하지 않음 |
| CLN-005 | 후향: 첫 360초; 다변량에서 DS·낮은 ASA 잔존 | PMID 20736433; DOI `10.1213/ANE.0b013e3181f2eacf` | DS 209; healthy 268 |

**허용 문장:** “소아 DS의 sevoflurane 흡입 유도에서 서맥 증가가 관찰되었다.”

**금지:** 개인 사건 예측, 예방 효과, 치료 권고, 모든 마취제로의 일반화.

### 3.2 Sympathetic failure 연관 (관찰, 유일 기전 아님)

- CLN-002 / PMID 40376277: 서맥·저혈압과 sympathetic failure 관찰 연관. DS hypotension 23/80 (29%).
- **주의 (CLN-003):** 같은 초록의 15/28 분모는 내부 불일치 → **재인용 금지** until full-text/clinician reconciliation.

### 3.3 Procedural sedation 혈압 궤적

- CLN-007 / PMID 40704557: DS vs age-matched non-DS에서 SBP mean difference -12.3 mmHg (95% CI -16.1 to -8.6); DBP -10.2 mmHg (95% CI -13.3 to -7.0).
- 임상 유의성·경보 임계값으로 쓰지 않는다(저자·원장 제한 유지).

### 3.4 전체 perioperative complication 단일 코호트 수치

- CLN-008 / PMID 40363932: 711명, 1,713건 비심장 수술·영상 마취에서 51건(2.98%); 합병증 중 호흡기 43.1%.
- **내부 non-DS 대조군 없음** → “일반 소아보다 높다” 비교 주장 금지.

### 3.5 Resting HRV 메타분석

- CLN-009 / PMID 30005737: 13개 연구; 요약상 RMSSD만 유의 (Hedges g -0.55, 95% CI -0.93 to -0.16).
- 대부분 비마취·이질적 → **개인 마취 위험 판정·DS 진단 대용 금지**.

### 3.6 HRV 방법론 표준·해석 경계

| claim_id | 요지 | PMID |
| --- | --- | --- |
| HRV-001 | 전통 short-term은 안정된 약 5분 중심 | PMID 8598068 |
| HRV-002 | LF/HF는 단순 sympathovagal balance가 아님 | PMID 23431279 |

## 4. LIMITED — 가설·연구 feature만

| claim_id | 요지 | PMID | 제품 함의 |
| --- | --- | --- | --- |
| CLN-010 | 정적 운동 중 낮은 BRS·둔화 반응 (12 DS vs 10 control) | PMID 16331125 | 비마취 소규모 → 환자 진단 금지 |
| CLN-011 | upright tilt 자율신경 반응 차이 (26 DS vs 11 control) | PMID 20307953 | 동적 가설 지지; 마취 예측 아님 |
| HRV-003 | 건강인 ultra-short에서 RMSSD 일부 재현 | PMID 21496161 | metric/window 검증 전 registry 진입 제한 |
| HRV-004 | 짧은 구간에서 주파수영역 정확도 저하 | PMID 16960742 | 길이/stationarity 실패 시 LF/HF 숨김 |
| HRV-005 | paced breathing이 ultra-short HRV에 영향 | PMID 29863781 | 환기·호흡수 공변량 필수 |
| HRV-006 | 2026 resting: HF≈60s / LF≈100s 등 지표별 최소 길이 힌트 | PMID 41946377 | **마취·DS 임상 cutoff 아님**; 민감도 분석 입력만 |
| CLN-003 | 초록 분모 불일치 | PMID 40376277 | 15/28 통계 금지 |

## 5. UNSUPPORTED / REJECTED — 넣지 말 것

| claim_id | 내용 |
| --- | --- |
| GEN-001 | 모든 마취제·모든 연령·모든 단계에서 동일한 DS 위험 — 입증 없음 |
| GEN-002 | Atropine hypersensitivity를 제품 claim/프로토콜 규칙으로 쓰기 — seed 근거 부족 |
| GEN-003 | 구체적 마취제 감량 %·우선 약물 규칙 — 지지되지 않음 |

부재는 “절대 없다”가 아니라 **Path B에 넣을 만큼 검증되지 않음**을 뜻한다.

## 6. 주제별 정리

### 6.1 Bradycardia (서맥)

- **검증됨:** 소아 sevoflurane 유도 창에서 DS군 서맥/HR 감소 증가 (CLN-001, CLN-004, CLN-005; PMID 40376277, 21109130, 20736433).
- **미확정:** age-appropriate bradycardia의 최종 정의·지속시간·source hierarchy — 임상의 adjudication 전 확정 금지 (`EVIDENCE_SUMMARY` §근거의 상충과 공백).
- **제품:** 연구 특성화·궤적 관찰 대상. “정확한 서맥 예측” 금지.

### 6.2 HRV 한계

- Resting만으로 위험도 판단 불가 (CLN-009).
- RMSSD/SD1: 단기 beat-to-beat 연구 지표; R-peak 품질·ectopy·최소 정상 RR·window·호흡/환기 함께 저장. 자율신경 진단 표시 금지.
- SDNN: 관찰 길이에 민감 → 다른 길이 window 직접 비교 금지; ultra-short는 별도 검증 전 비활성.
- LF/HF: UI에서 “교감/부교감 균형” 명명 금지 (HRV-002).
- 5분 표준(HRV-001)과 2026 ultra-short 결과(HRV-006)는 **방법론 자료**이지 DS 마취 cutoff가 아님.

### 6.3 CHD (선천성 심장질환)

- CLN-006 / PMID 21109130, 20736433: 일부 소아 sevoflurane 연구에서 CHD 유무와 별개인 DS 연관 관찰.
- **CHD를 무시할 근거는 아님.** CHD 유형·수술 여부·현재 혈역학·약물을 공변량·subgroup으로 보존 (`PICOTS`·원장 implication).

### 6.4 기전 (sympathetic / vagal / baroreflex)

- Sympathetic failure: 관찰 연관 (CLN-002) — 유일 인과·치료표적 아님.
- Vagal excess: 주원인 확정 불가; HF/RMSSD를 vagal dose meter로 쓰지 않음.
- Baroreflex: LIMITED 비마취 소규모 (CLN-010~011).

## 7. 제품이 말해도 되는 것 / 말하면 안 되는 것

### 7.1 허용 (RUO)

- “특정 소아 sevoflurane 유도 연구에서 DS군의 서맥과 혈역학 변화가 더 자주 관찰되었다.” (PMID 40376277 등)
- “환자별 ECG·PPG·BP·SpO2·EtCO2 변화를 동기화해 연구하는 도구가 필요하다.”
- “공개 데이터는 generic signal pipeline 검증에는 유용하지만 DS-specific 임상 성능을 입증하지 않는다.”
- “Research Instability Index는 검증되지 않은 연구 지표이며 확률·진단·경보가 아니다.”
- 표준 RUO 문장 (`EVIDENCE_SUMMARY` 결론):

> T21 Safe는 DS 환자의 마취·진정 중 환자별 생체신호 변화와 잠재적 혈역학 변화 전조를 **탐색**하기 위한 **연구용** 도구다. 임상적 유효성은 검증되지 않았으며 진단, 치료, 투약 또는 환자감시 목적으로 사용하지 않는다.

### 7.2 금지

- 합병증 예방, 심정지/서맥/저혈압 **정확한 예측**, 약물 용량 최적화·추천, 시술 진행 가능 판정.
- 공개 non-DS·성인·ICU·건강인 데이터로 DS/소아 임상 성능 입증 주장.
- RII를 확률·진단·예후·경보·치료 임계값으로 표기.
- atropine hypersensitivity, 감량 %, 우선 약물 규칙.
- 초록 불일치 수치(15/28) 및 원장에 없는 새 임상 수치 발명.
- 상세 금지 목록: [`../safety/PROHIBITED_CLAIMS.md`](../safety/PROHIBITED_CLAIMS.md)

## 8. 상충·공백 (논문 설계 시 주의)

1. Induction bradycardia ↑ ≠ 전체 perioperative complication ↑.
2. 기전 연관 ≠ 인과 치료표적.
3. Resting HRV 작은 차이와 provoked(tilt/exercise/induction) 동적 차이는 동시에 참일 수 있음.
4. 공개 파형은 주로 성인/ICU → 신호 코드 검증 ≠ 소아 DS 임상 주장.
5. 라벨(age-appropriate bradycardia, relative HR decline, hypotension, airway intervention)은 adjudication 전 확정 금지.

## 9. PMID 빠른 링크

- [40376277](https://pubmed.ncbi.nlm.nih.gov/40376277/) — prospective sympathetic failure/bradycardia
- [21109130](https://pubmed.ncbi.nlm.nih.gov/21109130/) — sevoflurane induction hemodynamics
- [20736433](https://pubmed.ncbi.nlm.nih.gov/20736433/) — bradycardia during sevoflurane induction
- [40704557](https://pubmed.ncbi.nlm.nih.gov/40704557/) — procedural sedation BP volatility
- [40363932](https://pubmed.ncbi.nlm.nih.gov/40363932/) — perioperative complications cohort
- [30005737](https://pubmed.ncbi.nlm.nih.gov/30005737/) — HRV SR/MA
- [16331125](https://pubmed.ncbi.nlm.nih.gov/16331125/) — baroreflex sensitivity
- [20307953](https://pubmed.ncbi.nlm.nih.gov/20307953/) — upright tilt
- [8598068](https://pubmed.ncbi.nlm.nih.gov/8598068/) — HRV Task Force
- [23431279](https://pubmed.ncbi.nlm.nih.gov/23431279/) — LF/HF critique

## 10. 변경 규칙

- 새 수치·PMID는 **Auditor가 FACT로 승격한 뒤에만** 원장·본 지식베이스에 반영한다. 임시 검색 결과는 [`LITERATURE_REFRESH_PLAN_KR.md`](LITERATURE_REFRESH_PLAN_KR.md) 절차를 따른다.
- 이 문서는 Path B RUO 연구 설계용이다. 임상 사용·규제 제출 단독 근거가 아니다.
