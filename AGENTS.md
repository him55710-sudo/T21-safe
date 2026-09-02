# T21 Safe repository instructions

## Repository structure and ownership

- `agent/research-data`: `docs/research`, `docs/regulatory`, `docs/safety`, `research`, `tools/datasets`
- `agent/signal-engine`: `services/api`, `services/engine`, `models`, `contracts`, `tests/backend`
- `agent/product-ui`: `apps/web`, `infra`, `tests/frontend`, root `README.md`, `AGENTS.md`, `docker-compose.yml`, `.github`

Do not edit another branch's owned paths. Hand changes to that branch and review them explicitly during integration.

## Product UI layout

- `apps/web/app`: Next.js App Router entry and web health endpoint
- `apps/web/components`: research workflow and monitor components
- `apps/web/hooks`: session/replay state
- `apps/web/lib/contracts.ts`: browser API/SSE contract and runtime validation
- `apps/web/lib/api.ts`: FastAPI endpoint integration
- `apps/web/lib/mock-stream.ts`: deterministic, synthetic UI stream
- `apps/web/fixtures`: required fixture descriptors
- `apps/web/tests`: component, integration, and Playwright tests
- `apps/web/docs`: product-facing research and human-factors documentation

## Install and run

```powershell
cd apps/web
pnpm install
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:8000"
$env:NEXT_PUBLIC_DEMO_MODE = "false"
pnpm dev
```

Docker API mode: `docker compose up --build`.

Docker frontend-only demo: `docker compose --profile demo up --build web-demo`.

## Build, test, lint, format

```powershell
cd apps/web
pnpm typecheck
pnpm lint
pnpm test
pnpm build
pnpm test:e2e
pnpm format:check
```

`pnpm build` must also pass the production forbidden-language scan.

## Safety restrictions

- Research Use Only / Shadow Mode. Never present this repository as a certified or validated patient monitor.
- LLMs may assist research organization and development review only. Never put an LLM in the real-time patient risk path.
- Inference must come from a version-pinned deterministic signal pipeline and a verifiable statistical/ML model. Track model, data, preprocessing, threshold, and validation versions.
- Hide the index unless baseline is calibrated, signal quality is usable, and backend risk output is valid with a numeric score.
- Do not add a baseline bypass.
- Do not infer Down syndrome, congenital heart disease, OSA, or anesthesia history from waveforms.
- Do not invent missing patient context.
- Do not claim DS-specific weights, calibration, validation, or activation without approved evidence.
- Medication events are read-only research metadata. Do not provide dose, treatment, procedural-clearance, or emergency predictions.
- Manual acknowledgment is a research annotation, never proof that a patient-care action occurred.
- Do not change `Research Instability Index` to a disease or outcome claim.
- Preserve the status vocabulary: BASELINE, STABLE, WATCH, ELEVATED, HIGH, INVALID.

## Forbidden clinical claims

Never render or imply instructions to change an anesthetic, administer a drug, declare a procedure safe, announce a diagnosis, predict arrest, or provide a dosing recommendation. Safe copy describes measured change, insufficient quality, research uncertainty, and the need to review complete patient context.

## No-PHI policy

- No names, medical-record numbers, exact dates of birth, contact details, addresses, facial images, free-text identifiable histories, or credentials in source, fixtures, logs, screenshots, commits, or exports.
- Use pseudonymous study subject IDs and coarse age/weight groups.
- Synthetic fixtures must be visibly labeled and contain no real patient records.
- Public data must retain attribution/license metadata and must not be represented as a verified DS case.
