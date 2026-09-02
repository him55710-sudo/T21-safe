# Data retention policy

This repository supplies a minimum policy template; the institution/IRB/data owner must approve final periods and deletion procedures before patient data are introduced.

| Data class | Default handling | Retention | Disposal |
|---|---|---|---|
| In-memory replay waveform | Process-local bounded buffer | Replay duration only | Cleared on completion/cancel/process exit |
| API request window | Ephemeral memory | Request duration only | Released after response; never application-persisted |
| Synthetic fixtures | Version-controlled | Project lifetime | Normal source-control policy |
| Public research sample | Outside Git checkout with manifest | Per source license/protocol | Verified deletion under data-steward policy |
| Future hospital waveform/metadata | Encrypted approved local store only | IRB/DUA-approved period | Logged secure deletion; backups included |
| Browser research export | User-selected local destination | Study-approved period | User/institution responsibility; encrypted storage required |
| Audit metadata | Institution-owned append-only store | Regulatory/IRB policy | Controlled archival/deletion; no raw signals |

## Rules

- Never commit raw patient/public waveform files, credentials, exact dates of birth, names, MRNs, contact data, addresses, facial images, or free-text identifiable histories.
- Use pseudonymous study IDs and keep the re-identification key in a separate, access-restricted institutional system.
- Do not place patient data in cloud-synced folders, crash reports, analytics, screenshots, issue trackers, or support bundles.
- Encrypt workstation disks and backups; test restore and deletion procedures.
- Suspension, withdrawal, legal hold, and incident-response handling must follow the approved protocol/DUA.

Automated retention enforcement is not implemented; this is a blocker for hospital patient-data use.
