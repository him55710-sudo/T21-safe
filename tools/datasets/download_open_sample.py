#!/usr/bin/env python3
"""Download one explicitly named open-data sample with a hard byte limit and manifest."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

try:
    from ._common import (
        DatasetToolError,
        dataset_by_id,
        inside_git_checkout,
        load_registry,
        positive_int,
        sha256_file,
        validate_open_https_url,
    )
except ImportError:  # direct script execution
    from _common import (
        DatasetToolError,
        dataset_by_id,
        inside_git_checkout,
        load_registry,
        positive_int,
        sha256_file,
        validate_open_https_url,
    )


DEFAULT_REGISTRY = Path(__file__).resolve().parents[2] / "research" / "dataset_registry.yaml"


def validate_dataset(row: dict[str, str]) -> None:
    if row.get("access_type") != "OPEN":
        raise DatasetToolError(
            f"dataset '{row.get('dataset_id')}' is {row.get('access_type')}; this tool will not bypass restricted access"
        )
    if not str(row.get("immediate_download_possible", "")).strip().lower().startswith(("yes", "true")):
        raise DatasetToolError("registry does not confirm immediate open download for this dataset")


def download_to_file(url: str, output: Path, byte_limit: int) -> tuple[str, int]:
    if output.exists():
        raise DatasetToolError(f"output already exists; refusing to overwrite: {output}")
    if inside_git_checkout(output):
        raise DatasetToolError("raw/sample downloads must be stored outside every Git checkout")
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name(output.name + ".part")
    if partial.exists():
        raise DatasetToolError(f"stale partial file exists; inspect and remove it first: {partial}")

    request = Request(url, headers={"User-Agent": "T21Safe-RUO-SampleDownloader/1.0"})
    written = 0
    final_url = url
    try:
        with urlopen(request, timeout=60) as response, partial.open("xb") as handle:
            final_url = response.geturl()
            validate_open_https_url(final_url)
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > byte_limit:
                raise DatasetToolError(
                    f"server reports {declared} bytes, exceeding explicit --limit {byte_limit}"
                )
            while True:
                chunk = response.read(min(1024 * 1024, byte_limit - written + 1))
                if not chunk:
                    break
                written += len(chunk)
                if written > byte_limit:
                    raise DatasetToolError(f"download exceeded explicit --limit {byte_limit} bytes")
                handle.write(chunk)
        os.replace(partial, output)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    return final_url, written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", required=True, help="exact HTTPS URL of one official open-data file")
    parser.add_argument("--limit", required=True, type=positive_int, help="hard maximum bytes to download")
    parser.add_argument("--dataset-id", required=True, help="OPEN dataset_id in dataset_registry.yaml")
    parser.add_argument("--output", required=True, type=Path, help="destination outside a Git checkout")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        validate_open_https_url(args.sample)
        row = dataset_by_id(load_registry(args.registry), args.dataset_id)
        validate_dataset(row)
        manifest_path = args.output.with_name(args.output.name + ".manifest.json")
        if manifest_path.exists():
            raise DatasetToolError(f"manifest already exists; refusing to overwrite: {manifest_path}")
        final_url, size = download_to_file(args.sample, args.output, args.limit)
        manifest = {
            "manifest_version": "1.0.0",
            "research_use_only": True,
            "dataset_id": row["dataset_id"],
            "source": args.sample,
            "resolved_source": final_url,
            "version": row["current_version"],
            "license": row["license"],
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            "file": str(args.output.resolve()),
            "size_bytes": size,
            "sha256": sha256_file(args.output),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"file": str(args.output), "manifest": str(manifest_path), "size_bytes": size}, indent=2))
        return 0
    except (DatasetToolError, OSError, ValueError) as exc:
        print(f"download_open_sample: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
