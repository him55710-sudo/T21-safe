"""Synthetic-only engineering sensitivity for pre-induction baseline windows."""

from __future__ import annotations

from typing import Any

import numpy as np

from t21_engine.adapters.synthetic_hospital_case import (
    SyntheticHospitalCase,
    build_synthetic_hospital_case,
)
from t21_engine.baseline.calibration import calibrate_baseline
from t21_engine.types import QualityResult

WINDOW_SECONDS = (180, 300)
REQUIRED_SENSITIVITY_CHANNELS = ("ecg_ii", "abp", "spo2_pct")


def _failure(case_id: str, reason: str) -> dict[str, Any]:
    return {
        "schema_version": "baseline-window-sensitivity/1.0",
        "status": "FAIL",
        "failure_reason_code": reason,
        "case_id": case_id,
        "synthetic_only": True,
        "clinical_validation": False,
        "clinical_window_choice": "PI_TO_DEFINE",
        "window_end_metadata": "ANESTHESIA_STAGE_INDUCTION_START_RESEARCH_METADATA",
        "windows_seconds": list(WINDOW_SECONDS),
        "rows": [],
        "safety": {"dosing": False, "alerts": False, "clinical_decision": False},
    }


def run_baseline_window_sensitivity(
    case: SyntheticHospitalCase | None = None,
    *,
    sample_rate_hz: float = 25.0,
    seed: int = 20250321,
) -> dict[str, Any]:
    """Compare 180 s and 300 s summaries ending at synthetic induction start.

    This is an engineering sensitivity calculation, not a clinical-window selection.
    Any missing prerequisite withholds all summary and delta rows.
    """
    if case is None:
        # The factory's preop stage is 15% of duration: 2,000 s gives exactly 300 s.
        case = build_synthetic_hospital_case(duration_s=2000.0, seed=seed)
    if not case.case_id.startswith("synthetic:hospital-") or case.contains_phi:
        return _failure(case.case_id, "NON_SYNTHETIC_OR_PHI_CASE")
    alignment = case.quality_report()
    if alignment.status != "PASS":
        if any(reason.code == "MISSING_CHANNEL" for reason in alignment.reasons):
            return _failure(case.case_id, "MISSING_REQUIRED_CHANNEL")
        return _failure(case.case_id, "CASE_ALIGNMENT_FAILURE")
    if any(name not in case.channels for name in REQUIRED_SENSITIVITY_CHANNELS):
        return _failure(case.case_id, "MISSING_REQUIRED_CHANNEL")

    induction_stages = [stage for stage in case.anesthesia_stages if stage.name == "induction"]
    if len(induction_stages) != 1 or not np.isfinite(induction_stages[0].start_s):
        return _failure(case.case_id, "MISSING_INDUCTION_START")
    induction_start_s = float(induction_stages[0].start_s)
    if induction_start_s < max(WINDOW_SECONDS):
        return _failure(case.case_id, "INSUFFICIENT_PREINDUCTION_WINDOW")

    try:
        batch = case.to_signal_batch(sample_rate_hz=sample_rate_hz)
    except ValueError:
        return _failure(case.case_id, "CASE_ALIGNMENT_FAILURE")
    quality = QualityResult(ecg_sqi=1.0, ppg_sqi=1.0, abp_sqi=1.0, usable=True)
    summaries: dict[int, dict[str, float]] = {}
    for window_seconds in WINDOW_SECONDS:
        start_s = induction_start_s - window_seconds
        mask = (batch.timestamps_s >= start_s) & (batch.timestamps_s < induction_start_s)
        expected_samples = int(round(window_seconds * sample_rate_hz))
        if int(np.count_nonzero(mask)) != expected_samples:
            return _failure(case.case_id, "INSUFFICIENT_PREINDUCTION_WINDOW")
        window_signals = {name: values[mask] for name, values in batch.signals.items()}
        if any(
            name not in window_signals or not np.isfinite(window_signals[name]).all()
            for name in REQUIRED_SENSITIVITY_CHANNELS
        ):
            return _failure(case.case_id, "MISSING_OR_NONFINITE_CHANNEL_DATA")
        # Use a local uniform clock after exact sample-count validation. Subtracting
        # large absolute timestamps can otherwise turn complete progress into
        # 0.9999999999999999 at the calibrator boundary.
        window_timestamps = np.arange(expected_samples, dtype=np.float64) / sample_rate_hz
        baseline = calibrate_baseline(
            window_timestamps,
            window_signals,
            sample_rate_hz,
            quality,
            baseline_seconds=window_seconds,
        )
        if not baseline.calibrated or baseline.median_hr is None or baseline.median_map is None:
            return _failure(case.case_id, "BASELINE_CALIBRATION_FAILURE")
        summaries[window_seconds] = {
            "hr_bpm": baseline.median_hr,
            "map_or_abp": baseline.median_map,
            "spo2_pct": float(np.median(window_signals["spo2_pct"])),
        }

    rows: list[dict[str, Any]] = []
    source_channels = {"hr_bpm": "ecg_ii", "map_or_abp": "abp", "spo2_pct": "spo2_pct"}
    for metric in ("hr_bpm", "map_or_abp", "spo2_pct"):
        short_value = summaries[180][metric]
        long_value = summaries[300][metric]
        absolute_delta = long_value - short_value
        relative_delta = absolute_delta / abs(short_value) * 100.0 if short_value != 0.0 else None
        rows.append(
            {
                "metric": metric,
                "source_channel": source_channels[metric],
                "window_180_value": short_value,
                "window_300_value": long_value,
                "absolute_delta_300_minus_180": absolute_delta,
                "relative_delta_pct_300_minus_180": relative_delta,
            }
        )

    return {
        "schema_version": "baseline-window-sensitivity/1.0",
        "status": "PASS",
        "failure_reason_code": None,
        "case_id": case.case_id,
        "synthetic_only": True,
        "clinical_validation": False,
        "clinical_window_choice": "PI_TO_DEFINE",
        "window_end_metadata": "ANESTHESIA_STAGE_INDUCTION_START_RESEARCH_METADATA",
        "induction_start_s": induction_start_s,
        "windows_seconds": list(WINDOW_SECONDS),
        "quality_basis": "DETERMINISTIC_SYNTHETIC_FIXTURE_ALIGNMENT_PASS",
        "rows": rows,
        "safety": {"dosing": False, "alerts": False, "clinical_decision": False},
    }


__all__ = ["run_baseline_window_sensitivity"]
