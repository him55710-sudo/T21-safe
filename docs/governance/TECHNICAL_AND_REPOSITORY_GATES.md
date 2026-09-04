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

## 4. All-up required workflow — M0-A decision

**Decision:** Add one stable, always-reporting required workflow in M0-A.

The workflow performs documentation path/link and whitespace checks plus a small reuse of existing secret-free unit smokes. It does not run new PROXY benches, access governed data, change clinical/model values, or require repository secrets. Keeping it unfiltered at the workflow trigger level ensures a required status is reported for every PR; path-sensitive validation remains inside its jobs.

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
| Docs-only / all-up workflow file | **Present** — `.github/workflows/all-up-required.yml` (M0-A) |
| Required status check wired in branch protection | **Founder/admin** — see §9 (not yet enabled) |

## 7. Current REPO_FACT baseline

Historical (freeze tip `edff0f1` M0 observation): branch protection / tags / releases / issues were empty at declaration time.

**Known current state (checked 2026-09-04 KST via GitHub API, post M0-A merge):**

| Setting | Value |
| --- | --- |
| Pull request reviews required | Yes — `required_approving_review_count=1`, `dismiss_stale_reviews=true` |
| `enforce_admins` | **`false`** (admins can bypass protection) |
| Force pushes to `main` | Denied (`allow_force_pushes=false`) |
| Branch deletions | Denied (`allow_deletions=false`) |
| Required status checks | **Not enabled** (API: required status checks not configured) |
| Required signatures / linear history | false |

Gaps remaining: wire **All-up required** as a required status check (§9); consider Founder decision on `enforce_admins`. Absences or bypass flags are governance facts — not clinical approval, validation, or a release.

## 8. M0-A evidence and operating documents

The implementation package is defined by the [Signal External Validity Plan](../research/SIGNAL_EXTERNAL_VALIDITY_PLAN.md), [Security Stage Matrix D0–D3](../security/SECURITY_STAGE_MATRIX_D0_D3.md), [Clinician Comprehension Protocol](../product/CLINICIAN_COMPREHENSION_PROTOCOL.md), [PI Decision Pack](../founder/PI_DECISION_PACK_KR.md), [Release Tag Process](RELEASE_TAG_PROCESS.md), and [RII Display Human-Factors Options](../model/RII_DISPLAY_HF_OPTIONS.md). The repository-wide, secret-free required check is [`.github/workflows/all-up-required.yml`](../../.github/workflows/all-up-required.yml); it verifies these paths and relative documentation links, then runs a small set of existing unit smokes.

These documents and checks do not unfreeze clinical definitions or authorize RII/PROXY/threshold/weight changes.

---

## 9. How to add `All-up required` as a required status check on `main`

Short sibling copy for admins: [`REQUIRED_CI_CHECK_HOWTO.md`](REQUIRED_CI_CHECK_HOWTO.md).

**Workflow file (already on `main` via M0-A):** [`.github/workflows/all-up-required.yml`](../../.github/workflows/all-up-required.yml)
**GitHub Actions check name:** `All-up required` (job names appear as `all-up-required / docs paths`, `all-up-required / forbidden-claim scan`, and `all-up-required / existing unit smokes`).
**M0 backlog:** M0-07 (human applies protection) · M0-06 (this gates doc).

### Why this workflow

- Always reports on PRs/pushes to `main` (no path filter at workflow `on:` level), so it can be a **stable required** check.
- Secret-free: docs path/link checks + small existing unit smokes only.
- Does **not** run new PROXY benches, mutate thresholds, or access governed/PHI data.

### Admin steps (GitHub UI)

1. Ensure the workflow has run at least once on a PR into `main` (GitHub only lists check names after they appear).
2. Open **Settings → Branches → Branch protection rule** for `main` (or create the rule if missing).
3. Enable **Require status checks to pass before merging**.
4. Enable **Require branches to be up to date before merging** only if the team accepts the extra merge friction (optional for M0).
5. Search and select the check(s) produced by the workflow. Prefer requiring the **workflow-level** rollup if shown as `All-up required`; otherwise require all job checks:
   - `all-up-required / docs paths`
   - `all-up-required / forbidden-claim scan`
   - `all-up-required / existing unit smokes`
6. Leave **Do not allow bypassing the above settings** / admin enforcement aligned with current policy: today **`enforce_admins=false`**. Turning enforce_admins on is a Founder decision (stronger freeze hygiene; admins lose bypass).
7. Save. Confirm with a docs-only PR that the required check appears and blocks merge when red.
8. Record confirmation (screenshot or settings note) on M0-07.

### Admin steps (approximate `gh` / API)

```bash
# Inspect current protection (may 404 fields that are unset)
gh api repos/<owner>/<repo>/branches/main/protection

# Example: put required status checks (adjust check names to match Actions UI exactly).
# WARNING: a PUT replaces the protection object — export current JSON first, merge carefully.
gh api repos/<owner>/<repo>/branches/main/protection/required_status_checks \
  --method PATCH \
  -f strict=false \
  -f 'contexts[]=All-up required'
```

If the API rejects unknown contexts, use the exact job check names from a completed workflow run. Do **not** invent alternate CI jobs during freeze.

### Explicit non-actions

- Do not push directly to `main`.
- Do not add PROXY/HYP or threshold gates as required checks during M0 freeze.
- Do not treat a green All-up check as clinical validation or FACT.
