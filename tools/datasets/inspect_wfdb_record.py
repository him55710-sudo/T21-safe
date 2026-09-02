#!/usr/bin/env python3
"""Inspect a bounded WFDB header from a local sample or an official HTTPS URL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

try:
    from ._common import DatasetToolError, positive_int, validate_open_https_url
except ImportError:  # direct script execution
    from _common import DatasetToolError, positive_int, validate_open_https_url


MAX_HEADER_BYTES = 128 * 1024


def parse_header(text: str, signal_limit: int) -> dict[str, object]:
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not lines:
        raise DatasetToolError("WFDB header is empty")
    first = lines[0].split()
    if len(first) < 3:
        raise DatasetToolError("WFDB first line must contain record, signal count, and sampling frequency")
    record = first[0]
    try:
        signal_count = int(first[1])
        sampling_frequency = float(first[2].split("/")[0])
    except ValueError as exc:
        raise DatasetToolError("WFDB signal count or sampling frequency is invalid") from exc
    if signal_count < 0:
        raise DatasetToolError("WFDB signal count cannot be negative")
    available = lines[1 : 1 + signal_count]
    if len(available) < signal_count:
        raise DatasetToolError(f"WFDB header declares {signal_count} signals but only {len(available)} lines are present")

    signals = []
    for index, line in enumerate(available[:signal_limit]):
        fields = line.split()
        if len(fields) < 2:
            raise DatasetToolError(f"WFDB signal line {index + 1} is malformed")
        description = " ".join(fields[8:]) if len(fields) > 8 else ""
        signals.append(
            {
                "index": index,
                "file": fields[0],
                "format": fields[1],
                "gain_units": fields[2] if len(fields) > 2 else None,
                "description": description,
            }
        )
    samples = None
    if len(first) > 3:
        try:
            samples = int(first[3])
        except ValueError:
            samples = first[3]
    return {
        "record": record,
        "signal_count": signal_count,
        "sampling_frequency_hz": sampling_frequency,
        "samples_per_signal": samples,
        "returned_signals": len(signals),
        "signals": signals,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", required=True, help="local .hea sample path or official HTTPS .hea URL")
    parser.add_argument("--limit", required=True, type=positive_int, help="maximum signal definitions to print")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.limit > 256:
            raise DatasetToolError("--limit must be 256 or less")
        if args.sample.startswith(("http://", "https://")):
            validate_open_https_url(args.sample)
            request = Request(args.sample, headers={"User-Agent": "T21Safe-RUO-WFDBInspector/1.0"})
            with urlopen(request, timeout=30) as response:
                payload = response.read(MAX_HEADER_BYTES + 1)
            source = args.sample
        else:
            path = Path(args.sample)
            payload = path.read_bytes()
            source = str(path.resolve())
        if len(payload) > MAX_HEADER_BYTES:
            raise DatasetToolError("WFDB header exceeds 128 KiB safety cap")
        result = parse_header(payload.decode("utf-8-sig"), args.limit)
        result["source"] = source
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (DatasetToolError, OSError, UnicodeError) as exc:
        print(f"inspect_wfdb_record: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
