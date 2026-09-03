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
        "list_demo_presets",
        "list_local_shadow_exports",
        "export_shadow_summary",
        "run_synthetic_demo",
        "run_time_align_qc",
        "run_sqi_missingness_impact",
        "run_baseline_window_sensitivity",
        "run_mitbih_beat_bench",
        "run_bidmc_align_resp_bench",
    }


def test_stdio_list_demo_presets_call_clinical_validation_false() -> None:
    """CODEX-046: stdio tools/call list_demo_presets is error-free RUO."""
    repository_root = Path(__file__).parents[3]
    engine_source = repository_root / "services" / "engine" / "src"
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(engine_source), existing) if part
    )
    requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "pytest-presets", "version": "1.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "list_demo_presets", "arguments": {}},
        },
    ]
    completed = subprocess.run(
        [sys.executable, "-m", "t21_engine.research_node_mcp.server"],
        input="".join(json.dumps(request) + chr(10) for request in requests),
        text=True,
        capture_output=True,
        cwd=repository_root,
        env=env,
        timeout=15,
        check=True,
    )
    responses = [json.loads(line) for line in completed.stdout.splitlines()]
    assert completed.stderr == ""
    payload = json.loads(responses[-1]["result"]["content"][0]["text"])
    assert responses[-1]["result"]["isError"] is False
    assert payload["status"] == "PASS"
    assert payload["clinical_validation"] is False
    assert payload["presets"][0]["id"] == "default"
