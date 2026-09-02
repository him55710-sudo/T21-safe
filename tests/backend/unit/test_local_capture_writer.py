from __future__ import annotations

import copy
from pathlib import Path

import pytest
from t21_engine.streaming.export_manifest import build_export_manifest
from t21_engine.streaming.local_capture_writer import LocalCaptureJsonlWriter


def _manifest() -> dict[str, object]:
    return build_export_manifest(
        export_id="synthetic-export-001",
        session_id="synthetic-session-001",
        event_ids=("synthetic-event-001",),
    )


def _capture() -> dict[str, object]:
    return {
        "session": {
            "storage_scope": "LOCAL_ONLY",
            "contains_phi": False,
            "pseudonymous_ids": True,
            "is_synthetic": True,
        },
        "mode": "OBSERVE_ONLY_SHADOW",
        "waveform_persistence": "NONE",
        "quality_gate": {"baseline_bypass": False},
        "controls": {
            "actuation": False,
            "dosing": False,
            "closed_loop": False,
            "drug_advice": False,
            "emr_write": False,
        },
    }


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


def test_writer_rejects_non_local_scheme() -> None:
    with pytest.raises(ValueError, match="URI scheme"):
        LocalCaptureJsonlWriter("s3://research-captures")


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


def test_writer_appends_manifest_line(tmp_path: Path) -> None:
    writer = LocalCaptureJsonlWriter(tmp_path, "capture.jsonl")

    assert writer.append_manifest(_manifest()) == tmp_path / "capture.jsonl"
    assert writer.path.read_text(encoding="utf-8").count("\n") == 1
