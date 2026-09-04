# M0 Completion Checklist

**Date:** 2026-09-04 (KST)<br>
**Freeze tip:** `edff0f1`<br>
**Path:** B / RUO / Shadow / `clinical_validation=false`<br>
**Rule:** Docs/governance gates only — no RII / PROXY / threshold / MCP feature expansion.

Related: [`FREEZE_DECLARATION_M0.md`](FREEZE_DECLARATION_M0.md) · [`TECHNICAL_AND_REPOSITORY_GATES.md`](TECHNICAL_AND_REPOSITORY_GATES.md) · [`REQUIRED_CI_CHECK_HOWTO.md`](REQUIRED_CI_CHECK_HOWTO.md) · [`M0_ISSUE_BACKLOG.md`](M0_ISSUE_BACKLOG.md) · [`../research/CLINICAL_RESEARCH_LOCK_V0.md`](../research/CLINICAL_RESEARCH_LOCK_V0.md)

---

## DONE — M0-A / M0-B / M0-C items landed (repo)

| Item | Evidence | Notes |
| --- | --- | --- |
| M0-A all-up workflow | [`.github/workflows/all-up-required.yml`](../../.github/workflows/all-up-required.yml) | Docs paths + unit smokes; always reports on PR/`main` |
| M0-A gate docs | [`TECHNICAL_AND_REPOSITORY_GATES.md`](TECHNICAL_AND_REPOSITORY_GATES.md), evidence set in §8 | Signal validity, security matrix, clinician protocol, PI pack, release tags, RII display HF options |
| M0-A freeze declaration | [`FREEZE_DECLARATION_M0.md`](FREEZE_DECLARATION_M0.md) | Tip `edff0f1`; obsolete `c6806e1` |
| M0-B hospital aggregate feasibility | [`../business/HOSPITAL_AGGREGATE_FEASIBILITY_QUERY_KR.md`](../business/HOSPITAL_AGGREGATE_FEASIBILITY_QUERY_KR.md) | Founder-facing query; agents do not email sites |
| M0-B schema/clock pilot acceptance | [`../research/SCHEMA_CLOCK_PILOT_ACCEPTANCE.md`](../research/SCHEMA_CLOCK_PILOT_ACCEPTANCE.md) | Eng vs SITE_REQUIRED vs PI_REQUIRED classes |
| M0-B hospital data request spec | [`../research/HOSPITAL_DATA_REQUEST_SPEC.md`](../research/HOSPITAL_DATA_REQUEST_SPEC.md) | Extract contract draft |
| M0-C forbidden-claim scan job | workflow job `all-up-required / forbidden-claim scan` | Pure Python scan; does **not** run `apps/web/scripts/check-forbidden.mjs` |
| M0-C fault-injection plan | [`../research/FAULT_INJECTION_MIXED_RATE_PLAN.md`](../research/FAULT_INJECTION_MIXED_RATE_PLAN.md) | PLAN only + pure-Python alignment unit tests |
| M0-C required-check how-to | [`REQUIRED_CI_CHECK_HOWTO.md`](REQUIRED_CI_CHECK_HOWTO.md) | Admin procedure + observed API state |
| M0 backlog draft | [`M0_ISSUE_BACKLOG.md`](M0_ISSUE_BACKLOG.md) | M0-01..M0-15 tracking until GitHub issues exist |

---

## STILL PI / SITE — Lock table (`CLINICAL_RESEARCH_LOCK_V0`)

Clinical cells remain `PI_REQUIRED` / `PI_TO_DEFINE`. Agents must **not** invent fills. Source: [`../research/CLINICAL_RESEARCH_LOCK_V0.md`](../research/CLINICAL_RESEARCH_LOCK_V0.md) Decision table.

| Decision (Lock) | Status | Who |
| --- | --- | --- |
| Primary endpoint family | `PI_REQUIRED` | PI |
| Study population | `PI_REQUIRED` | PI |
| Windowing / observation context | `PI_REQUIRED` | PI (eng defaults stay ENGINEERING_DEFAULT) |
| Bradycardia — absolute threshold | `PI_REQUIRED` / `PI_TO_DEFINE` | PI |
| Bradycardia — relative threshold | `PI_REQUIRED` | PI |
| HRV role | `PI_REQUIRED` | PI |
| SpO2 / Airway context | `PI_REQUIRED` | PI (+ BIDMC usability) |
| BIDMC (and similar public PPG/resp sets) | `PI_REQUIRED` | PI / research gate |
| FACT elevation | `PI_REQUIRED` | Founder + PI; remains false under Path B |
| Hypotension MAP / duration | `PI_REQUIRED` | PI |
| RII watch/elevated/high bins | `PI_REQUIRED` | PI / freeze |
| DS_HYPOTHESIS_MODE / PROXY labeling | Lock reminder | Already constrained — not DS-calibrated validation |
| Timezone / NTP / export clock / DUA transfer | `SITE_REQUIRED` | Site IT / honest broker (see schema/clock pilot) |
| Branch protection: required status checks on `main` | Human / Founder (M0-07) | See how-to — green workflow alone ≠ Done |

### 한국어 요약 (PI/SITE 잔여)

- **PI:** 일차 평가변수·인구집단·서맥 절대/상대 역치·HRV·SpO2/기도·FACT 승격 등 Lock 표의 임상 셀은 여전히 PI 결정 대기.
- **SITE:** 시간대/NTP, export 경로, 비식별, DUA/IRB, 소표본 파일럿 전달은 기관 담당.
- **저장소:** tip `edff0f1` 동결 유지. RII/PROXY/threshold/MCP 기능 확장 금지. 필수 CI 체크 UI 적용은 Founder/admin(M0-07).

---

## Exit package pointer

When Founder reviews unfreeze vs extend-freeze, assemble: Freeze SHA, Lock version, provenance, gates, this checklist Done vs PI/SITE, and 30-day recommendation ([`M0_ISSUE_BACKLOG.md`](M0_ISSUE_BACKLOG.md) M0-15).
