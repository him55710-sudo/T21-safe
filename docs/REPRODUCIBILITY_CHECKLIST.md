# Reproducibility checklist

Audit date: 2026-09-02. Host: Windows, Python 3.12.13, Node.js 24.19.0, pnpm
11.19.0, Git 2.53.0. The supported project minimums remain Python 3.11 and Node
20.9. Exact application dependency versions are pinned by `apps/web/pnpm-lock.yaml`
and bounded in the Python package metadata.

| Workflow | Command/evidence | Result |
| --- | --- | --- |
| Python dependency install | editable `t21-engine[dev,wfdb,training]` 0.2.0 and `t21-api[dev]` 0.2.0 | PASS |
| Web dependency install | `pnpm install --frozen-lockfile` | PASS |
| Dataset registry | `verify_dataset_registry.py --limit 20` | PASS: 13 datasets, 30 required fields |
| Small public sample | bounded BIDMC `bidmc01.hea` (595 B) and `bidmc01.dat` (600,010 B), official PhysioNet host | PASS |
| Dataset manifest | `generate_data_manifest.py`, hard file limit 10 | PASS: 5 input files, SHA-256 for every file |
| WFDB inspection | `inspect_wfdb_record.py --limit 8` | PASS: 5 signals, 125 Hz, 60,001 samples in header |
| Public waveform replay | `replay_wfdb_sample.py --limit 8` | PASS: 1,000 samples and 8 events; safe `INVALID` because ABP is absent |
| Native backend | Uvicorn on `127.0.0.1:8000`, `OFFLINE_MODE=true` | PASS: health, cases, replay create, custom SSE signal/end |
| Native frontend | Next.js standalone server on `127.0.0.1:3000` | PASS |
| Real API/browser integration | API cases → context → 180 s baseline → live replay → natural completion | PASS: final source time 240 s, `REPLAY COMPLETE`, no console/page errors |
| Offline boundary | offline adapter integration test | PASS: network cases hidden and direct network-backed replay blocked |
| Synthetic safety matrix | required ECG/PPG/ABP/multimodal cases | PASS: 14 focused scenarios |
| Backend suite | `python -m pytest -q` | PASS: 61 tests; one dependency deprecation warning |
| Dataset-tool suite | unittest discovery | PASS: 8 tests |
| Static Python checks | Ruff and strict mypy | PASS |
| Web unit/integration | Vitest | PASS: 21 tests |
| Web static/build | TypeScript, ESLint, Prettier, Next production build, forbidden-copy scan | PASS |
| Browser E2E/export | Playwright 1920×1080 research flow and JSON download | PASS: 1 scenario |
| Accessibility automation | axe WCAG 2 A/AA at 1920×1080 | PASS: 0 violations; gradient contrast remains manual/incomplete |
| Compose/Dockerfile static validation | parsed YAML plus API target, offline default, read-only/tmpfs, standalone/non-root/telemetry assertions | PASS |
| Docker Compose runtime | `docker compose up --build` | NOT RUN: Docker was not installed on the audit host |

## Reproduction invariants

- `OFFLINE_MODE=true` is the API and Compose default.
- Synthetic and local-fixture operation performs no public-data network access.
- No LLM, cloud database, hosted analytics, or external telemetry participates in
  signal preprocessing, feature extraction, index calculation, or explanation.
- API contracts are regenerated from Pydantic/FastAPI and compared byte-for-object
  equality in integration tests.
- The app version is 0.2.0, pipeline version is `pipeline-v0.2`, feature schema is
  `features-v0.1`, and the unfitted deterministic index artifact is `rii-v0.1`.
- Public samples and manifests remain outside the Git checkout.
- A public waveform load is a technical interoperability check. It does not establish
  an outcome label, clinical threshold, DS validity, pediatric validity, or external
  validation.

## Known reproducibility gaps

1. Docker images and Compose health checks require verification on a Docker-capable
   machine.
2. Python transitive dependencies do not yet have a hash-locked requirements file or
   SBOM; package bounds alone are insufficient for regulated reproducibility.
3. There is no release-signing or model/config compatibility enforcement at startup.
4. Arbitrary pre-downloaded WFDB records can be checked by the local CLI, but the web
   UI has no institution-managed local record catalog.
5. Export, retention, access control, and audit logging are prototype/browser-local,
   not an institutionally validated research data system.
