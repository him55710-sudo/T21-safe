# Founder Cursor dual-MCP setup

> **Research Use Only / Shadow Mode**  
> **clinical_validation=false**  
> These tools are not a certified or validated patient monitor and must not be
> used for patient-care decisions.

1. From the repository root, install the engine into the Python environment Cursor
   will use:

   ```bash
   python -m pip install -e "services/engine[dev,wfdb]"
   ```

2. In Cursor's MCP settings, paste the complete dual `mcpServers` JSON block from
   [Unified local MCP configuration](UNIFIED_MCP.md#install). Replace both absolute
   path placeholders with the Python executable and this repository's paths.

3. Fully restart Cursor so it reloads the MCP server configuration.

4. Open Cursor's MCP tools view and verify that both `fantasia-proxy` and
   `research-node` appear with their tools. Their outputs must retain the
   `clinical_validation=false` and Research Use Only / Shadow Mode boundaries.

Before opening Cursor, verify both server processes directly from the repository
root:

```bash
python scripts/smoke_dual_mcp.py
```

Success prints one `PASS` line and the discovered tool list for each server. A
`FAIL` line produces a nonzero exit code. This check requires neither a live Cursor
desktop nor VitalDB.
