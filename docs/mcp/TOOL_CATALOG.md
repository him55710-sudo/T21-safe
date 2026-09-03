# MCP Tool Catalog

> **RUO / Path B / `clinical_validation=false`**
>
> Research Use Only. Path B engineering tooling. Not for clinical diagnosis,
> dosing, alerts, or drug-safety claims. Shadow / PROXY / synthetic scopes only.

This file is **auto-generated** by `scripts/generate_mcp_tool_catalog.py` from
`t21_engine.fantasia_mcp.server.TOOLS`,
`t21_engine.research_node_mcp.server.TOOLS`, and
`t21_engine.proxy_hyp_mcp.server.TOOLS`. Do not edit by hand.

Regenerate from the repository root:

```bash
python scripts/generate_mcp_tool_catalog.py
```

---

## fantasia-proxy

Local Fantasia WFDB sample and HRV/age-stability **PROXY** benchmark MCP tools.

| Tool name | Description |
| --- | --- |
| `list_records` | List local Fantasia WFDB records and SHA-256 fixture status. |
| `load_sample` | Load at most 1000 samples from one local Fantasia WFDB record. |
| `run_hrv_proxy_bench` | Run the deterministic Fantasia HRV/age-stability PROXY benchmark. |

---

## proxy-hyp

Local PROXY HYP-01/03/07 bench list/run MCP tools (MIT-BIH+Fantasia fixtures only).

| Tool name | Description |
| --- | --- |
| `list_proxy_hyp_benches` | List locked PROXY HYP-01/03/07 benches (MIT-BIH+Fantasia fixture-only; clinical_validation=false; LF/HF not primary; RQ-004 HYPOTHESIS). |
| `run_proxy_hyp_benches` | Run PROXY HYP-01/03/07 local benches and optionally write JSON/MD tables. No network; no BIDMC; no waveforms returned. |

---

## research-node

Synthetic demo/QC, shadow JSONL, SQI/baseline sensitivity, and BIDMC/MIT-BIH
**PROXY** benchmark MCP tools.

| Tool name | Description |
| --- | --- |
| `list_demo_presets` | List read-only synthetic Research Node demo CLI presets (no I/O). |
| `list_local_shadow_exports` | List local shadow JSONL exports without returning record content. |
| `export_shadow_summary` | Validate a local shadow JSONL file and return aggregate counts only. |
| `run_synthetic_demo` | Run deterministic synthetic alignment QC and observe-only replay. |
| `run_time_align_qc` | Run raw-clock alignment QC on a deterministic synthetic case. |
| `run_mitbih_beat_bench` | Run the pinned local MIT-BIH beat-detection PROXY engineering benchmark. |
| `run_bidmc_align_resp_bench` | Run the pinned local BIDMC alignment/RESP PROXY engineering benchmark. |
| `run_sqi_missingness_impact` | Run synthetic-only SQI/missingness engineering sensitivity; PI_TO_DEFINE. |
| `run_baseline_window_sensitivity` | Compare fixed 180/300-second synthetic baseline summaries; PI_TO_DEFINE. |

---

## Notes

- Banner: RUO / Path B / `clinical_validation=false`
- Source of truth: in-process `TOOLS` registries (no network)
- Output path: `docs/mcp/TOOL_CATALOG.md`
