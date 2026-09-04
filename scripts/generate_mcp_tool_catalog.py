#!/usr/bin/env python3
"""Auto-generate docs/mcp/TOOL_CATALOG.md from Fantasia and Research Node TOOLS."""

from __future__ import annotations

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ENGINE_SOURCE = REPOSITORY_ROOT / "services" / "engine" / "src"
OUTPUT_PATH = REPOSITORY_ROOT / "docs" / "mcp" / "TOOL_CATALOG.md"

_engine_src = str(ENGINE_SOURCE)
if _engine_src not in sys.path:
    sys.path.insert(0, _engine_src)

from t21_engine.fantasia_mcp.server import TOOLS as FANTASIA_TOOLS  # noqa: E402
from t21_engine.research_node_mcp.server import TOOLS as RESEARCH_TOOLS  # noqa: E402
from t21_engine.proxy_hyp_mcp.server import TOOLS as PROXY_HYP_TOOLS  # noqa: E402


def _tool_rows(tools: list[dict]) -> str:
    lines = ["| Tool name | Description |", "| --- | --- |"]
    for tool in tools:
        name = str(tool.get("name", "")).replace("|", "\\|")
        desc = str(tool.get("description", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{name}` | {desc} |")
    return "\n".join(lines)


def render_catalog() -> str:
    """Return markdown for the RUO / Path B MCP tool catalog."""
    return f"""# MCP Tool Catalog

> **RUO / Path B / `clinical_validation=false`**
>
> Research Use Only. Path B engineering tooling. Not for clinical diagnostic use,
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

{_tool_rows(list(FANTASIA_TOOLS))}

---

## proxy-hyp

Local PROXY HYP-01/03/07 bench list/run MCP tools (MIT-BIH+Fantasia fixtures only).

{_tool_rows(list(PROXY_HYP_TOOLS))}

---

## research-node

Synthetic demo/QC, shadow JSONL, SQI/baseline sensitivity, and BIDMC/MIT-BIH
**PROXY** benchmark MCP tools.

{_tool_rows(list(RESEARCH_TOOLS))}

---

## Notes

- Banner: RUO / Path B / `clinical_validation=false`
- Source of truth: in-process `TOOLS` registries (no network)
- Output path: `docs/mcp/TOOL_CATALOG.md`
"""


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = render_catalog()
    if not text.endswith("\n"):
        text += "\n"
    OUTPUT_PATH.write_text(text, encoding="utf-8")
    print(OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
