# T21 Safe research API

FastAPI transport for the deterministic signal engine. Every route is Research Use Only;
no request is persisted and no endpoint returns treatment or dosing advice.

## Run

```powershell
python -m pip install -e "services/engine" -e "services/api"
python -m uvicorn t21_api.main:app --host 127.0.0.1 --port 8000
```

Or build from the repository root:

```powershell
docker build -f services/api/Dockerfile -t t21-safe-api:0.1.0 .
docker run --rm -p 8000:8000 t21-safe-api:0.1.0
```

## Contract

- `GET /health` — exact service/mode/version status.
- `GET /v1/cases` — public/local/synthetic case metadata and attribution.
- `POST /v1/replays` — creates one in-memory, single-consumer replay session.
- `GET /v1/stream/{session_id}` — SSE `signal` events; session is removed on end/cancel.
- `POST /v1/analyze-window` — ephemeral de-identified batch analysis.
- `GET /v1/evidence` — evidence/version metadata and limitations.

Example:

```powershell
$body = @{ case_id='synthetic:composite-demo'; speed=100; baseline_seconds=180 } |
  ConvertTo-Json
$session = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/replays `
  -ContentType application/json -Body $body
curl.exe -N "http://127.0.0.1:8000$($session.stream_url)"
```

The committed [OpenAPI contract](../../contracts/openapi.json) and
[event schema](../../contracts/event.schema.json) are generated from the Pydantic/FastAPI
models and must be regenerated when a model changes.
