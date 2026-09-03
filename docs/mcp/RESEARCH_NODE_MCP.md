# Research Node MCP

The Research Node MCP is a thin, local wrapper around existing deterministic
synthetic and public-data PROXY engineering workflows. It is for engineering QC and
shadow-mode research only: `clinical_validation=false` and
`mode=OBSERVE_ONLY_SHADOW`. Public-data tools are PROXY benches, never clinical or
DS validation.

It does not require Fantasia and does not accept or load VitalDB, CapnoBase, PulseDB,
MIMIC, patient, or PHI inputs. It has no dosing, alerting, actuation, closed-loop,
drug-advice, or EMR-write capability. Output is optional and limited to local
shadow-capture metadata JSONL; waveform and PHI persistence are disabled.
Each JSONL record declares its contract explicitly: `shadow-capture/1.0` for capture
events and `export-manifest/1.0` for manifests.

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
- `run_mitbih_beat_bench` calls the existing pinned-record MIT-BIH-style beat bench
  against a local promoted dataset or the explicitly labeled synthetic CI fixture.
  Its only parameter is the non-negative beat-match window; it accepts no path.
- `run_bidmc_align_resp_bench` calls the existing pinned-record BIDMC
  alignment/respiration bench against a local promoted dataset or the explicitly
  labeled synthetic CI fixture. It accepts no parameters or paths.
- `list_local_shadow_exports` lists local `*.jsonl` filenames and sizes only; it does
  not return record contents.
- `export_shadow_summary` validates one local, bounded JSONL file and returns only
  schema versions and aggregate capture/manifest counts. Despite its name, it is
  read-only and does not create or upload an export.

The two synthetic sensitivity tools are read-only and return `PI_TO_DEFINE` in every response,
including failures. Their outputs are engineering sensitivity summaries only;
`clinical_validation=false` and `synthetic_only=true` remain explicit. They neither
choose clinical cutoffs nor select a clinical baseline window.

The MIT-BIH and BIDMC tools are also read-only and network-free. Every success or
failure includes `clinical_validation=false`, a `PROXY / ENGINEERING ONLY` banner,
an explicit no-DS/no-clinical-claims statement, and the underlying dataset's
`master_verified_proxy` gate. PROXY verification authorizes an engineering bench;
it does not verify clinical performance. Neither tool accepts an arbitrary local
path, returns waveforms, or writes an artifact.

URI schemes (`s3://`, `gs://`, `http://`, `https://`, `file://`), network shares, and
paths marked as PHI or patient data are rejected before any directory is created.
The read tools apply the same URI/network-share/PHI-path rejection and fail closed on
unknown schema versions, malformed records, symlinks, non-JSONL files, or files over
10 MiB. No tool has a cloud transport or returns waveforms.
Every PASS, rejection, or fail-closed tool payload repeats the non-clinical safety
gates.

## Verify

```bash
python -m pytest tests/backend/unit/test_research_node_mcp.py \
  tests/backend/unit/test_research_node_mcp_stdio.py \
  tests/backend/integration/test_research_node_demo.py
```
