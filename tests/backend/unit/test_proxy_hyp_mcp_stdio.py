"""CODEX-109: stdio smoke for PROXY HYP MCP."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

MEETING_ONEPAGER_POINTER = "docs/founder/MEETING_ONEPAGER_PROXY_v0.1_KR.md"
REQUIRED_TOOL_CLAIM_GUARDS = (
    "Path B",
    "Research Use Only",
    "clinical_validation=false",
    "no FACT",
)


def test_stdio_initialize_and_list_tools() -> None:
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
                "clientInfo": {"name": "pytest-smoke", "version": "1.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    completed = subprocess.run(
        [sys.executable, "-m", "t21_engine.proxy_hyp_mcp.server"],
        input="".join(json.dumps(r) + "\n" for r in requests),
        text=True,
        capture_output=True,
        cwd=repository_root,
        env=env,
        timeout=10,
        check=True,
    )
    responses = [json.loads(line) for line in completed.stdout.splitlines()]
    assert completed.stderr == ""
    assert responses[0]["result"]["serverInfo"]["name"] == "t21-proxy-hyp-mcp"
    tools = responses[1]["result"]["tools"]
    names = {tool["name"] for tool in tools}
    assert names == {"list_proxy_hyp_benches", "run_proxy_hyp_benches"}
    for tool in tools:
        description = tool["description"]
        assert MEETING_ONEPAGER_POINTER in description
        for guard in REQUIRED_TOOL_CLAIM_GUARDS:
            assert guard in description, (
                f"{tool['name']}: missing claim guard {guard!r}"
            )


def test_stdio_run_proxy_hyp_benches_clinical_false(tmp_path: Path) -> None:
    repository_root = Path(__file__).parents[3]
    engine_source = repository_root / "services" / "engine" / "src"
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(engine_source), existing) if part
    )
    out = tmp_path / "mcp-out"
    requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "run_proxy_hyp_benches",
                "arguments": {"output_dir": str(out)},
            },
        }
    ]
    completed = subprocess.run(
        [sys.executable, "-m", "t21_engine.proxy_hyp_mcp.server"],
        input="".join(json.dumps(r) + "\n" for r in requests),
        text=True,
        capture_output=True,
        cwd=repository_root,
        env=env,
        timeout=30,
        check=True,
    )
    response = json.loads(completed.stdout.splitlines()[0])
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["status"] == "PASS"
    assert payload["clinical_validation"] is False
    assert "BIDMC" in payload.get("prohibited", [])
    assert payload.get("pooled_instability_score") is None
