#!/usr/bin/env python3
"""Initialize both local MCP servers over stdio and list their tools."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ENGINE_SOURCE = REPOSITORY_ROOT / "services" / "engine" / "src"


@dataclass(frozen=True)
class ServerSpec:
    label: str
    module: str
    server_name: str
    expected_tools: frozenset[str]


SERVERS = (
    ServerSpec(
        label="fantasia-proxy",
        module="t21_engine.fantasia_mcp.server",
        server_name="t21-fantasia-mcp",
        expected_tools=frozenset(
            {"list_records", "load_sample", "run_hrv_proxy_bench"}
        ),
    ),
    ServerSpec(
        label="research-node",
        module="t21_engine.research_node_mcp.server",
        server_name="t21-research-node-mcp",
        expected_tools=frozenset(
            {
                "run_synthetic_demo",
                "run_time_align_qc",
                "run_sqi_missingness_impact",
                "run_baseline_window_sensitivity",
            }
        ),
    ),
)


def smoke_server(spec: ServerSpec, *, timeout: float = 10) -> list[str]:
    """Return the advertised tools after validating the MCP handshake."""
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(ENGINE_SOURCE), existing_pythonpath) if part
    )
    requests = (
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "dual-mcp-smoke", "version": "1.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    )
    completed = subprocess.run(
        [sys.executable, "-m", spec.module],
        input="".join(json.dumps(request) + "\n" for request in requests),
        text=True,
        capture_output=True,
        cwd=REPOSITORY_ROOT,
        env=env,
        timeout=timeout,
        check=False,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or f"exit code {completed.returncode}"
        raise RuntimeError(detail)
    if completed.stderr:
        raise RuntimeError(f"server wrote to stderr: {completed.stderr.strip()}")

    responses = [json.loads(line) for line in completed.stdout.splitlines()]
    if len(responses) != 2:
        raise RuntimeError(f"expected 2 responses, received {len(responses)}")

    initialize = responses[0]
    if initialize.get("id") != 1:
        raise RuntimeError("initialize response id was not 1")
    actual_name = initialize.get("result", {}).get("serverInfo", {}).get("name")
    if actual_name != spec.server_name:
        raise RuntimeError(
            f"expected server name {spec.server_name!r}, received {actual_name!r}"
        )

    tools_response = responses[1]
    if tools_response.get("id") != 2:
        raise RuntimeError("tools/list response id was not 2")
    tools = sorted(
        tool["name"] for tool in tools_response.get("result", {}).get("tools", [])
    )
    if set(tools) != spec.expected_tools:
        raise RuntimeError(
            f"expected tools {sorted(spec.expected_tools)!r}, received {tools!r}"
        )
    return tools


def main() -> int:
    print("Research Use Only / Shadow Mode | clinical_validation=false")
    failed = False
    for spec in SERVERS:
        try:
            tools = smoke_server(spec)
        except (OSError, subprocess.SubprocessError, ValueError, RuntimeError) as exc:
            failed = True
            print(f"FAIL {spec.label}: {exc}")
        else:
            print(f"PASS {spec.label}: {', '.join(tools)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
