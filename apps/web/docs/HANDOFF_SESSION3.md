# Session 3 handoff: product UI (historical)

This file records the pre-integration state of the product branch. The listed
signal-engine integration actions were completed during the 2026-09-02
research-readiness audit; current architecture and limits are documented under
`docs/architecture`, `docs/product`, and `docs/security`.

## Delivered

- Complete Next.js App Router research flow: start, context, 180-second baseline, live monitor, explanation, case review, and evidence.
- Exact core stream schema validation with Zod and API clients for all six requested endpoints.
- Deterministic browser mock with five required `SYNTHETIC` scenarios, public-data disclaimer, local fixture option, and accelerated source-time replay.
- Canvas ECG/PPG/ABP rendering, quality gating, baseline deltas, reason list, timeline events, annotations, replay control, and JSON/CSV/HTML research exports.
- A temporary FastAPI contract shim was used on the isolated product branch; it was removed after integration with `services/api`.
- Component/integration tests and a 1920×1080 Playwright flow.

## Signal-engine integration actions (completed)

1. The browser validates the backend event and maps it to the UI event in `apps/web/lib/api.ts`.
2. Root Docker Compose builds `services/api`; the temporary shim is no longer present.
3. The API uses an explicit local-origin CORS allowlist and disables SSE proxy buffering.
4. Case, signal, baseline, quality, risk, and evidence shapes are normalized without changing deterministic scoring.
5. Backend invalidation remains authoritative and a numeric score is withheld whenever output is invalid.
6. Model-card and research-protocol links resolve to static research documents.

## Research-data handoff

The competitor UX reference and human-factors drafts are temporarily in `apps/web/docs` because `docs/research`, `docs/regulatory`, and `docs/safety` belong to `agent/research-data`. Research-data owners should review citations, regulatory phrasing, license text, evidence IDs, DS literature wording, and formal human-factors validation needs before promoting content into their owned directories.

## Known integration limits

- Docker was authored for API/web operation, but the host used for this session did not have Docker installed, so container startup requires verification on a Docker-capable machine.
- The current model and feature versions are prototype identifiers.
- VitalDB and WFDB are optional public-data adapters; no public patient record is bundled and network access is disabled by default.
- Exports are local browser downloads without research storage, access control, audit log, or retention policy.
- Formal WCAG contrast, clinician simulated-use, and performance profiling on target hardware remain required.
