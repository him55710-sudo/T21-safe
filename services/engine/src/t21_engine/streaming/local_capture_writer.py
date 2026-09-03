"""Append-only, local-disk persistence for observe-only shadow metadata."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlsplit

_DISABLED_CONTROLS = ("actuation", "dosing", "closed_loop", "drug_advice", "emr_write")
_WAVEFORM_KEYS = {"signals", "waveforms", "raw_waveforms", "raw_signals"}
_DEFAULT_MAX_FILE_BYTES = 10 * 1024 * 1024
SHADOW_CAPTURE_SCHEMA_VERSION = "shadow-capture/1.0"
EXPORT_MANIFEST_SCHEMA_VERSION = "export-manifest/1.0"


def _require_disabled_controls(value: object) -> None:
    if not isinstance(value, Mapping) or any(
        value.get(name) is not False for name in _DISABLED_CONTROLS
    ):
        raise ValueError("local capture requires all observe-only controls to be false")


def _contains_waveform_field(value: object) -> bool:
    if isinstance(value, Mapping):
        return any(
            key in _WAVEFORM_KEYS or _contains_waveform_field(child)
            for key, child in value.items()
        )
    if isinstance(value, (list, tuple)):
        return any(_contains_waveform_field(child) for child in value)
    return False


def _validate_capture(capture: Mapping[str, object]) -> None:
    if capture.get("schema_version") != SHADOW_CAPTURE_SCHEMA_VERSION:
        raise ValueError("unsupported shadow capture schema version")
    if (
        capture.get("clinical_validation") is not False
        or capture.get("synthetic_only") is not True
    ):
        raise ValueError("shadow capture must be non-clinical and synthetic-only")
    session = capture.get("session")
    if not isinstance(session, Mapping):
        raise ValueError("shadow capture requires session metadata")
    if session.get("storage_scope") != "LOCAL_ONLY":
        raise ValueError("shadow capture storage must be local-only")
    if session.get("contains_phi") is not False:
        raise ValueError("shadow capture must declare contains_phi=false")
    if session.get("pseudonymous_ids") is not True or session.get("is_synthetic") is not True:
        raise ValueError("local capture requires synthetic data and pseudonymous identifiers")
    if capture.get("mode") != "OBSERVE_ONLY_SHADOW":
        raise ValueError("shadow capture must be observe-only")
    if capture.get("waveform_persistence") != "NONE" or _contains_waveform_field(capture):
        raise ValueError("local capture rejects waveform persistence")
    quality_gate = capture.get("quality_gate")
    if not isinstance(quality_gate, Mapping) or quality_gate.get("baseline_bypass") is not False:
        raise ValueError("local capture rejects a baseline bypass")
    _require_disabled_controls(capture.get("controls"))


def _validate_manifest(manifest: Mapping[str, object]) -> None:
    if manifest.get("schema_version") != EXPORT_MANIFEST_SCHEMA_VERSION:
        raise ValueError("unsupported export manifest schema version")
    if (
        manifest.get("clinical_validation") is not False
        or manifest.get("synthetic_only") is not True
    ):
        raise ValueError("export manifest must be non-clinical and synthetic-only")
    if manifest.get("storage_scope") != "LOCAL_ONLY":
        raise ValueError("export manifest storage must be local-only")
    if manifest.get("content_scope") != "SHADOW_CAPTURE_METADATA_ONLY":
        raise ValueError("export manifest must contain shadow-capture metadata only")
    if manifest.get("mode") != "OBSERVE_ONLY_SHADOW":
        raise ValueError("export manifest must be observe-only")
    if manifest.get("is_synthetic") is not True:
        raise ValueError("export manifest requires synthetic data")
    if manifest.get("includes_waveforms") is not False or manifest.get("includes_phi") is not False:
        raise ValueError("local capture rejects waveforms and PHI")
    _require_disabled_controls(manifest.get("controls"))


class LocalCaptureJsonlWriter:
    """Write validated shadow captures and manifests to one local JSONL file."""

    def __init__(
        self,
        directory: str | os.PathLike[str],
        filename: str = "shadow-capture.jsonl",
        *,
        max_file_bytes: int = _DEFAULT_MAX_FILE_BYTES,
    ) -> None:
        directory_text = os.fspath(directory)
        if urlsplit(directory_text).scheme:
            raise ValueError("local capture directory must not use a URI scheme")
        if not filename or Path(filename).name != filename or "://" in filename:
            raise ValueError("local capture filename must be a local basename")
        if (
            isinstance(max_file_bytes, bool)
            or not isinstance(max_file_bytes, int)
            or max_file_bytes <= 0
        ):
            raise ValueError("local capture max_file_bytes must be a positive integer")

        local_directory = Path(directory_text).expanduser()
        local_directory.mkdir(parents=True, exist_ok=True)
        if not local_directory.is_dir():
            raise ValueError("local capture directory must be a directory")
        self.path = local_directory.resolve() / filename
        self.max_file_bytes = max_file_bytes
        if self.path.is_symlink():
            raise ValueError("local capture file must not be a symbolic link")

    def append_capture(self, capture: Mapping[str, object]) -> Path:
        _validate_capture(capture)
        return self._append(capture)

    def append_manifest(self, manifest: Mapping[str, object]) -> Path:
        _validate_manifest(manifest)
        return self._append(manifest)

    def _append(self, value: Mapping[str, object]) -> Path:
        line = json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True)
        encoded_line = f"{line}\n".encode()
        if len(encoded_line) > self.max_file_bytes:
            raise ValueError("local capture record exceeds max_file_bytes")
        with self.path.open("ab") as handle:
            current_size = os.fstat(handle.fileno()).st_size
            if current_size + len(encoded_line) > self.max_file_bytes:
                raise ValueError("local capture file exceeds max_file_bytes")
            handle.write(encoded_line)
            handle.flush()
            os.fsync(handle.fileno())
        return self.path


__all__ = ["LocalCaptureJsonlWriter"]
