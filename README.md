# T21 Safe

Local-first physiological signal research for perioperative instability hypotheses.

**Research prototype. Not for diagnosis, treatment, dosing, or clinical monitoring.**

This repository contains a deterministic signal engine, local FastAPI service, and local dashboard. The prototype supports synthetic and explicitly enabled public-data replay, signal-quality-gated index display, 180-second patient-specific baseline calibration, Canvas waveforms, structured feature explanations, evidence traceability, and pseudonymous research-session export.

## Quick start

With Docker:

```powershell
docker compose up --build
```

Open `http://localhost:3000`. This starts the real deterministic engine API and web dashboard with `OFFLINE_MODE=true`.

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

See [QUICKSTART.md](QUICKSTART.md) for the verified local workflow and [apps/web/README.md](apps/web/README.md) for frontend details.

## Audit and readiness

- [Final research readiness report](FINAL_RESEARCH_READINESS_REPORT.md)
- [System overview](docs/architecture/SYSTEM_OVERVIEW.md) and [offline operation](docs/architecture/OFFLINE_OPERATION.md)
- [Claim audit](docs/safety/CLAIM_AUDIT.md) and [prohibited claims](docs/safety/PROHIBITED_CLAIMS.md)
- [Data lineage](docs/data/DATA_LINEAGE.md) and [dataset use boundaries](docs/data/DATA_USAGE_BOUNDARIES.md)
- [Model audit](docs/model/MODEL_AUDIT.md) and [feature traceability](docs/model/FEATURE_TRACEABILITY_MATRIX.md)
- [Reproducibility checklist](docs/REPRODUCIBILITY_CHECKLIST.md)

## Safety boundary

No LLM participates in risk calculation. The current deterministic index is an engineering hypothesis, not a fitted or clinically validated model. Synthetic and public non-DS data can verify software and generic signal processing only; they do not establish clinical thresholds, DS-specific calibration, or population performance.
