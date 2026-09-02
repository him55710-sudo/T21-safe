"""Offline MIT-BIH-style R-peak detector engineering benchmark.

This module reports beat matching counts only.  It is a PROXY engineering check,
not clinical validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from t21_engine.adapters.wfdb_adapter import WFDB_CATALOG
from t21_engine.beats.rpeak import detect_r_peaks

SCHEMA_VERSION = "mitbih-beat-bench/1.0"
DEFAULT_RECORD = "100"
SYNTHETIC_ANNOTATION_SUFFIX = ".synthetic-annotations.json"
CATALOG_CASE_ID = "wfdb:mitdb-100"
# WFDB beat annotation symbols; rhythm/change/noise annotations are excluded.
BEAT_SYMBOLS = frozenset(
    {"N", "L", "R", "B", "A", "a", "J", "S", "V", "r", "F", "e", "j", "n", "E", "/", "f", "Q", "?"}
)


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _default_sample_root() -> Path | None:
    repository = _repository_root()
    for relative in (
        Path("data/public/mitdb/1.0.0"),
        Path("tests/backend/fixtures/wfdb_mitdb_synthetic"),
    ):
        for candidate in (relative, repository / relative):
            if candidate.is_dir():
                return candidate.resolve()
    return None


def match_beats(
    reference_samples: np.ndarray[Any, Any],
    detected_samples: np.ndarray[Any, Any],
    tolerance_samples: int,
) -> tuple[list[tuple[int, int]], list[int], list[int]]:
    """One-to-one chronological matching, choosing the nearest eligible detection."""
    if tolerance_samples < 0:
        raise ValueError("tolerance_samples must be non-negative")
    references = sorted(int(value) for value in np.asarray(reference_samples).tolist())
    detections = sorted(int(value) for value in np.asarray(detected_samples).tolist())
    unmatched = set(range(len(detections)))
    matches: list[tuple[int, int]] = []
    missed: list[int] = []
    for reference in references:
        candidates = [
            index
            for index in unmatched
            if abs(detections[index] - reference) <= tolerance_samples
        ]
        if not candidates:
            missed.append(reference)
            continue
        selected = min(candidates, key=lambda index: (abs(detections[index] - reference), index))
        matches.append((reference, detections[selected]))
        unmatched.remove(selected)
    false = [detections[index] for index in sorted(unmatched)]
    return matches, missed, false


def _load_annotations(record_base: Path) -> tuple[np.ndarray[Any, np.dtype[np.int64]], str]:
    atr_path = record_base.with_suffix(".atr")
    if atr_path.is_file():
        import wfdb

        annotation = wfdb.rdann(str(record_base), "atr")
        samples = [
            int(sample)
            for sample, symbol in zip(annotation.sample, annotation.symbol, strict=True)
            if str(symbol) in BEAT_SYMBOLS
        ]
        if not samples:
            raise ValueError("annotation contains no beat symbols")
        return np.asarray(samples, dtype=np.int64), "WFDB_ATR"

    fixture_path = record_base.with_suffix(SYNTHETIC_ANNOTATION_SUFFIX)
    if not fixture_path.is_file():
        raise FileNotFoundError("beat annotation file is missing")
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if payload.get("format") != "synthetic_mitbih_style_beat_annotations_v1":
        raise ValueError("synthetic annotation format is not explicitly labeled")
    if (
        payload.get("synthetic") is not True
        or payload.get("contains_real_mitbih_bytes") is not False
    ):
        raise ValueError("synthetic annotation provenance is incomplete")
    samples = payload.get("beat_samples")
    if (
        not isinstance(samples, list)
        or not samples
        or any(not isinstance(sample, int) or sample < 0 for sample in samples)
    ):
        raise ValueError("synthetic beat annotations are invalid")
    return np.asarray(samples, dtype=np.int64), "SYNTHETIC_JSON_EQUIVALENT"


def _failure(reason: str, record: str, match_window_ms: float) -> dict[str, Any]:
    metadata = WFDB_CATALOG[CATALOG_CASE_ID]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "FAIL",
        "failure_reason_code": reason,
        "clinical_validation": False,
        "proxy_ecg_only": True,
        "network_required": False,
        "dataset": {
            "catalog_case_id": CATALOG_CASE_ID,
            "dataset_name": metadata.dataset_name,
            "dataset_version": metadata.dataset_version,
            "master_verified_proxy": metadata.public_bench_enabled,
        },
        "match_window_ms": match_window_ms,
        "records": [{"record": record, "status": "FAIL", "failure_reason_code": reason}],
        "aggregate": None,
    }


def run_mitbih_beat_bench(
    sample_root: str | Path | None = None,
    *,
    record: str = DEFAULT_RECORD,
    match_window_ms: float = 150.0,
) -> dict[str, Any]:
    """Evaluate the local detector against local annotations without network access."""
    if not np.isfinite(match_window_ms) or match_window_ms < 0.0:
        raise ValueError("match_window_ms must be finite and non-negative")
    metadata = WFDB_CATALOG[CATALOG_CASE_ID]
    if not metadata.public_bench_enabled:
        return _failure("DATASET_NOT_PROMOTED", record, match_window_ms)
    root = Path(sample_root).resolve() if sample_root is not None else _default_sample_root()
    if root is None or not root.is_dir():
        return _failure("MISSING_SAMPLE", record, match_window_ms)
    record_base = root / record
    if not record_base.with_suffix(".hea").is_file():
        return _failure("MISSING_SAMPLE", record, match_window_ms)
    try:
        annotations, annotation_source = _load_annotations(record_base)
    except FileNotFoundError:
        return _failure("MISSING_ANNOTATIONS", record, match_window_ms)
    except (ImportError, OSError, TypeError, ValueError):
        return _failure("ANNOTATION_LOAD_FAILURE", record, match_window_ms)

    try:
        import wfdb

        waveform = wfdb.rdrecord(str(record_base))
        fs = float(waveform.fs)
        matrix = np.asarray(waveform.p_signal, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[1] < 1 or not np.isfinite(fs) or fs <= 0.0:
            raise ValueError("invalid WFDB waveform")
        detected = detect_r_peaks(matrix[:, 0], fs).indices
    except (ImportError, OSError, RuntimeError, TypeError, ValueError):
        return _failure("WFDB_LOAD_FAILURE", record, match_window_ms)

    tolerance = int(round(match_window_ms * fs / 1000.0))
    matches, missed, false = match_beats(annotations, detected, tolerance)
    errors_ms = [
        abs(detected_sample - reference) * 1000.0 / fs
        for reference, detected_sample in matches
    ]
    timing = {
        "mean_abs_error_ms": float(np.mean(errors_ms)) if errors_ms else None,
        "median_abs_error_ms": float(np.median(errors_ms)) if errors_ms else None,
        "max_abs_error_ms": float(np.max(errors_ms)) if errors_ms else None,
    }
    row: dict[str, Any] = {
        "record": record,
        "status": "PASS",
        "failure_reason_code": None,
        "annotation_source": annotation_source,
        "sample_rate_hz": fs,
        "annotated_beats": int(annotations.size),
        "detected_beats": int(detected.size),
        "matched_beats": len(matches),
        "missed_beats_fn": len(missed),
        "false_beats_fp": len(false),
        **timing,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "failure_reason_code": None,
        "clinical_validation": False,
        "proxy_ecg_only": True,
        "network_required": False,
        "dataset": {
            "catalog_case_id": CATALOG_CASE_ID,
            "dataset_name": metadata.dataset_name,
            "dataset_version": metadata.dataset_version,
            "master_verified_proxy": True,
        },
        "match_window_ms": match_window_ms,
        "records": [row],
        "aggregate": {
            "records_evaluated": 1,
            "annotated_beats": row["annotated_beats"],
            "detected_beats": row["detected_beats"],
            "matched_beats": row["matched_beats"],
            "missed_beats_fn": row["missed_beats_fn"],
            "false_beats_fp": row["false_beats_fp"],
            **timing,
        },
    }
