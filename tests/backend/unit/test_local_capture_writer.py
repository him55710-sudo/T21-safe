from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, cast

import pytest
from jsonschema import Draft202012Validator
from t21_engine.streaming.export_manifest import build_export_manifest
from t21_engine.streaming.local_capture_writer import LocalCaptureJsonlWriter

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CAPTURE_SCHEMA_PATH = REPOSITORY_ROOT / "contracts" / "shadow-capture.schema.json"
MANIFEST_SCHEMA_PATH = REPOSITORY_ROOT / "contracts" / "export-manifest.schema.json"
CAPTURE_FIXTURE_PATH = (
    REPOSITORY_ROOT / "tests" / "backend" / "fixtures" / "shadow_capture.synthetic.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return cast(dict[str, Any], json.load(handle))


def _validator(path: Path) -> Draft202012Validator:
    schema = _load_json(path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _manifest() -> dict[str, object]:
    return build_export_manifest(
        export_id="synthetic-export-001",
        session_id="synthetic-session-001",
        event_ids=("synthetic-event-001",),
    )


def _capture() -> dict[str, object]:
    return cast(dict[str, object], _load_json(CAPTURE_FIXTURE_PATH))


@pytest.mark.parametrize("unsafe_field", ["includes_waveforms", "includes_phi"])
def test_writer_fails_closed_before_appending_manifest(
    tmp_path: Path, unsafe_field: str
) -> None:
    writer = LocalCaptureJsonlWriter(tmp_path)
    manifest = copy.deepcopy(_manifest())
    manifest[unsafe_field] = True

    with pytest.raises(ValueError, match="rejects waveforms and PHI"):
        writer.append_manifest(manifest)

    assert not writer.path.exists()


@pytest.mark.parametrize(
    "unsafe_control",
    ["actuation", "dosing", "closed_loop", "drug_advice", "emr_write"],
)
def test_writer_rejects_enabled_manifest_control_without_persisting(
    tmp_path: Path, unsafe_control: str
) -> None:
    writer = LocalCaptureJsonlWriter(tmp_path)
    manifest = copy.deepcopy(_manifest())
    controls = manifest["controls"]
    assert isinstance(controls, dict)
    controls[unsafe_control] = True

    with pytest.raises(ValueError, match="observe-only controls"):
        writer.append_manifest(manifest)

    assert not writer.path.exists()


@pytest.mark.parametrize(
    "cloud_directory",
    [
        "s3://research-captures",
        "gs://research-captures",
        "https://example.test/captures",
    ],
)
def test_writer_rejects_cloud_directory_uri(cloud_directory: str) -> None:
    with pytest.raises(ValueError, match="URI scheme"):
        LocalCaptureJsonlWriter(cloud_directory)


def test_writer_rejects_cloud_uri_filename_without_creating_local_output(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="local basename"):
        LocalCaptureJsonlWriter(tmp_path, "s3://research-captures/capture.jsonl")

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (("session", "contains_phi", True), "contains_phi=false"),
        ((None, "raw_waveforms", [1.0, 2.0]), "waveform persistence"),
    ],
)
def test_writer_fails_closed_before_appending_capture(
    tmp_path: Path,
    mutation: tuple[str | None, str, object],
    message: str,
) -> None:
    writer = LocalCaptureJsonlWriter(tmp_path)
    capture = _capture()
    parent, field, value = mutation
    target = capture if parent is None else capture[parent]
    assert isinstance(target, dict)
    target[field] = value

    with pytest.raises(ValueError, match=message):
        writer.append_capture(capture)

    assert not writer.path.exists()


@pytest.mark.parametrize(
    "unsafe_control",
    ["actuation", "dosing", "closed_loop", "drug_advice", "emr_write"],
)
def test_writer_rejects_enabled_capture_control_without_persisting(
    tmp_path: Path, unsafe_control: str
) -> None:
    writer = LocalCaptureJsonlWriter(tmp_path)
    capture = _capture()
    controls = capture["controls"]
    assert isinstance(controls, dict)
    controls[unsafe_control] = True

    with pytest.raises(ValueError, match="observe-only controls"):
        writer.append_capture(capture)

    assert not writer.path.exists()


def test_writer_round_trips_capture_and_manifest_lines_against_contracts(
    tmp_path: Path,
) -> None:
    writer = LocalCaptureJsonlWriter(tmp_path, "capture.jsonl")
    capture = _capture()
    manifest = _manifest()

    assert writer.append_capture(capture) == tmp_path / "capture.jsonl"
    assert writer.append_manifest(manifest) == tmp_path / "capture.jsonl"

    lines = writer.path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    persisted_capture, persisted_manifest = (json.loads(line) for line in lines)
    _validator(CAPTURE_SCHEMA_PATH).validate(persisted_capture)
    _validator(MANIFEST_SCHEMA_PATH).validate(persisted_manifest)
    assert persisted_capture == capture
    assert persisted_manifest == manifest


def test_writer_refuses_append_that_would_exceed_size_limit(tmp_path: Path) -> None:
    first_writer = LocalCaptureJsonlWriter(tmp_path, max_file_bytes=10_000)
    first_writer.append_manifest(_manifest())
    original_content = first_writer.path.read_bytes()
    bounded_writer = LocalCaptureJsonlWriter(
        tmp_path,
        max_file_bytes=len(original_content),
    )

    with pytest.raises(ValueError, match="exceeds max_file_bytes"):
        bounded_writer.append_manifest(_manifest())

    assert bounded_writer.path.read_bytes() == original_content


def test_writer_refuses_single_oversized_record_without_creating_file(
    tmp_path: Path,
) -> None:
    writer = LocalCaptureJsonlWriter(tmp_path, max_file_bytes=1)

    with pytest.raises(ValueError, match="record exceeds max_file_bytes"):
        writer.append_manifest(_manifest())

    assert not writer.path.exists()
