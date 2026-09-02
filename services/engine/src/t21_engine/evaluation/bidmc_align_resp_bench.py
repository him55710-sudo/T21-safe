"""Offline BIDMC ECG/PPG/RESP alignment and respiration-rate PROXY bench.

The reported values are engineering diagnostics, not clinical performance metrics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.signal import find_peaks

from t21_engine.adapters.wfdb_adapter import WFDB_CATALOG
from t21_engine.beats.alignment import pulse_arrival_time_ms
from t21_engine.beats.pulse_peak import detect_pulse_peaks
from t21_engine.beats.rpeak import detect_r_peaks

SCHEMA_VERSION = "bidmc-align-resp-bench/1.0"
CATALOG_CASE_ID = "wfdb:bidmc01"
DEFAULT_RECORD = "bidmc01"
SYNTHETIC_REFERENCE_SUFFIX = ".synthetic-resp-reference.json"
REQUIRED_CHANNELS = ("ecg", "ppg", "resp")


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _default_sample_root() -> Path | None:
    repository = _repository_root()
    for relative in (
        Path("data/public/bidmc/1.0.0"),
        Path("tests/backend/fixtures/wfdb_bidmc_synthetic"),
    ):
        for candidate in (relative, repository / relative):
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
        "proxy_multisignal_only": True,
        "network_required": False,
        "dataset": {
            "catalog_case_id": CATALOG_CASE_ID,
            "dataset_name": metadata.dataset_name,
            "dataset_version": metadata.dataset_version,
            "master_verified_proxy": metadata.public_bench_enabled,
        },
        "records": [{"record": record, "status": "FAIL", "failure_reason_code": reason}],
        "aggregate": None,
    }


def _canonical_channel(raw_name: object) -> str | None:
    normalized = str(raw_name).strip().lower().rstrip(",")
    if normalized in {"ii", "mlii", "ecg", "ekg", "ecg_ii"}:
        return "ecg"
    if normalized == "pleth" or normalized.startswith("ppg"):
        return "ppg"
    if "resp" in normalized:
        return "resp"
    return None


def _load_breath_reference(record_base: Path) -> tuple[np.ndarray[Any, np.dtype[np.int64]], str]:
    annotation_path = record_base.with_suffix(".breath")
    if annotation_path.is_file():
        import wfdb

        annotation = wfdb.rdann(str(record_base), "breath")
        samples = np.asarray(annotation.sample, dtype=np.int64)
        if samples.size < 2 or np.any(samples < 0):
            raise ValueError("breath annotation contains insufficient samples")
        return samples, "WFDB_BREATH"

    fixture_path = record_base.with_suffix(SYNTHETIC_REFERENCE_SUFFIX)
    if not fixture_path.is_file():
        raise FileNotFoundError("breath reference is missing")
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if payload.get("format") != "synthetic_bidmc_resp_reference_v1":
        raise ValueError("synthetic respiration reference format is not explicit")
    if (
        payload.get("synthetic") is not True
        or payload.get("contains_real_bidmc_bytes") is not False
    ):
        raise ValueError("synthetic respiration reference provenance is incomplete")
    raw_samples = payload.get("breath_samples")
    if (
        not isinstance(raw_samples, list)
        or len(raw_samples) < 2
        or any(not isinstance(sample, int) or sample < 0 for sample in raw_samples)
    ):
        raise ValueError("synthetic respiration reference samples are invalid")
    return np.asarray(raw_samples, dtype=np.int64), "SYNTHETIC_JSON_EQUIVALENT"


def _rate_bpm(samples: np.ndarray[Any, Any], sample_rate_hz: float) -> float | None:
    if samples.size < 2:
        return None
    span_seconds = float(samples[-1] - samples[0]) / sample_rate_hz
    if span_seconds <= 0.0:
        return None
    return float((samples.size - 1) * 60.0 / span_seconds)


def run_bidmc_align_resp_bench(
    sample_root: str | Path | None = None,
    *,
    record: str = DEFAULT_RECORD,
) -> dict[str, Any]:
    """Measure common-timebase alignment and RESP rate against local breath labels."""
    metadata = WFDB_CATALOG[CATALOG_CASE_ID]
    if not metadata.public_bench_enabled:
        return _failure("DATASET_NOT_PROMOTED", record)
    root = Path(sample_root).resolve() if sample_root is not None else _default_sample_root()
    if root is None or not root.is_dir():
        return _failure("MISSING_SAMPLE", record)
    record_base = root / record
    if not record_base.with_suffix(".hea").is_file():
        return _failure("MISSING_SAMPLE", record)

    try:
        references, reference_source = _load_breath_reference(record_base)
    except FileNotFoundError:
        return _failure("MISSING_RESP_REFERENCE", record)
    except (ImportError, OSError, TypeError, ValueError):
        return _failure("RESP_REFERENCE_LOAD_FAILURE", record)

    try:
        import wfdb

        waveform = wfdb.rdrecord(str(record_base))
        fs = float(waveform.fs)
        matrix = np.asarray(waveform.p_signal, dtype=np.float64)
        names = list(waveform.sig_name)
        if (
            matrix.ndim != 2
            or matrix.shape[0] < 2
            or matrix.shape[1] != len(names)
            or not np.isfinite(fs)
            or fs <= 0.0
            or not np.isfinite(matrix).all()
        ):
            raise ValueError("invalid WFDB waveform")
        channels: dict[str, np.ndarray[Any, np.dtype[np.float64]]] = {}
        channel_columns: dict[str, int] = {}
        for column, name in enumerate(names):
            canonical = _canonical_channel(name)
            if canonical is not None and canonical not in channels:
                channels[canonical] = matrix[:, column]
                channel_columns[canonical] = column
        raw_skews = getattr(waveform, "skew", None)
        declared_skews = [0] * len(names) if raw_skews is None else raw_skews
        skews = [0 if value is None else int(value) for value in declared_skews]
        if len(skews) != len(names):
            raise ValueError("invalid WFDB channel skew metadata")
    except (ImportError, OSError, RuntimeError, TypeError, ValueError):
        return _failure("WFDB_LOAD_FAILURE", record)

    if any(channel not in channels for channel in REQUIRED_CHANNELS):
        return _failure("MISSING_REQUIRED_CHANNEL", record)
    if references[-1] >= matrix.shape[0]:
        return _failure("RESP_REFERENCE_OUT_OF_RANGE", record)

    r_peaks = detect_r_peaks(channels["ecg"], fs)
    pulse_peaks = detect_pulse_peaks(channels["ppg"], fs)
    pulse_arrival_ms, alignment_confidence = pulse_arrival_time_ms(r_peaks, pulse_peaks)
    resp = channels["resp"]
    spread = float(np.percentile(resp, 95) - np.percentile(resp, 5))
    detected_breaths, _ = find_peaks(
        resp,
        distance=max(1, int(1.0 * fs)),
        prominence=max(0.15 * spread, 1e-9),
    )
    reference_rate = _rate_bpm(references, fs)
    detected_rate = _rate_bpm(detected_breaths, fs)
    if pulse_arrival_ms is None or reference_rate is None or detected_rate is None:
        return _failure("INSUFFICIENT_DETECTIONS", record)

    channel_offsets_ms = {
        name: skews[channel_columns[name]] * 1000.0 / fs for name in REQUIRED_CHANNELS
    }
    sync_error_ms = max(channel_offsets_ms.values()) - min(channel_offsets_ms.values())
    alignment = {
        "timebase": "WFDB_SHARED_SAMPLE_CLOCK",
        "channels": list(REQUIRED_CHANNELS),
        "sample_count_per_channel": {name: int(channels[name].size) for name in REQUIRED_CHANNELS},
        "declared_channel_offset_ms": channel_offsets_ms,
        "max_start_skew_ms": sync_error_ms,
        "max_end_skew_ms": sync_error_ms,
        "max_sample_count_delta": 0,
        "ecg_ppg_median_pulse_arrival_ms": pulse_arrival_ms,
        "ecg_ppg_alignment_confidence": alignment_confidence,
    }
    respiration = {
        "reference_source": reference_source,
        "reference_breaths": int(references.size),
        "detected_breaths": int(detected_breaths.size),
        "reference_rate_bpm": reference_rate,
        "detected_rate_bpm": detected_rate,
        "signed_error_bpm": detected_rate - reference_rate,
        "absolute_error_bpm": abs(detected_rate - reference_rate),
    }
    row = {
        "record": record,
        "status": "PASS",
        "failure_reason_code": None,
        "sample_rate_hz": fs,
        "alignment": alignment,
        "respiration_rate": respiration,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "failure_reason_code": None,
        "clinical_validation": False,
        "proxy_multisignal_only": True,
        "network_required": False,
        "dataset": {
            "catalog_case_id": CATALOG_CASE_ID,
            "dataset_name": metadata.dataset_name,
            "dataset_version": metadata.dataset_version,
            "master_verified_proxy": True,
        },
        "records": [row],
        "aggregate": {
            "records_evaluated": 1,
            "max_start_skew_ms": sync_error_ms,
            "max_end_skew_ms": sync_error_ms,
            "resp_rate_mean_absolute_error_bpm": respiration["absolute_error_bpm"],
            "resp_rate_max_absolute_error_bpm": respiration["absolute_error_bpm"],
        },
    }
