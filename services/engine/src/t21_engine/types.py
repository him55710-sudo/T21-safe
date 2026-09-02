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
        if not np.isfinite(self.timestamps_s).all():
            raise ValueError("timestamps_s must contain only finite values")
        for name, values in self.signals.items():
            if values.ndim != 1:
                raise ValueError(f"signal {name} must be one-dimensional")
            if values.size != self.timestamps_s.size:
                raise ValueError(f"signal {name} must align with timestamps_s")
            sample_rate = self.sample_rates_hz.get(name)
            if sample_rate is None or not np.isfinite(sample_rate) or sample_rate <= 0.0:
                raise ValueError(f"signal {name} requires a positive finite sample rate")
        rates = [self.sample_rates_hz[name] for name in self.signals]
        if rates and not all(np.isclose(rate, rates[0]) for rate in rates[1:]):
            raise ValueError("signals on one timestamp grid must share a sample rate")
        if not np.isfinite(self.latency_ms) or self.latency_ms < 0.0:
            raise ValueError("latency_ms must be non-negative and finite")
        if self.out_of_order_count < 0:
            raise ValueError("out_of_order_count must be non-negative")
        if not np.isfinite(self.synchronization_error_ms) or self.synchronization_error_ms < 0.0:
            raise ValueError("synchronization_error_ms must be non-negative and finite")


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
class ShadowFeatureWindow:
    """Local research capture of already-computed features; never an action request."""

    window_seconds: int
    valid_beat_count: int
    absolute_change: dict[str, float | None]
    relative_change_pct: dict[str, float | None]
    hrv: dict[str, float | None]
    limitations: tuple[str, ...]
    evidence_status: str = "RESEARCH_HYPOTHESIS"
    clinical_decision_thresholds: str = "PI_TO_DEFINE"


@dataclass(frozen=True, slots=True)
class ShadowSafetyControls:
    """Fail-closed capabilities for an observe-only Path B session."""

    actuation: bool = False
    dosing: bool = False
    closed_loop: bool = False
    drug_advice: bool = False
    emr_write: bool = False

    def __post_init__(self) -> None:
        if any((self.actuation, self.dosing, self.closed_loop, self.drug_advice, self.emr_write)):
            raise ValueError(
                "shadow capture rejects actuation, dosing, closed-loop, drug advice, and EMR writes"
            )


@dataclass(frozen=True, slots=True)
class ExportManifest:
    """Fail-closed description of a local shadow-metadata research export."""

    export_id: str
    session_id: str
    event_ids: tuple[str, ...]
    includes_waveforms: bool = False
    includes_phi: bool = False
    storage_scope: str = "LOCAL_ONLY"
    content_scope: str = "SHADOW_CAPTURE_METADATA_ONLY"
    mode: str = "OBSERVE_ONLY_SHADOW"
    is_synthetic: bool = True
    controls: ShadowSafetyControls = field(default_factory=ShadowSafetyControls)

    def __post_init__(self) -> None:
        if not self.export_id or not self.session_id or not self.event_ids:
            raise ValueError("export_id, session_id, and event_ids must be non-empty")
        if any(not event_id for event_id in self.event_ids):
            raise ValueError("event_ids must not contain empty values")
        if self.includes_waveforms or self.includes_phi:
            raise ValueError("local research exports reject waveforms and PHI")
        if self.storage_scope != "LOCAL_ONLY":
            raise ValueError("research exports are local-only")
        if self.content_scope != "SHADOW_CAPTURE_METADATA_ONLY":
            raise ValueError("research exports contain shadow-capture metadata only")
        if self.mode != "OBSERVE_ONLY_SHADOW":
            raise ValueError("research exports are observe-only")
        if not self.is_synthetic:
            raise ValueError("research exports require synthetic, non-PHI data")


@dataclass(frozen=True, slots=True)
class RiskResult:
    score: float | None
    level: RiskLevel
    valid: bool
    confidence: float
    observation_context_seconds: int
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
