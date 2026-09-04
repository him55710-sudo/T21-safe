# Technical and Repository Gates

**Date:** 2026-09-04 (KST)  
**Scope:** Governance proposal for Path B / RUO repository hygiene during Evidence-First M0 freeze  
**Tip HEAD:** `edff0f1`  
**Preference:** Document first. Optional minimal docs-only workflow only if tiny and path-filtered.

---

## 1. Branch protection proposal (`main`)

| Gate | Proposal | Rationale |
| --- | --- | --- |
| PR required | Yes — no direct commits to `main` | Auditability; freeze visibility |
| Force push | **Deny** on `main` (and release tags) | Tip/SHA integrity; obsolete SHA drift prevention |
| Deletion | Deny branch deletion of `main` | Safety |
| Required reviewers | ≥1 human (Founder or designated maintainer) for code; docs-only may use lighter rule if team agrees | Agents must not self-merge clinical/eng value changes |
| Status checks | See §2 — start with existing smoke where applicable; add docs path check only when ready | Do not block M0 docs on unrelated flaky benches |
| Linear history (optional) | Squash or rebase-merge OK; no force on `main` after merge | Keep tip readable |
| Signed commits (optional later) | Not required for M0 | Defer |

**Do not:** push directly to `main`, merge freeze-breakers (RII/threshold edits) without Founder unfreeze note.

---

## 2. Required checks (proposal)

### Near-term (document; wire gradually)

| Check | When required | Notes |
| --- | --- | --- |
| Existing Path B / proxy / MCP smokes | PRs touching `services/**`, `apps/**`, bench scripts | Already present under `.github/workflows/` — do not expand benches during freeze |
| Forbidden-claims / RUO scan (if already in repo) | UI/copy PRs | Backstop only (`PROHIBITED_CLAIMS.md`) |
| Docs path filter | PRs that **only** change `docs/**` | Prefer noop or markdown link lint; must not run heavy benches |

### Explicit non-goals during M0 freeze

- New PROXY HYP CI jobs
- Threshold/RII tuning gates that imply clinical acceptance
- Auto-merge bots on `main`

---

## 3. All-up CI scaffolding (proposal only)

1. **Path filters**  
   - `docs/**` → docs-only job  
   - `services/engine/**` → engine unit/smokes (unchanged set)  
   - MCP/apps → existing MCP workflows only when those paths change  

2. **Freeze-aware label**  
   - PRs changing `config.py` or `deterministic_index.py` numeric defaults require label `founder-unfreeze` + governance note linking `FREEZE_DECLARATION_M0.md`.

3. **Artifact**  
   - Every merge to `main` should record resulting `git rev-parse HEAD` in release/demo docs when tips move (post-unfreeze).

---

## 4. Docs-only workflow — decision for this PR

**Decision:** Document first; **no new workflow file in this commit**.

Rationale:

- Multiple smokes already exist; adding another workflow mid-freeze increases tip noise.
- M0 success is docs/governance completeness, not CI expansion.
- If added later, constraints: `paths: ['docs/**']` only; job = checkout + `git diff --check` or markdown link check; **no** engine/bench execution.

Suggested stub shape (do **not** apply until approved):

```yaml
# .github/workflows/docs-path-check.yml  (FUTURE — not added in M0 commit)
name: docs-path-check
on:
  pull_request:
    paths: ['docs/**']
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: noop docs marker
        run: test -d docs && echo "docs path OK"
```

---

## 5. Agent / PR operating rules (M0)

- Branch for this work: `grok/evidence-first-reset` → PR into `main`.
- Docs/governance only; **no** value edits in `services/engine/src/t21_engine/config.py` or `risk/deterministic_index.py`.
- Do not push `main`. Do not merge without human.
- Observation SHA `c6806e1` is obsolete; cite `edff0f1` until Founder sets a new freeze tip.

---

## 6. Acceptance for “gates landed”

| Criterion | M0 bar |
| --- | --- |
| This document merged via PR | Required |
| GitHub branch protection UI applied | Founder/admin action (tracked as M0 backlog issue) |
| Docs-only workflow file | Optional / deferred |

## 7. Current REPO_FACT baseline

- `REPO_FACT` (`edff0f1`, repository state supplied/checked for M0): `main` branch protection is absent.
- `REPO_FACT` (`edff0f1`, repository state supplied/checked for M0): tags, releases, and issues are empty.
- These absences are governance gaps; they are not evidence of approval, validation, or a release.
