"""Local-first, observe-only shadow capture helpers.

This module serializes outputs from the existing deterministic SQI, artifact, and
feature pipelines. It does not calculate clinical decisions or persist waveforms.
"""

from __future__ import annotations

import numpy as np

from t21_engine.config import QualityConfig
from t21_engine.preprocessing.artifact_detection import summarize_artifacts
from t21_engine.quality.quality_gate import evaluate_quality
from t21_engine.types import FeatureSet, QualityResult, ShadowFeatureWindow, ShadowSafetyControls

SHORT_WINDOW_HRV_LIMITATION = (
    "RESEARCH_HYPOTHESIS: short-window HRV and LF/HF have limited utility; LF/HF may be "
    "confounded by respiration and is not established for perioperative use."
)
SHADOW_CAPTURE_SCHEMA_VERSION = "shadow-capture/1.0"


def _feature_window(
    feature_set: FeatureSet, *, baseline_calibrated: bool
) -> ShadowFeatureWindow:
    values = feature_set.values
    absolute_change: dict[str, float | None] = {
        "hr_bpm": values.get("delta_hr_bpm"),
        "map_mm_hg": values.get("delta_map_mm_hg"),
        "ppg_amplitude": values.get("ppg_amplitude_delta"),
    }
    relative_change_pct: dict[str, float | None] = {
        "hr": values.get("delta_hr_pct"),
        "map": values.get("delta_map_pct"),
        "ppg_amplitude": values.get("ppg_amp_delta_pct"),
    }
    if not baseline_calibrated:
        absolute_change = dict.fromkeys(absolute_change)
        relative_change_pct = dict.fromkeys(relative_change_pct)
    return ShadowFeatureWindow(
        window_seconds=feature_set.window_seconds,
        valid_beat_count=feature_set.valid_beat_count,
        absolute_change=absolute_change,
        relative_change_pct=relative_change_pct,
        hrv={
            "rmssd_ms": values.get("rmssd_ms"),
            "sdnn_ms": values.get("sdnn_ms"),
            "lf_power": values.get("lf_power"),
            "hf_power": values.get("hf_power"),
            "lf_hf_ratio": values.get("lf_hf_ratio"),
        },
        limitations=tuple(dict.fromkeys((*feature_set.limitations, SHORT_WINDOW_HRV_LIMITATION))),
    )


def build_shadow_capture(
    *,
    session_id: str,
    event_id: str,
    subject_id: str,
    is_synthetic: bool,
    baseline_calibrated: bool,
    quality_config: QualityConfig,
    feature_windows: dict[int, FeatureSet],
    signals: dict[str, np.ndarray],
    sample_rates_hz: dict[str, float],
    out_of_order_count: int = 0,
    timestamp_synchronized: bool = True,
) -> dict[str, object]:
    """Build a non-persistent capture envelope from existing pipeline results."""
    controls = ShadowSafetyControls()
    quality: QualityResult = evaluate_quality(
        signals,
        sample_rates_hz,
        quality_config,
        out_of_order_count=out_of_order_count,
        timestamp_synchronized=timestamp_synchronized,
        valid_beat_count=min(
            (window.valid_beat_count for window in feature_windows.values()), default=0
        ),
    )
    artifacts = {
        name: {
            "missing_fraction": summary.missing_fraction,
            "flatline_fraction": summary.flatline_fraction,
            "clipping_fraction": summary.clipping_fraction,
            "abrupt_change_fraction": summary.abrupt_change_fraction,
            "implausible_fraction": summary.implausible_fraction,
        }
        for name, values in signals.items()
        if name in {"ecg_ii", "ppg", "abp"}
        for summary in (summarize_artifacts(values),)
    }
    windows = [
        _feature_window(
            feature_windows[window], baseline_calibrated=baseline_calibrated
        )
        for window in sorted(feature_windows)
    ]
    quality_reasons = list(quality.reasons)
    if not baseline_calibrated:
        quality_reasons.append(
            "Baseline is not calibrated; baseline-relative changes are withheld."
        )
    return {
        "schema_version": SHADOW_CAPTURE_SCHEMA_VERSION,
        "clinical_validation": False,
        "synthetic_only": True,
        "session": {
            "session_id": session_id,
            "subject_id": subject_id,
            "pseudonymous_ids": True,
            "is_synthetic": is_synthetic,
            "synthetic_label": "SYNTHETIC_DATA" if is_synthetic else None,
            "storage_scope": "LOCAL_ONLY",
            "contains_phi": False,
        },
        "event_id": event_id,
        "mode": "OBSERVE_ONLY_SHADOW",
        "controls": {
            "actuation": controls.actuation,
            "dosing": controls.dosing,
            "closed_loop": controls.closed_loop,
            "drug_advice": controls.drug_advice,
            "emr_write": controls.emr_write,
        },
        "quality_gate": {
            "implementation": "t21_engine.quality.quality_gate.evaluate_quality",
            "ecg_sqi": quality.ecg_sqi,
            "ppg_sqi": quality.ppg_sqi,
            "abp_sqi": quality.abp_sqi,
            "usable": quality.usable and baseline_calibrated,
            "unavailable_signals": list(quality.unavailable_signals),
            "reasons": list(dict.fromkeys(quality_reasons)),
            "gap_fraction": quality.gap_fraction,
            "timestamp_synchronized": quality.timestamp_synchronized,
            "baseline_calibrated": baseline_calibrated,
            "baseline_bypass": False,
            "threshold_status": "ENGINEERING_HYPOTHESIS_OR_PI_TO_DEFINE",
            "artifacts": artifacts,
        },
        "feature_windows": [
            {
                "window_seconds": window.window_seconds,
                "valid_beat_count": window.valid_beat_count,
                "absolute_change": window.absolute_change,
                "relative_change_pct": window.relative_change_pct,
                "hrv": window.hrv,
                "limitations": list(window.limitations),
                "evidence_status": window.evidence_status,
                "clinical_decision_thresholds": window.clinical_decision_thresholds,
            }
            for window in windows
        ],
        "waveform_persistence": "NONE",
    }


__all__ = [
    "SHADOW_CAPTURE_SCHEMA_VERSION",
    "SHORT_WINDOW_HRV_LIMITATION",
    "build_shadow_capture",
]
