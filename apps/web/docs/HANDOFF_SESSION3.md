# Session 3 handoff: product UI

## Delivered

- Complete Next.js App Router research flow: start, context, 180-second baseline, live monitor, explanation, case review, and evidence.
- Exact core stream schema validation with Zod and API clients for all six requested endpoints.
- Deterministic browser mock with five required `SYNTHETIC` scenarios, public-data disclaimer, local fixture option, and accelerated source-time replay.
- Canvas ECG/PPG/ABP rendering, quality gating, baseline deltas, reason list, timeline events, annotations, replay control, and JSON/CSV/HTML research exports.
- FastAPI contract shim under `infra/api-shim` plus API-mode and frontend-only Docker services.
- Component/integration tests and a 1920×1080 Playwright flow.

## Signal-engine integration actions

1. Compare `apps/web/lib/contracts.ts` against the merged Session 2 contract. Preserve required keys and either remove UI-only optionals or add them to the documented backend response.
2. Replace the `infra/api-shim` build target in root `docker-compose.yml` with the merged `services/api` Docker target. Do not move shim logic into `services/engine`.
3. Confirm CORS allows the production web origin and SSE proxy buffering is disabled.
4. Confirm each `/v1/cases` item includes UI attribution, license, kind, and `verified_ds`, or provide a mapping endpoint/contract.
5. Confirm signal objects expose numeric value, unit, samples, availability, and optional sample rate. If the engine streams samples separately, add an adapter in `apps/web/lib/api.ts`, not in the deterministic model path.
6. Confirm baseline failure reasons and per-signal SQI are versioned. The UI will not add a baseline bypass.
7. Confirm risk invalidation is produced deterministically by the backend and that `score` is null whenever `valid` is false.
8. Replace placeholder model-card and research-protocol links.

## Research-data handoff

The competitor UX reference and human-factors drafts are temporarily in `apps/web/docs` because `docs/research`, `docs/regulatory`, and `docs/safety` belong to `agent/research-data`. Research-data owners should review citations, regulatory phrasing, license text, evidence IDs, DS literature wording, and formal human-factors validation needs before promoting content into their owned directories.

## Known integration limits

- Docker was authored for API/web operation, but the host used for this session did not have Docker installed, so container startup requires verification on a Docker-capable machine.
- The current model and feature versions are prototype identifiers.
- VitalDB is a labeled integration placeholder; no public patient record is bundled.
- Exports are local browser downloads without research storage, access control, audit log, or retention policy.
- Formal WCAG contrast, clinician simulated-use, and performance profiling on target hardware remain required.
