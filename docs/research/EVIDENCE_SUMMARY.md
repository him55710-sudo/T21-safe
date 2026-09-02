# DS 마취·진정 생리 불안정성 근거 요약

문서 상태: RUO 연구설계용 근거 합성<br>
검색·검증 기준일: 2026-09-02<br>
정량 주장 원장: [`EVIDENCE_LEDGER.csv`](EVIDENCE_LEDGER.csv)<br>
문헌 라이브러리: [`research/literature.bib`](../../research/literature.bib)

## 결론부터

소아 Down syndrome(DS)에서 **sevoflurane 흡입 유도 중 서맥이 비교군보다 더 자주 관찰되었다**는 근거는 여러 관찰연구에서 일관된다. 가장 최근 전향 연구는 첫 300초 동안 DS 54/93(58%), typically developing(TD) 22/102(22%)를 보고했다(PMID 40376277; DOI `10.4274/jpr.galenos.2024.87528`; CLN-001). 그러나 이 결과는 특정 약제·소아·유도 단계의 근거이며, 모든 연령·마취제·시술 단계의 보편적 위험으로 확장할 수 없다.

반대로 “DS 마취는 전반적으로 항상 고위험”이라는 표현도 근거에 맞지 않는다. 2025년 단일기관 후향 코호트는 711명, 1,713건의 비심장 수술·영상 마취에서 51건(2.98%)의 합병증을 보고했고, 그중 43.1%가 호흡기 사건이었다(PMID 40363932; DOI `10.3390/jcm14092900`; CLN-008). 내부 비-DS 대조군이 없으므로 이 수치를 일반 소아보다 높다는 비교 근거로 사용할 수 없다.

따라서 정확한 제품 설명은 다음과 같다.

> T21 Safe는 DS 환자의 마취·진정 중 환자별 생체신호 변화와 잠재적 혈역학 변화 전조를 탐색하기 위한 연구용 도구다. 임상적 유효성은 검증되지 않았으며 진단, 치료, 투약 또는 환자감시 목적으로 사용하지 않는다.

## 질문별 판정

### 1. DS 환자에게 마취 중 서맥 위험이 증가하는가?

**판정: VERIFIED_CLINICAL_EVIDENCE — 단, 맥락 제한.**

- 전향 관찰연구: 소아 sevoflurane 유도 첫 300초, DS 93명 대 TD 102명; 서맥 58% 대 22%(PMID 40376277; CLN-001).
- 후향 matched 연구: 11,201건 중 확인한 DS 소아 96명에서 matched 비교군보다 서맥 빈도와 baseline 대비 HR 감소가 컸다(PMID 21109130; DOI `10.1016/j.jclinane.2010.05.002`; CLN-004).
- 별도 후향 연구: DS 209명, healthy control 268명, 첫 360초; 다변량 분석에서 DS와 낮은 ASA physical status가 독립 요인으로 남았다(PMID 20736433; DOI `10.1213/ANE.0b013e3181f2eacf`; CLN-005).

이 근거가 허용하는 문장은 “소아 DS의 sevoflurane 흡입 유도에서 서맥 증가가 관찰되었다”까지다. 개인 사건 예측, 예방 효과 또는 치료 권고는 입증하지 않는다.

### 2. 모든 마취제와 모든 연령에 동일한가?

**판정: UNSUPPORTED_OR_REJECTED.**

핵심 비교연구는 소아 sevoflurane 흡입 유도에 집중되어 있다. procedural sedation의 소아·젊은 성인 연구는 혈압 감소 차이를 보고했지만 약제·절차가 이질적이다(PMID 40704557; CLN-007). 성인 DS의 다양한 마취제, 유지·각성 단계, 치과진정 전체에 동일한 상대위험을 적용할 근거가 없다. 연구 프로토콜은 약제군·연령·단계별 상호작용을 사전 정의하고, 데이터가 적으면 추정 대신 `insufficient data`를 표시해야 한다.

### 3. sympathetic failure, vagal excess, baroreflex impairment 중 무엇이 근거가 있는가?

**판정: 기전별 근거 수준이 다르며 단일 원인 확정 불가.**

- **Sympathetic failure:** 전향 마취 유도 연구에서 서맥·저혈압과 연관되었다(PMID 40376277; CLN-002). 관찰적 연관이지 확정된 유일 기전은 아니다. PubMed 초록에는 hypotension 23/80과 이후 15/28이라는 분모 불일치가 있어 15/28을 재인용하지 않는다(CLN-003).
- **Vagal/parasympathetic excess:** 해당 전향 연구가 secondary outcome으로 조사했으나 현재 근거 묶음만으로 “vagal excess가 주원인”이라 확정할 수 없다. HRV의 HF 또는 RMSSD를 직접 vagal dose meter처럼 쓰지 않는다.
- **Baroreflex impairment:** 정적운동 연구 12 DS 대 10 control에서 낮은 BRS, tilt 연구 26 DS 대 11 control에서 더 작은 BRS 변화가 보고되었다(PMID 16331125; PMID 20307953; CLN-010~011). 모두 소규모 비마취 생리연구이므로 LIMITED_EVIDENCE다.

제품에서는 이 기전을 진단명이나 처치 근거로 표시하지 않고, 연구 feature와 가설로만 기록한다.

### 4. RMSSD, SDNN, LF, HF, LF/HF를 짧은 마취 window에서 어떻게 해석하는가?

**판정: metric/window별 검증과 SQI가 선행되어야 한다.**

| 지표 | 허용되는 연구 해석 | 짧은 window 규칙 |
| --- | --- | --- |
| RMSSD / SD1 | 단기 beat-to-beat 변동성의 연구 지표. 일부 건강인 ultra-short 조건에서 비교적 재현성이 있었다(PMID 21496161; PMID 29863781). | R-peak 품질, ectopy, 최소 정상 RR 수, window 길이, 호흡/환기 상태를 함께 저장한다. 임상 자율신경 진단으로 표시하지 않는다. |
| SDNN | 관찰 길이의 영향을 크게 받는 전체 변동성 지표. | 다른 길이 window끼리 직접 비교하지 않는다. ultra-short 사용은 별도 검증 전 비활성화한다. |
| LF | 교감신경만의 지표가 아니며 여러 생리 요소가 섞인다(PMID 23431279). | 안정성·길이 요구가 부족하면 계산하더라도 사용자 출력에서 숨긴다. 짧은 구간 정확도 저하 근거가 있다(PMID 16960742). |
| HF | 호흡성 동성부정맥과 호흡 빈도·환기의 영향을 강하게 받는다. | respiratory signal/ventilator context 없이 부교감 활성의 직접 척도로 해석하지 않는다. |
| LF/HF | sympathovagal balance의 정확한 단일 척도가 아니다(PMID 23431279; DOI `10.3389/fphys.2013.00026`). | UI에서 “교감/부교감 균형”이라고 명명하지 않는다. 탐색적 분석에서만 사용한다. |

전통적 short-term 기준은 안정된 약 5분 구간을 중심으로 한다(PMID 8598068; HRV-001). 2026년 건강인 resting 연구의 60/100초 또는 200/290초 결과는 지표별 허용오차에 따른 방법론 자료일 뿐, 마취·DS 임상 cutoff가 아니다(PMID 41946377; HRV-006).

### 5. Resting HRV만으로 DS 위험도를 판단할 수 있는가?

**판정: 아니오.**

13개 연구의 체계적 문헌고찰·메타분석에서 resting 비교의 일관된 차이는 제한적이었고, 요약상 RMSSD만 유의했다(Hedges g -0.55, 95% CI -0.93~-0.16; PMID 30005737; CLN-009). 연구들은 이질적이고 대부분 마취 상황이 아니다. Resting HRV는 baseline characterization에 쓸 수 있으나 개인 마취 위험 판정이나 DS 진단 대용으로 사용할 수 없다.

### 6. 선천성 심장질환(CHD)과 독립적인가?

**판정: 일부 소아 sevoflurane 연구에서 독립적 연관을 지지하지만, CHD를 무시할 근거는 아니다.**

PMID 21109130은 CHD 유무에 따른 결과가 유사하다고 보고했고, PMID 20736433의 다변량 분석에서도 DS가 남았다(CLN-006). 잔여 교란과 표본 제한이 있으므로 CHD 유형·수술 여부·현재 혈역학·약물을 반드시 공변량 및 subgroup으로 보존한다.

### 7. 전체 perioperative complication은 실제로 얼마나 높은가?

**판정: 하나의 보편적 비율을 제시할 수 없다.**

단일기관 코호트의 2.98%는 특정 정의, 비심장 수술/영상, 해당 병원 기간과 진료체계의 값이다(PMID 40363932; CLN-008). 환자 711명에 마취 1,713건이므로 반복 시술도 있다. 비교군이 없어 “일반 소아보다 높다”는 결론을 내릴 수 없고, 연구별 endpoint 정의가 달라 단순 병합하지 않는다.

### 8. atropine hypersensitivity, 감량 비율, 특정 약물 우선 사용은 충분한가?

**판정: UNSUPPORTED_OR_REJECTED.**

검토한 원 논문과 seed 근거에서 보편적 atropine hypersensitivity, 특정 마취제 감량 퍼센트, 우선 약물 규칙을 지지하는 현대적 비교 근거를 확인하지 못했다(GEN-002~003). 이는 “그 현상이 절대 없다”는 뜻이 아니라 Path B 제품에 넣을 만큼 검증되지 않았다는 뜻이다. 해당 문구·계산·alert·프로토콜 규칙은 금지한다.

### 9. 과장 없이 제품 필요성을 어떻게 설명하는가?

**판정: RESEARCH_HYPOTHESIS.**

허용 문장:

- “특정 소아 sevoflurane 유도 연구에서 DS군의 서맥과 혈역학 변화가 더 자주 관찰되었다.”
- “환자별 ECG·PPG·BP·SpO2·EtCO2 변화를 동기화해 연구하는 도구가 필요하다.”
- “공개 데이터는 generic signal pipeline 검증에는 유용하지만 DS-specific 임상 성능을 입증하지 않는다.”
- “Research Instability Index는 검증되지 않은 연구 지표이며 확률·진단·경보가 아니다.”

금지 문장은 [`CLINICAL_SAFETY_BOUNDARIES.md`](../safety/CLINICAL_SAFETY_BOUNDARIES.md)에서 통제한다.

## 근거의 상충과 공백

1. **국소 endpoint 대 전체 합병증:** induction bradycardia 근거와 전체 perioperative complication rate는 서로 다른 질문이다. 전자가 증가했다고 후자 전체가 높다고 결론 내리지 않는다.
2. **기전 대 관찰:** sympathetic failure 연관은 중요한 전향 근거지만 인과 치료표적 확정이 아니다.
3. **Resting 대 provoked physiology:** resting HRV의 작은/불일치 차이와 tilt·exercise·induction 중 동적 반응 차이는 동시에 참일 수 있다.
4. **소아 대 성인:** 공개 파형은 주로 성인/ICU다. 신호 코드 검증은 가능하나 소아 DS 임상 주장으로 이전할 수 없다.
5. **라벨 공백:** age-appropriate bradycardia, significant relative HR decline, hypotension, airway intervention의 최종 정의는 임상의 adjudication 전에 확정하지 않는다.

## 원문 링크

- [PMID 40376277 — prospective sympathetic failure/bradycardia study](https://pubmed.ncbi.nlm.nih.gov/40376277/)
- [PMID 21109130 — hemodynamic changes during sevoflurane induction](https://pubmed.ncbi.nlm.nih.gov/21109130/)
- [PMID 20736433 — bradycardia during sevoflurane induction](https://pubmed.ncbi.nlm.nih.gov/20736433/)
- [PMID 40704557 — procedural sedation hemodynamic volatility](https://pubmed.ncbi.nlm.nih.gov/40704557/)
- [PMID 40363932 — perioperative complications cohort](https://pubmed.ncbi.nlm.nih.gov/40363932/)
- [PMID 30005737 — HRV systematic review/meta-analysis](https://pubmed.ncbi.nlm.nih.gov/30005737/)
- [PMID 16331125 — baroreflex sensitivity](https://pubmed.ncbi.nlm.nih.gov/16331125/)
- [PMID 20307953 — upright tilt](https://pubmed.ncbi.nlm.nih.gov/20307953/)
