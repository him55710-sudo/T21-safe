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
EXPECTED_VERSION = "shadow-capture/1.0"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return cast(dict[str, Any], json.load(handle))


def _validator() -> Draft202012Validator:
    schema = _load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def test_shadow_jsonl_lines_match_schema_and_version(tmp_path: Path) -> None:
    capture = _load_json(FIXTURE_PATH)
    jsonl_path = tmp_path / "shadow-capture.jsonl"
    _write_jsonl(jsonl_path, [capture, capture])

    validator = _validator()
    versions: list[str] = []
    with jsonl_path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            validator.validate(record)
            versions.append(record["schema_version"])
            assert record["clinical_validation"] is False
            assert record["mode"] == "OBSERVE_ONLY_SHADOW"

    assert versions == [EXPECTED_VERSION, EXPECTED_VERSION]


def test_shadow_jsonl_rejects_wrong_schema_version(tmp_path: Path) -> None:
    capture = copy.deepcopy(_load_json(FIXTURE_PATH))
    capture["schema_version"] = "shadow-capture/0.9"
    jsonl_path = tmp_path / "bad-version.jsonl"
    _write_jsonl(jsonl_path, [capture])

    line = jsonl_path.read_text(encoding="utf-8").splitlines()[0]
    record = json.loads(line)
    assert record["schema_version"] != EXPECTED_VERSION
    with pytest.raises(ValidationError):
        _validator().validate(record)


@pytest.mark.parametrize(
    ("path", "invalid_value"),
    [
        (("clinical_validation",), True),
        (("controls", "dosing"), True),
    ],
)
def test_shadow_jsonl_rejects_non_shadow_safety_values(
    tmp_path: Path, path: tuple[str, ...], invalid_value: object
) -> None:
    capture = copy.deepcopy(_load_json(FIXTURE_PATH))
    target = capture
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = invalid_value
    jsonl_path = tmp_path / "bad-safety.jsonl"
    _write_jsonl(jsonl_path, [capture])

    record = json.loads(jsonl_path.read_text(encoding="utf-8").splitlines()[0])
    with pytest.raises(ValidationError):
        _validator().validate(record)


def test_shadow_jsonl_counts_only_pinned_schema_version(tmp_path: Path) -> None:
    good = _load_json(FIXTURE_PATH)
    bad = copy.deepcopy(good)
    bad["schema_version"] = "shadow-capture/0.9"
    jsonl_path = tmp_path / "mixed.jsonl"
    _write_jsonl(jsonl_path, [good, bad, good])

    pinned = 0
    with jsonl_path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("schema_version") == EXPECTED_VERSION:
                pinned += 1
    assert pinned == 2
