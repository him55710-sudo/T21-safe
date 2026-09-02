"""VitalDB public virtual-real-time adapter with explicit fixture fallback."""

from __future__ import annotations

import asyncio
import time
from contextlib import suppress
from datetime import datetime
from typing import Any

import httpx
import numpy as np

from t21_engine.adapters.base import CaseDescriptor, DataAdapter
from t21_engine.types import SignalBatch, SourceMetadata

VITALDB_ATTRIBUTION = "VitalDB Open Dataset, CC BY 4.0; Lee HC et al., Scientific Data (2022)."

TRACK_MAP = {
    "SNUADC/ECG_II": "ecg_ii",
    "SNUADC/PLETH": "ppg",
    "SNUADC/ART": "abp",
    "Solar8000/HR": "hr_bpm",
    "Solar8000/ART_SBP": "sbp_mm_hg",
    "Solar8000/ART_DBP": "dbp_mm_hg",
    "Solar8000/ART_MBP": "map_mm_hg",
    "Solar8000/PLETH_SPO2": "spo2_pct",
    "Solar8000/ETCO2": "etco2_mm_hg",
    "Solar8000/RR": "resp_bpm",
}


class VitalDBAdapter(DataAdapter):
    def __init__(
        self,
        *,
        base_url: str = "https://api.vitaldb.net",
        location: str = "OR1",
        timeout_seconds: float = 12.0,
        target_sample_rate_hz: float = 100.0,
        fallback: DataAdapter | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.location = location
        self.timeout_seconds = timeout_seconds
        self.target_sample_rate_hz = target_sample_rate_hz
        self.fallback = fallback
        self._client = client

    async def list_cases(self) -> list[CaseDescriptor]:
        return [
            CaseDescriptor(
                case_id="vitaldb:public-live",
                title="VitalDB public virtual real-time operating room",
                source="VitalDB",
                data_type="public perioperative waveform",
                available_signals=tuple(TRACK_MAP.values()),
                is_synthetic=False,
                ds_status="unknown_or_non_ds",
                clinical_use_allowed=False,
                attribution=VITALDB_ATTRIBUTION,
            )
        ]

    async def load_case(
        self,
        case_id: str,
        *,
        duration_seconds: float | None = None,
    ) -> SignalBatch:
        if case_id != "vitaldb:public-live":
            raise KeyError(f"unknown VitalDB case: {case_id}")
        # VitalDB FHIR currently rejects decimal strings such as ``window=3.0``.
        window = max(1, min(int(round(duration_seconds or 10.0)), 60))
        started = time.perf_counter()
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self.timeout_seconds)
        observations: dict[str, dict[str, Any]] = {}
        errors: list[str] = []

        async def fetch_track(
            track: str, canonical: str
        ) -> tuple[str, dict[str, Any] | None, str | None]:
            try:
                response = await client.get(
                    f"{self.base_url}/fhir/Location/{self.location}/$sample",
                    params={"code": track, "window": window},
                )
                response.raise_for_status()
                payload = response.json()
                if payload.get("resourceType") == "Observation" and payload.get("valueSampledData"):
                    return canonical, payload, None
                return canonical, None, f"{track}: no sampled data"
            except (httpx.HTTPError, ValueError, TypeError) as exc:
                return canonical, None, f"{track}: {type(exc).__name__}"

        try:
            results = await asyncio.gather(
                *(fetch_track(track, canonical) for track, canonical in TRACK_MAP.items())
            )
            for canonical, payload, error in results:
                if payload is not None:
                    observations[canonical] = payload
                elif error is not None:
                    errors.append(error)
        finally:
            if owns_client:
                await client.aclose()

        if not observations:
            if self.fallback is None:
                raise ConnectionError("VitalDB returned no usable tracks: " + "; ".join(errors))
            fallback = await self.fallback.load_case(
                "vitaldb:fallback", duration_seconds=duration_seconds
            )
            fallback.provenance["fallback_reason"] = "; ".join(errors) or "no usable tracks"
            fallback.latency_ms = (time.perf_counter() - started) * 1000.0
            return fallback

        target_fs = self.target_sample_rate_hz
        target_count = max(1, int(round(window * target_fs)))
        timestamps = np.arange(target_count, dtype=np.float64) / target_fs
        signals: dict[str, np.ndarray[Any, np.dtype[np.float64]]] = {}
        sample_rates: dict[str, float] = {}
        source_case_id = "unknown"
        source_case_ids: set[str] = set()
        effective_starts: list[float] = []
        for canonical, observation in observations.items():
            sampled = observation["valueSampledData"]
            values = self._decode_sampled_data(sampled)
            period_ms = float(sampled.get("period", 1000.0))
            source_fs = 1000.0 / period_ms
            source_times = np.arange(values.size, dtype=np.float64) / source_fs
            finite = np.isfinite(values)
            if finite.sum() >= 2:
                resampled = np.interp(timestamps, source_times[finite], values[finite])
                resampled[timestamps > source_times[finite][-1]] = np.nan
            elif finite.sum() == 1:
                resampled = np.full(target_count, values[finite][0], dtype=np.float64)
            else:
                continue
            signals[canonical] = resampled.astype(np.float64)
            sample_rates[canonical] = target_fs
            observation_case_id = self._case_id(observation)
            if observation_case_id is not None:
                source_case_id = observation_case_id
                source_case_ids.add(observation_case_id)
            effective_start = observation.get("effectivePeriod", {}).get("start")
            if effective_start:
                with suppress(ValueError):
                    effective_starts.append(
                        datetime.fromisoformat(
                            str(effective_start).replace("Z", "+00:00")
                        ).timestamp()
                    )

        if not signals:
            raise ValueError("VitalDB observations contained no decodable samples")
        synchronization_error_ms = (
            (max(effective_starts) - min(effective_starts)) * 1000.0
            if len(effective_starts) >= 2
            else 0.0
        )
        return SignalBatch(
            timestamps_s=timestamps,
            signals=signals,
            sample_rates_hz=sample_rates,
            source=SourceMetadata(
                dataset="VitalDB",
                case_id=f"vitaldb:{source_case_id}",
                is_synthetic=False,
                ds_status="unknown_or_non_ds",
                attribution=VITALDB_ATTRIBUTION,
                data_type="public perioperative waveform",
            ),
            provenance={
                name: "raw:VitalDB FHIR virtual real-time API; resampled to 100 Hz"
                for name in signals
            }
            | {
                "source_case_consistency": (
                    "consistent" if len(source_case_ids) <= 1 else "mismatched_across_tracks"
                )
            },
            latency_ms=(time.perf_counter() - started) * 1000.0,
            timestamp_synchronized=(
                synchronization_error_ms <= 100.0 and len(source_case_ids) <= 1
            ),
            synchronization_error_ms=synchronization_error_ms,
        )

    @staticmethod
    def _decode_sampled_data(sampled: dict[str, Any]) -> np.ndarray[Any, np.dtype[np.float64]]:
        tokens = str(sampled.get("data", "")).split()
        origin = float(sampled.get("origin", {}).get("value", 0.0))
        factor = float(sampled.get("factor", 1.0))
        lower = float(sampled.get("lowerLimit", "nan"))
        upper = float(sampled.get("upperLimit", "nan"))
        values: list[float] = []
        for token in tokens:
            if token in {"E", "U", "L", "N"}:
                values.append(np.nan)
            elif token == "<":
                values.append(lower)
            elif token == ">":
                values.append(upper)
            else:
                try:
                    values.append(origin + factor * float(token))
                except ValueError:
                    values.append(np.nan)
        return np.asarray(values, dtype=np.float64)

    @staticmethod
    def _case_id(observation: dict[str, Any]) -> str | None:
        encounter = str(observation.get("encounter", {}).get("reference", ""))
        if encounter.startswith("Encounter/"):
            return encounter.split("/", 1)[1]
        for extension in observation.get("extension", []):
            if str(extension.get("url", "")).endswith("replay-source"):
                for item in extension.get("extension", []):
                    if item.get("url") == "caseid":
                        return str(item.get("valueInteger"))
        return None
