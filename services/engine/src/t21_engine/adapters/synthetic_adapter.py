"""Deterministic synthetic scenarios for safe offline verification."""

from __future__ import annotations

import numpy as np

from t21_engine.adapters.base import CaseDescriptor, DataAdapter
from t21_engine.types import SignalBatch, SourceMetadata

SCENARIOS = (
    "stable-baseline",
    "progressive-hr-decline",
    "progressive-map-decline",
    "ppg-amplitude-reduction",
    "ecg-motion-artifact",
    "ppg-signal-loss",
    "temporary-desaturation",
    "recovery-after-event",
    "composite-demo",
)


class SyntheticAdapter(DataAdapter):
    def __init__(self, sample_rate_hz: float = 100.0, seed: int = 20250321) -> None:
        self.sample_rate_hz = sample_rate_hz
        self.seed = seed

    async def list_cases(self) -> list[CaseDescriptor]:
        return [
            CaseDescriptor(
                case_id=f"synthetic:{scenario}",
                title=f"Synthetic {scenario.replace('-', ' ')}",
                source="T21 deterministic synthetic generator",
                data_type="generated waveform",
                available_signals=("ECG_II", "PPG", "ABP", "HR", "MAP", "SpO2"),
                is_synthetic=True,
                ds_status="synthetic_not_applicable",
                clinical_use_allowed=False,
                attribution="Generated locally; no patient data.",
            )
            for scenario in SCENARIOS
        ]

    async def load_case(
        self,
        case_id: str,
        *,
        duration_seconds: float | None = None,
    ) -> SignalBatch:
        scenario = case_id.removeprefix("synthetic:")
        if scenario not in SCENARIOS:
            raise KeyError(f"unknown synthetic scenario: {case_id}")
        duration = float(duration_seconds or 240.0)
        if duration <= 0:
            raise ValueError("duration_seconds must be positive")

        fs = self.sample_rate_hz
        timestamps = np.arange(0.0, duration, 1.0 / fs, dtype=np.float64)
        rng = np.random.default_rng(self.seed + SCENARIOS.index(scenario))
        event_start = min(180.0, duration * 0.8)
        progress = np.clip((timestamps - event_start) / max(duration - event_start, 1.0), 0.0, 1.0)

        hr = np.full_like(timestamps, 72.0)
        map_values = np.full_like(timestamps, 82.0)
        ppg_scale = np.ones_like(timestamps)
        spo2 = np.full_like(timestamps, 98.0)

        if scenario in {"progressive-hr-decline", "composite-demo", "recovery-after-event"}:
            hr -= 26.0 * progress
        if scenario in {"progressive-map-decline", "composite-demo", "recovery-after-event"}:
            map_values -= 30.0 * progress
        if scenario in {"ppg-amplitude-reduction", "composite-demo", "recovery-after-event"}:
            ppg_scale -= 0.65 * progress
        if scenario in {"temporary-desaturation", "composite-demo"}:
            center = event_start + max(duration - event_start, 1.0) * 0.55
            spo2 -= 10.0 * np.exp(-0.5 * ((timestamps - center) / 12.0) ** 2)
        if scenario == "recovery-after-event":
            recovery = np.clip((timestamps - (event_start + 25.0)) / 25.0, 0.0, 1.0)
            hr += 24.0 * recovery
            map_values += 27.0 * recovery
            ppg_scale += 0.58 * recovery

        phase = np.cumsum(hr / 60.0) / fs
        cardiac_phase = np.mod(phase, 1.0)
        ecg = 0.03 * np.sin(2.0 * np.pi * 1.2 * timestamps)
        ecg += 1.1 * np.exp(-0.5 * ((cardiac_phase - 0.08) / 0.018) ** 2)
        ecg -= 0.15 * np.exp(-0.5 * ((cardiac_phase - 0.12) / 0.025) ** 2)
        ecg += rng.normal(0.0, 0.012, timestamps.size)

        delayed_phase = np.mod(cardiac_phase - 0.18, 1.0)
        ppg_pulse = np.exp(-5.0 * delayed_phase) * (1.0 - np.exp(-35.0 * delayed_phase))
        ppg = ppg_scale * ppg_pulse + rng.normal(0.0, 0.006, timestamps.size)
        pulse_pressure = 42.0 * ppg_scale
        abp = map_values - pulse_pressure / 3.0 + pulse_pressure * ppg_pulse
        abp += rng.normal(0.0, 0.25, timestamps.size)

        if scenario == "ecg-motion-artifact":
            mask = (timestamps >= event_start) & (timestamps < event_start + 20.0)
            ecg[mask] += rng.normal(0.0, 1.5, int(mask.sum()))
        if scenario == "ppg-signal-loss":
            mask = (timestamps >= event_start) & (timestamps < event_start + 25.0)
            ppg[mask] = np.nan

        sbp = map_values + (2.0 / 3.0) * pulse_pressure
        dbp = map_values - (1.0 / 3.0) * pulse_pressure
        signals = {
            "ecg_ii": ecg.astype(np.float64),
            "ppg": ppg.astype(np.float64),
            "abp": abp.astype(np.float64),
            "hr_bpm": hr.astype(np.float64),
            "sbp_mm_hg": sbp.astype(np.float64),
            "dbp_mm_hg": dbp.astype(np.float64),
            "map_mm_hg": map_values.astype(np.float64),
            "spo2_pct": spo2.astype(np.float64),
            "etco2_mm_hg": np.full_like(timestamps, 36.0),
            "resp_bpm": np.full_like(timestamps, 14.0),
        }
        return SignalBatch(
            timestamps_s=timestamps,
            signals=signals,
            sample_rates_hz={name: fs for name in signals},
            source=SourceMetadata(
                dataset="T21 synthetic generator",
                case_id=case_id,
                is_synthetic=True,
                ds_status="synthetic_not_applicable",
                attribution="Generated locally with a pinned deterministic seed; no PHI.",
                data_type="generated waveform",
            ),
            provenance={name: "raw:deterministic_synthetic_v0.1" for name in signals},
        )
