# Offline operation

`OFFLINE_MODE=true` is the API default and the Docker Compose default.

## Offline behavior

- Only deterministic synthetic scenarios and the bundled local fixture are listed.
- VitalDB and remote WFDB identifiers are rejected before any network request.
- The engine, API, dashboard, baseline, features, index, explanations, and exports operate locally.
- No cloud telemetry, external LLM, hosted database, or analytics dependency exists.
- Next.js telemetry is disabled in container builds and runtime.

## Offline verification

```powershell
$env:OFFLINE_MODE = "true"
python -m pytest tests\backend\integration\test_adapters_api.py -q
docker compose config
```

The integration test asserts that network-backed cases are absent and that a direct VitalDB replay request returns a controlled 503 without network access. Synthetic replay remains available. Public-source acquisition is a separate, explicitly online research step; downloaded files and manifests should then be transferred into the approved offline environment under institutional policy.

## Known limitation

The repository does not yet provide a configurable local-WFDB catalog for arbitrary pre-downloaded records. That is a hospital PoC gap, not permission to enable internet access in a restricted environment.
