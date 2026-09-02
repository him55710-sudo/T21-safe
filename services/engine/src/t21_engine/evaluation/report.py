"""Serializable evaluation report helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def build_evaluation_report(
    metrics: dict[str, Any],
    *,
    dataset_version: str,
    dataset_checksum: str,
    feature_schema_version: str,
    model_version: str,
    seed: int,
) -> dict[str, Any]:
    return {
        "created_at": datetime.now(UTC).isoformat(),
        "dataset_version": dataset_version,
        "dataset_checksum": dataset_checksum,
        "feature_schema_version": feature_schema_version,
        "model_version": model_version,
        "deterministic_seed": seed,
        "metrics": metrics,
        "population": "generic non-DS research data only",
        "clinical_validation": False,
    }
