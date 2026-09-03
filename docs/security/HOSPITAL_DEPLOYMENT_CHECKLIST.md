# Hospital Deployment Checklist (stub)

**Status:** STUB · Path B · local-first · RUO / Shadow  
**Not:** cloud SaaS PHI store · clinical alarm product · closed-loop

---

## Local-first

- [ ] Deploy on hospital-controlled host / approved LAN only
- [ ] No default outbound PHI or waveform sync
- [ ] Operator-owned paths for samples (`data/public/...` outside git when real PhysioNet bytes)

## No cloud PHI

- [ ] Confirm ExportManifest / capture writer reject cloud URI schemes
- [ ] `contains_phi` / `includes_phi` forced `false` for research export path
- [ ] `waveform_persistence` / `includes_waveforms` forced none/false
- [ ] No credentials in repo, logs, or screenshots

## ExportManifest flags (engineering)

- [ ] `storage_scope=LOCAL_ONLY`
- [ ] `includes_phi=false`, `includes_waveforms=false`
- [ ] Observe-only controls: actuation/dosing/closed_loop/drug_advice/emr_write all false

## Access & ops (placeholder)

- [ ] Local auth / workstation policy — `HOSPITAL_TO_DEFINE` (do not invent RBAC product in this stub)
- [ ] Audit log retention — see `docs/security/AUDIT_LOG_POLICY.md`
- [ ] Incident contact — `FOUNDER_TO_FILL`

## Banned go-live language

Do not describe the node as a cleared patient monitor or dosing advisor.

## Partner pack

- PHI-false ExportManifest one-pager: [`docs/business/export-manifest-phi-false-1p.md`](../business/export-manifest-phi-false-1p.md)
- KR: [`docs/founder/EXPORT_MANIFEST_PHI_FALSE_KR.md`](../founder/EXPORT_MANIFEST_PHI_FALSE_KR.md)
