from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, cast

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPOSITORY_ROOT / "contracts" / "shadow-capture.schema.json"
FIXTURE_PATH = (
    REPOSITORY_ROOT / "tests" / "backend" / "fixtures" / "shadow_capture.synthetic.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return cast(dict[str, Any], json.load(handle))


def _validator() -> Draft202012Validator:
    schema = _load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_synthetic_shadow_capture_fixture_matches_draft_2020_12_schema() -> None:
    _validator().validate(_load_json(FIXTURE_PATH))


@pytest.mark.parametrize(
    ("path", "invalid_value"),
    [
        (("controls", "dosing"), True),
        (("controls", "actuation"), True),
        (("session", "contains_phi"), True),
        (("waveform_persistence",), "LOCAL"),
    ],
)
def test_schema_rejects_non_shadow_safety_values(
    path: tuple[str, ...], invalid_value: object
) -> None:
    capture = copy.deepcopy(_load_json(FIXTURE_PATH))
    target = capture
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = invalid_value

    with pytest.raises(ValidationError):
        _validator().validate(capture)


@pytest.mark.parametrize(
    "missing_control",
    ["actuation", "dosing", "closed_loop", "drug_advice", "emr_write"],
)
def test_schema_rejects_missing_fail_closed_control(missing_control: str) -> None:
    capture = copy.deepcopy(_load_json(FIXTURE_PATH))
    del capture["controls"][missing_control]

    with pytest.raises(ValidationError):
        _validator().validate(capture)
