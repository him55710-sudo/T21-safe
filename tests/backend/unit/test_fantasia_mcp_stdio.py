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


def test_stdio_hrv_bench_fail_closed_keeps_non_clinical_age_banners() -> None:
    """CODEX-043: stdio tools/call keeps clinical_validation=false and age claim bans."""
    repository_root = Path(__file__).parents[3]
    engine_source = repository_root / "services" / "engine" / "src"
    fixture = (
        repository_root / "tests" / "backend" / "fixtures" / "wfdb_fantasia_synthetic"
    )
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
                "clientInfo": {"name": "pytest-age-pin", "version": "1.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "run_hrv_proxy_bench",
                "arguments": {"sample_root": str(fixture)},
            },
        },
    ]
    completed = subprocess.run(
        [sys.executable, "-m", "t21_engine.fantasia_mcp.server"],
        input="".join(json.dumps(request) + chr(10) for request in requests),
        text=True,
        capture_output=True,
        cwd=repository_root,
        env=env,
        timeout=30,
        check=True,
    )
    responses = [json.loads(line) for line in completed.stdout.splitlines()]
    assert completed.stderr == ""
    payload = json.loads(responses[-1]["result"]["content"][0]["text"])
    assert payload["clinical_validation"] is False
    assert "clinical_age_effect" in payload["prohibited_claims"]
    assert frozenset(payload["prohibited_claims"]) >= frozenset(
        {"DS", "anesthesia", "clinical_age_effect", "PTT_PPG"}
    )
    # PASS path pins PI_TO_DEFINE; FAIL path (no wfdb) must still refuse clinical age claims.
    if payload["status"] == "PASS":
        age = payload["records"][0]["age_stability"]
        assert age["reason"] == "PI_TO_DEFINE"
        assert age["age_metadata_available"] is False
        assert payload["aggregate"]["age_stability_status"] == "UNAVAILABLE"
    else:
        assert payload["status"] == "FAIL"
        blob = json.dumps(payload).lower()
        assert "years old" not in blob
