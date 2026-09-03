"""Fail-closed handlers for the synthetic Research Node MCP."""

from __future__ import annotations

import asyncio
import json
import math
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from t21_engine.adapters.synthetic_hospital_case import build_synthetic_hospital_case
from t21_engine.demo import (
    DEFAULT_BASELINE_SECONDS,
    DEFAULT_DURATION_SECONDS,
    DEFAULT_SEED,
    DEFAULT_SESSION_ID,
    run_demo,
)
from t21_engine.evaluation.baseline_window_sensitivity import (
    run_baseline_window_sensitivity as evaluate_baseline_window_sensitivity,
)
from t21_engine.evaluation.bidmc_align_resp_bench import (
    run_bidmc_align_resp_bench as evaluate_bidmc_align_resp_bench,
)
from t21_engine.evaluation.mitbih_beat_bench import (
    run_mitbih_beat_bench as evaluate_mitbih_beat_bench,
)
from t21_engine.evaluation.sqi_missingness_impact import (
    run_sqi_missingness_impact as evaluate_sqi_missingness_impact,
)
from t21_engine.streaming.local_capture_writer import (
    EXPORT_MANIFEST_SCHEMA_VERSION,
    SHADOW_CAPTURE_SCHEMA_VERSION,
    _validate_capture,
    _validate_manifest,
)

_MAX_SHADOW_EXPORT_BYTES = 10 * 1024 * 1024

_PHI_PATH_COMPONENT = re.compile(
    r"(?:^|[-_.])(phi|patient(?:[-_]?data)?|mrn|protected[-_]?health[-_]?information)(?:$|[-_.])",
    re.IGNORECASE,
)


def _gates() -> dict[str, Any]:
    return {
        "clinical_validation": False,
        "synthetic_only": True,
        "contains_phi": False,
        "intended_use": "RESEARCH_USE_ONLY",
        "mode": "OBSERVE_ONLY_SHADOW",
        "network_required": False,
        "fantasia_required": False,
        "vitaldb_allowed": False,
        "controls": {
            "actuation": False,
            "dosing": False,
            "alerts": False,
            "closed_loop": False,
            "drug_advice": False,
            "emr_write": False,
        },
    }


def _result(status: str, **payload: Any) -> dict[str, Any]:
    return {"status": status, **_gates(), **payload}


def _evaluation_result(payload: dict[str, Any]) -> dict[str, Any]:
    """Attach MCP safety gates without changing the evaluation result."""
    return {
        **payload,
        **_gates(),
        "mission": "CODEX-023",
        "pi_to_define_banner": "PI_TO_DEFINE — engineering output; no clinical interpretation",
    }


def _evaluation_failure(schema_version: str, reason: str = "INVALID_PARAMETERS") -> dict[str, Any]:
    return _evaluation_result(
        {
            "schema_version": schema_version,
            "status": "FAIL_CLOSED",
            "failure_reason_code": reason,
            "rows": [],
        }
    )


def _proxy_bench_result(payload: dict[str, Any], *, scope: str) -> dict[str, Any]:
    """Attach explicit Path B non-clinical gates to an existing PROXY report."""
    dataset = payload.get("dataset")
    master_verified_proxy = (
        dataset.get("master_verified_proxy") if isinstance(dataset, dict) else False
    )
    records = payload.get("records")
    sources = records if isinstance(records, list) else []
    synthetic_only = bool(sources) and all(
        isinstance(row, dict)
        and (
            row.get("annotation_source") == "SYNTHETIC_JSON_EQUIVALENT"
            or (
                isinstance(row.get("respiration_rate"), dict)
                and row["respiration_rate"].get("reference_source")
                == "SYNTHETIC_JSON_EQUIVALENT"
            )
        )
        for row in sources
    )
    return {
        **payload,
        **_gates(),
        "synthetic_only": synthetic_only,
        "mission": "CODEX-026",
        "scope": scope,
        "read_only": True,
        "master_verified_proxy": master_verified_proxy is True,
        "proxy_banner": (
            "PROXY / ENGINEERING ONLY — clinical_validation=false; "
            "no DS or clinical claims"
        ),
    }


def run_mitbih_beat_bench(*, match_window_ms: float = 150.0) -> dict[str, Any]:
    """Run the pinned-record, local-only MIT-BIH beat-detection PROXY bench."""
    if (
        isinstance(match_window_ms, bool)
        or not isinstance(match_window_ms, (int, float))
        or not math.isfinite(match_window_ms)
        or match_window_ms < 0
    ):
        payload = {
            "schema_version": "mitbih-beat-bench/1.0",
            "status": "FAIL_CLOSED",
            "failure_reason_code": "INVALID_PARAMETERS",
            "records": [],
            "aggregate": None,
        }
    else:
        try:
            payload = evaluate_mitbih_beat_bench(match_window_ms=float(match_window_ms))
        except (ImportError, OSError, OverflowError, RuntimeError, TypeError, ValueError):
            payload = {
                "schema_version": "mitbih-beat-bench/1.0",
                "status": "FAIL_CLOSED",
                "failure_reason_code": "BENCH_EXECUTION_FAILED",
                "records": [],
                "aggregate": None,
            }
    return _proxy_bench_result(payload, scope="MITBIH_BEAT_PROXY")


def run_bidmc_align_resp_bench() -> dict[str, Any]:
    """Run the pinned-record, local-only BIDMC alignment/RESP PROXY bench."""
    try:
        payload = evaluate_bidmc_align_resp_bench()
    except (ImportError, OSError, RuntimeError, TypeError, ValueError):
        payload = {
            "schema_version": "bidmc-align-resp-bench/1.0",
            "status": "FAIL_CLOSED",
            "failure_reason_code": "BENCH_EXECUTION_FAILED",
            "records": [],
            "aggregate": None,
        }
    return _proxy_bench_result(payload, scope="BIDMC_ALIGN_RESP_PROXY")


def _local_output_dir(
    output_dir: str | os.PathLike[str] | None,
) -> tuple[Path | None, dict[str, Any] | None]:
    if output_dir is None:
        return None, None
    raw = os.fspath(output_dir)
    if urlsplit(raw).scheme or raw.startswith(("//", "\\\\")):
        return None, _result(
            "REJECTED",
            failure_reason_code="NON_LOCAL_URI_REJECTED",
            message="Only local filesystem output directories are accepted.",
        )
    if any(_PHI_PATH_COMPONENT.search(part) for part in Path(raw).parts):
        return None, _result(
            "REJECTED",
            failure_reason_code="PHI_PATH_REJECTED",
            message="Output paths marked as PHI or patient data fail closed.",
        )
    try:
        return Path(raw).expanduser().resolve(), None
    except (OSError, RuntimeError):
        return None, _result("REJECTED", failure_reason_code="INVALID_LOCAL_PATH")


def _local_input_path(
    raw_path: str | os.PathLike[str],
) -> tuple[Path | None, dict[str, Any] | None]:
    raw = os.fspath(raw_path)
    if urlsplit(raw).scheme or raw.startswith(("//", "\\\\")):
        return None, _result("REJECTED", failure_reason_code="NON_LOCAL_URI_REJECTED")
    if any(_PHI_PATH_COMPONENT.search(part) for part in Path(raw).parts):
        return None, _result("REJECTED", failure_reason_code="PHI_PATH_REJECTED")
    try:
        unresolved = Path(raw).expanduser()
        if unresolved.is_symlink():
            return None, _result("REJECTED", failure_reason_code="SYMLINK_REJECTED")
        path = unresolved.resolve(strict=True)
    except (OSError, RuntimeError):
        return None, _result("REJECTED", failure_reason_code="LOCAL_PATH_NOT_FOUND")
    return path, None


def list_local_shadow_exports(*, directory: str) -> dict[str, Any]:
    """List bounded local JSONL files without reading or returning record content."""
    local_dir, failure = _local_input_path(directory)
    if failure is not None:
        return failure
    if local_dir is None or not local_dir.is_dir():
        return _result("REJECTED", failure_reason_code="LOCAL_DIRECTORY_REQUIRED")
    exports = []
    try:
        for path in sorted(local_dir.glob("*.jsonl")):
            if path.is_file() and not path.is_symlink():
                size = path.stat().st_size
                exports.append(
                    {
                        "filename": path.name,
                        "size_bytes": size,
                        "summarizable": size <= _MAX_SHADOW_EXPORT_BYTES,
                    }
                )
    except OSError:
        return _result("FAIL_CLOSED", failure_reason_code="LOCAL_EXPORT_LIST_FAILED")
    return _result("PASS", schema_version="shadow-export-list/1.0", exports=exports)


def export_shadow_summary(*, path: str) -> dict[str, Any]:
    """Validate one local JSONL export and return metadata-only aggregate counts."""
    local_path, failure = _local_input_path(path)
    if failure is not None:
        return failure
    if (
        local_path is None
        or not local_path.is_file()
        or local_path.suffix != ".jsonl"
        or local_path.is_symlink()
    ):
        return _result("REJECTED", failure_reason_code="LOCAL_JSONL_FILE_REQUIRED")
    try:
        if local_path.stat().st_size > _MAX_SHADOW_EXPORT_BYTES:
            return _result("REJECTED", failure_reason_code="LOCAL_EXPORT_TOO_LARGE")
        capture_count = manifest_count = 0
        with local_path.open(encoding="utf-8") as handle:
            for line in handle:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError
                version = value.get("schema_version")
                if version == SHADOW_CAPTURE_SCHEMA_VERSION:
                    _validate_capture(value)
                    capture_count += 1
                elif version == EXPORT_MANIFEST_SCHEMA_VERSION:
                    _validate_manifest(value)
                    manifest_count += 1
                else:
                    raise ValueError
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return _result("FAIL_CLOSED", failure_reason_code="INVALID_SHADOW_JSONL")
    return _result(
        "PASS",
        schema_version="shadow-export-summary/1.0",
        capture_schema_version=SHADOW_CAPTURE_SCHEMA_VERSION,
        manifest_schema_version=EXPORT_MANIFEST_SCHEMA_VERSION,
        capture_count=capture_count,
        manifest_count=manifest_count,
        record_count=capture_count + manifest_count,
    )


def run_time_align_qc(
    *, duration_seconds: float = 12.0, seed: int = 20250321
) -> dict[str, Any]:
    """Build the pinned synthetic case and run its existing alignment QC."""
    try:
        case = build_synthetic_hospital_case(duration_s=duration_seconds, seed=seed)
        report = case.quality_report().to_dict()
    except (TypeError, ValueError) as exc:
        return _result(
            "FAIL_CLOSED",
            failure_reason_code="INVALID_SYNTHETIC_INPUT",
            message=str(exc),
        )
    return _result(
        str(report["status"]),
        mission="CODEX-021",
        case_id=case.case_id,
        duration_seconds=duration_seconds,
        seed=seed,
        alignment_qc=report,
    )


def run_synthetic_demo(
    *,
    duration_seconds: float = 12.0,
    baseline_seconds: int = 3,
    seed: int = 20250321,
    output_dir: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    """Run the existing replay demo and optionally export local shadow metadata."""
    local_dir, failure = _local_output_dir(output_dir)
    if failure is not None:
        return failure
    try:
        report = asyncio.run(
            run_demo(
                duration_seconds=duration_seconds,
                baseline_seconds=baseline_seconds,
                seed=seed,
                output_dir=local_dir,
            )
        )
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        return _result("FAIL_CLOSED", failure_reason_code="SYNTHETIC_DEMO_FAILED", message=str(exc))
    return {**report, **_gates(), "mission": "CODEX-021"}


def run_sqi_missingness_impact(
    *,
    sample_rate_hz: float = 100.0,
    window_seconds: float = 30.0,
    gap_fractions: list[float] | tuple[float, ...] = (0.0, 0.10, 0.25),
    noise_std: list[float] | tuple[float, ...] = (0.0, 0.20),
    seed: int = 20250321,
) -> dict[str, Any]:
    """Run the existing synthetic-only SQI/missingness evaluation."""
    valid_sequences = isinstance(gap_fractions, (list, tuple)) and isinstance(
        noise_std, (list, tuple)
    )
    numeric_levels = (*gap_fractions, *noise_std) if valid_sequences else ()
    if (
        isinstance(sample_rate_hz, bool)
        or not isinstance(sample_rate_hz, (int, float))
        or not math.isfinite(sample_rate_hz)
        or sample_rate_hz <= 0
        or isinstance(window_seconds, bool)
        or not isinstance(window_seconds, (int, float))
        or not math.isfinite(window_seconds)
        or window_seconds <= 0
        or not valid_sequences
        or not gap_fractions
        or not noise_std
        or len(numeric_levels) != len(gap_fractions) + len(noise_std)
        or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for value in numeric_levels
        )
        or isinstance(seed, bool)
        or not isinstance(seed, int)
    ):
        return _evaluation_failure("sqi-missingness-impact/1.0")
    try:
        payload = evaluate_sqi_missingness_impact(
            sample_rate_hz=sample_rate_hz,
            window_seconds=window_seconds,
            gap_fractions=gap_fractions,
            noise_std=noise_std,
            seed=seed,
        )
    except (OverflowError, TypeError, ValueError):
        return _evaluation_failure("sqi-missingness-impact/1.0")
    return _evaluation_result(payload)


def run_baseline_window_sensitivity(
    *, sample_rate_hz: float = 25.0, seed: int = 20250321
) -> dict[str, Any]:
    """Run the existing synthetic-only fixed 180/300-second comparison."""
    if (
        isinstance(sample_rate_hz, bool)
        or not isinstance(sample_rate_hz, (int, float))
        or not math.isfinite(sample_rate_hz)
        or sample_rate_hz <= 0
        or isinstance(seed, bool)
        or not isinstance(seed, int)
    ):
        return _evaluation_failure("baseline-window-sensitivity/1.0")
    try:
        payload = evaluate_baseline_window_sensitivity(
            sample_rate_hz=sample_rate_hz,
            seed=seed,
        )
    except (OverflowError, TypeError, ValueError):
        return _evaluation_failure("baseline-window-sensitivity/1.0")
    return _evaluation_result(payload)


__all__ = [
    "export_shadow_summary",
    "list_local_shadow_exports",
    "run_baseline_window_sensitivity",
    "run_bidmc_align_resp_bench",
    "run_mitbih_beat_bench",
    "run_sqi_missingness_impact",
    "run_synthetic_demo",
    "run_time_align_qc",
]


def list_demo_presets() -> dict[str, Any]:
    """Return read-only synthetic demo CLI presets (no waveforms, no I/O)."""
    return _result(
        "PASS",
        schema_version="demo-presets/1.0",
        mission="CODEX-042",
        presets=[
            {
                "id": "default",
                "label": "synthetic-research-node-demo",
                "duration_seconds": DEFAULT_DURATION_SECONDS,
                "baseline_seconds": DEFAULT_BASELINE_SECONDS,
                "seed": DEFAULT_SEED,
                "session_id": DEFAULT_SESSION_ID,
                "synthetic_only": True,
                "clinical_validation": False,
            }
        ],
    )
