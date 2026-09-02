"""Small local CSV fixture adapter for network-independent replay tests."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from t21_engine.adapters.base import CaseDescriptor, DataAdapter
from t21_engine.types import SignalBatch, SourceMetadata


class LocalFixtureAdapter(DataAdapter):
    def __init__(self, fixture_path: Path, *, sample_rate_hz: float = 10.0) -> None:
        self.fixture_path = fixture_path
        self.sample_rate_hz = sample_rate_hz

    async def list_cases(self) -> list[CaseDescriptor]:
        if not self.fixture_path.exists():
            return []
        return [
            CaseDescriptor(
                case_id="local:fixture",
                title="Bundled synthetic waveform fixture",
                source="local synthetic fixture",
                data_type="synthetic CSV waveform",
                available_signals=("ECG_II", "PPG", "ABP", "HR", "MAP", "SpO2"),
                is_synthetic=True,
                ds_status="synthetic_not_applicable",
                clinical_use_allowed=False,
                attribution="Generated synthetic local fixture; contains no patient records.",
            )
        ]

    async def load_case(
        self,
        case_id: str,
        *,
        duration_seconds: float | None = None,
    ) -> SignalBatch:
        if case_id not in {"local:fixture", "vitaldb:fallback"}:
            raise KeyError(f"unknown local fixture: {case_id}")
        if not self.fixture_path.exists():
            raise FileNotFoundError(self.fixture_path)
        with self.fixture_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            raise ValueError("fixture contains no rows")
        names = [name for name in rows[0] if name != "timestamp_s"]
        timestamps = np.asarray([float(row["timestamp_s"]) for row in rows], dtype=np.float64)
        signals = {
            name: np.asarray(
                [float(row[name]) if row[name].strip() else np.nan for row in rows],
                dtype=np.float64,
            )
            for name in names
        }
        repeated = False
        if duration_seconds is not None:
            if not np.isfinite(duration_seconds) or duration_seconds <= 0.0:
                raise ValueError("duration_seconds must be positive and finite")
            target_count = max(1, int(round(duration_seconds * self.sample_rate_hz)))
            repeated = target_count > timestamps.size
            signals = {
                name: np.resize(values, target_count).astype(np.float64)
                for name, values in signals.items()
            }
            timestamps = np.arange(target_count, dtype=np.float64) / self.sample_rate_hz
        provenance_suffix = (
            f"; cyclic synthetic repetition to {duration_seconds:g}s"
            if repeated and duration_seconds is not None
            else ""
        )
        return SignalBatch(
            timestamps_s=timestamps,
            signals=signals,
            sample_rates_hz={name: self.sample_rate_hz for name in signals},
            source=SourceMetadata(
                dataset="Local synthetic fixture",
                case_id="local:fixture",
                is_synthetic=True,
                ds_status="synthetic_not_applicable",
                attribution="Generated synthetic local fixture; contains no patient records.",
                data_type="synthetic CSV waveform",
            ),
            provenance={
                name: f"raw:csv:{self.fixture_path.name}{provenance_suffix}" for name in signals
            },
        )
