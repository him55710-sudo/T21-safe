# M0 Issue Backlog (Evidence-First)

**Date:** 2026-09-04 (KST)  
**Tip freeze:** `edff0f1`  
**Purpose:** Issue drafts M0-01..M0-15 when `gh milestone` may fail — this file is the source of truth until issues exist in GitHub.

**Default labels (suggested):** `m0`, `docs`, `governance`, `path-b`, `ruo`, `freeze`  
**Do not label as:** `clinical-validation`, `fact`, `rii-tuning` (out of freeze scope)

---

## M0-01 — Publish Freeze Declaration

- **Title:** M0: Record eng tip freeze at edff0f1  
- **Acceptance:** `docs/governance/FREEZE_DECLARATION_M0.md` merged; no docs cite `c6806e1` as current tip without obsolete marking.  
- **Labels:** `m0`, `governance`, `freeze`

## M0-02 — Founder Refocus Decision (KR)

- **Title:** M0: Founder-facing Evidence-First refocus decision  
- **Acceptance:** `docs/founder/T21_REFOCUS_DECISION_KR.md` states STOP/CONTINUE and PROXY ≠ DS.  
- **Labels:** `m0`, `docs`, `founder`

## M0-03 — Clinical Research Lock v0 table

- **Title:** M0: Clinical Research Lock v0 with PI_REQUIRED rows  
- **Acceptance:** Decision table exists; clinical cells are PI_REQUIRED/PI_TO_DEFINE with options; no invented fills.  
- **Labels:** `m0`, `research`, `pi-required`

## M0-04 — Threshold/weight provenance inventory

- **Title:** M0: Provenance for config.py + deterministic_index.py  
- **Acceptance:** `docs/model/THRESHOLD_WEIGHT_PROVENANCE.md` lists symbols with file:line and classes; **zero** code value changes.  
- **Labels:** `m0`, `docs`, `model`

## M0-05 — 90-day evidence roadmap (KR)

- **Title:** M0: 0–30 / 31–60 / 61–90 evidence milestones  
- **Acceptance:** `docs/roadmap/90_DAY_EVIDENCE_ROADMAP_KR.md` prioritizes M0; no freeze-violating feature promises.  
- **Labels:** `m0`, `docs`, `roadmap`

## M0-06 — Repository gates proposal

- **Title:** M0: Branch protection + required checks proposal  
- **Acceptance:** `docs/governance/TECHNICAL_AND_REPOSITORY_GATES.md` documents PR-required, no force-push `main`, docs-first CI stance.  
- **Labels:** `m0`, `governance`, `ci`

## M0-07 — Apply GitHub branch protection (human)

- **Title:** M0: Admin applies branch protection on main  
- **Acceptance:** `main` requires PR; force-push denied; screenshot or settings note linked in PR comment.  
- **Labels:** `m0`, `governance`, `founder-action`  
- **Blocked on:** repo admin rights

## M0-08 — Doc dedup map + README pointers

- **Title:** M0: Dedup map keep/merge/archive  
- **Acceptance:** `DOC_DEDUP_MAP.md` present; founder README links Refocus + Freeze (follow-up edit OK).  
- **Labels:** `m0`, `docs`

## M0-09 — PI session #1 — endpoint & population options

- **Title:** M0: PI narrows primary endpoint family + population options  
- **Acceptance:** Lock table amendment note (v0.1 draft) records chosen option letters or explicit defer; still no numeric invention by agents.  
- **Labels:** `m0`, `pi-required`, `research`  
- **Blocked on:** PI availability

## M0-10 — PI session #1b — bradycardia abs/rel + windowing

- **Title:** M0: PI options for abs/rel brady and windowing  
- **Acceptance:** Lock rows updated; eng `relative_hr_decline_pct` / windows remain untouched in code.  
- **Labels:** `m0`, `pi-required`, `freeze`

## M0-11 — Obsolete SHA scrub checklist

- **Title:** M0: Scrub c6806e1 from active founder/meeting docs  
- **Acceptance:** Search shows `c6806e1` only as obsolete mention or zero hits in active talk tracks; current tip `edff0f1`.  
- **Labels:** `m0`, `docs`

## M0-12 — PROXY claim boundary reaffirmation

- **Title:** M0: Reaffirm PROXY ≠ DS; no FACT from fixtures  
- **Acceptance:** Meeting one-pager + Refocus + Lock agree: ECG HR-event/SQI only; `clinical_validation=false`.  
- **Labels:** `m0`, `safety`, `ruo`

## M0-13 — BIDMC usability gate checklist (docs only)

- **Title:** M0: Document BIDMC do-not-run usability gate  
- **Acceptance:** Checklist exists under research or Lock notes; no BIDMC bench code added.  
- **Labels:** `m0`, `research`, `docs`

## M0-14 — Freeze-breaker PR labeling rule

- **Title:** M0: Document founder-unfreeze label for config/RII PRs  
- **Acceptance:** Gates doc describes label; team agrees PRs touching RiskConfig numerics need Founder note.  
- **Labels:** `m0`, `governance`

## M0-15 — M0 exit package for Founder

- **Title:** M0: Assemble unfreeze review package (docs only)  
- **Acceptance:** Single checklist: Freeze SHA, Lock version, provenance, gates, backlog Done/Blocked, 30-day recommendation; Founder decides unfreeze **or** extend freeze.  
- **Labels:** `m0`, `founder-action`, `governance`

---

## Tracking tips

- If `gh issue create` / milestone works later, mirror titles above and link issue URLs back into this file.  
- Closing an issue without acceptance evidence is not Done.  
- Code changes to RII/thresholds close **nothing** here — they are freeze violations unless Founder unfreezes first.
