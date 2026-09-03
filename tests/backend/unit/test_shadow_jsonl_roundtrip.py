"""CODEX-058: Shadow JSONL write→validate roundtrip (test-only)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator

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


def test_shadow_jsonl_roundtrip_write_then_validate(tmp_path: Path) -> None:
    """Write minimal synthetic shadow JSONL, then validate each line."""
    capture = _load_json(FIXTURE_PATH)
    assert capture["schema_version"] == EXPECTED_VERSION
    assert capture["clinical_validation"] is False

    out = tmp_path / "roundtrip-shadow.jsonl"
    lines = [capture, capture]
    with out.open("w", encoding="utf-8") as handle:
        for record in lines:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")

    assert out.is_file()
    raw = out.read_text(encoding="utf-8").splitlines()
    assert len(raw) == 2

    validator = _validator()
    for line in raw:
        record = json.loads(line)
        validator.validate(record)
        assert record["schema_version"] == EXPECTED_VERSION
        assert record["clinical_validation"] is False
        assert record["mode"] == "OBSERVE_ONLY_SHADOW"
        assert record["controls"]["dosing"] is False


def test_shadow_jsonl_roundtrip_rejects_mutated_version_on_reread(tmp_path: Path) -> None:
    capture = _load_json(FIXTURE_PATH)
    capture = dict(capture)
    capture["schema_version"] = "shadow-capture/0.9"
    out = tmp_path / "bad-roundtrip.jsonl"
    out.write_text(json.dumps(capture) + "\n", encoding="utf-8")
    record = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert record["schema_version"] != EXPECTED_VERSION
    from jsonschema.exceptions import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        _validator().validate(record)
