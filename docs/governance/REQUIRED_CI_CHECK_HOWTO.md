# Required CI Check How-to — `All-up required`

**Status:** REQUIRED M0 repository-control action<br>
**Target branch:** `main`<br>
**Workflow:** [`.github/workflows/all-up-required.yml`](../../.github/workflows/all-up-required.yml)<br>
**Boundary:** Repository governance only; this check does not approve clinical definitions or model behavior.

## Required setting

An administrator must configure the successful `All-up required` workflow checks as required status checks for pull requests into `main`. Direct pushes to `main` remain prohibited. Do not enable auto-merge as part of this procedure.

The workflow always runs on `pull_request` to `main` and reports these job checks:

- `all-up-required / docs paths`
- `all-up-required / forbidden-claim scan`
- `all-up-required / existing unit smokes`

GitHub may display the selectable contexts with the workflow prefix, job name, or both. Select the contexts emitted by the current `All-up required` run; do not type an unobserved name from memory.

## GitHub settings procedure

1. Open the repository **Settings → Branches** (or **Rules → Rulesets**, if rulesets govern `main`).
2. Create or edit the rule targeting exactly `main`.
3. Require a pull request before merging and require status checks to pass.
4. Search the check picker using a completed PR run of **All-up required**.
5. Mark all emitted `all-up-required` job contexts above as required.
6. Require the branch to be up to date before merging if that matches the repository's merge policy.
7. Block force pushes and branch deletion; save/enforce the rule.

If the repository uses a ruleset, record its name and active/enforced state. If it uses classic branch protection, record the protection rule URL or screenshot location without credentials.

## Verification

Use a documentation-only PR to verify all of the following:

| Verification | Expected result |
| --- | --- |
| PR targets `main` | Both All-up job contexts appear |
| A required job is pending | Merge is blocked |
| A required job fails | Merge is blocked |
| Both required jobs pass and reviews are satisfied | CI no longer blocks merge |
| Direct push/force push test by policy inspection | Disallowed; do not perform a destructive live test |

Record the PR URL, rule/ruleset name, observed check-context names, verifier, and UTC verification date in the governance issue or PR. A green workflow without the enforced branch rule is not completion.

## Change control and troubleshooting

- Renaming the workflow or either job can orphan the required context. Update branch protection only after the renamed check has reported on a PR.
- Do not apply a workflow-level path filter: a required check that never reports can leave a PR permanently pending.
- Do not remove or bypass a required context to merge a failing PR. Fix the failure or use the repository's documented, human-approved emergency governance process.
- GitHub administration is a Founder/repository-admin action. Contributors and agents may prepare this guide and evidence but must not claim the setting is active until verified in repository settings.


## Known protection state (2026-09-04 KST)

Queried via GitHub branch protection API for `main`:

| Setting | Observed |
| --- | --- |
| PR reviews required | Yes (`required_approving_review_count=1`, stale reviews dismissed) |
| `enforce_admins` | **`false`** — admins can still bypass; Founder may tighten later |
| Force push / deletion | Denied |
| Required status checks | **See M0-C API attempt below** |

A green workflow without the required-check rule is **not** Done for M0-07.

See [Technical and Repository Gates](TECHNICAL_AND_REPOSITORY_GATES.md) §9 and [M0 Issue Backlog](M0_ISSUE_BACKLOG.md) (M0-07).

### M0-C API attempt (required status checks) — outcome

**Result (2026-09-04 KST): required status checks are still NOT enabled on `main`.**

| Step | Result |
| --- | --- |
| `GET .../protection/required_status_checks` | HTTP 404 — `Required status checks not enabled` |
| `POST` / `PUT` on `.../protection/required_status_checks` only | HTTP 404 — sub-resource absent until created via full protection update |
| Full `PUT .../branches/main/protection` with `required_status_checks` | **Not applied** — treated as risky (can replace the whole protection object); left for Founder/admin UI or carefully reviewed API merge |

Observed protection that remains in place: PR reviews required (`required_approving_review_count=1`, dismiss stale), `enforce_admins=false`, force-push/deletion denied.

Target contexts to require once applied (exact Actions job names):

1. `all-up-required / docs paths`
2. `all-up-required / forbidden-claim scan`
3. `all-up-required / existing unit smokes`

**How to enable (Founder/admin):** use Settings → Branches (procedure above) after this PR’s **All-up required** run has reported the new forbidden-claim job at least once; or export current protection JSON, merge `required_status_checks` carefully, and `PUT` the full object. Do not push `main` directly. A green workflow without the required-check rule is still **not** Done for M0-07.
