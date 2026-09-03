# MCP tool catalog

**Status:** auto-generated · Path B / RUO / Shadow
**clinical_validation:** `false`

Regenerate:

```bash
PYTHONPATH=services/engine/src python scripts/generate_mcp_tool_catalog.py
```

This catalog is Research Use Only. It is not a clinical monitor. No dosing,
actuation, closed-loop, drug advice, EMR write, or DS clinical claims.
Every tool response must keep `clinical_validation=false`.

## fantasia-proxy (`t21-fantasia-mcp`)

| Tool | Description |
| --- | --- |
| `list_records` | List local Fantasia WFDB records and SHA-256 fixture status. |
| `load_sample` | Load at most 1000 samples from one local Fantasia WFDB record. |
| `run_hrv_proxy_bench` | Run the deterministic Fantasia HRV/age-stability PROXY benchmark. |

## research-node (`t21-research-node-mcp`)

| Tool | Description |
| --- | --- |
| `list_local_shadow_exports` | List local shadow JSONL exports without returning record content. |
| `export_shadow_summary` | Validate a local shadow JSONL file and return aggregate counts only. |
| `run_synthetic_demo` | Run deterministic synthetic alignment QC and observe-only replay. |
| `run_time_align_qc` | Run raw-clock alignment QC on a deterministic synthetic case. |
| `run_mitbih_beat_bench` | Run the pinned local MIT-BIH beat-detection PROXY engineering benchmark. |
| `run_bidmc_align_resp_bench` | Run the pinned local BIDMC alignment/RESP PROXY engineering benchmark. |
| `run_sqi_missingness_impact` | Run synthetic-only SQI/missingness engineering sensitivity; PI_TO_DEFINE. |
| `run_baseline_window_sensitivity` | Compare fixed 180/300-second synthetic baseline summaries; PI_TO_DEFINE. |
