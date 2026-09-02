"""Offline Fantasia-style HRV reproducibility and age-metadata PROXY bench.

This is an engineering check only. It does not validate clinical, age-related,
Down-syndrome, anesthesia, or PTT/PPG claims.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from t21_engine.adapters.wfdb_adapter import WFDB_CATALOG
from t21_engine.beats.rpeak import detect_r_peaks
from t21_engine.features.hrv import rr_intervals_ms, time_domain_hrv

SCHEMA_VERSION = "fantasia-hrv-age-bench/1.0"
CATALOG_CASE_ID = "wfdb:fantasia-f1o01"
DEFAULT_RECORD = "f1o01"
METRIC_NAMES = ("rr_mean_ms", "rmssd_ms", "sdnn_ms", "poincare_sd1_ms", "poincare_sd2_ms")


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _default_sample_root() -> Path | None:
    repository = _repository_root()
    for relative in (
        Path("data/public/fantasia/1.0.0"),
        Path("tests/backend/fixtures/wfdb_fantasia_synthetic"),
    ):
        candidate = repository / relative
        if candidate.is_dir():
            return candidate.resolve()
    return None


def _failure(reason: str, record: str) -> dict[str, Any]:
    metadata = WFDB_CATALOG[CATALOG_CASE_ID]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "FAIL",
        "failure_reason_code": reason,
        "clinical_validation": False,
        "operational_proxy_ok": metadata.public_bench_enabled,
        "research_use_only": True,
        "network_required": False,
        "prohibited_claims": ["DS", "anesthesia", "clinical_age_effect", "PTT_PPG"],
        "dataset": {
            "catalog_case_id": CATALOG_CASE_ID,
            "dataset_name": metadata.dataset_name,
            "dataset_version": metadata.dataset_version,
            "license_notes": metadata.license_notes,
        },
        "records": [{"record": record, "status": "FAIL", "failure_reason_code": reason}],
        "aggregate": None,
    }


def _verify_fixture(root: Path) -> str | None:
    manifest_path = root / "sha256-manifest.json"
    if not manifest_path.is_file():
        return "MISSING_MANIFEST"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("sample_kind") != "synthetic_fixture_equivalent":
            return "INVALID_FIXTURE_PROVENANCE"
        files = manifest["files"]
        if not isinstance(files, dict) or not files:
            return "INVALID_FIXTURE_PROVENANCE"
        for name, expected in files.items():
            path = root / str(name)
            if not path.is_file():
                return "MISSING_SAMPLE"
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != str(expected).lower().removeprefix("sha256:"):
                return "SHA256_MISMATCH"
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return "INVALID_FIXTURE_PROVENANCE"
    return None


def _age_metadata(root: Path, record: str) -> dict[str, Any]:
    path = root / f"{record}.synthetic-metadata.json"
    if not path.is_file():
        return {
            "status": "UNAVAILABLE",
            "reason": "PI_TO_DEFINE",
            "age_metadata_available": False,
            "age_stability_metrics": None,
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return {
            "status": "FAIL",
            "reason": "INVALID_AGE_METADATA",
            "age_metadata_available": False,
            "age_stability_metrics": None,
        }
    if payload.get("age_metadata_available") is not True:
        return {
            "status": "UNAVAILABLE",
            "reason": "PI_TO_DEFINE",
            "age_metadata_available": False,
            "age_stability_metrics": None,
        }
    # A single record cannot establish between-age stability, even if metadata exists.
    return {
        "status": "UNAVAILABLE",
        "reason": "INSUFFICIENT_AGE_GROUPS",
        "age_metadata_available": True,
        "age_stability_metrics": None,
    }


def run_fantasia_hrv_age_bench(
    sample_root: str | Path | None = None, *, record: str = DEFAULT_RECORD
) -> dict[str, Any]:
    """Run deterministic split-window HRV diagnostics against a local WFDB record."""
    metadata = WFDB_CATALOG[CATALOG_CASE_ID]
    if not metadata.public_bench_enabled:
        return _failure("DATASET_NOT_PROMOTED", record)
    root = Path(sample_root).resolve() if sample_root is not None else _default_sample_root()
    if root is None or not root.is_dir() or not (root / f"{record}.hea").is_file():
        return _failure("MISSING_SAMPLE", record)
    provenance_failure = _verify_fixture(root)
    if provenance_failure is not None:
        return _failure(provenance_failure, record)
    try:
        import wfdb

        waveform = wfdb.rdrecord(str(root / record))
        fs = float(waveform.fs)
        matrix = np.asarray(waveform.p_signal, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[1] < 1 or not np.isfinite(matrix).all() or fs <= 0:
            raise ValueError("invalid waveform")
        beats = detect_r_peaks(matrix[:, 0], fs)
        rr = rr_intervals_ms(beats)
    except (ImportError, OSError, RuntimeError, TypeError, ValueError):
        return _failure("WFDB_LOAD_FAILURE", record)
    if rr.size < 12:
        return _failure("INSUFFICIENT_RR_INTERVALS", record)

    midpoint = rr.size // 2
    first = time_domain_hrv(rr[:midpoint])
    second = time_domain_hrv(rr[midpoint:])
    repeated = time_domain_hrv(rr.copy())
    full = time_domain_hrv(rr)
    split_deltas: dict[str, float | None] = {}
    for name in METRIC_NAMES:
        first_value = first[name]
        second_value = second[name]
        split_deltas[name] = (
            abs(first_value - second_value)
            if first_value is not None and second_value is not None
            else None
        )
    age_stability = _age_metadata(root, record)
    if age_stability["status"] == "FAIL":
        return _failure(str(age_stability["reason"]), record)
    row: dict[str, Any] = {
        "record": record,
        "status": "PASS",
        "failure_reason_code": None,
        "sample_rate_hz": fs,
        "rr_interval_count": int(rr.size),
        "time_domain_hrv_full": full,
        "split_window_absolute_delta": split_deltas,
        "deterministic_recompute_exact": full == repeated,
        "age_stability": age_stability,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "failure_reason_code": None,
        "clinical_validation": False,
        "operational_proxy_ok": True,
        "research_use_only": True,
        "network_required": False,
        "prohibited_claims": ["DS", "anesthesia", "clinical_age_effect", "PTT_PPG"],
        "dataset": {
            "catalog_case_id": CATALOG_CASE_ID,
            "dataset_name": metadata.dataset_name,
            "dataset_version": metadata.dataset_version,
            "license_notes": metadata.license_notes,
        },
        "records": [row],
        "aggregate": {
            "records_evaluated": 1,
            "deterministic_recompute_exact": row["deterministic_recompute_exact"],
            "age_stability_status": age_stability["status"],
        },
    }
