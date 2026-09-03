"""CODEX-048: pin ExportManifest schema_version (mirror shadow JSONL style)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, cast

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from t21_engine.streaming.export_manifest import build_export_manifest

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPOSITORY_ROOT / "contracts" / "export-manifest.schema.json"
EXPECTED_VERSION = "export-manifest/1.0"


def _load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        return cast(dict[str, Any], json.load(handle))


def _validator() -> Draft202012Validator:
    schema = _load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _valid_manifest() -> dict[str, object]:
    return build_export_manifest(
        export_id="synthetic-export-001",
        session_id="synthetic-session-001",
        event_ids=("synthetic-event-001",),
    )


def test_export_manifest_schema_const_pins_version() -> None:
    schema = _load_schema()
    assert schema["properties"]["schema_version"]["const"] == EXPECTED_VERSION


def test_export_manifest_matches_pinned_schema_version() -> None:
    manifest = _valid_manifest()
    _validator().validate(manifest)
    assert manifest["schema_version"] == EXPECTED_VERSION
    assert manifest["clinical_validation"] is False
    assert manifest["mode"] == "OBSERVE_ONLY_SHADOW"


def test_export_manifest_rejects_wrong_schema_version() -> None:
    manifest = copy.deepcopy(_valid_manifest())
    manifest["schema_version"] = "export-manifest/0.9"
    assert manifest["schema_version"] != EXPECTED_VERSION
    with pytest.raises(ValidationError):
        _validator().validate(manifest)


@pytest.mark.parametrize(
    ("path", "invalid_value"),
    [
        (("clinical_validation",), True),
        (("synthetic_only",), False),
        (("controls", "dosing"), True),
        (("includes_waveforms",), True),
        (("includes_phi",), True),
    ],
)
def test_export_manifest_rejects_non_shadow_safety_values(
    path: tuple[str, ...], invalid_value: object
) -> None:
    manifest = copy.deepcopy(_valid_manifest())
    target: dict[str, Any] = cast(dict[str, Any], manifest)
    for key in path[:-1]:
        target = cast(dict[str, Any], target[key])
    target[path[-1]] = invalid_value
    with pytest.raises(ValidationError):
        _validator().validate(manifest)