# Doc Dedup Map (Founder / Research / Governance)

**Date:** 2026-09-04 (KST)  
**Method:** `ls docs/**` inventory + role overlap judgment  
**Goal:** keep / merge / archive guidance — **no mass deletes in M0**; mark intent only.

Tip HEAD: `edff0f1`. Path B / RUO / Shadow.

---

## Legend

| Action | Meaning |
| --- | --- |
| **KEEP** | Canonical for its role; update in place |
| **MERGE** | Fold content into canonical; leave stub or pointer later |
| **ARCHIVE** | Historical; do not expand; point readers to canonical |
| **SUPERSEDE** | Replaced by Evidence-First M0 docs for decision-making |

---

## Founder-facing (KR)

| Path | Action | Notes |
| --- | --- | --- |
| `docs/founder/T21_REFOCUS_DECISION_KR.md` | **KEEP** (new canonical decision) | Why freeze; STOP/CONTINUE |
| `docs/founder/MEETING_ONEPAGER_PROXY_v0.1_KR.md` | **KEEP** (talk track) | PROXY scope only; update tip refs away from obsolete SHA when editing |
| `docs/founder/PROXY_HYP_RESULTS_KR.md` | **KEEP** | Engineering results pack; not clinical |
| `docs/founder/README.md` | **KEEP** | Index — should link Refocus + freeze docs |
| `docs/founder/MCP_ONBOARDING_KR.md` | **KEEP** | DX |
| `docs/founder/DUAL_MCP_TROUBLESHOOTING_KR.md` | **KEEP** | DX |
| `docs/founder/HOSPITAL_DEMO_RUNBOOK_KR.md` | **KEEP** | Demo ops |
| `docs/founder/HOSPITAL_DEMO_ONBOARDING_KR.md` | **MERGE** candidate into runbook later | Overlap with runbook/onboarding |
| `docs/founder/RESEARCH_NODE_DEMO_CHECKLIST_KR.md` | **KEEP** | Checklist |
| `docs/founder/EXPORT_MANIFEST_PHI_FALSE_KR.md` | **KEEP** | Overlaps business one-pager — keep KR founder copy |
| `docs/founder/hospital-demo-showcard.example.*` | **KEEP** | Examples |

---

## Research

| Path | Action | Notes |
| --- | --- | --- |
| `docs/research/CLINICAL_RESEARCH_LOCK_V0.md` | **KEEP** (new canonical lock) | PI_REQUIRED table |
| `docs/research/RESEARCH_PRD.md` | **KEEP** | Product research requirements |
| `docs/research/CLINICAL_QUESTIONS.md` | **KEEP** | CQ map; Lock references families |
| `docs/research/PICOTS.md` | **KEEP** | Align to Lock in 31–60d |
| `docs/research/VALIDATION_ROADMAP.md` | **KEEP** | Phase gates; roadmap KR is evidence calendar not replacement |
| `docs/research/FIRST_STUDY_PROTOCOL_KR.md` | **KEEP** | Protocol draft |
| `docs/research/IRB_PROTOCOL_DRAFT.md` | **KEEP** | |
| `docs/research/STATISTICAL_ANALYSIS_PLAN.md` | **KEEP** | |
| `docs/research/LABELING_PROTOCOL.md` | **KEEP** | |
| `docs/research/EVIDENCE_SUMMARY.md` + `EVIDENCE_LEDGER.csv` | **KEEP** | Ledger of claims/evidence |
| `docs/research/DATA_GAP_MAP.md` | **KEEP** | |
| `docs/research/DATASET_PRIORITY_MATRIX.md` | **KEEP** | |
| `docs/research/HOSPITAL_DATA_REQUEST_SPEC.md` | **KEEP** | |
| `docs/research/ASSUMPTIONS.md` | **KEEP** | Mark PRODUCT_ASSUMPTION vs PI_REQUIRED |
| `docs/research/RESEARCH_REVIEW_BOARD.md` | **KEEP** | Process |
| `docs/research/COMPETITOR_REFERENCE_PATTERNS.md` | **ARCHIVE** candidate | Low priority during freeze |
| `docs/research/HANDOFF_SESSION1.md` | **ARCHIVE** | Session notes; do not treat as lock |

---

## Roadmap / Governance / Model (M0)

| Path | Action | Notes |
| --- | --- | --- |
| `docs/roadmap/90_DAY_EVIDENCE_ROADMAP_KR.md` | **KEEP** | Evidence calendar; does not replace VALIDATION_ROADMAP phases |
| `docs/governance/FREEZE_DECLARATION_M0.md` | **KEEP** | Tip freeze |
| `docs/governance/TECHNICAL_AND_REPOSITORY_GATES.md` | **KEEP** | Branch protection proposal |
| `docs/governance/DOC_DEDUP_MAP.md` | **KEEP** | This file |
| `docs/governance/M0_ISSUE_BACKLOG.md` | **KEEP** | Issues if gh milestone fails |
| `docs/model/THRESHOLD_WEIGHT_PROVENANCE.md` | **KEEP** | Complements MODEL_AUDIT / FEATURE_TRACEABILITY |
| `docs/model/MODEL_AUDIT.md` | **KEEP** | Broader audit |
| `docs/model/FEATURE_TRACEABILITY_MATRIX.md` | **KEEP** | |
| `docs/model/FAILURE_MODES.md` | **KEEP** | |

---

## Safety / Regulatory / Business (pointer rules)

| Path | Action | Notes |
| --- | --- | --- |
| `docs/safety/PROHIBITED_CLAIMS.md` | **KEEP** (hard boundary) | All founder decks must defer |
| `docs/safety/CLINICAL_SAFETY_BOUNDARIES.md` | **KEEP** | |
| `docs/regulatory/INTENDED_USE_DRAFT.md` | **KEEP** | RUO intended use |
| `docs/business/*one-pager*` | **KEEP** | Partner-facing; must not outclaim meeting one-pager |

---

## Overlap resolutions (M0)

1. **Decision narrative:** `T21_REFOCUS_DECISION_KR` **SUPERSEDES** ad-hoc tip freeze notes in README footers until README is edited to point here.  
2. **Clinical parameter choices:** Lock table **SUPERSEDES** informal `PI_TO_DEFINE` mentions for tracking — meeting one-pager remains the **spoken** PROXY boundary.  
3. **90-day KR roadmap vs VALIDATION_ROADMAP:** complementary — calendar vs phase science gates; do not merge files yet.  
4. **Hospital demo onboarding vs runbook:** schedule MERGE after freeze; both KEEP for now.  
5. **Obsolete SHA `c6806e1`:** strip on next touch of any doc that still cites it; prefer `edff0f1`.

---

## Explicit non-actions in M0

- No bulk deletion.  
- No rewriting RESEARCH_PRD clinical fills.  
- No moving PROXY results into “validation” folders.
