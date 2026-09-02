"""Synthetic-only SQI and missingness engineering impact table."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from t21_engine.adapters.synthetic_hospital_case import (
    SyntheticHospitalCase,
    build_synthetic_hospital_case,
)
from t21_engine.config import QualityConfig
from t21_engine.quality.quality_gate import evaluate_quality

DEFAULT_GAP_FRACTIONS = (0.0, 0.10, 0.25)
DEFAULT_NOISE_STD = (0.0, 0.20)
QUALITY_CHANNELS = ("ecg_ii", "ppg", "abp")


def _failure(reason: str, *, case_id: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": "sqi-missingness-impact/1.0",
        "status": "FAIL",
        "failure_reason_code": reason,
        "case_id": case_id,
        "synthetic_only": True,
        "clinical_validation": False,
        "clinical_threshold_interpretation": "PI_TO_DEFINE",
        "rows": [],
        "safety": {"dosing": False, "alerts": False, "clinical_decision": False},
    }


def _valid_levels(values: Sequence[float], *, upper: float | None = None) -> bool:
    return bool(values) and all(
        np.isfinite(value) and value >= 0.0 and (upper is None or value <= upper)
        for value in values
    )


def _perturb_window(
    signals: dict[str, np.ndarray],
    *,
    gap_fraction: float,
    noise_std: float,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    perturbed = {name: values.copy() for name, values in signals.items()}
    for name in QUALITY_CHANNELS:
        values = perturbed[name]
        finite = values[np.isfinite(values)]
        scale = float(np.std(finite)) if finite.size else 0.0
        if noise_std:
            values += rng.normal(0.0, noise_std * scale, values.size)
        gap_samples = int(np.ceil(gap_fraction * values.size))
        if gap_samples:
            start = (values.size - gap_samples) // 2
            values[start : start + gap_samples] = np.nan
    return perturbed


def run_sqi_missingness_impact(
    case: SyntheticHospitalCase | None = None,
    *,
    quality_config: QualityConfig | None = None,
    sample_rate_hz: float = 100.0,
    window_seconds: float = 30.0,
    gap_fractions: Sequence[float] = DEFAULT_GAP_FRACTIONS,
    noise_std: Sequence[float] = DEFAULT_NOISE_STD,
    seed: int = 20250321,
) -> dict[str, Any]:
    """Measure QC usability after deterministic gaps/noise in synthetic channels.

    ``noise_std`` is expressed as a multiple of each window/channel standard
    deviation. Threshold interpretation is intentionally left to the PI.
    """
    config = quality_config or QualityConfig()
    if (
        not np.isfinite(sample_rate_hz)
        or sample_rate_hz <= 0.0
        or not np.isfinite(window_seconds)
        or window_seconds <= 0.0
        or not _valid_levels(gap_fractions, upper=1.0)
        or not _valid_levels(noise_std)
        or not isinstance(seed, int)
    ):
        return _failure("INVALID_PARAMETERS", case_id=case.case_id if case else None)

    if case is None:
        case = build_synthetic_hospital_case(duration_s=120.0, seed=seed)
    if not case.case_id.startswith("synthetic:hospital-") or case.contains_phi:
        return _failure("NON_SYNTHETIC_OR_PHI_CASE", case_id=case.case_id)
    if case.quality_report().status != "PASS":
        return _failure("CASE_ALIGNMENT_FAILURE", case_id=case.case_id)

    try:
        batch = case.to_signal_batch(sample_rate_hz=sample_rate_hz)
    except ValueError:
        return _failure("CASE_ALIGNMENT_FAILURE", case_id=case.case_id)
    if any(name not in batch.signals for name in QUALITY_CHANNELS):
        return _failure("MISSING_REQUIRED_CHANNEL", case_id=case.case_id)

    samples_per_window = int(round(window_seconds * sample_rate_hz))
    if samples_per_window < 2 or not np.isclose(
        samples_per_window / sample_rate_hz, window_seconds
    ):
        return _failure("INVALID_PARAMETERS", case_id=case.case_id)
    candidate_windows = batch.timestamps_s.size // samples_per_window
    if candidate_windows < 1:
        return _failure("NO_COMPLETE_WINDOWS", case_id=case.case_id)

    rows: list[dict[str, Any]] = []
    scenarios = [(gap, 0.0) for gap in gap_fractions]
    scenarios.extend((0.0, level) for level in noise_std if level != 0.0)
    for scenario_index, (gap_fraction, noise_level) in enumerate(scenarios):
        quality_results = []
        for window_index in range(candidate_windows):
            start = window_index * samples_per_window
            stop = start + samples_per_window
            signals = {name: values[start:stop] for name, values in batch.signals.items()}
            perturbed = _perturb_window(
                signals,
                gap_fraction=gap_fraction,
                noise_std=noise_level,
                rng=np.random.default_rng(seed + scenario_index * 10_000 + window_index),
            )
            quality_results.append(evaluate_quality(perturbed, batch.sample_rates_hz, config))

        usable_windows = sum(result.usable for result in quality_results)
        rows.append(
            {
                "scenario": (
                    "clean"
                    if gap_fraction == 0.0 and noise_level == 0.0
                    else f"gap_{gap_fraction:.3f}"
                    if gap_fraction
                    else f"noise_{noise_level:.3f}_channel_sd"
                ),
                "gap_fraction_injected": gap_fraction,
                "noise_std_channel_sd": noise_level,
                "candidate_windows": candidate_windows,
                "available_analysis_windows": usable_windows,
                "usable_windows": usable_windows,
                "qc_pass_rate": usable_windows / candidate_windows,
                "mean_ecg_sqi": float(np.mean([result.ecg_sqi for result in quality_results])),
                "mean_ppg_sqi": float(np.mean([result.ppg_sqi for result in quality_results])),
                "mean_abp_sqi": float(np.mean([result.abp_sqi for result in quality_results])),
            }
        )

    return {
        "schema_version": "sqi-missingness-impact/1.0",
        "status": "PASS",
        "failure_reason_code": None,
        "case_id": case.case_id,
        "synthetic_only": True,
        "clinical_validation": False,
        "window_seconds": window_seconds,
        "minimum_sqi": config.minimum_sqi,
        "minimum_sqi_source": "QualityConfig.minimum_sqi",
        "clinical_threshold_interpretation": "PI_TO_DEFINE",
        "rows": rows,
        "safety": {"dosing": False, "alerts": False, "clinical_decision": False},
    }


__all__ = ["run_sqi_missingness_impact"]
