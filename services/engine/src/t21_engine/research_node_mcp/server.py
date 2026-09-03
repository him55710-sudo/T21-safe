"""Newline-delimited stdio MCP server for the synthetic Research Node."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from typing import Any, TextIO

from t21_engine.research_node_mcp.handlers import (
    run_baseline_window_sensitivity,
    run_sqi_missingness_impact,
    run_synthetic_demo,
    run_time_align_qc,
)

SERVER_INFO = {"name": "t21-research-node-mcp", "version": "0.1.0"}
_COMMON_PROPERTIES = {
    "duration_seconds": {"type": "number", "minimum": 10, "default": 12},
    "seed": {"type": "integer", "default": 20250321},
}
TOOLS = [
    {
        "name": "run_synthetic_demo",
        "description": "Run deterministic synthetic alignment QC and observe-only replay.",
        "inputSchema": {
            "type": "object",
            "properties": {
                **_COMMON_PROPERTIES,
                "baseline_seconds": {"type": "integer", "minimum": 1, "default": 3},
                "output_dir": {
                    "type": "string",
                    "description": (
                        "Optional local-only directory for metadata JSONL and ExportManifest."
                    ),
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "run_time_align_qc",
        "description": "Run raw-clock alignment QC on a deterministic synthetic case.",
        "inputSchema": {
            "type": "object",
            "properties": _COMMON_PROPERTIES,
            "additionalProperties": False,
        },
    },
    {
        "name": "run_sqi_missingness_impact",
        "description": (
            "Run synthetic-only SQI/missingness engineering sensitivity; PI_TO_DEFINE."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "sample_rate_hz": {"type": "number", "exclusiveMinimum": 0, "default": 100},
                "window_seconds": {"type": "number", "exclusiveMinimum": 0, "default": 30},
                "gap_fractions": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0, "maximum": 1},
                    "minItems": 1,
                    "default": [0, 0.1, 0.25],
                },
                "noise_std": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0},
                    "minItems": 1,
                    "default": [0, 0.2],
                },
                "seed": {"type": "integer", "default": 20250321},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "run_baseline_window_sensitivity",
        "description": (
            "Compare fixed 180/300-second synthetic baseline summaries; PI_TO_DEFINE."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "sample_rate_hz": {"type": "number", "exclusiveMinimum": 0, "default": 25},
                "seed": {"type": "integer", "default": 20250321},
            },
            "additionalProperties": False,
        },
    },
]
HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    "run_synthetic_demo": run_synthetic_demo,
    "run_time_align_qc": run_time_align_qc,
    "run_sqi_missingness_impact": run_sqi_missingness_impact,
    "run_baseline_window_sensitivity": run_baseline_window_sensitivity,
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
                "isError": payload.get("status") != "PASS",
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
