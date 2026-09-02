"""Shared, dependency-light types and safety invariants."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]


class PipelineMode(StrEnum):
    GENERIC_VALIDATION_MODE = "GENERIC_VALIDATION_MODE"
    DS_HYPOTHESIS_MODE = "DS_HYPOTHESIS_MODE"


class RiskLevel(StrEnum):
    BASELINE = "BASELINE"
    STABLE = "STABLE"
    WATCH = "WATCH"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class SourceMetadata:
    dataset: str
    case_id: str
    is_synthetic: bool
    ds_status: str = "unknown_or_non_ds"
    age_group: str = "unknown"
    clinical_use_allowed: bool = False
    attribution: str = ""
    data_type: str = "waveform"


@dataclass(slots=True)
class SignalBatch:
    timestamps_s: FloatArray
    signals: dict[str, FloatArray]
    sample_rates_hz: dict[str, float]
    source: SourceMetadata
    provenance: dict[str, str] = field(default_factory=dict)
    latency_ms: float = 0.0
    gap_detected: bool = False
    out_of_order_count: int = 0
    timestamp_synchronized: bool = True
    synchronization_error_ms: float = 0.0

    def __post_init__(self) -> None:
        if self.timestamps_s.ndim != 1:
            raise ValueError("timestamps_s must be one-dimensional")
        for name, values in self.signals.items():
            if values.ndim != 1:
                raise ValueError(f"signal {name} must be one-dimensional")


@dataclass(frozen=True, slots=True)
class QualityResult:
    ecg_sqi: float | None
    ppg_sqi: float | None
    abp_sqi: float | None
    usable: bool
    unavailable_signals: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    gap_fraction: float = 0.0
    timestamp_synchronized: bool = True


@dataclass(frozen=True, slots=True)
class BeatSeries:
    indices: npt.NDArray[np.int64]
    times_s: FloatArray
    confidence: float
    kind: str


@dataclass(frozen=True, slots=True)
class DistributionSummary:
    minimum: float
    p25: float
    median: float
    p75: float
    maximum: float


@dataclass(frozen=True, slots=True)
class BaselineState:
    calibrated: bool
    progress: float
    confidence: float
    median_hr: float | None = None
    hr_iqr: float | None = None
    median_map: float | None = None
    median_ppg_amplitude: float | None = None
    rmssd_ms: float | None = None
    sdnn_ms: float | None = None
    quality_median: float | None = None
    available_modalities: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    hr_distribution: DistributionSummary | None = None
    quality_distribution: DistributionSummary | None = None


@dataclass(frozen=True, slots=True)
class FeatureSet:
    values: dict[str, float | None]
    window_seconds: int
    valid_beat_count: int
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RiskResult:
    score: float | None
    level: RiskLevel
    valid: bool
    confidence: float
    horizon_seconds: int
    reasons: tuple[str, ...]
    model_version: str
    data_source: str
    population_validated_on: str = "non-DS research data only"
    limitations: tuple[str, ...] = (
        "Not a calibrated clinical probability.",
        "Not validated for Down syndrome or pediatric clinical use.",
    )

    def __post_init__(self) -> None:
        if self.valid and self.score is None:
            raise ValueError("a valid research index requires a score")
        if not self.valid and (self.score is not None or self.level is not RiskLevel.INVALID):
            raise ValueError("an invalid research index must withhold score and use INVALID level")
        if self.score is not None and not 0.0 <= self.score <= 100.0:
            raise ValueError("score must be within 0..100")


JsonObject = dict[str, Any]
