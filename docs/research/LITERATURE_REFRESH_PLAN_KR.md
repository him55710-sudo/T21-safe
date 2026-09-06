# PubMed 문헌 갱신 계획 (FACT 승격 전)

문서 상태: Path B RUO — 검색·후보 관리 절차<br>
기준일: 2026-09-06<br>
현행 seed 기준일: 2026-09-02 ([`EVIDENCE_SUMMARY.md`](EVIDENCE_SUMMARY.md), [`EVIDENCE_LEDGER.csv`](EVIDENCE_LEDGER.csv))

> **절대 규칙:** 검색으로 찾은 새 논문·초록 수치는 **Auditor가 FACT로 승격하기 전까지** `EVIDENCE_LEDGER`·제품 문장·논문 Abstract에 넣지 않는다. 후보는 `CANDIDATE` / `NEEDS_AUDIT`만 사용한다. 임상 수치를 발명하지 않는다.

## 1. 목적

1. Seed PMID 이후 신규·반박·확장 문헌을 주기적으로 훑는다.
2. 상충·초록 품질 이슈(예: CLN-003 분모 불일치)를 full-text 대기열에 올린다.
3. 제품·논문 claim 경계를 유지한 채 근거 원장만 안전하게 갱신한다.

## 2. 역할

| 역할 | 할 일 | 하지 말 일 |
| --- | --- | --- |
| Searcher / 연구보조 | PubMed 질의 실행, 후보 표 작성, PDF/초록 링크 수집 | 원장 status를 VERIFIED로 바꿈; 제품 카피 수정 |
| Clinical Evidence Reviewer | 맥락·일반화·기전 과장을 검토 | Auditor 없이 FACT 선언 |
| **Auditor** | PMID/DOI·전문·표 대조 후 status 승격/거절 | 검색어만으로 VERIFIED 부여 |
| PI | endpoint·임상 문장 승인 | 미감사 수치를 발표에 사용 |
| Biostat | 메타·표본·이질성 해석 | 미등록 endpoint로 효과 병합 |

## 3. 상태 머신 (필수)

```
SEARCH_HIT → CANDIDATE_SCREEN → NEEDS_FULLTEXT → AUDITOR_REVIEW
    → FACT_VERIFIED_CLINICAL_EVIDENCE
    → FACT_LIMITED_EVIDENCE
    → FACT_UNSUPPORTED_OR_REJECTED
    → HOLD (정보 부족)
```

- `CANDIDATE_*` / `NEEDS_*` / `HOLD`는 **문서·이슈·스프레드시트 초안**에만 존재한다.
- `FACT_*`만 [`EVIDENCE_LEDGER.csv`](EVIDENCE_LEDGER.csv)의 `status` 열과 [`MEDICAL_KNOWLEDGE_BASE_KR.md`](MEDICAL_KNOWLEDGE_BASE_KR.md)에 반영한다.
- Research Hypothesis(GEN-004류)는 합성 문장이며, 새 관찰 수치를 붙이려면 별도 claim_id + Auditor 필요.

## 4. 검색 주기와 범위

| 주기 | 범위 | 산출물 |
| --- | --- | --- |
| 분기 1회 (최소) | 아래 질의군 + seed PMID “similar articles” | `docs/research/_candidates/YYYY-MM-DD_pubmed_refresh.md` (gitignore 가능) |
| 주요 논문/프로토콜 제출 2주 전 | 동일 + full-text 우선순위 재정렬 | Auditor 큐 |
| 긴급 | 안전·규제·경쟁 이슈 PMID | HOLD 또는 임시 safety note (제품 claim 아님) |

### 4.1 질의군 (초안 — 실행 시 날짜·필터 기록)

1. **DS + anesthesia/sedation + bradycardia/hemodynamic**  
   `(Down syndrome OR trisomy 21) AND (anesthesia OR sevoflurane OR sedation) AND (bradycardia OR hemodynamic OR hypotension)`
2. **DS + HRV / autonomic**  
   `(Down syndrome OR trisomy 21) AND (heart rate variability OR baroreflex OR autonomic)`
3. **HRV methods / ultra-short / LF-HF critique** (인구 DS 필수 아님)  
   `ultra-short HRV` / `LF/HF sympathovagal` 등 — Methods 근거용; DS cutoff로 승격하지 않음
4. **Seed 전방 인용:** PMID 40376277, 21109130, 20736433, 40704557, 40363932, 30005737

각 실행 시 기록: 실행 시각(Asia/Seoul), PubMed 필터, hit 수, 검토자 이니셜.

## 5. 후보 표 스키마 (FACT 전)

| 열 | 내용 |
| --- | --- |
| candidate_id | `CAND-YYYYMMDD-##` |
| pmid / doi | 필수 하나 이상 |
| title / year | |
| study_design | |
| population_age / context | 소아? sevoflurane? 비마취? |
| claimed_numbers | 초록·표에서 **그대로** 옮겨 적기 (계산·반올림 금지) |
| conflict_with | 기존 claim_id (있으면) |
| screen | include / exclude + 이유 |
| audit_status | `NEEDS_FULLTEXT` / `READY_FOR_AUDITOR` / `HOLD` |
| proposed_ledger_status | 제안만; Auditor가 최종 |

**금지:** 초록 분모가 안 맞으면(CLN-003 유형) 숫자를 고치지 말고 `HOLD` + reconciliation 요청.

## 6. Auditor FACT 승격 체크리스트

Auditor는 다음을 모두 만족할 때만 ledger에 행을 추가·수정한다.

1. ☐ PMID/DOI로 원문 또는 신뢰 가능한 전문 표 확인  
2. ☐ population / exposure / window / comparator가 claim 문장과 일치  
3. ☐ 정량은 표·본문에서 재확인; 초록-only면 `LIMITED` 또는 HOLD  
4. ☐ 기존 VERIFIED와 상충 시 둘 다 남기고 limitations에 명시 (조용히 덮어쓰지 않음)  
5. ☐ `research_implication`에 제품 금지 문구 포함  
6. ☐ [`literature.bib`](../../research/literature.bib) 항목 추가  
7. ☐ Summary·Knowledge Base·금지 claim 문서 동기화 PR  
8. ☐ 날짜·Auditor 이니셜을 PR description에 기록  

승격 전 제품 UI·IR·데모 스크립트에 후보 수치를 넣지 않는다.

## 7. 기존 seed에 대한 고정 대기열

| 항목 | 이유 | 다음 액션 |
| --- | --- | --- |
| PMID 40376277 hypotension 15/28 | CLN-003 분모 불일치 | full-text/table; 15/28 재인용 금지 유지 |
| PMID 21109130 exact bradycardia rate | 초록에 exact rate 없음 | full-text rate만 Auditor 후 인용 |
| Atropine / 감량% (GEN-002~003) | seed 부족 | 약리 리뷰 후에도 제품 규칙 금지 기본; FACT면 ledger만 |
| HRV-006 (PMID 41946377) | resting methods | DS 마취 cutoff로 승격 금지; LIMITED 유지 원칙 |

## 8. 산출물 경로

| 단계 | 경로 |
| --- | --- |
| 후보 초안 | `docs/research/_candidates/` 또는 이슈 본문 (원장 아님) |
| FACT 원장 | `docs/research/EVIDENCE_LEDGER.csv` |
| 서술 합성 | `docs/research/EVIDENCE_SUMMARY.md`, `MEDICAL_KNOWLEDGE_BASE_KR.md` |
| Bib | `research/literature.bib` |

## 9. Definition of Done (한 번의 refresh)

- [ ] 질의·날짜·hit 수 기록됨  
- [ ] 후보 표에 screen 완료  
- [ ] Auditor 큐에 READY/HOLD 분류됨  
- [ ] **FACT 반영은 Auditor 승인 PR만**  
- [ ] FACT 없는 수치가 Knowledge Base·제품·IR에 유입되지 않음  

이 계획 자체는 문헌 검색 허가가 아니며, 기관 도서관·라이선스·전문 접근 규칙을 따른다.
