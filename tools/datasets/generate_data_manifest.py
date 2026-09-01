#!/usr/bin/env python3
"""Generate a checksum manifest for one explicitly bounded local sample."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from ._common import DatasetToolError, limited_files, positive_int, sha256_file
except ImportError:  # direct script execution
    from _common import DatasetToolError, limited_files, positive_int, sha256_file


def build_manifest(sample: Path, limit: int, source: str, version: str, license_name: str) -> dict[str, object]:
    files = limited_files(sample, limit)
    base = sample if sample.is_dir() else sample.parent
    entries = []
    for path in files:
        entries.append(
            {
                "path": path.relative_to(base).as_posix() if sample.is_dir() else path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {
        "manifest_version": "1.0.0",
        "research_use_only": True,
        "source": source,
        "version": version,
        "license": license_name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sample_root": str(sample.resolve()),
        "file_count": len(entries),
        "files": entries,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", required=True, type=Path, help="one local file or directory")
    parser.add_argument("--limit", required=True, type=positive_int, help="maximum files allowed")
    parser.add_argument("--source", required=True, help="official source URL or institutional accession")
    parser.add_argument("--version", required=True)
    parser.add_argument("--license", required=True, dest="license_name")
    parser.add_argument("--output", type=Path, help="write JSON here; defaults to stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = build_manifest(args.sample, args.limit, args.source, args.version, args.license_name)
        serialized = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            if args.output.exists():
                raise DatasetToolError(f"output already exists; refusing to overwrite: {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized, encoding="utf-8")
            print(json.dumps({"manifest": str(args.output), "file_count": manifest["file_count"]}, indent=2))
        else:
            print(serialized, end="")
        return 0
    except (DatasetToolError, OSError) as exc:
        print(f"generate_data_manifest: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

