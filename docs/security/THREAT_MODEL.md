# Threat model

## Assets

Future hospital waveforms, pseudonymous subject mappings, study metadata, model/config versions, research outputs, credentials, and audit records. The current repository contains only synthetic/development fixture data and public-source metadata.

## Adversaries and failures

| Threat | Path | Impact | Current/required mitigation |
|---|---|---|---|
| Accidental internet egress | Public adapter or remote API URL | PHI/raw waveform disclosure | Offline default; review environment; host firewall; prohibit remote `NEXT_PUBLIC_API_URL` |
| Unauthorized LAN user | Exposed API/dashboard without auth | Data access/session misuse | Bind localhost by default; RBAC/TLS/firewall required before LAN deployment |
| Malicious/malformed waveform | Oversized arrays, NaN, timestamps | Resource exhaustion or misleading output | Request bounds, strict schemas, bounded buffer, quality/OOD gates; fuzz/load tests remain |
| Replay session theft | Guess/use session ID | Unauthorized stream consumption | Random ID, one consumer, TTL; authentication required for hospital use |
| Supply-chain compromise | Python/npm/container dependencies | Code execution/data exfiltration | Lockfile/pinned ranges, build-script allowlist, scans and signed SBOM/releases still required |
| Cross-origin abuse | Browser page calls local API | Local data access | Exact CORS allowlist; no wildcard/credentials; CSRF/auth design needed with stateful features |
| PHI in logs/exports | Exceptions, user-entered ID, browser download | Privacy breach | No request logging/persistence by app; pseudonymous form; log redaction/export policy required |
| Tampered model/config | Local file modification | Misleading score | Registry/version metadata; file signing/checksum and release verification remain |
| Stale/delayed/out-of-order data | Device/network failure | Misleading current state | Latency/dropout/synchronization gates with `INVALID` response |
| Dataset-license breach | Unapproved download/redistribution | Legal/governance harm | Allowlisted bounded tools, manifests, DUA registry, data steward review |
| Research output used for care | Screenshot/export/workflow drift | Patient harm | RUO/shadow disclaimers, no actions/recommendations; training and access governance required |

## Security invariants

1. No PHI or raw waveform leaves the approved local boundary.
2. No runtime function requires internet access in offline mode.
3. No LLM or hosted inference service enters the score path.
4. Invalid/stale/unsynchronized input cannot retain a previous valid score.
5. Audit logs, when implemented, contain metadata only—not signal payload or free-text clinical history.
6. A system failure cannot affect approved clinical monitors or patient-care workflow.
