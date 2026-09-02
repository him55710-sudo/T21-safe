# T21 Safe web

T21 Safe is a Research Use Only / Shadow Mode perioperative monitoring prototype. It displays deterministic waveform replay, patient-specific baseline calibration, signal-quality gating, an inspectable Research Instability Index, structured feature explanations, and anonymized research-session review.

Research prototype. Not for diagnosis, treatment, dosing, or clinical monitoring.

## Requirements

- Node.js 20.9 or newer
- pnpm 11
- Docker with Compose for container integration

## Browser-only demo

```powershell
cd apps/web
pnpm install
Copy-Item .env.example .env.local
pnpm dev
```

`.env.example` enables local demo mode. Open `http://localhost:3000`. The mock stream works without FastAPI.

## Live API mode

Create `.env.local`:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEMO_MODE=false
NEXT_PUBLIC_DEFAULT_CASE=progressive_instability
```

Start the FastAPI service separately, then run `pnpm dev`. The browser uses:

- `GET /health`
- `GET /v1/cases`
- `POST /v1/replays`
- `GET /v1/stream/{session_id}`
- `POST /v1/analyze-window`
- `GET /v1/evidence`

The runtime validator is `lib/contracts.ts`; client integration is `lib/api.ts`.

## Docker

API mode with the product-branch contract shim:

```powershell
docker compose up --build
```

Open `http://localhost:3000`. The `api` service is the disposable `infra/api-shim`, used only until the signal-engine FastAPI service is merged.

Frontend-only demo mode:

```powershell
docker compose --profile demo up --build web-demo
```

Open `http://localhost:3001`. This service has no API dependency.

## Quality commands

```powershell
cd apps/web
pnpm typecheck
pnpm lint
pnpm test
pnpm build
pnpm test:e2e
pnpm format:check
```

`pnpm build` creates a Next.js standalone production build and scans production output for prohibited patient-care phrases. Playwright executes the complete synthetic-instability flow at 1920×1080.

## Mock fixtures

Fixture descriptors live in `fixtures/`; the exact-contract deterministic stream generator is `lib/mock-stream.ts`.

- `stable_case`
- `progressive_instability`
- `artifact_case`
- `missing_signal_case`
- `recovery_case`

All five are labeled `SYNTHETIC`. The public-data option carries an explicit statement that it is not a verified Down syndrome case.

## Architecture

- Next.js App Router + React + strict TypeScript
- TanStack Query for backend health and metadata reads
- Zod validation at the SSE boundary
- Canvas waveform rendering (no per-sample DOM nodes)
- Vitest + React Testing Library + Playwright
- Standalone Next.js Docker output

See `ASSUMPTIONS.md`, `docs/UX_ARCHITECTURE.md`, and `docs/HUMAN_FACTORS.md` before changing risk, quality, baseline, or wording behavior.
