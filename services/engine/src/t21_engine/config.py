"""Versioned configuration for the deterministic signal pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite


@dataclass(frozen=True, slots=True)
class FilterConfig:
    ecg_low_hz: float = 0.5
    ecg_high_hz: float = 35.0
    ppg_low_hz: float = 0.4
    ppg_high_hz: float = 8.0
    abp_low_hz: float = 0.3
    abp_high_hz: float = 12.0
    order: int = 3
    mains_hz: float | None = None


@dataclass(frozen=True, slots=True)
class QualityConfig:
    minimum_sqi: float = 0.55
    maximum_gap_fraction: float = 0.15
    maximum_flatline_fraction: float = 0.2
    minimum_valid_beats: int = 4
    synchronization_tolerance_ms: float = 100.0
    maximum_source_latency_ms: float = 1000.0


@dataclass(frozen=True, slots=True)
class RiskConfig:
    model_version: str = "rii-v0.1"
    observation_context_seconds: int = 120
    relative_hr_decline_weight: float = 25.0
    relative_map_decline_weight: float = 35.0
    relative_ppg_amplitude_decline_weight: float = 15.0
    hr_slope_weight: float = 5.0
    map_slope_weight: float = 10.0
    low_spo2_weight: float = 10.0
    relative_hr_decline_full_scale_pct: float = 35.0
    relative_map_decline_full_scale_pct: float = 35.0
    relative_ppg_amplitude_decline_full_scale_pct: float = 60.0
    hr_slope_full_scale_bpm_min: float = 12.0
    map_slope_full_scale_mm_hg_min: float = 15.0
    spo2_reference_pct: float = 94.0
    spo2_full_scale_decline_pct: float = 10.0
    watch_threshold: float = 25.0
    elevated_threshold: float = 50.0
    high_threshold: float = 75.0
    hypotension_map_mm_hg: float = 65.0
    hypotension_duration_seconds: float = 60.0
    relative_hr_decline_pct: float = -20.0
    relative_map_decline_pct: float = -20.0

    def __post_init__(self) -> None:
        weights = (
            self.relative_hr_decline_weight,
            self.relative_map_decline_weight,
            self.relative_ppg_amplitude_decline_weight,
            self.hr_slope_weight,
            self.map_slope_weight,
            self.low_spo2_weight,
        )
        scales = (
            self.relative_hr_decline_full_scale_pct,
            self.relative_map_decline_full_scale_pct,
            self.relative_ppg_amplitude_decline_full_scale_pct,
            self.hr_slope_full_scale_bpm_min,
            self.map_slope_full_scale_mm_hg_min,
            self.spo2_full_scale_decline_pct,
        )
        if not all(isfinite(value) and value >= 0.0 for value in weights):
            raise ValueError("risk weights must be non-negative and finite")
        if not isfinite(sum(weights)) or abs(sum(weights) - 100.0) > 1e-9:
            raise ValueError("risk weights must sum to 100")
        if not all(isfinite(value) and value > 0.0 for value in scales):
            raise ValueError("risk full-scale values must be positive and finite")
        if not 0.0 <= self.watch_threshold < self.elevated_threshold < self.high_threshold <= 100.0:
            raise ValueError("risk thresholds must be ordered within 0..100")


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuration pinned by version for repeatable research runs."""

    config_version: str = "pipeline-v0.2"
    waveform_sample_rate_hz: float = 100.0
    feature_update_seconds: float = 1.0
    baseline_seconds: int = 180
    baseline_minimum_fraction: float = 0.8
    feature_windows_seconds: tuple[int, ...] = (30, 60, 180)
    buffer_seconds: int = 240
    deterministic_seed: int = 20250321
    filters: FilterConfig = field(default_factory=FilterConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
