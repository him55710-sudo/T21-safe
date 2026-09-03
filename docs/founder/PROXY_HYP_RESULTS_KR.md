# PROXY HYP-01/03/07 결과 팩 (Founder)

## Auditor DSCS labels (먼저 읽기)

Notion HANDOFF: `https://app.notion.com/p/3d09631d743b81bcbfd6f4d0fa78522a`

| HYP | Auditor label | 의미 (엔지니어링만) |
| --- | --- | --- |
| HYP-01 | **PARTIALLY_SUPPORTED** | HR-event / SQI PROXY 범위에서만 부분 지지 — **clinical FACT 아님** |
| HYP-03 | **STRETCH if positive PROXY** / **OK as neg-control-QA** | 양성 PROXY로 과장 금지; negative-control / methods QA로만 OK |
| HYP-07 | **STRETCH if positive PROXY** / **OK as neg-control-QA** | age-band engine QA만; 양성 해석 STRETCH |
| RQ-004 | **HYPOTHESIS** | resting HRV → peri-op = gap — FACT 승격 금지 |
| LF/HF | **not primary**; **&lt;180s withheld** | Task Force 게이트 미만 창에서 withhold |
| Age metadata | **UNAVAILABLE** / `PI_TO_DEFINE` | synthetic fixture에 age band 없음 |
| v0.1 claim collapse | **ECG HR-event / SQI만** | broader autonomic/age/HRV “positive PROXY”로 확대 금지 |
| Airway + BIDMC | **do-not-run** | 이 트랙에서 실행·확장 금지 |
| `clinical_validation` | **`false`** | 전 산출물 |
| FACT | **없음** | Auditor/Founder pack에 clinical FACT 선언 없음 |

## METHODS_CRITIQUE (이어서 읽기)

이 문서는 **엔지니어링 PROXY 벤치 결과 포인터**입니다. 임상 성능·DS·마취 성과 claim이 **아닙니다.** Auditor DSCS 라벨이 결과표·SHA보다 우선합니다.

| 게이트 | 상태 |
| --- | --- |
| PROXY ≠ DS | **강제** — MIT-BIH/Fantasia ≠ Down syndrome peri-op 데이터 |
| `clinical_validation` | **`false`** (모든 JSON/MD 스탬프) |
| 임계값 | **`PI_TO_DEFINE`** — abs/rel HR, window, age-band, stability tolerance 하드코딩 금지 |
| RQ-004 (resting HRV → peri-op) | **`HYPOTHESIS` / gap만** — FACT로 승격 금지 |
| LF/HF | **primary endpoint 아님** (HYP-03 negative-control / methods stress) |
| RQ-003 (age HRV → induction) | **causation 아님** — HYP-07는 engine QA만 |
| Pooled instability score | **없음** |

### 방법 한계 (selection / confounding / leakage)

- **Selection:** 공개 PhysioNet ambulatory/resting fixture(및 synthetic fixture-equivalent)만 사용. OR/ICU/DS 표본이 아님 → 일반화·채택도 해석 금지.
- **Confounding:** Fantasia age/resp·MIT-BIH arrhythmia 맥락이 마취·약물·수술 자극과 얽히지 않음. residual peri-op confounding을 이 벤치로 해소할 수 없음.
- **Leakage:** 로컬 fixture·observe-only Path B. PHI/파형 클라우드 반출 없음. “성능 숫자”를 임상 lockbox/test에 재사용하지 말 것. Dataset Master 행은 experiment-approved가 아님 (PROXY fixture only).
- **레이어:** FACT ≠ INTERPRETATION ≠ HYPOTHESIS. `HUMAN_REVIEW_REQUIRED` HYP Claim은 **라벨**이지 임상 사실이 아님.

### 금지

06b / BIDMC / Airway / Driver-map / PHI cloud / dosing / closed-loop / DS·peri-op 성능 claim / LF/HF 실시간 바이오마커 주장.

---

Path B · RUO · MIT-BIH + Fantasia **로컬 fixture만**.

## Freeze tip

`v2.1-proxy-hyp-benches` (`2026-09-04 UTC`) — CODEX-101–109; wording patch CODEX-111 (Auditor DSCS labels).

## 한 줄 요약

Founder 승인 PROXY Analysis Plan v0.1 벤치(HYP-01/03/07)가 `main`에 착륙했고, 원커맨드 러너가 JSON/MD 결과표를 만듭니다. 위 **METHODS_CRITIQUE**를 결과표보다 우선합니다.

## 랜딩 SHA

| CODEX | HYP | SHA | 역할 태그 |
| --- | --- | --- | --- |
| 101 | HYP-01 MIT-BIH abs/rel brady-def sensitivity | `af98247` | `PROXY_ECG_BENCHMARK` |
| 102 | HYP-03 Fantasia short-window HRV/LF-HF (LF/HF non-primary, RQ-004=HYPOTHESIS) | `6318771` | `PROXY_HRV_AGE_STABILITY` |
| 103 | HYP-07 Fantasia age-band HRV engine QA | `f0f7692` | `PROXY_HRV_AGE_STABILITY` |
| 104 | 원커맨드 러너 + JSON/MD 테이블 | `d0b3988` | — |
| 105 | CI smoke (fixture-only, no BIDMC) | `385b812` | — |
| 106 | ARTIFACTS_INDEX + founder KR results pack | `b710db6` | — |

## 실행

```bash
make proxy-hyp-benches
# 또는
bash scripts/run_proxy_hyp_benches.sh /tmp/t21-proxy-hyp-benches
```

출력:

- `proxy-hyp-bench-report.json` — 전체 리포트 + FACT / INTERPRETATION / HYPOTHESIS
- `proxy-hyp-bench-results.md` — 요약 표

## 결과 읽는 법 (게이트 재확인)

- Auditor: HYP-01 **PARTIALLY_SUPPORTED** (HR-event/SQI); HYP-03/07 **STRETCH**/neg-control-QA — **no FACT**
- Airway+BIDMC **do-not-run**; v0.1 claims collapsed to ECG HR-event/SQI
- LF/HF **&lt;180s withheld**; age metadata **UNAVAILABLE**
- `clinical_validation=false` 스탬프 확인
- 레이어 분리: FACT ≠ INTERPRETATION ≠ HYPOTHESIS
- HYP Claim은 `HUMAN_REVIEW_REQUIRED` 라벨 — 임상 사실 아님
- LF/HF는 **primary 아님** (HYP-03); RQ-004는 HYPOTHESIS/gap 유지
- age-band는 engine QA만 (HYP-07); RQ-003 causation 아님
- pooled instability score **없음**

## 인덱스 / Master

- Artifacts index: [`docs/benchmarks/ARTIFACTS_INDEX.md`](../benchmarks/ARTIFACTS_INDEX.md) § PROXY Analysis Plan v0.1
- Method Master (Notion): `P2E-METHOD-PROXY-PLAN-V01` CODEX_READY
