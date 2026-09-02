"""Read-only model registry validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast


def load_registry(path: Path) -> dict[str, Any]:
    """Load the registry's JSON-compatible YAML subset without an extra parser dependency."""
    payload = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    if payload.get("schema_version") != "1.0":
        raise ValueError("unsupported model registry schema")
    return payload


def register_research_model(path: Path, entry: dict[str, Any]) -> None:
    """Atomically add a non-clinical model entry after an explicit training run."""
    registry = load_registry(path)
    required = {
        "model_id",
        "model_version",
        "artifact",
        "feature_schema_version",
        "dataset_version",
        "dataset_checksum",
        "training_environment",
        "clinical_validation",
        "ds_validated",
        "pediatric_validated",
        "calibrated_probability",
        "population_validated_on",
        "status",
    }
    missing = required - entry.keys()
    if missing:
        raise ValueError(f"model entry is missing required fields: {sorted(missing)}")
    if any(
        entry.get(name) is not False
        for name in (
            "clinical_validation",
            "ds_validated",
            "pediatric_validated",
            "calibrated_probability",
        )
    ):
        raise ValueError(
            "research registry entries must explicitly deny clinical, DS, pediatric, "
            "and calibrated-probability claims"
        )
    if entry.get("status") != "research_only":
        raise ValueError("research registry entries must use research_only status")
    if entry.get("population_validated_on") != "generic non-DS research data only":
        raise ValueError("research registry population must remain generic non-DS")
    for name in ("model_id", "model_version", "artifact", "dataset_version", "dataset_checksum"):
        value = entry.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"model entry field {name} must be a non-empty string")
    if not isinstance(entry.get("training_environment"), dict):
        raise ValueError("training_environment must be a mapping")
    models = cast(list[dict[str, Any]], registry.setdefault("models", []))
    if any(model.get("model_id") == entry["model_id"] for model in models):
        raise ValueError(f"model_id is already registered: {entry['model_id']}")
    models.append(entry)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
