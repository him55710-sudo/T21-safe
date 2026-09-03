# Fantasia local-first MCP

The Fantasia MCP exposes bounded, read-only access to local Fantasia v1.0.0 WFDB
records for the `PROXY_HRV_AGE_STABILITY` engineering workflow. It is Research Use
Only: `clinical_validation=false`. It is not a DS or anesthesia workflow and does not
provide PTT/PPG analysis. The VERIFIED PROXY gate references Notion page
`3d09631d743b81efae8fe2731113b4f6`.

No network download is performed. By default the server selects
`data/public/fantasia/1.0.0/` when present, then the visibly synthetic fixture at
`tests/backend/fixtures/wfdb_fantasia_synthetic/`. Explicit inputs must be local paths;
URI schemes and network-share paths are rejected, including `s3://`, `gs://`,
`http://`, `https://`, and `file://`.

## Install and run

From the repository root:

```bash
python -m pip install -e "services/engine[wfdb]"
t21-fantasia-mcp
```

The dependency-free server transport uses newline-delimited JSON-RPC 2.0 over stdin
and stdout and implements MCP `initialize`, `tools/list`, and `tools/call`. It can also
be launched without the console script:

```bash
PYTHONPATH=services/engine/src python -m t21_engine.fantasia_mcp.server
```

Example client configuration:

```json
{
  "mcpServers": {
    "fantasia-proxy": {
      "command": "python",
      "args": ["-m", "t21_engine.fantasia_mcp.server"]
    }
  }
}
```

The environment running the client must have the engine package installed, or set
`PYTHONPATH` to `services/engine/src`.

## Tools

- `list_records`: lists local `.hea` records and reports synthetic-fixture SHA-256
  verification when a manifest is present.
- `load_sample`: returns 1–1000 waveform samples from one record. It verifies the
  fixture manifest before loading and requires the optional `wfdb` dependency.
- `run_hrv_proxy_bench`: calls the existing versioned
  `fantasia_hrv_age_bench` implementation and preserves its failure semantics.

Every successful or rejected tool payload repeats the scope and non-clinical gates.
Use the fixture for offline CI; it is synthetic and is not a real participant record.

## Verify

```bash
python -m pytest tests/backend/unit/test_fantasia_mcp.py \
  tests/backend/unit/test_fantasia_hrv_age_bench.py
```
