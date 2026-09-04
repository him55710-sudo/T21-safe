# Freeze Declaration — M0 (Evidence-First)

**Declared:** 2026-09-04 (KST)  
**Freeze tip SHA:** `edff0f1abcf417729fd3029266d2c46e11b2b688` (`edff0f1`)  
**Obsolete observation SHA:** `c6806e1` — do not cite  
**Path:** B / RUO / Shadow / `clinical_validation=false`  
**Authority:** Founder unfreeze required to lift

Related: [`../founder/T21_REFOCUS_DECISION_KR.md`](../founder/T21_REFOCUS_DECISION_KR.md), [`../research/CLINICAL_RESEARCH_LOCK_V0.md`](../research/CLINICAL_RESEARCH_LOCK_V0.md), [`TECHNICAL_AND_REPOSITORY_GATES.md`](TECHNICAL_AND_REPOSITORY_GATES.md).

---

## 1. What is frozen

| Scope | Frozen? | Detail |
| --- | --- | --- |
| Eng tip / freeze-tip churn | **YES** | Tip pinned to `edff0f1` for docs and demos |
| `RiskConfig` / RII weights & bins | **YES** | `config.py` values — read-only |
| `deterministic_index.py` scoring constants | **YES** | Including hardcoded `10.0` BASELINE boundary |
| New PROXY benches / HYP expansions | **YES** | No new bench packs claiming clinical meaning |
| MCP tool/surface expansion | **YES** | Docs/onboarding OK; new tools/endpoints not |
| FACT / `clinical_validation` elevation | **YES** | Remains false |
| Dosing / closed-loop / alarm UX | **YES** (permanent prohibition under Path B) | See `PROHIBITED_CLAIMS.md` |
| Docs / governance / research lock | **NO** | Continues |
| M0 issue backlog tracking | **NO** | Continues |
| Existing Path B demo runbooks (docs) | **NO** | Text fixes OK; no tip-moving code |

---

## 2. What “frozen tip” means operationally

1. Agents and contributors **do not** open PRs whose purpose is RII tuning, threshold edits, or new PROXY HYP while this declaration is active.  
2. Any accidental diff to `config.py` / `deterministic_index.py` numerics is a freeze violation — revert.  
3. Meeting materials cite **`edff0f1`**, not `c6806e1` or intermediate tips unless Founder supersedes this file.  
4. PROXY results remain **engineering evidence** (ECG HR-event / SQI readiness) — **PROXY ≠ DS clinical validation**.

---

## 3. Unfreeze criteria (Founder)

Unfreeze is **not** automatic at day 30. Minimum package:

- Clinical Research Lock version with PI-reviewed narrowed options (fills still only by PI).  
- Provenance doc current.  
- Explicit Founder note: new tip SHA + what may change (e.g. docs-only vs allowed eng).  
- No FACT elevation implied by unfreeze alone.

---

## 4. Sign-off block

| Role | Status |
| --- | --- |
| Declaring agent / docs commit | Recorded via Evidence-First Refocus M0 PR |
| Founder acknowledgment | `PI_REQUIRED` / Founder action |
| PI acknowledgment of Lock table | `PI_REQUIRED` |

---

## 5. One-line freeze statement

**Until Founder unfreezes, T21 Safe Path B holds eng tip `edff0f1`: no RII/threshold/PROXY-bench/MCP-expansion tip churn; docs and Clinical Research Lock only.**
