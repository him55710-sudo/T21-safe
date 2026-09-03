# PROXY HYP-01/03/07 결과 팩 (Founder)

Path B · RUO · `clinical_validation=false` · PROXY ≠ DS  
MIT-BIH + Fantasia **로컬 fixture만**. BIDMC / Airway / Driver-map / PHI / 투약·closed-loop **없음**.

## 한 줄 요약

Founder 승인 PROXY Analysis Plan v0.1 벤치(HYP-01/03/07)가 `main`에 착륙했고, 원커맨드 러너가 JSON/MD 결과표를 만듭니다. 숫자는 **임상 claim이 아닙니다.** 임계값은 `PI_TO_DEFINE`.

## 랜딩 SHA

| CODEX | HYP | SHA | 역할 태그 |
| --- | --- | --- | --- |
| 101 | HYP-01 MIT-BIH abs/rel brady-def sensitivity | `af98247` | `PROXY_ECG_BENCHMARK` |
| 102 | HYP-03 Fantasia short-window HRV/LF-HF (LF/HF non-primary, RQ-004=HYPOTHESIS) | `6318771` | `PROXY_HRV_AGE_STABILITY` |
| 103 | HYP-07 Fantasia age-band HRV engine QA | `f0f7692` | `PROXY_HRV_AGE_STABILITY` |
| 104 | 원커맨드 러너 + JSON/MD 테이블 | `d0b3988` | — |
| 105 | CI smoke (fixture-only, no BIDMC) | `385b812` | — |

## 실행

```bash
make proxy-hyp-benches
# 또는
bash scripts/run_proxy_hyp_benches.sh /tmp/t21-proxy-hyp-benches
```

출력:

- `proxy-hyp-bench-report.json` — 전체 리포트 + FACT / INTERPRETATION / HYPOTHESIS
- `proxy-hyp-bench-results.md` — 요약 표

## 읽는 법 (게이트)

- `clinical_validation=false` 스탬프 확인
- 레이어 분리: FACT ≠ INTERPRETATION ≠ HYPOTHESIS
- HYP Claim은 `HUMAN_REVIEW_REQUIRED` 라벨 — 임상 사실 아님
- LF/HF는 **primary 아님** (HYP-03); RQ-004는 HYPOTHESIS/gap 유지
- age-band는 engine QA만 (HYP-07); RQ-003 causation 아님
- pooled instability score **없음**

## 인덱스 / Master

- Artifacts index: [`docs/benchmarks/ARTIFACTS_INDEX.md`](../benchmarks/ARTIFACTS_INDEX.md) § PROXY Analysis Plan v0.1
- Method Master (Notion): `P2E-METHOD-PROXY-PLAN-V01` CODEX_READY

## 금지

06b / BIDMC / Airway / Driver-map / PHI cloud / dosing / closed-loop / DS·peri-op 성능 claim.
