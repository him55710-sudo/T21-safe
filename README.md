# T21 Safe

Patient-specific perioperative safety intelligence for physiologically vulnerable patients, starting with Down syndrome.

**Research prototype. Not for diagnosis, treatment, dosing, or clinical monitoring.**

This branch contains the product UI and a disposable FastAPI contract shim. The prototype supports deterministic synthetic replay, signal-quality-gated index display, 180-second patient-specific baseline calibration, Canvas waveforms, structured feature explanations, evidence traceability, and anonymized research-session export.

## Quick start

With Docker:

```powershell
docker compose up --build
```

Open `http://localhost:3000`. This starts `web` and the product-branch `infra/api-shim`.

Frontend-only demo:

```powershell
docker compose --profile demo up --build web-demo
```

Open `http://localhost:3001`.

Local browser-only demo:

```powershell
cd apps/web
pnpm install
Copy-Item .env.example .env.local
pnpm dev
```

See [apps/web/README.md](apps/web/README.md) for environment variables, API contract, test commands, architecture, and fixture details. See [apps/web/docs/HANDOFF_SESSION3.md](apps/web/docs/HANDOFF_SESSION3.md) before merging the Session 2 backend.

## Safety boundary

No LLM participates in risk calculation. Real inference must come only from a version-pinned deterministic signal pipeline and verified statistical/ML model. The current fixtures and contract shim demonstrate UI states; they do not establish clinical thresholds, DS-specific calibration, or population validation.
