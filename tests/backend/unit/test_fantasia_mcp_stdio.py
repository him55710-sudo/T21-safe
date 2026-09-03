from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_stdio_server_initialize_and_lists_tools() -> None:
    """Smoke-test the real stdio process without a desktop client or dataset download."""
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
        [sys.executable, "-m", "t21_engine.fantasia_mcp.server"],
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
    assert responses[0]["result"]["serverInfo"]["name"] == "t21-fantasia-mcp"
    assert responses[0]["result"]["capabilities"] == {"tools": {}}
    assert responses[1]["id"] == 2
    assert {tool["name"] for tool in responses[1]["result"]["tools"]} == {
        "list_records",
        "load_sample",
        "run_hrv_proxy_bench",
    }
