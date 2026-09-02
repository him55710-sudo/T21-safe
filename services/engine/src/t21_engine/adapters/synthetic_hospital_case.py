"""Deterministic, non-clinical multi-channel hospital case fixtures.

The raw case keeps a clock per channel so ingestion alignment failures can be
tested before data are placed on the engine's shared timestamp grid.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal, TypeAlias

import numpy as np

from t21_engine.adapters.base import CaseDescriptor, DataAdapter
from t21_engine.types import SignalBatch, SourceMetadata

SYNTHETIC_HOSPITAL_CASE_ID = "synthetic:hospital-stable"
REQUIRED_CHANNELS = ("ecg_ii", "ppg", "abp", "spo2_pct", "resp")
StageName: TypeAlias = Literal["preop", "induction", "maintenance", "emergence", "PACU"]


@dataclass(frozen=True, slots=True)
class SyntheticChannel:
    name: str
    timestamps_s: np.ndarray
    values: np.ndarray
    sample_rate_hz: float
    unit: str


@dataclass(frozen=True, slots=True)
class AnesthesiaStage:
    """Synthetic research metadata; not a care event or recommendation."""

    name: StageName
    start_s: float
    end_s: float


@dataclass(frozen=True, slots=True)
class AlignmentFailure:
    code: str
    channel: str | None
    detail: str


@dataclass(frozen=True, slots=True)
class AlignmentReport:
    status: Literal["PASS", "FAIL"]
    reasons: tuple[AlignmentFailure, ...]
    checked_channels: tuple[str, ...]
    clinical_validation: bool = False
    synthetic_only: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reasons": [asdict(reason) for reason in self.reasons],
            "checked_channels": list(self.checked_channels),
            "clinical_validation": self.clinical_validation,
            "synthetic_only": self.synthetic_only,
        }


@dataclass(frozen=True, slots=True)
class SyntheticHospitalCase:
    case_id: str
    duration_s: float
    channels: dict[str, SyntheticChannel]
    anesthesia_stages: tuple[AnesthesiaStage, ...]
    synthetic_label: str = "SYNTHETIC_DATA"
    contains_phi: bool = False
    clinical_validation: bool = False
    mode: str = "OBSERVE_ONLY_SHADOW"

    def quality_report(
        self,
        *,
        alignment_tolerance_s: float = 0.020,
        gap_factor: float = 1.5,
    ) -> AlignmentReport:
        """Check raw channel clocks and fail closed with stable reason codes."""
        failures: list[AlignmentFailure] = []
        if not self.case_id.startswith("synthetic:hospital-"):
            failures.append(
                AlignmentFailure("NOT_SYNTHETIC_CASE", None, "Case ID lacks synthetic prefix.")
            )
        for name in REQUIRED_CHANNELS:
            channel = self.channels.get(name)
            if channel is None:
                failures.append(
                    AlignmentFailure("MISSING_CHANNEL", name, "Required channel is absent.")
                )
                continue
            timestamps = channel.timestamps_s
            if (
                timestamps.ndim != 1
                or channel.values.ndim != 1
                or timestamps.size != channel.values.size
            ):
                failures.append(
                    AlignmentFailure("LENGTH_MISMATCH", name, "Values and timestamps must align.")
                )
                continue
            if timestamps.size < 2 or not np.isfinite(timestamps).all():
                failures.append(
                    AlignmentFailure("INVALID_TIMESTAMPS", name, "Clock requires finite samples.")
                )
                continue
            deltas = np.diff(timestamps)
            if np.any(deltas <= 0.0):
                failures.append(
                    AlignmentFailure(
                        "OUT_OF_ORDER", name, "Timestamps must be strictly increasing."
                    )
                )
            if not np.isfinite(channel.sample_rate_hz) or channel.sample_rate_hz <= 0.0:
                failures.append(
                    AlignmentFailure(
                        "INVALID_SAMPLE_RATE", name, "Sample rate must be positive and finite."
                    )
                )
                continue
            expected_period = 1.0 / channel.sample_rate_hz
            if np.any(deltas > expected_period * gap_factor):
                failures.append(
                    AlignmentFailure(
                        "TIMESTAMP_GAP", name, "A timestamp interval exceeds tolerance."
                    )
                )
            if abs(float(timestamps[0])) > alignment_tolerance_s:
                failures.append(
                    AlignmentFailure(
                        "START_MISALIGNED", name, "Channel start is outside tolerance."
                    )
                )
            expected_last = (
                np.ceil(self.duration_s * channel.sample_rate_hz) - 1.0
            ) * expected_period
            if abs(float(timestamps[-1]) - expected_last) > max(
                alignment_tolerance_s, expected_period * 0.51
            ):
                failures.append(
                    AlignmentFailure("END_MISALIGNED", name, "Channel end is outside tolerance.")
                )
        return AlignmentReport(
            status="FAIL" if failures else "PASS",
            reasons=tuple(failures),
            checked_channels=tuple(sorted(self.channels)),
        )

    def to_signal_batch(self, *, sample_rate_hz: float = 100.0) -> SignalBatch:
        """Align a passing raw case to the existing engine batch contract."""
        report = self.quality_report()
        if report.status != "PASS":
            codes = ", ".join(reason.code for reason in report.reasons)
            raise ValueError(f"synthetic hospital alignment failed closed: {codes}")
        timestamps = np.arange(0.0, self.duration_s, 1.0 / sample_rate_hz, dtype=np.float64)
        signals = {
            name: np.interp(timestamps, channel.timestamps_s, channel.values).astype(np.float64)
            for name, channel in self.channels.items()
        }
        return SignalBatch(
            timestamps_s=timestamps,
            signals=signals,
            sample_rates_hz={name: sample_rate_hz for name in signals},
            source=SourceMetadata(
                dataset="T21 synthetic hospital case factory",
                case_id=self.case_id,
                is_synthetic=True,
                ds_status="synthetic_not_applicable",
                attribution="Generated locally with a pinned seed; synthetic-only and no PHI.",
                data_type="generated multi-signal perioperative waveform",
            ),
            provenance={name: "raw:deterministic_synthetic_hospital_v0.1" for name in signals},
        )


def _clock(duration_s: float, sample_rate_hz: float) -> np.ndarray:
    return np.arange(0.0, duration_s, 1.0 / sample_rate_hz, dtype=np.float64)


def build_synthetic_hospital_case(
    *, duration_s: float = 60.0, seed: int = 20250321
) -> SyntheticHospitalCase:
    """Create a reproducible, visibly synthetic hospital-style case."""
    if duration_s < 10.0:
        raise ValueError("duration_s must be at least 10 seconds")
    rates = {"ecg_ii": 250.0, "ppg": 100.0, "abp": 125.0, "spo2_pct": 1.0, "resp": 25.0}
    units = {"ecg_ii": "a.u.", "ppg": "a.u.", "abp": "a.u.", "spo2_pct": "a.u.", "resp": "a.u."}
    channels: dict[str, SyntheticChannel] = {}
    for offset, (name, rate) in enumerate(rates.items()):
        timestamps = _clock(duration_s, rate)
        rng = np.random.default_rng(seed + offset)
        cardiac_phase = np.mod(timestamps * 1.2, 1.0)
        respiratory = np.sin(2.0 * np.pi * 0.23 * timestamps)
        if name == "ecg_ii":
            values = 0.025 * np.sin(2.0 * np.pi * 1.2 * timestamps)
            values += np.exp(-0.5 * ((cardiac_phase - 0.08) / 0.018) ** 2)
            values += rng.normal(0.0, 0.008, timestamps.size)
        elif name == "ppg":
            phase = np.mod(cardiac_phase - 0.18, 1.0)
            values = np.exp(-5.0 * phase) * (1.0 - np.exp(-35.0 * phase))
            values += rng.normal(0.0, 0.004, timestamps.size)
        elif name == "abp":
            phase = np.mod(cardiac_phase - 0.16, 1.0)
            pulse = np.exp(-5.0 * phase) * (1.0 - np.exp(-35.0 * phase))
            values = 0.55 + 0.35 * pulse + rng.normal(0.0, 0.002, timestamps.size)
        elif name == "spo2_pct":
            values = 0.97 + 0.002 * respiratory + rng.normal(0.0, 0.0005, timestamps.size)
        else:
            values = respiratory + rng.normal(0.0, 0.01, timestamps.size)
        channels[name] = SyntheticChannel(
            name, timestamps, values.astype(np.float64), rate, units[name]
        )

    boundaries = np.asarray([0.0, 0.15, 0.30, 0.70, 0.85, 1.0]) * duration_s
    stage_names: tuple[StageName, ...] = (
        "preop",
        "induction",
        "maintenance",
        "emergence",
        "PACU",
    )
    stages = tuple(
        AnesthesiaStage(name, float(boundaries[index]), float(boundaries[index + 1]))
        for index, name in enumerate(stage_names)
    )
    return SyntheticHospitalCase(SYNTHETIC_HOSPITAL_CASE_ID, duration_s, channels, stages)


class SyntheticHospitalAdapter(DataAdapter):
    """Thin adapter from the factory into the replay pipeline's shared grid."""

    def __init__(self, *, sample_rate_hz: float = 100.0, seed: int = 20250321) -> None:
        self.sample_rate_hz = sample_rate_hz
        self.seed = seed

    async def list_cases(self) -> list[CaseDescriptor]:
        return [
            CaseDescriptor(
                case_id=SYNTHETIC_HOSPITAL_CASE_ID,
                title="Synthetic hospital perioperative case",
                source="T21 deterministic synthetic hospital case factory",
                data_type="generated multi-signal waveform",
                available_signals=("ECG_II", "PPG", "ABP", "SpO2", "RESP"),
                is_synthetic=True,
                ds_status="synthetic_not_applicable",
                clinical_use_allowed=False,
                attribution="Generated locally; synthetic-only and no patient data.",
            )
        ]

    async def load_case(
        self, case_id: str, *, duration_seconds: float | None = None
    ) -> SignalBatch:
        if case_id != SYNTHETIC_HOSPITAL_CASE_ID:
            raise KeyError(f"unknown synthetic hospital case: {case_id}")
        case = build_synthetic_hospital_case(
            duration_s=float(duration_seconds or 60.0), seed=self.seed
        )
        return case.to_signal_batch(sample_rate_hz=self.sample_rate_hz)


__all__ = [
    "AlignmentFailure",
    "AlignmentReport",
    "AnesthesiaStage",
    "REQUIRED_CHANNELS",
    "SYNTHETIC_HOSPITAL_CASE_ID",
    "SyntheticChannel",
    "SyntheticHospitalAdapter",
    "SyntheticHospitalCase",
    "build_synthetic_hospital_case",
]
