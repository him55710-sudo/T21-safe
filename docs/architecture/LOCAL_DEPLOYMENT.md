# Local deployment

## Supported topology

The supported research topology is a single workstation or an isolated hospital LAN: browser → local Next.js dashboard → local FastAPI → local deterministic engine. No hosted service is required.

## Docker

From the repository root:

```powershell
$env:OFFLINE_MODE = "true"
docker compose up --build
```

Open `http://localhost:3000`. FastAPI is exposed at `http://localhost:8000` for local inspection. The API container is read-only with a temporary `/tmp`; the frontend runs as a non-root user. Next.js telemetry is disabled.

## Native development

Use Python 3.11+ and Node 20.9+:

```powershell
python -m pip install -e ".\services\engine[dev,wfdb]" -e ".\services\api[dev]"
python -m uvicorn t21_api.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
Set-Location apps\web
pnpm install --frozen-lockfile
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:8000"
$env:NEXT_PUBLIC_DEMO_MODE = "false"
pnpm dev
```

Keep `NEXT_PUBLIC_API_URL` on localhost or an approved hospital-LAN endpoint. For another LAN origin, explicitly set `T21_ALLOWED_ORIGINS`; do not use `*`.

## Production-research hardening before hospital use

Use full-disk encryption, local TLS, host firewall allowlists, named user accounts with least privilege, automatic session lock, encrypted backups, time-synchronized hosts, and an institution-owned audit sink. These controls are designed but not fully implemented in this repository.
