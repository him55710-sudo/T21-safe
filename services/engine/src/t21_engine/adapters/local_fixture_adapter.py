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
                title="Bundled de-identified waveform fixture",
                source="local fixture",
                data_type="CSV waveform",
                available_signals=("ECG_II", "PPG", "ABP", "HR", "MAP", "SpO2"),
                is_synthetic=False,
                ds_status="unknown_or_non_ds",
                clinical_use_allowed=False,
                attribution="Local development fixture; not clinical data.",
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
        if duration_seconds is not None:
            keep = timestamps <= duration_seconds
            timestamps = timestamps[keep]
            signals = {name: values[keep] for name, values in signals.items()}
        return SignalBatch(
            timestamps_s=timestamps,
            signals=signals,
            sample_rates_hz={name: self.sample_rate_hz for name in signals},
            source=SourceMetadata(
                dataset="Local fixture",
                case_id="local:fixture",
                is_synthetic=False,
                attribution="Local development fixture; not clinical data.",
            ),
            provenance={name: f"raw:csv:{self.fixture_path.name}" for name in signals},
        )
