"""Fail-closed handlers for the synthetic Research Node MCP."""

from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from t21_engine.adapters.synthetic_hospital_case import build_synthetic_hospital_case
from t21_engine.demo import run_demo

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


__all__ = ["run_synthetic_demo", "run_time_align_qc"]
