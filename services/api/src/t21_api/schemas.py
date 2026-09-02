"""Pydantic v2 API contracts."""

from __future__ import annotations

from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from t21_engine.types import PipelineMode, RiskLevel

AgeGroup = Literal[
    "unknown",
    "neonate",
    "infant",
    "child",
    "adolescent",
    "adult",
    "older_adult",
]

ANALYZE_SIGNAL_NAMES = frozenset(
    {
        "ecg_ii",
        "ppg",
        "abp",
        "hr_bpm",
        "sbp_mm_hg",
        "dbp_mm_hg",
        "map_mm_hg",
        "spo2_pct",
        "etco2_mm_hg",
        "resp",
        "resp_bpm",
        "bis",
    }
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class HealthResponse(StrictModel):
    status: Literal["ok"] = "ok"
    mode: Literal["research"] = "research"
    version: str = "0.2.0"


class CaseResponse(StrictModel):
    case_id: str
    title: str
    source: str
    data_type: str
    available_signals: list[str]
    is_synthetic: bool
    ds_status: str
    clinical_use_allowed: bool
    attribution: str


class ReplayRequest(StrictModel):
    case_id: str = Field(min_length=1, max_length=200)
    speed: float = Field(default=1.0, gt=0.0, le=1000.0)
    baseline_seconds: int = Field(default=180, ge=3, le=600)
    mode: PipelineMode = PipelineMode.GENERIC_VALIDATION_MODE


class ReplayResponse(StrictModel):
    session_id: str
    stream_url: str


class SourceEvent(StrictModel):
    dataset: str
    case_id: str
    is_synthetic: bool
    attribution: str
    data_type: str


class PatientContextEvent(StrictModel):
    ds_status: str
    age_group: AgeGroup


class SignalsEvent(StrictModel):
    ecg_ii: list[float | None]
    ppg: list[float | None]
    abp: list[float | None]
    hr_bpm: float | None
    sbp_mm_hg: float | None
    dbp_mm_hg: float | None
    map_mm_hg: float | None
    spo2_pct: float | None
    etco2_mm_hg: float | None


class QualityEvent(StrictModel):
    ecg_sqi: float | None = Field(default=None, ge=0.0, le=1.0)
    ppg_sqi: float | None = Field(default=None, ge=0.0, le=1.0)
    abp_sqi: float | None = Field(default=None, ge=0.0, le=1.0)
    usable: bool
    unavailable_signals: list[str]
    reasons: list[str]
    gap_fraction: float = Field(ge=0.0, le=1.0)
    timestamp_synchronized: bool


class BaselineEvent(StrictModel):
    calibrated: bool
    progress: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str]
    values: dict[str, float | None]


class FeaturesEvent(StrictModel):
    delta_hr_pct: float | None
    hr_slope_bpm_min: float | None
    rmssd_ms: float | None
    sdnn_ms: float | None
    ppg_amp_delta_pct: float | None
    map_slope_mm_hg_min: float | None
    ptt_ms: float | None


class RiskEvent(StrictModel):
    name: Literal["Research Instability Index"]
    score: float | None = Field(default=None, ge=0.0, le=100.0)
    level: RiskLevel
    valid: bool
    observation_context_seconds: int = Field(gt=0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str]
    model_version: str
    data_source: str
    population_validated_on: str
    limitations: list[str]

    @model_validator(mode="after")
    def validate_withholding(self) -> RiskEvent:
        if self.valid and self.score is None:
            raise ValueError("valid risk output requires a score")
        if not self.valid and (self.score is not None or self.level is not RiskLevel.INVALID):
            raise ValueError("invalid risk output must withhold score and use INVALID")
        return self


class TransportEvent(StrictModel):
    source_latency_ms: float = Field(ge=0.0)
    processing_latency_ms: float = Field(ge=0.0)
    data_gap: bool
    out_of_order_count: int = Field(ge=0)
    synchronization_error_ms: float = Field(ge=0.0)


class ProvenanceEvent(StrictModel):
    raw: dict[str, str]
    processed: dict[str, str]


class StreamEvent(StrictModel):
    timestamp_ms: int = Field(ge=0)
    mode: PipelineMode
    source: SourceEvent
    patient_context: PatientContextEvent
    signals: SignalsEvent
    quality: QualityEvent
    baseline: BaselineEvent
    features: FeaturesEvent
    risk: RiskEvent
    transport: TransportEvent
    provenance: ProvenanceEvent
    disclaimer: Literal[
        "Research prototype; not for diagnosis, treatment, dosing, or clinical monitoring."
    ]


class AnalyzeWindowRequest(StrictModel):
    timestamps_s: list[float] = Field(min_length=2, max_length=120_000)
    signals: dict[str, list[float | None]] = Field(
        json_schema_extra=cast(
            dict[str, Any],
            {"propertyNames": {"enum": sorted(ANALYZE_SIGNAL_NAMES)}},
        )
    )
    sample_rate_hz: float = Field(gt=0.0, le=1000.0)
    baseline_seconds: int = Field(default=180, ge=3, le=600)
    mode: PipelineMode = PipelineMode.GENERIC_VALIDATION_MODE
    ds_status: Literal["unknown_or_non_ds", "research_hypothesis_only"] = "unknown_or_non_ds"
    age_group: AgeGroup = "unknown"

    @field_validator("signals")
    @classmethod
    def validate_signal_names(
        cls, signals: dict[str, list[float | None]]
    ) -> dict[str, list[float | None]]:
        if not signals:
            raise ValueError("at least one canonical signal is required")
        unknown = sorted(set(signals) - ANALYZE_SIGNAL_NAMES)
        if unknown:
            raise ValueError(f"unsupported signal names: {unknown}")
        return signals

    @model_validator(mode="after")
    def validate_alignment(self) -> AnalyzeWindowRequest:
        expected = len(self.timestamps_s)
        if any(len(values) != expected for values in self.signals.values()):
            raise ValueError("all signal arrays must align with timestamps_s")
        return self


class EvidenceItem(StrictModel):
    evidence_id: str
    feature_or_model: str
    citation: str
    url: str
    applicability: str
    limitation: str


class EvidenceResponse(StrictModel):
    model_version: str
    feature_schema_version: str
    clinical_validation: bool
    items: list[EvidenceItem]
