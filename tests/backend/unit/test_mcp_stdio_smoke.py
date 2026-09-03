from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


PROXY_PUBLIC_BENCH_TOOLS = frozenset(
    {"run_mitbih_beat_bench", "run_bidmc_align_resp_bench"}
)


@pytest.mark.parametrize(
    ("module", "server_name", "expected_tools"),
    [
        (
            "t21_engine.fantasia_mcp.server",
            "t21-fantasia-mcp",
            {"list_records", "load_sample", "run_hrv_proxy_bench"},
        ),
        (
            "t21_engine.research_node_mcp.server",
            "t21-research-node-mcp",
            {
                "run_synthetic_demo",
                "run_time_align_qc",
                "run_sqi_missingness_impact",
                "run_baseline_window_sensitivity",
                "list_local_shadow_exports",
                "export_shadow_summary",
                "run_mitbih_beat_bench",
                "run_bidmc_align_resp_bench",
            },
        ),
    ],
    ids=("fantasia-proxy", "research-node"),
)
def test_mcp_stdio_initialize_and_tools_list(
    module: str, server_name: str, expected_tools: set[str]
) -> None:
    """Smoke-test both real stdio servers without a live desktop client."""
    repository_root = Path(__file__).parents[3]
    engine_source = repository_root / "services" / "engine" / "src"
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(engine_source), existing_pythonpath) if part
    )
    requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "pytest-shared-smoke", "version": "1.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]

    completed = subprocess.run(
        [sys.executable, "-m", module],
        input="".join(json.dumps(request) + "\n" for request in requests),
        text=True,
        capture_output=True,
        cwd=repository_root,
        env=env,
        timeout=10,
        check=True,
    )

    responses = [json.loads(line) for line in completed.stdout.splitlines()]
    assert completed.stderr == ""
    assert len(responses) == 2
    assert responses[0]["id"] == 1
    assert responses[0]["result"]["serverInfo"]["name"] == server_name
    assert responses[0]["result"]["capabilities"] == {"tools": {}}
    assert responses[1]["id"] == 2
    advertised = {tool["name"] for tool in responses[1]["result"]["tools"]}
    assert advertised == expected_tools
    if server_name == "t21-research-node-mcp":
        assert PROXY_PUBLIC_BENCH_TOOLS <= advertised
