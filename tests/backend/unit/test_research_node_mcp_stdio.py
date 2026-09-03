from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_stdio_server_initialize_and_lists_tools() -> None:
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
                "clientInfo": {"name": "pytest-smoke", "version": "1.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]

    completed = subprocess.run(
        [sys.executable, "-m", "t21_engine.research_node_mcp.server"],
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
    assert responses[0]["result"]["serverInfo"]["name"] == "t21-research-node-mcp"
    assert {tool["name"] for tool in responses[1]["result"]["tools"]} == {
        "run_synthetic_demo",
        "run_time_align_qc",
        "run_sqi_missingness_impact",
        "run_baseline_window_sensitivity",
    }
