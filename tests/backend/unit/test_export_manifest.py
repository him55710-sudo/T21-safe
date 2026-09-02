from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, cast

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from t21_engine.streaming.export_manifest import build_export_manifest
from t21_engine.types import ExportManifest

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPOSITORY_ROOT / "contracts" / "export-manifest.schema.json"


def _validator() -> Draft202012Validator:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        schema = cast(dict[str, Any], json.load(handle))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _valid_manifest() -> dict[str, object]:
    return build_export_manifest(
        export_id="synthetic-export-001",
        session_id="synthetic-session-001",
        event_ids=("synthetic-event-001",),
    )


def test_local_shadow_metadata_manifest_matches_schema() -> None:
    manifest = _valid_manifest()

    _validator().validate(manifest)
    assert manifest["includes_waveforms"] is False
    assert manifest["includes_phi"] is False
    assert manifest["storage_scope"] == "LOCAL_ONLY"


@pytest.mark.parametrize("unsafe_field", ["includes_waveforms", "includes_phi"])
def test_manifest_model_rejects_unsafe_content(unsafe_field: str) -> None:
    arguments: dict[str, object] = {
        "export_id": "synthetic-export-001",
        "session_id": "synthetic-session-001",
        "event_ids": ("synthetic-event-001",),
        unsafe_field: True,
    }

    with pytest.raises(ValueError, match="reject waveforms and PHI"):
        ExportManifest(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize("unsafe_field", ["includes_waveforms", "includes_phi"])
def test_manifest_schema_rejects_unsafe_content(unsafe_field: str) -> None:
    manifest = copy.deepcopy(_valid_manifest())
    manifest[unsafe_field] = True

    with pytest.raises(ValidationError):
        _validator().validate(manifest)


def test_manifest_rejects_non_synthetic_export() -> None:
    with pytest.raises(ValueError, match="synthetic, non-PHI"):
        build_export_manifest(
            export_id="research-export-001",
            session_id="research-session-001",
            event_ids=("research-event-001",),
            is_synthetic=False,
        )
