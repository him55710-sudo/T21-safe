# T21 Research Node — 한 장 소개 (Founder / PI용 초안)

**문서 상태:** DRAFT · Founder 검토용 · 이메일 미발송  
**경로 제안:** `docs/business/research-node-one-pager.md`  
**작성:** T21 제품·사업 분석가 · 2026-09-03 KST  
**근거 범위:** Constitution v0.1 · Business & Research Plan §1–2 · PROHIBITED_CLAIMS · 공개 문헌 PMID만  
**금지:** PHI · 파형 · DUA 원본 · 병원 접촉/이메일 (Founder 승인 전)

---

## 한 문장

**T21 Research Node**는 다운증후군(T21) 환자의 마취·진정 **과거·연구용 생체신호를 병원 안에서** 정리·품질검사·재현 가능하게 분석하기 위한 **로컬 연구 소프트웨어**입니다. 실시간 임상 경보·예측 의료기기가 아닙니다.

---

## What (하는 일)

| 항목 | 내용 |
| --- | --- |
| 위치 | 병원/연구단 **내부** 워크스테이션 또는 승인 LAN |
| 입력 | ECG, PPG, BP, SpO2, EtCO2/호흡, (가용 시) EEG/BIS, 마취·시술·약물·사건 **시간 스탬프** |
| 핵심 기능 | 시계 정렬 · 신호 품질(SQI) · 누락/잡음 리포트 · 단계(phase) 타임라인 · 연구용 export |
| 산출 | 비식별 표·통계·품질 보고서 · (승인 후) 논문용 요약 — **원자료는 병원 소유** |
| 제품 사다리 1단계 | Research Node → Study Console → Shadow → (근거 후) 임상 제품 검토 |

---

## Not-what (하지 않는 일)

- 서맥·저혈압·심정지 **예측** 또는 “조기 진단”
- 합병증 **예방** 주장
- 투약·용량·atropine/propofol 등 **처치 권고**
- 펌프·ventilator·EHR **제어/closed-loop**
- “이 소프트웨어가 있으면 일반의원에서도 DS 마취가 안전해진다” 주장
- 공개 non-DS 데이터 성능을 **DS 임상 검증**으로 포장

---

## 지금 가능한 소개 문장 (권장)

> “다운증후군 마취·진정 생체신호 연구를 **재현 가능하게** 만드는 **연구용·로컬** 소프트웨어입니다. 원자료는 병원이 소유하고, T21은 정리·품질·분석 도구를 제공합니다.”

## 절대 쓰지 말 문장

> “AI가 DS 마취 위험을 예측합니다 / 사고를 예방합니다 / 서맥을 조기에 진단합니다.”

(근거: `docs/safety/PROHIBITED_CLAIMS.md`, Constitution §3)

---

## 왜 먼저 Research Node인가

1. 공개 저장소 기준: 기술 데모는 가능하나 **DS 병원 파형·사건 정답표·학습 모델·임상 성능 검증은 없음** (계획서 평가).
2. 첫 질문은 예측이 아니라 **“자료가 있고, 패턴을 믿을 수 있게 볼 수 있는가?”**.
3. 기존 모니터가 이미 HR/SpO2를 보여주므로, **서맥 재알림만**으로는 연구·구매 이유가 약함.

---

## PI_TO_DEFINE (임상·기관)

- [ ] 우선 환경: 소아 vs 성인 vs 혼재 · OR vs 진정 · 치과마취 비중 — `PI_TO_DEFINE`
- [ ] 첫 공동연구 PI·기관 — `PI_TO_DEFINE` (접촉은 Founder만)
- [ ] IRB/waiver 경로·동의 범위 — `PI_TO_DEFINE`

---

## 인용 (공개)

- Constitution / Path B: Notion `T21 Safe Project Constitution v0.1`
- 금지 주장: repo `docs/safety/PROHIBITED_CLAIMS.md`
- 제품 사다리: Business & Research Plan §2-1 (2026-09-03)
