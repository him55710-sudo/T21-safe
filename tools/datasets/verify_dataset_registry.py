#!/usr/bin/env python3
"""Validate the YAML/CSV dataset registry pair under an explicit row cap."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from ._common import DatasetToolError, load_registry, positive_int, require_fields
except ImportError:  # direct script execution
    from _common import DatasetToolError, load_registry, positive_int, require_fields


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_YAML = REPO_ROOT / "research" / "dataset_registry.yaml"
DEFAULT_CSV = REPO_ROOT / "research" / "dataset_registry.csv"
ACCESS_TYPES = {"OPEN", "CREDENTIAL_REQUIRED", "INSTITUTIONAL", "UNKNOWN"}
SETTINGS = {"INTRAOPERATIVE", "PROCEDURAL_SEDATION", "ICU", "HEALTHY_VOLUNTEER", "AMBULATORY"}
DS_VALUES = {"YES", "NO", "UNCERTAIN"}
ROLES = {
    "LIVE_DEMO",
    "SIGNAL_PRETRAINING",
    "FEATURE_VALIDATION",
    "GENERIC_EVENT_MODEL",
    "EXTERNAL_VALIDATION",
    "DS_FINE_TUNING",
    "NOT_RECOMMENDED",
}
EVIDENCE = {
    "VERIFIED_CLINICAL_EVIDENCE",
    "VERIFIED_OFFICIAL_INFORMATION",
    "LIMITED_EVIDENCE",
    "RESEARCH_HYPOTHESIS",
    "PRODUCT_ASSUMPTION",
    "UNSUPPORTED_OR_REJECTED",
}


def normalize(row: dict[str, Any], fields: list[str]) -> dict[str, str]:
    return {field: "" if row.get(field) is None else str(row.get(field)) for field in fields}


def validate_registry(payload: dict[str, Any], csv_rows: list[dict[str, str]], limit: int) -> list[str]:
    errors: list[str] = []
    fields = payload.get("field_order")
    datasets = payload.get("datasets")
    if not isinstance(fields, list) or not fields or len(fields) != len(set(fields)):
        return ["field_order must be a non-empty list of unique field names"]
    if not isinstance(datasets, list):
        return ["datasets must be a list"]
    if len(datasets) > limit:
        return [f"registry has {len(datasets)} rows, exceeding explicit --limit {limit}"]
    if len(datasets) < 12:
        errors.append("registry must contain at least 12 datasets")
    if len(csv_rows) != len(datasets):
        errors.append(f"CSV row count {len(csv_rows)} does not match YAML row count {len(datasets)}")
    csv_fields = list(csv_rows[0].keys()) if csv_rows else []
    if csv_fields != fields:
        errors.append("CSV header order does not exactly match field_order")

    ids: set[str] = set()
    for index, raw in enumerate(datasets, start=1):
        if not isinstance(raw, dict):
            errors.append(f"row {index}: dataset must be an object")
            continue
        context = f"row {index} ({raw.get('dataset_id', '<missing>')})"
        errors.extend(require_fields(raw, fields, context))
        dataset_id = str(raw.get("dataset_id", ""))
        if dataset_id in ids:
            errors.append(f"{context}: duplicate dataset_id")
        ids.add(dataset_id)
        if raw.get("access_type") not in ACCESS_TYPES:
            errors.append(f"{context}: invalid access_type '{raw.get('access_type')}'")
        if raw.get("setting") not in SETTINGS:
            errors.append(f"{context}: invalid setting '{raw.get('setting')}'")
        if raw.get("down_syndrome_identifiable") not in DS_VALUES:
            errors.append(f"{context}: invalid down_syndrome_identifiable value")
        if raw.get("recommended_project_role") not in ROLES:
            errors.append(f"{context}: invalid recommended_project_role")
        if raw.get("evidence_status") not in EVIDENCE:
            errors.append(f"{context}: invalid evidence_status")
        source = urlparse(str(raw.get("official_source", "")))
        if source.scheme != "https" or not source.netloc:
            errors.append(f"{context}: official_source must be an HTTPS URL")
        if str(raw.get("last_verified_date")) != str(payload.get("last_verified_date")):
            errors.append(f"{context}: last_verified_date differs from registry header")
        verified_ds_count = str(raw.get("DS_case_count_verified")).strip()
        if (
            raw.get("down_syndrome_identifiable") != "YES"
            and verified_ds_count.isdigit()
            and int(verified_ds_count) > 0
        ):
            errors.append(f"{context}: positive DS count requires down_syndrome_identifiable=YES")

    for index, (yaml_row, csv_row) in enumerate(zip(datasets, csv_rows), start=1):
        if normalize(yaml_row, fields) != normalize(csv_row, fields):
            errors.append(f"row {index}: YAML and CSV values differ")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", required=True, type=positive_int, help="maximum allowed registry rows")
    parser.add_argument("--sample", type=Path, default=DEFAULT_YAML, help="registry YAML sample/path")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = load_registry(args.sample)
        with args.csv.open("r", encoding="utf-8-sig", newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
        errors = validate_registry(payload, csv_rows, args.limit)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, ensure_ascii=False), file=sys.stderr)
            return 2
        print(
            json.dumps(
                {
                    "valid": True,
                    "datasets": len(payload["datasets"]),
                    "fields": len(payload["field_order"]),
                    "yaml": str(args.sample),
                    "csv": str(args.csv),
                },
                indent=2,
            )
        )
        return 0
    except (DatasetToolError, OSError, csv.Error) as exc:
        print(f"verify_dataset_registry: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
