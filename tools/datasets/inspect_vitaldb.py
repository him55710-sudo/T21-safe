#!/usr/bin/env python3
"""Inspect a bounded slice of VitalDB case metadata; never fetch waveform bulk data."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

try:
    from ._common import DatasetToolError, positive_int, validate_open_https_url
except ImportError:  # direct script execution
    from _common import DatasetToolError, positive_int, validate_open_https_url


DEFAULT_CASES_URL = "https://api.vitaldb.net/cases"
MAX_METADATA_BYTES = 4 * 1024 * 1024


def parse_payload(payload: bytes, limit: int) -> list[dict[str, Any]]:
    text = payload.decode("utf-8-sig")
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise DatasetToolError("VitalDB metadata is neither valid JSON nor headered CSV")
        return [dict(row) for _, row in zip(range(limit), reader)]

    if isinstance(decoded, list):
        rows = decoded
    elif isinstance(decoded, dict):
        rows = next(
            (decoded[key] for key in ("data", "cases", "results") if isinstance(decoded.get(key), list)),
            None,
        )
        if rows is None:
            rows = [decoded]
    else:
        raise DatasetToolError("VitalDB metadata JSON must be an object or list")
    return [row if isinstance(row, dict) else {"value": row} for row in rows[:limit]]


def read_bounded(handle: Any, max_bytes: int = MAX_METADATA_BYTES) -> bytes:
    payload = handle.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise DatasetToolError(
            f"metadata response exceeds the {max_bytes}-byte safety cap; use a pre-sampled metadata file"
        )
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", required=True, type=positive_int, help="maximum metadata rows to print (required)")
    parser.add_argument("--sample", type=Path, help="optional local synthetic/open metadata JSON or CSV")
    parser.add_argument("--url", default=DEFAULT_CASES_URL, help="official VitalDB case-metadata endpoint")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.limit > 100:
            raise DatasetToolError("--limit must be 100 or less for metadata inspection")
        if args.sample:
            payload = args.sample.read_bytes()
            if len(payload) > MAX_METADATA_BYTES:
                raise DatasetToolError("local metadata sample exceeds the 4 MiB safety cap")
            source = str(args.sample.resolve())
        else:
            validate_open_https_url(args.url)
            request = Request(args.url, headers={"User-Agent": "T21Safe-RUO-DatasetInspector/1.0"})
            with urlopen(request, timeout=30) as response:
                payload = read_bounded(response)
            source = args.url
        records = parse_payload(payload, args.limit)
        print(json.dumps({"source": source, "returned": len(records), "records": records}, indent=2, ensure_ascii=False))
        return 0
    except (DatasetToolError, OSError, UnicodeError) as exc:
        print(f"inspect_vitaldb: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
