# Release Tag Process — M0-A

**Scope:** Auditable repository tags for research/demo artifacts

**Restriction:** A tag is a provenance marker, not regulatory clearance, clinical validation, or permission for patient-care use.

## Roles

| Role | Responsibility |
| --- | --- |
| Release proposer | Prepares PR, evidence checklist, candidate identifier, and release notes |
| Reviewer | Confirms scope, tests, claims, provenance, and freeze compliance |
| Founder/release authority | Approves creation of protected release tag |
| Security/data owner | Required when stage, dependency risk, or governed data handling changes |

The proposer must not self-approve a release that changes governed scope. Tags are created only from a reviewed commit on `main`; no direct push to `main` is part of this process.

## Tag classes and naming

| Class | Pattern | Use |
| --- | --- | --- |
| Research snapshot | `research-vMAJOR.MINOR.PATCH` | Reproducible research package |
| Demo snapshot | `demo-vMAJOR.MINOR.PATCH` | Synthetic-only controlled demo |

Do not use `clinical`, `validated`, `approved`, `safe`, or a disease/outcome claim in tag names. During M0 freeze, documentation work may prepare a candidate, but no tag implies unfreeze. Pre-release suffixes such as `-rc.1` may be used only when the repository hosting rules and release notes clearly mark them non-final.

## Preconditions

1. Candidate commit is reachable from `origin/main` and was merged by PR.
2. Required status checks pass, including `all-up-required`.
3. Worktree and submodule state, if any, are clean and recorded.
4. Release notes state RUO/Shadow status, `clinical_validation=false`, change scope, known limitations, and evidence boundaries.
5. Dataset/model/preprocessing/configuration identifiers relevant to the artifact are pinned; governed data are not embedded.
6. No secret, PHI, forbidden claim, or unapproved binary/artifact is present.
7. Freeze-sensitive changes have an explicit Founder unfreeze decision; otherwise they are absent.
8. Rollback/withdrawal owner and retained evidence location are named.

## Procedure

1. Open a release-preparation PR containing release notes/checklist only as needed; link approvals and issues.
2. Record the exact full candidate SHA after merge and independently verify CI on that SHA.
3. Founder/release authority records approval for the exact tag name and SHA.
4. Create an **annotated, signed tag** where signing infrastructure is available. The annotation includes scope, RUO status, approver, and evidence-pack location.
5. Push the explicit tag ref only; never use a broad `--tags` push.
6. Verify the remote tag resolves to the approved SHA and signature/annotation is readable.
7. Publish release notes, checksums, SBOM/provenance references, and limitations without patient or participant data.
8. Record the tag, SHA, date/time, actor, approvals, CI run, and artifact hashes in the release ledger or release record.

Illustrative commands (execute only after approval):

```bash
git fetch origin main --tags
git tag -s research-v0.1.0 <approved-full-sha> -m "RUO research snapshot; clinical_validation=false"
git push origin refs/tags/research-v0.1.0
git ls-remote --tags origin refs/tags/research-v0.1.0
```

If signing is unavailable, stop and document the gap; the Founder may explicitly authorize an annotated unsigned tag for M0 with compensating SHA verification. Lightweight tags are not used.

## Immutability and correction

Published tags are immutable: do not force-update or reuse a version. If incorrect, preserve evidence, mark the associated release withdrawn/deprecated, document the reason and impact, and issue a new incremented tag after review. A compromised credential or artifact invokes incident response and remote distribution containment; deleting a tag requires explicit Founder and security approval and an audit record.

## Verification checklist

- [ ] Tag name and full SHA match approval
- [ ] Commit is on `origin/main`
- [ ] Required CI is green on the candidate SHA
- [ ] Signature/annotation and remote resolution verified
- [ ] RUO/Shadow limitations and `clinical_validation=false` visible
- [ ] Evidence identifiers, checksums, and known gaps recorded
- [ ] No PHI, secrets, forbidden claims, or unapproved data/artifacts
- [ ] Withdrawal/rollback owner recorded

Related: [Technical and Repository Gates](TECHNICAL_AND_REPOSITORY_GATES.md), [Security Stage Matrix](../security/SECURITY_STAGE_MATRIX_D0_D3.md), [Freeze Declaration](FREEZE_DECLARATION_M0.md).
