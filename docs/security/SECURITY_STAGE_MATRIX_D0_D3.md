# Security Stage Matrix D0–D3

**Status:** Minimum security gates by maturity stage

**Scope:** Path B / RUO / Shadow; no stage implies certification, clinical validation, or authorization for patient-care use.

## Stage definitions

| Stage | Permitted environment | Data boundary | Exit authority |
| --- | --- | --- | --- |
| D0 — local development | Isolated developer/test environment | Synthetic data only; no credentials in repository | Engineering owner |
| D1 — controlled demo | Access-controlled internal or partner demo | Synthetic fixtures only, visibly labeled | Security owner + product owner |
| D2 — governed retrospective research | Approved research environment | Pseudonymized study data under IRB/DUA as applicable | Data custodian + security + PI |
| D3 — prospective shadow research | Hospital-controlled shadow environment; no control path | Minimum necessary approved data; no patient-care output | Institution + security + PI + Founder |

## Required controls

| Control domain | D0 | D1 | D2 | D3 |
| --- | --- | --- | --- | --- |
| Purpose and authorization | Repository rules accepted | Written demo scope and named owner | IRB/DUA and data-use purpose recorded | Prospective protocol, site approval, and shadow-only boundary recorded |
| Identity and access | Individual accounts; least privilege | Named users; MFA where supported; remove stale access | SSO/MFA, role-based access, periodic review | Hospital identity controls, privileged-access review, rapid revocation |
| Secrets | No committed secrets; local secret mechanism | Managed secrets; rotation owner | Site-approved secret store and rotation evidence | Site-approved store, scoped service identities, rotation/expiry monitoring |
| Data | Synthetic-only marker | Synthetic-only marker and export review | Pseudonymous IDs, minimization, approved storage/transfer | Minimum necessary collection, approved interfaces, strict segregation from care systems |
| Encryption | Platform defaults documented | TLS for transit; encrypted managed storage | Approved encryption in transit/at rest; key ownership documented | Institution-approved cryptography and key lifecycle |
| Network | Local/deny by default where feasible | Ingress allowlist or authenticated access | Segmented research environment; documented egress | Hospital segmentation, allowlisted flows, no actuator/closed-loop route |
| Logging | Local diagnostic logs; no PHI | Authentication/admin/security events | Access, export, configuration, and processing audit trail | Central monitoring, alert routing, time synchronization, audit retention |
| Dependencies | Lockfiles and review | Vulnerability/dependency scan before demo | SBOM, provenance, severity triage and remediation SLA | Signed/reproducible release evidence where feasible; continuous triage |
| Change/release | PR review and required CI | Immutable demo commit/tag | Approved release tag and rollback artifact | Site change approval, staged rollout, tested rollback and stop authority |
| Backup/recovery | Source control; disposable synthetic data | Configuration recovery tested | Backup scope, restore test, retention/deletion evidence | Site-approved continuity objectives and recovery exercise |
| Incident response | Maintainer contact | Demo stop procedure | Security/privacy escalation and evidence preservation | Joint site response, disconnect/stop procedure, notification duties mapped |
| Verification | Secret scan and unit smoke | Threat-model review and demo checklist | Security test, access review, data-flow verification | Predeployment assessment and periodic control review |

## Universal fail-closed gates

Progression is blocked when authorization, data provenance, identity controls, encryption, auditability, incident ownership, or deletion/retention terms are absent. Suspected PHI in source, fixture, log, screenshot, export, or CI artifact stops distribution and invokes the incident process. D3 output remains observational and must not drive alarms, therapy, dosing, procedural clearance, or device control.

## Evidence packet and review cadence

Each stage packet records scope, system/data-flow diagram, asset owner, data classification, access list, threat-model version, dependency/SBOM evidence, test results, open risks with acceptance owner/expiry, incident contacts, backup/restore evidence where applicable, release identifier, and approvals. Re-review occurs before stage promotion, after material architecture/data/vendor change, and at the institution's required cadence.

## Demotion and shutdown

Credential exposure, unauthorized data, loss of auditability, unapproved network flow, expired authorization, or critical unresolved vulnerability triggers containment and stage demotion or shutdown. Recovery requires documented remediation and the same authorities that approved the stage.

Related: [Threat Model](THREAT_MODEL.md), [Audit Log Policy](AUDIT_LOG_POLICY.md), [Data Retention Policy](DATA_RETENTION_POLICY.md), [Release Tag Process](../governance/RELEASE_TAG_PROCESS.md).
