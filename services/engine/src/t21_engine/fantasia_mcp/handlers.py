"""Tool handlers for the local-only Fantasia MCP server."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np

from t21_engine.evaluation.fantasia_hrv_age_bench import run_fantasia_hrv_age_bench

SCOPE = "PROXY_HRV_AGE_STABILITY"
MASTER_NOTION_PAGE_ID = "3d09631d743b81efae8fe2731113b4f6"
MAX_SAMPLE_COUNT = 1_000
_RECORD_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}")
_URI_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _default_root() -> Path:
    repository = _repository_root()
    for relative in (
        Path("data/public/fantasia/1.0.0"),
        Path("tests/backend/fixtures/wfdb_fantasia_synthetic"),
    ):
        candidate = repository / relative
        if candidate.is_dir():
            return candidate.resolve()
    return (repository / "data/public/fantasia/1.0.0").resolve()


def _gates() -> dict[str, Any]:
    return {
        "clinical_validation": False,
        "scope": SCOPE,
        "not_ds_or_anesthesia": True,
        "not_ptt_ppg": True,
        "master_verified_proxy": True,
        "master_verified_proxy_reference": {
            "system": "Notion",
            "page_id": MASTER_NOTION_PAGE_ID,
        },
        "research_use_only": True,
        "network_required": False,
    }


def _result(status: str, **payload: Any) -> dict[str, Any]:
    return {"status": status, **_gates(), **payload}


def _local_root(sample_root: str | Path | None) -> tuple[Path | None, dict[str, Any] | None]:
    raw = str(sample_root) if sample_root is not None else str(_default_root())
    if _URI_PATTERN.match(raw) or raw.startswith(("//", "\\\\")):
        return None, _result(
            "REJECTED",
            failure_reason_code="NON_LOCAL_URI_REJECTED",
            message=(
                "Only local filesystem paths are accepted; URI and network-share "
                "inputs fail closed."
            ),
        )
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        return None, _result("FAIL", failure_reason_code="MISSING_SAMPLE_ROOT")
    if not root.is_dir():
        return None, _result("FAIL", failure_reason_code="MISSING_SAMPLE_ROOT")
    return root, None


def _valid_record(record: str) -> bool:
    return _RECORD_PATTERN.fullmatch(record) is not None


def _manifest(root: Path) -> tuple[dict[str, str] | None, str | None]:
    path = root / "sha256-manifest.json"
    if not path.is_file():
        return None, None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        files = payload["files"]
        if not isinstance(files, dict):
            raise TypeError
        normalized = {
            str(name): str(digest).lower().removeprefix("sha256:") for name, digest in files.items()
        }
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return None, "INVALID_SHA256_MANIFEST"
    return normalized, None


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_records(sample_root: str | Path | None = None) -> dict[str, Any]:
    """List local WFDB record names and fixture-integrity status."""
    root, failure = _local_root(sample_root)
    if failure is not None or root is None:
        return failure or _result("FAIL", failure_reason_code="MISSING_SAMPLE_ROOT")
    manifest, manifest_error = _manifest(root)
    if manifest_error is not None:
        return _result("FAIL", failure_reason_code=manifest_error, sample_root=str(root))
    records = sorted(path.stem for path in root.glob("*.hea") if _valid_record(path.stem))
    rows: list[dict[str, Any]] = []
    for record in records:
        names = [f"{record}.hea", f"{record}.dat"]
        expected = manifest or {}
        verified = bool(manifest) and all(
            (root / name).is_file()
            and name in expected
            and _file_digest(root / name) == expected[name]
            for name in names
        )
        rows.append({"record": record, "sha256_verified": verified})
    return _result(
        "PASS",
        dataset="fantasia/1.0.0",
        catalog_case_id="wfdb:fantasia-f1o01",
        sample_root=str(root),
        records=rows,
    )


def load_sample(
    sample_root: str | Path | None = None,
    *,
    record: str = "f1o01",
    sample_count: int = 100,
) -> dict[str, Any]:
    """Load a bounded prefix of one local Fantasia WFDB record."""
    root, failure = _local_root(sample_root)
    if failure is not None or root is None:
        return failure or _result("FAIL", failure_reason_code="MISSING_SAMPLE_ROOT")
    if not _valid_record(record):
        return _result("REJECTED", failure_reason_code="INVALID_RECORD_NAME")
    if (
        isinstance(sample_count, bool)
        or not isinstance(sample_count, int)
        or not 1 <= sample_count <= MAX_SAMPLE_COUNT
    ):
        return _result("REJECTED", failure_reason_code="INVALID_SAMPLE_COUNT")
    if not (root / f"{record}.hea").is_file():
        return _result("FAIL", failure_reason_code="MISSING_SAMPLE", record=record)
    manifest, manifest_error = _manifest(root)
    if manifest_error is not None:
        return _result("FAIL", failure_reason_code=manifest_error, record=record)
    if manifest:
        for name in (f"{record}.hea", f"{record}.dat"):
            path = root / name
            if not path.is_file() or name not in manifest or _file_digest(path) != manifest[name]:
                return _result("FAIL", failure_reason_code="SHA256_MISMATCH", record=record)
    try:
        import wfdb

        loaded = wfdb.rdrecord(str(root / record), sampfrom=0, sampto=sample_count)
        matrix = np.asarray(loaded.p_signal, dtype=np.float64)
        if matrix.ndim != 2 or not np.isfinite(matrix).all():
            raise ValueError("invalid waveform")
    except ImportError:
        return _result("FAIL", failure_reason_code="WFDB_DEPENDENCY_MISSING", record=record)
    except (OSError, RuntimeError, TypeError, ValueError):
        return _result("FAIL", failure_reason_code="WFDB_LOAD_FAILURE", record=record)
    return _result(
        "PASS",
        dataset="fantasia/1.0.0",
        record=record,
        sample_rate_hz=float(loaded.fs),
        signal_names=list(getattr(loaded, "sig_name", [])),
        sample_count=int(matrix.shape[0]),
        samples=matrix.tolist(),
        sha256_verified=bool(manifest),
    )


def run_hrv_proxy_bench(
    sample_root: str | Path | None = None, *, record: str = "f1o01"
) -> dict[str, Any]:
    """Run the versioned deterministic Fantasia HRV/age-stability PROXY bench."""
    root, failure = _local_root(sample_root)
    if failure is not None or root is None:
        return failure or _result("FAIL", failure_reason_code="MISSING_SAMPLE_ROOT")
    if not _valid_record(record):
        return _result("REJECTED", failure_reason_code="INVALID_RECORD_NAME")
    report = run_fantasia_hrv_age_bench(root, record=record)
    return {**report, **_gates(), "scope": SCOPE}
