# Local security architecture

## Trust boundary

Supported deployment is one encrypted workstation or an institution-controlled LAN. Browser, Next.js, FastAPI, engine, approved data directory, and optional audit sink remain inside that boundary. The public internet is not part of the default runtime.

```text
Approved local data directory
        ↓ read-only adapter
Local deterministic engine ← in-memory replay session
        ↓ strict Pydantic/SSE contract
Local FastAPI (local/LAN CORS allowlist)
        ↓
Local dashboard → user-initiated local export
```

## Implemented controls

- `OFFLINE_MODE=true` by default; network-backed adapters are hidden and rejected.
- No external LLM/API, hosted database, cloud telemetry, Sentry, PostHog, or hosted vector database dependency.
- API binds to localhost in native instructions; LAN exposure is explicit.
- CORS defaults to localhost/127.0.0.1 and does not allow credentials or wildcard origins.
- Strict request/event schemas and bounded input sizes.
- In-memory, single-consumer replay sessions with TTL and deletion on completion.
- Bounded/cleared signal buffer; no API persistence or raw-waveform logging.
- API container is read-only with temporary `/tmp`; frontend runs non-root.
- Next.js telemetry is disabled in build/runtime containers.
- Synthetic/local fixture is the default offline data path.

## Required hospital controls not yet implemented

- Full-disk encryption and encrypted, institution-managed backups.
- Local TLS using hospital certificates; no plaintext cross-host traffic.
- SSO or local RBAC with least privilege (research viewer, operator, data steward, auditor).
- Session idle/absolute timeouts and workstation lock policy.
- Append-only audit log with pseudonymous identifiers and no waveform/PHI payload.
- Firewall allowlists, endpoint protection, vulnerability/patch management, dependency scanning, and signed releases.
- Institution-owned data directory permissions, retention automation, secure deletion, and restore testing.

Until those controls are implemented and verified, the repository is suitable for technical demonstration, not a hospital patient-data PoC.
