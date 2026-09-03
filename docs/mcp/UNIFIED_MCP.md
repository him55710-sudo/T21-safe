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
matrix from the repository root:

```bash
python -m pytest tests/backend/unit/test_mcp_stdio_smoke.py
```

The matrix starts each server, completes MCP `initialize`, and asserts its
`tools/list` response. See the server-specific guides for tool scope and additional
checks: [Fantasia MCP](FANTASIA_MCP.md) and
[Research Node MCP](RESEARCH_NODE_MCP.md).

> **Research Use Only / Shadow Mode · clinical_validation=false**

