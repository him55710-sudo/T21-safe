# T21 Safe quick start

T21 Safe is a local-first, Research Use Only signal-replay prototype. It is not a
medical device and is not for diagnosis, treatment, dosing, alarms, or clinical
monitoring. The displayed Research Instability Index is a deterministic engineering
hypothesis, not a calibrated probability.

## Prerequisites

- Python 3.11 or newer
- Node.js 20.9 or newer and pnpm 11
- Docker Desktop only if using the container path

Run commands from the repository root unless a step says otherwise. Keep public or
patient-derived data outside the Git checkout.

## 1. Install dependencies

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".\services\engine[dev,wfdb,training]" -e ".\services\api[dev]"

Set-Location apps\web
corepack enable
pnpm install --frozen-lockfile
Set-Location ..\..
```

## 2. Start the local API and dashboard

In terminal A:

```powershell
$env:OFFLINE_MODE = "true"
$env:T21_ALLOWED_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
& .\.venv\Scripts\python.exe -m uvicorn t21_api.main:app --host 127.0.0.1 --port 8000
```

In terminal B:

```powershell
Set-Location apps\web
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:8000"
$env:NEXT_PUBLIC_DEMO_MODE = "false"
$env:NEXT_PUBLIC_DEFAULT_CASE = "progressive_instability"
pnpm dev
```

Open `http://127.0.0.1:3000`. `OFFLINE_MODE=true` exposes only the synthetic cases
and bundled local fixture. Remote VitalDB and WFDB identifiers are hidden and blocked
before a network request.

For a browser-only synthetic demo, omit terminal A and run terminal B with
`NEXT_PUBLIC_DEMO_MODE=true`.

## 3. Verify a synthetic API replay

```powershell
$body = @{
  case_id = "synthetic:stable-baseline"
  speed = 1000
  baseline_seconds = 3
  mode = "GENERIC_VALIDATION_MODE"
} | ConvertTo-Json

$session = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/replays -ContentType application/json -Body $body
Invoke-WebRequest -Uri ("http://127.0.0.1:8000" + $session.stream_url) | Select-Object -ExpandProperty Content
```

The stream must contain `event: signal`, terminate with `event: end`, and withhold a
numeric score whenever quality, baseline, latency, dropout, or synchronization gates
fail.

## 4. Download and inspect one bounded public sample

This step intentionally uses the internet. Review the dataset terms first. BIDMC is
adult ICU data for generic signal-processing interoperability only; it is not
perioperative, pediatric, or verified DS data.

```powershell
$sampleRoot = Join-Path $env:TEMP ("t21-safe-bidmc01-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $sampleRoot | Out-Null

& .\.venv\Scripts\python.exe tools\datasets\download_open_sample.py `
  --dataset-id bidmc-ppg-resp `
  --sample https://physionet.org/files/bidmc/1.0.0/bidmc01.hea `
  --limit 65536 `
  --output (Join-Path $sampleRoot bidmc01.hea)

& .\.venv\Scripts\python.exe tools\datasets\download_open_sample.py `
  --dataset-id bidmc-ppg-resp `
  --sample https://physionet.org/files/bidmc/1.0.0/bidmc01.dat `
  --limit 1048576 `
  --output (Join-Path $sampleRoot bidmc01.dat)

& .\.venv\Scripts\python.exe tools\datasets\inspect_wfdb_record.py `
  --sample (Join-Path $sampleRoot bidmc01.hea) --limit 8
```

## 5. Generate the sample manifest and replay locally

```powershell
& .\.venv\Scripts\python.exe tools\datasets\generate_data_manifest.py `
  --sample $sampleRoot --limit 10 `
  --source https://physionet.org/content/bidmc/1.0.0/ `
  --version 1.0.0 `
  --license "Open Data Commons Attribution License 1.0" `
  --output (Join-Path $sampleRoot sample-manifest.json)

& .\.venv\Scripts\python.exe tools\datasets\replay_wfdb_sample.py `
  --sample (Join-Path $sampleRoot bidmc01.hea) --limit 8 --baseline-seconds 3
```

The BIDMC sample contains ECG, PPG, and respiration but no ABP. The expected fail-safe
result is a successful load/replay with `risk_valid: false` and `risk_level:
"INVALID"`; missing a required modality must not be converted into a confident score.

## 6. Run verification

```powershell
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe -m unittest discover -s tools\datasets\tests -v
& .\.venv\Scripts\python.exe -m ruff check services tests tools
Push-Location services\engine
& ..\..\.venv\Scripts\python.exe -m mypy
Pop-Location

Set-Location apps\web
pnpm typecheck
pnpm lint
pnpm test
pnpm build
pnpm test:e2e
pnpm format:check
Set-Location ..\..
```

## 7. Export a research session

Complete a synthetic replay, open **Case review**, and choose **Export anonymized
JSON**, CSV, or HTML. Exports are browser-local and are not an approved clinical
record. Enter only pseudonymous study IDs; never enter names, MRNs, dates of birth, or
free-text PHI.

## Docker alternative

```powershell
$env:OFFLINE_MODE = "true"
docker compose up --build
```

Open `http://localhost:3000`. The API container is read-only except for `/tmp`, the
web container runs as a non-root user, and Next.js telemetry is disabled. Docker was
not available on the 2026-09-02 audit host; container startup therefore remains a
machine-specific verification step even though the compose file and both native
services were inspected and run.
