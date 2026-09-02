"""Versioned configuration for the deterministic signal pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


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
    watch_threshold: float = 25.0
    elevated_threshold: float = 50.0
    high_threshold: float = 75.0
    hypotension_map_mm_hg: float = 65.0
    hypotension_duration_seconds: float = 60.0
    relative_hr_decline_pct: float = -20.0
    relative_map_decline_pct: float = -20.0


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
