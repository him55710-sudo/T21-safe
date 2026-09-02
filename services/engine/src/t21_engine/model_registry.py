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
    required = {"model_id", "model_version", "artifact", "feature_schema_version"}
    missing = required - entry.keys()
    if missing:
        raise ValueError(f"model entry is missing required fields: {sorted(missing)}")
    if entry.get("ds_validated") is not False or entry.get("clinical_validation") is not False:
        raise ValueError("research registry entries must explicitly deny DS/clinical validation")
    models = cast(list[dict[str, Any]], registry.setdefault("models", []))
    if any(model.get("model_id") == entry["model_id"] for model in models):
        raise ValueError(f"model_id is already registered: {entry['model_id']}")
    models.append(entry)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
