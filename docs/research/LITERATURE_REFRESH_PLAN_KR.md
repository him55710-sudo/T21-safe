# 문헌 새로고침 계획 (PubMed seed → Auditor 전)

문서 상태: Path B RUO — 검색·후보화만, FACT 아님<br>
기준일: 2026-09-06<br>
원천 원장: [`EVIDENCE_SUMMARY.md`](EVIDENCE_SUMMARY.md), [`EVIDENCE_LEDGER.csv`](EVIDENCE_LEDGER.csv)<br>
문헌 라이브러리: [`research/literature.bib`](../../research/literature.bib)<br>
원천 검색·검증 기준일: 2026-09-02

> **규칙:** PubMed를 다시 검색해도 **새 수치·PMID를 제품 문장·지식베이스·원장에 바로 넣지 않는다.** 후보는 `CANDIDATE`로만 두고, Auditor가 FACT/`VERIFIED_*`로 승격한 뒤에만 [`EVIDENCE_LEDGER.csv`](EVIDENCE_LEDGER.csv)와 [`MEDICAL_KNOWLEDGE_BASE_KR.md`](MEDICAL_KNOWLEDGE_BASE_KR.md)에 반영한다. 본 계획은 RII/PROXY tip을 확장하지 않는다.

## 1. 목적

1. 기존 seed(원장 claim_id CLN-*/HRV-*/GEN-*) 주변의 **최신·관련** 문헌을 빠짐없이 다시 훑는다.
2. 중복·철회·초록-본문 불일치를 조기에 걸러 `LIMITED`/`UNSUPPORTED` 경계를 유지한다.
3. 창업자·PI가 “무엇이 아직 가설인지”를 한눈에 보게 한다.

## 2. 현재 seed (원장에 이미 있는 PMID만 — 신규 발명 금지)

임상·관찰 묶음: `40376277`, `21109130`, `20736433`, `40704557`, `40363932`, `30005737`, `16331125`, `20307953`
HRV·방법론: `8598068`, `23431279`, `21496161`, `16960742`, `29863781`, `41946377`
합성·경계: GEN-001~004 (일부는 “qualifying source 없음”)

이 목록 밖의 PMID는 **검색 히트일 뿐**이며, Auditor 전 FACT가 아니다.

## 3. 새로고침 주기·역할

| 단계 | 담당 | 산출물 | FACT? |
| --- | --- | --- | --- |
| A. Query 실행 | 연구 보조 / Eng (문서만) | 검색식·실행일·히트 수(건수만) | 아니오 |
| B. 제목·초록 스크리닝 | 연구 보조 | 포함/제외 이유 표 | 아니오 |
| C. 전문 확보·초록 수치 대조 | PI 지정 reader | 불일치 flag (예: CLN-003형) | 아니오 |
| D. claim 초안 | 문서 작성자 | `CANDIDATE` 행 (별도 staging) | 아니오 |
| E. Auditor 심사 | Auditor | status 부여·원장 merge | **이때만** |
| F. 지식베이스 반영 | 문서 소유자 | `MEDICAL_KNOWLEDGE_BASE_KR` 개정 | E 이후 |

권장 주기: M0 동결 중에는 **분기 1회 또는 PI 회의 전**; 동결 해제 후 protocol lock 직전 1회 필수. 긴급 철회(retraction) 알림은 주기와 무관하게 B→E를 단축한다.

## 4. 검색식 골격 (예시 — 결과 수치를 미리 적지 않음)

실행 시 날짜·히트 수는 로그에만 남기고 본문/원장에 “N건이 증명한다”고 쓰지 않는다.

1. **DS + sevoflurane/induction bradycardia**
   `Down syndrome` / `trisomy 21` + `sevoflurane` + (`bradycardia` OR `heart rate`)
2. **DS + sedation hemodynamics**
   `Down syndrome` + (`sedation` OR `procedural`) + (`hypotension` OR `blood pressure`)
3. **DS + perioperative complications**
   `Down syndrome` + `anesthesia` + `complications` (비심장 맥락 주의)
4. **DS + HRV / baroreflex (비마취 생리)**
   `Down syndrome` + (`heart rate variability` OR `baroreflex`)
5. **HRV methods (마취 비특이)**
   ultra-short HRV, LF/HF critique, Task Force — 기존 HRV-* seed 인용·관련 인용 추적

포함: 인간, 영어 또는 한국어 초록 가능, 원 연구·체계적 고찰·합의 표준.
제외: 동물만, DS 미확인, 용량/약물 추천 단독 서술, 제품 마케팅, 원장과 무관한 유전자 치료 등.

## 5. Staging 표 형식 (원장에 직접 쓰지 말 것)

별도 파일 예: `docs/research/_staging/LIT_CANDIDATES_YYYYMMDD.csv` (커밋 시 PHI·환자자료 금지)

| 필드 | 내용 |
| --- | --- |
| candidate_id | `CAND-YYYYMMDD-###` |
| pubmed_id | 숫자만 |
| linked_question_id | Q1–Q9 등 기존 질문 |
| proposed_status | 제안일 뿐; Auditor가 확정 |
| one_line_claim_ko | 과장 없는 한 문장 |
| population_context | 연령·약제·단계 |
| quantitative_fields | 초록/본문에 **명시된 것만**; 없으면 비움 |
| conflict_with_ledger | 기존 claim과 충돌 여부 |
| action | `HOLD` / `REQUEST_FULLTEXT` / `SUBMIT_TO_AUDITOR` |

**금지:** staging 숫자를 IR·데모·지식베이스 본문에 복사.

## 6. Auditor 승격 기준 (요약)

승격(`VERIFIED_CLINICAL_EVIDENCE` 등) 전에 확인:

- [ ] 전문(또는 합의 표준 원문)과 초록 수치 일치
- [ ] 인구·노출·comparator·window가 claim 문장에 묶여 있음
- [ ] 단일 센터·후향·소표본 한계가 `limitations`에 남음
- [ ] 제품 금지 주장(예측·예방·투약·보편 위험)으로 읽히지 않음
- [ ] GEN-002/003류(atropine hypersensitivity, 감량 %)는 현대 비교 근거 없이 승격하지 않음

반려 시: `LIMITED_EVIDENCE` 또는 `UNSUPPORTED_OR_REJECTED`로만 기록. “근거 없음” ≠ “현상 절대 없음”.

## 7. 지식베이스·창업자 문서 반영 규칙

| 문서 | Auditor 전 | Auditor 후 |
| --- | --- | --- |
| `EVIDENCE_LEDGER.csv` | 변경 없음 (staging만) | 행 추가/status 갱신 |
| `EVIDENCE_SUMMARY.md` | 변경 없음 | 질문별 판정 문단 개정 |
| `MEDICAL_KNOWLEDGE_BASE_KR.md` | 링크·절차만 | VERIFIED/LIMITED 표 갱신 |
| Founder packs / IR | 기존 허용 문장만 | 승격 claim만 인용 |

`clinical_validation=false` · Shadow · Path B는 문헌 새로고침만으로 바뀌지 않는다.

## 8. 창업자용 짧은 안내

- 검색을 했다고 해서 **새 논문 숫자로 병원·투자자 설명을 바꾸지 마세요.**
- “검토 중(CANDIDATE)”과 “원장에 오른 근거(VERIFIED)”를 말로 구분해 주세요.
- 철회·정정 알림이 오면 제품 문장을 쓰기 전에 Auditor 게이트를 먼저 요청하세요.

## 9. 변경 로그

| 날짜 (KST) | 내용 |
| --- | --- |
| 2026-09-06 | 최초 계획 — seed는 2026-09-02 원장 기준; FACT 자동 승격 없음 |
