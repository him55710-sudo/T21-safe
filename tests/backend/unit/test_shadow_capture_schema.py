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
    capture = _load_json(FIXTURE_PATH)
    _validator().validate(capture)
    assert capture["schema_version"] == "shadow-capture/1.0"


@pytest.mark.parametrize(
    ("path", "invalid_value"),
    [
        (("controls", "dosing"), True),
        (("controls", "actuation"), True),
        (("session", "contains_phi"), True),
        (("waveform_persistence",), "LOCAL"),
        (("quality_gate", "baseline_bypass"), True),
        (("quality_gate", "threshold_status"), "VALIDATED"),
        (("quality_gate", "ecg_sqi"), 1.1),
        (("quality_gate", "gap_fraction"), -0.1),
        (("quality_gate", "artifacts", "ecg_ii", "missing_fraction"), 1.1),
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
    "missing_field",
    [
        "ecg_sqi",
        "ppg_sqi",
        "abp_sqi",
        "usable",
        "unavailable_signals",
        "reasons",
        "gap_fraction",
        "timestamp_synchronized",
        "artifacts",
        "baseline_bypass",
        "threshold_status",
    ],
)
def test_schema_rejects_missing_quality_gate_telemetry(missing_field: str) -> None:
    capture = copy.deepcopy(_load_json(FIXTURE_PATH))
    del capture["quality_gate"][missing_field]

    with pytest.raises(ValidationError):
        _validator().validate(capture)


def test_schema_rejects_incomplete_artifact_summary() -> None:
    capture = copy.deepcopy(_load_json(FIXTURE_PATH))
    del capture["quality_gate"]["artifacts"]["ecg_ii"]["clipping_fraction"]

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
