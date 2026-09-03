# Research Node MCP

The Research Node MCP is a thin, local wrapper around the existing deterministic
synthetic hospital case, time-alignment quality report, replay pipeline,
`LocalCaptureJsonlWriter`, and `ExportManifest`. It is for synthetic demo, engineering
QC, and shadow-mode research only: `clinical_validation=false`, `synthetic_only=true`,
and `mode=OBSERVE_ONLY_SHADOW`.

It does not require Fantasia and does not accept or load VitalDB, CapnoBase, PulseDB,
MIMIC, patient, or PHI inputs. It has no dosing, alerting, actuation, closed-loop,
drug-advice, or EMR-write capability. Output is optional and limited to local
shadow-capture metadata JSONL; waveform and PHI persistence are disabled.

## Install and run

From the repository root:

```bash
python -m pip install -e "services/engine[dev]"
t21-research-node-mcp
```

The dependency-free transport uses newline-delimited JSON-RPC 2.0 over stdin/stdout
and implements MCP `initialize`, `tools/list`, and `tools/call`. It can also run from
a source checkout:

```bash
PYTHONPATH=services/engine/src python -m t21_engine.research_node_mcp.server
```

## Client configuration

After installing the engine into an environment visible to the client, add:

```json
{
  "mcpServers": {
    "t21-research-node": {
      "command": "t21-research-node-mcp",
      "args": []
    }
  }
}
```

Desktop clients may require the absolute executable path. For a source checkout, use
absolute paths for Python and `PYTHONPATH`:

```json
{
  "mcpServers": {
    "t21-research-node": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "t21_engine.research_node_mcp.server"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/T21-safe/services/engine/src"
      }
    }
  }
}
```

## Tools and fail-closed behavior

- `run_time_align_qc` builds the pinned-seed synthetic hospital fixture and calls its
  existing raw-clock `quality_report`.
- `run_synthetic_demo` calls the existing `run_demo` replay path. With no
  `output_dir`, it writes nothing. With a local `output_dir`, it appends validated
  metadata records and an `ExportManifest` to `shadow-capture.jsonl`.
- `run_sqi_missingness_impact` calls the existing deterministic synthetic SQI and
  missingness evaluation. Optional parameters only control engineering sampling,
  injected gap fractions, injected noise levels, and the deterministic seed.
- `run_baseline_window_sensitivity` calls the existing fixed 180-second versus
  300-second synthetic baseline comparison. It does not accept alternate windows.

Both evaluation tools are read-only and return `PI_TO_DEFINE` in every response,
including failures. Their outputs are engineering sensitivity summaries only;
`clinical_validation=false` and `synthetic_only=true` remain explicit. They neither
choose clinical cutoffs nor select a clinical baseline window.

URI schemes (`s3://`, `gs://`, `http://`, `https://`, `file://`), network shares, and
paths marked as PHI or patient data are rejected before any directory is created.
Every PASS, rejection, or fail-closed tool payload repeats the non-clinical safety
gates.

## Verify

```bash
python -m pytest tests/backend/unit/test_research_node_mcp.py \
  tests/backend/unit/test_research_node_mcp_stdio.py \
  tests/backend/integration/test_research_node_demo.py
```
