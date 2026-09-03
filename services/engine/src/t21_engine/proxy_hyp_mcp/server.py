"""Minimal newline-delimited stdio MCP server for PROXY HYP-01/03/07 tools."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from typing import Any, TextIO

from t21_engine.proxy_hyp_mcp.handlers import (
    list_proxy_hyp_benches,
    run_proxy_hyp_benches_tool,
)

SERVER_INFO = {"name": "t21-proxy-hyp-mcp", "version": "0.1.0"}
TOOLS = [
    {
        "name": "list_proxy_hyp_benches",
        "description": (
            "List locked PROXY HYP-01/03/07 benches (MIT-BIH+Fantasia fixture-only; "
            "clinical_validation=false; LF/HF not primary; RQ-004 HYPOTHESIS)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "run_proxy_hyp_benches",
        "description": (
            "Run PROXY HYP-01/03/07 local benches and optionally write JSON/MD tables. "
            "No network; no BIDMC; no waveforms returned."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "mitbih_root": {"type": "string"},
                "fantasia_root": {"type": "string"},
                "output_dir": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
]
HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    "list_proxy_hyp_benches": list_proxy_hyp_benches,
    "run_proxy_hyp_benches": run_proxy_hyp_benches_tool,
}


def _response(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return _response(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        )
    if method == "tools/list":
        return _response(request_id, {"tools": TOOLS})
    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name") if isinstance(params, dict) else None
        arguments = params.get("arguments", {}) if isinstance(params, dict) else {}
        handler = HANDLERS.get(name) if isinstance(name, str) else None
        if handler is None or not isinstance(arguments, dict):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "Unknown tool or invalid arguments"},
            }
        try:
            payload = handler(**arguments)
        except TypeError:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "Invalid tool arguments"},
            }
        return _response(
            request_id,
            {
                "content": [{"type": "text", "text": json.dumps(payload, separators=(",", ":"))}],
                "isError": payload.get("status") not in {"PASS", "REJECTED"},
            },
        )
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": "Method not found"},
    }


def serve(stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> None:
    for line in stdin:
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                raise TypeError
            response = handle_request(request)
        except (json.JSONDecodeError, TypeError):
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
        if response is not None:
            stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
            stdout.flush()


def main() -> None:
    serve()


if __name__ == "__main__":
    main()
