# Audit log policy

The current prototype has no durable audit log. The following design is required before hospital data or multi-user LAN use.

## Events to record

- Authentication success/failure, logout, role/permission changes, and session timeout.
- Study session create/end, source manifest ID, pseudonymous subject ID, replay mode, and operator ID.
- Model, pipeline, feature schema, threshold/config, application, and dataset-manifest versions.
- Data import/export, destination class, record count, and approval/reference ID.
- Offline-mode changes, adapter enablement, configuration changes, and administrative actions.
- Quality-gate invalidation, processing failures, and security-relevant errors.

## Never record

Raw waveform samples, names, MRNs, exact DOB, contact/address data, credentials/tokens, free-text clinical histories, full API bodies, or treatment notes.

## Integrity and access

Use an append-only local/institution-owned sink with UTC timestamps, synchronized clocks, event IDs, actor/role, action, object pseudonym, result, software/config versions, and chained integrity hashes or equivalent tamper evidence. Restrict read access to auditors/data stewards; application operators must not alter records.

## Retention and review

Retention period, review cadence, incident escalation, export approval, and secure disposal require institutional approval. Alert on repeated authentication failure, offline-mode disablement, unauthorized export, audit-sink failure, and model/config checksum mismatch. A failed audit sink should block patient-data research sessions unless the approved protocol defines a documented contingency.
