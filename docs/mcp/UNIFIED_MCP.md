# Unified local MCP configuration

> **Research Use Only / Shadow Mode**  
> **clinical_validation=false**  
> Neither server is a certified or validated patient monitor, and neither may be
> used for patient-care decisions.

This configuration registers both local T21 Safe MCP servers. The Fantasia proxy is
bounded to the local `PROXY_HRV_AGE_STABILITY` engineering workflow; the Research
Node is bounded to deterministic synthetic demo and engineering-QC workflows.

## Install

From the repository root, install the engine in editable mode into the Python
environment used by the MCP client:

```bash
python -m pip install -e "services/engine[dev,wfdb]"
```

The install provides `t21-fantasia-mcp` and `t21-research-node-mcp`. Desktop clients
may not inherit the shell's `PATH`, so the ready-to-paste configuration below uses
the module entry points instead. Replace `/absolute/path/to/python` and the
repository path with absolute paths for your environment:

```json
{
  "mcpServers": {
    "fantasia-proxy": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "t21_engine.fantasia_mcp.server"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/T21-safe/services/engine/src"
      }
    },
    "research-node": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "t21_engine.research_node_mcp.server"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/T21-safe/services/engine/src"
      }
    }
  }
}
```

With the editable install, `PYTHONPATH` is normally unnecessary. It is included so
the same block also works directly from a source checkout. If preferred, remove each
`env` entry and use `t21-fantasia-mcp` or `t21-research-node-mcp` as the corresponding
`command`, with `"args": []`; use absolute executable paths if the client cannot find
them.

No live desktop client is needed to verify either server. Run the shared stdio smoke
script from the repository root:

```bash
python scripts/smoke_dual_mcp.py
```

It prints a `PASS` or `FAIL` result and the discovered tool list for each server.
For a one-command Founder DX Path B check (demo + dual-MCP smoke + `TOOL_CATALOG` dry-diff), run `bash scripts/verify_path_b_mcp.sh`.
The equivalent pytest checks are:

```bash
python -m pytest tests/backend/unit/test_mcp_stdio_smoke.py \
  tests/backend/unit/test_smoke_dual_mcp_script.py
```

These checks start each server, complete MCP `initialize`, and assert its
`tools/list` response. See the server-specific guides for tool scope and additional
checks: [Fantasia MCP](FANTASIA_MCP.md) and
[Research Node MCP](RESEARCH_NODE_MCP.md).

For the short Cursor install-and-restart sequence, see the
[Founder dual-MCP setup checklist](FOUNDER_DUAL_MCP_SETUP.md).

The Research Node advertises `run_synthetic_demo`, `run_time_align_qc`,
`run_sqi_missingness_impact`, `run_baseline_window_sensitivity`,
`run_mitbih_beat_bench`, and `run_bidmc_align_resp_bench`, plus the two bounded
shadow-export inspection tools. The MIT-BIH and BIDMC tools are read-only,
network-free PROXY engineering benches with pinned records, no arbitrary path input,
`clinical_validation=false`, and no DS or clinical claims.

> **Research Use Only / Shadow Mode · clinical_validation=false**
