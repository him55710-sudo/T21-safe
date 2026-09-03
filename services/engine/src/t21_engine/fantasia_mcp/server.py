"""Minimal newline-delimited stdio MCP server for local Fantasia tools."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from typing import Any, TextIO

from t21_engine.fantasia_mcp.handlers import list_records, load_sample, run_hrv_proxy_bench

SERVER_INFO = {"name": "t21-fantasia-mcp", "version": "0.1.0"}
TOOLS = [
    {
        "name": "list_records",
        "description": "List local Fantasia WFDB records and SHA-256 fixture status.",
        "inputSchema": {
            "type": "object",
            "properties": {"sample_root": {"type": "string"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "load_sample",
        "description": "Load at most 1000 samples from one local Fantasia WFDB record.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sample_root": {"type": "string"},
                "record": {"type": "string", "default": "f1o01"},
                "sample_count": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "run_hrv_proxy_bench",
        "description": "Run the deterministic Fantasia HRV/age-stability PROXY benchmark.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sample_root": {"type": "string"},
                "record": {"type": "string", "default": "f1o01"},
            },
            "additionalProperties": False,
        },
    },
]
HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    "list_records": list_records,
    "load_sample": load_sample,
    "run_hrv_proxy_bench": run_hrv_proxy_bench,
}


def _response(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    """Handle the MCP subset used by stdio clients."""
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
                "isError": payload.get("status") != "PASS",
            },
        )
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": "Method not found"},
    }


def serve(stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> None:
    """Serve newline-delimited JSON-RPC without writing diagnostics to stdout."""
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
