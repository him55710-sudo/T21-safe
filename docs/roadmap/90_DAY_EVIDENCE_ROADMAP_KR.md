# 90일 Evidence-First 로드맵 (KR)

**기준일:** 2026-09-04 (KST)  
**Eng tip HEAD:** `edff0f1` (freeze — Founder unfreeze 전 tip churn 금지)  
**경로:** Path B / RUO / Shadow / `clinical_validation=false`  
**원칙:** M0 우선 · 임상 fill 발명 금지 · PROXY ≠ DS · 코드 feature/RII 튜닝 약속 없음

근거: [`../founder/T21_REFOCUS_DECISION_KR.md`](../founder/T21_REFOCUS_DECISION_KR.md), [`../research/CLINICAL_RESEARCH_LOCK_V0.md`](../research/CLINICAL_RESEARCH_LOCK_V0.md), [`../governance/FREEZE_DECLARATION_M0.md`](../governance/FREEZE_DECLARATION_M0.md), [`../governance/M0_ISSUE_BACKLOG.md`](../governance/M0_ISSUE_BACKLOG.md).

---

## Days 0–30 — M0 Evidence Lock (지금)

| 마일스톤 | 증거 산출물 | 비고 |
| --- | --- | --- |
| M0-A Freeze 선언 고정 | `FREEZE_DECLARATION_M0.md` + tip SHA `edff0f1` | tip/RII/PROXY bench STOP |
| M0-B Clinical Research Lock | `CLINICAL_RESEARCH_LOCK_V0.md` PI 회의 1회 이상 | Options만 좁힘; 값 fill 금지 |
| M0-C Provenance | `THRESHOLD_WEIGHT_PROVENANCE.md` 읽기 전용 추적 | config/deterministic_index **변경 없음** |
| M0-D Doc dedup | `DOC_DEDUP_MAP.md` keep/merge/archive | Founder/research 중복 정리 |
| M0-E Repo gates 제안 | `TECHNICAL_AND_REPOSITORY_GATES.md` | branch protection 제안; 강제 푸시 금지 |
| M0-F Issue backlog | `M0_ISSUE_BACKLOG.md` M0-01..15 | gh milestone 실패 시 문서가 소스 |

**하지 않음 (0–30):** 새 PROXY HYP, MCP 확장, RII weight 변경, FACT, dosing/closed-loop, freeze tip 남발.

**30일 한 줄:** PI와 endpoint/population/brady abs·rel/windowing Options를 회의로 축소하고 tip SHA는 `edff0f1`에 고정한다.

---

## Days 31–60 — Protocol & Data Readiness (코드 tip 여전히 freeze 기본)

| 마일스톤 | 증거 산출물 | 비고 |
| --- | --- | --- |
| Lock v0.1 | Research Lock 개정 (옵션 축소 기록) | 여전히 PI_REQUIRED 잔여 허용 |
| Protocol 정렬 | `FIRST_STUDY_PROTOCOL_KR` / IRB draft ↔ Lock 교차 | 임상 발명 fill 없이 교차표만 |
| Data gap | `DATA_GAP_MAP` / hospital request spec 갱신 | Path B DUA/IRB 전제; 수집 약속 ≠ tip |
| BIDMC usability gate 문서 | go/no-go 체크리스트만 | do-not-run 유지 가능 |
| Human-review pack | Founder 미팅 one-pager를 Lock v0.1에 재정렬 | PROXY claim 범위 유지 (HR-event/SQI) |

**하지 않음:** Founder unfreeze 없이 eng tip 이동, threshold 코드 패치, clinical_validation 플래그 변경.

---

## Days 61–90 — Silent Evidence Package (Shadow 준비 문서)

| 마일스톤 | 증거 산출물 | 비고 |
| --- | --- | --- |
| SAP 초안 정합 | `STATISTICAL_ANALYSIS_PLAN` ↔ Lock | threshold는 test에서 조정 금지 원칙 재확인 |
| Phase gate 재확인 | `VALIDATION_ROADMAP` Phase 0→1 진입 조건 | 공개 데이터 ≠ DS 성능 |
| Shadow isolation 체크 | 임상 비노출·RUO 문구·금지 claim 스캔 정책 | 코드 기능 신설 약속 아님 |
| Founder unfreeze 심사 패키지 | tip SHA, Lock 버전, provenance, gates, backlog Done 목록 | **Unfreeze는 Founder 전권** |
| (조건부) 최소 docs CI | docs path filter noop/링크 체크 | feature CI 확장 아님 |

**금지 유지:** FACT elevation, dosing, closed-loop, PROXY→DS 일반화, RII를 확률/알람으로 표기.

---

## 성공 정의 (90일)

- Clinical Research Lock이 PI 검토 흔적과 함께 versioned.
- Tip 기준 SHA가 문서 전역에서 `edff0f1`(또는 Founder 지정 freeze)로 일치; `c6806e1` 잔존 0.
- `config.py` / `deterministic_index.py` 값이 freeze 기간 동안 변경되지 않음.
- M0 backlog 이슈가 추적 가능(문서 또는 gh).
- PR/branch protection 제안이 governance에 기록됨.

## 실패 모드 (즉시 중단 신호)

- tip churn 재개 / RII 튜닝 PR
- PROXY 결과를 DS 임상 검증처럼 미팅에서 사용
- PI_REQUIRED 칸을 에이전트가 숫자로 “채워 넣음”
