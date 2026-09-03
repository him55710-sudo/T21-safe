# T21 Safe — 미팅용 한 장 (PROXY v0.1)

**일자:** 2026-09-04 (KST)
**성격:** Path B / RUO / observe-only · **임상 검증 아님** · **PROXY ≠ 다운증후군(DS)**
**근거:** Auditor 게이트 MATCH · `HUMAN_REVIEW_REQUIRED` · pack `e374856` · freeze `v2.2-proxy-hyp-guards`

## 한 줄 요약
공개 ECG 데이터(MIT-BIH·Fantasia)로 **엔진이 돌아가는지**를 점검한 연구용 PROXY 벤치입니다.
**미팅에서 말할 수 있는 것**은 ECG **심박 사건 정의·신호품질(SQI) 준비도**뿐이고, **환자·마취·예측 성능 주장은 하지 않습니다.**

## 허용 문장 (이 범위만)
- “공개 ECG로 **심박 사건 정의와 SQI 파이프라인**을 로컬에서 돌리는 단계입니다.”
- “MIT-BIH 스타일 fixture에서 하네스는 PASS입니다. **절대/상대 서맥 정의의 일치도는 임계값이 정해지기 전이라 아직 없습니다** (`PI_TO_DEFINE`).”
- “결과는 **엔지니어링 증거**이며 `clinical_validation=false`입니다.”
**부분 지지 라벨:** HYP-01 = **PARTIALLY_SUPPORTED** (HR-event / SQI only)

## 말하지 말 것 (STRETCH / BLOCK)
| 주제 | 라벨 | 이유 |
|---|---|---|
| HRV를 peri-op 불안정 지표로 | **STRETCH** | 양성 PROXY 금지. 음성대조·QA만. RQ-004 HYPOTHESIS. |
| 연령대 자율신경 / sevo 기전 | **STRETCH / BLOCK** | 나이 메타데이터 없음. RQ-003 인과 아님. |
| DS 발생률·병원 FAR·lead-time | **METHOD BLOCK** | PROXY fixture ≠ DS 마취 데이터. |
| Airway / SpO2 / BIDMC | **do-not-run** | BIDMC usability 미평가. |
| FACT / 임상 검증 | **금지** | Fixture PASS ≠ Master FACT. |

## 숫자 (fixture smoke — 발명 없음)
- HYP-01: PASS · synthetic-equivalent · abs/rel=`PI_TO_DEFINE` · concordance=null
- HYP-03: PASS · 초단기 time-domain · LF/HF withheld (<180s, primary=false)
- HYP-07: PASS · 3-record recompute exact · age=UNAVAILABLE
N=`PI_TO_DEFINE` (smoke ≠ power).

## 방법론 한계 (미팅에서 먼저)
1. Selection: PhysioNet ≠ 소아 DS OR
2. Confounding: 마취·기도·CHD·OSA 없음
3. Endpoints: HRV 양성 바이오마커 금지
4. Leakage: fixture→임상 lockbox 금지
벤치 유지, 주장만 접음. 허용 claim=ECG HR-event/SQI.

## Eng 상태
101–115 · freeze v2.1 / v2.2 · partner zip/MCP/demo pointers · no PI/mail by agents

## 다음
PI_TO_DEFINE thresholds · BIDMC gate later · Track A Founder-only
