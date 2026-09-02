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

    def __post_init__(self) -> None:
        bands = (
            ("ECG", self.ecg_low_hz, self.ecg_high_hz),
            ("PPG", self.ppg_low_hz, self.ppg_high_hz),
            ("ABP", self.abp_low_hz, self.abp_high_hz),
        )
        for name, low_hz, high_hz in bands:
            if not all(isfinite(value) for value in (low_hz, high_hz)) or not (
                0.0 < low_hz < high_hz
            ):
                raise ValueError(f"{name} filter cutoffs must be finite and ordered")
        if self.order < 1:
            raise ValueError("filter order must be positive")
        if self.mains_hz is not None and (not isfinite(self.mains_hz) or self.mains_hz <= 0.0):
            raise ValueError("mains frequency must be positive and finite")


@dataclass(frozen=True, slots=True)
class QualityConfig:
    minimum_sqi: float = 0.55
    maximum_gap_fraction: float = 0.15
    maximum_flatline_fraction: float = 0.2
    minimum_valid_beats: int = 4
    synchronization_tolerance_ms: float = 100.0
    maximum_source_latency_ms: float = 1000.0

    def __post_init__(self) -> None:
        fractions = (
            self.minimum_sqi,
            self.maximum_gap_fraction,
            self.maximum_flatline_fraction,
        )
        if not all(isfinite(value) and 0.0 <= value <= 1.0 for value in fractions):
            raise ValueError("quality fractions must be finite within 0..1")
        if self.minimum_valid_beats < 1:
            raise ValueError("minimum_valid_beats must be positive")
        if (
            not isfinite(self.synchronization_tolerance_ms)
            or self.synchronization_tolerance_ms < 0.0
        ):
            raise ValueError("synchronization tolerance must be non-negative and finite")


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
        if not (
            0.0 <= self.watch_threshold < self.elevated_threshold < self.high_threshold <= 100.0
        ):
            raise ValueError("risk thresholds must be ordered within 0..100")
        if self.horizon_seconds <= 0:
            raise ValueError("risk horizon must be positive")
        if not isfinite(self.hypotension_map_mm_hg) or self.hypotension_map_mm_hg <= 0.0:
            raise ValueError("hypotension MAP threshold must be positive and finite")
        if (
            not isfinite(self.hypotension_duration_seconds)
            or self.hypotension_duration_seconds <= 0.0
        ):
            raise ValueError("hypotension duration must be positive and finite")
        if not all(
            isfinite(value) and value <= 0.0
            for value in (self.relative_hr_decline_pct, self.relative_map_decline_pct)
        ):
            raise ValueError("relative decline thresholds must be finite and non-positive")
        if not isfinite(self.spo2_reference_pct) or not 0.0 <= self.spo2_reference_pct <= 100.0:
            raise ValueError("SpO2 reference must be finite within 0..100")
        if not self.model_version.strip():
            raise ValueError("model_version must not be empty")


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

    def __post_init__(self) -> None:
        if not self.config_version.strip():
            raise ValueError("config_version must not be empty")
        if not isfinite(self.waveform_sample_rate_hz) or self.waveform_sample_rate_hz <= 0.0:
            raise ValueError("waveform sample rate must be positive and finite")
        if not isfinite(self.feature_update_seconds) or self.feature_update_seconds <= 0.0:
            raise ValueError("feature update interval must be positive and finite")
        if self.baseline_seconds <= 0:
            raise ValueError("baseline_seconds must be positive")
        if not (
            isfinite(self.baseline_minimum_fraction) and 0.0 < self.baseline_minimum_fraction <= 1.0
        ):
            raise ValueError("baseline minimum fraction must be within (0, 1]")
        if (
            not self.feature_windows_seconds
            or any(window <= 0 for window in self.feature_windows_seconds)
            or len(set(self.feature_windows_seconds)) != len(self.feature_windows_seconds)
        ):
            raise ValueError("feature windows must be unique positive durations")
        if self.buffer_seconds <= 0:
            raise ValueError("buffer_seconds must be positive")
