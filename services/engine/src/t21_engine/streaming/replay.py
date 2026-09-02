"""End-to-end deterministic replay pipeline producing API-ready events."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from dataclasses import replace

import numpy as np

from t21_engine.baseline.calibration import calibrate_baseline
from t21_engine.config import PipelineConfig
from t21_engine.features import extract_features
from t21_engine.preprocessing.filters import preprocess_ecg, preprocess_ppg
from t21_engine.quality.quality_gate import evaluate_quality
from t21_engine.risk.deterministic_index import compute_research_instability_index
from t21_engine.streaming.ring_buffer import RingBuffer
from t21_engine.types import PipelineMode, SignalBatch

DISCLAIMER = "Research prototype; not for diagnosis, treatment, dosing, or clinical monitoring."


def _last_value(values: np.ndarray | None) -> float | None:
    if values is None:
        return None
    finite = values[np.isfinite(values)]
    return float(finite[-1]) if finite.size else None


def _waveform_values(values: np.ndarray | None) -> list[float | None]:
    if values is None:
        return []
    return [float(value) if np.isfinite(value) else None for value in values]


class ReplayPipeline:
    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()

    async def events(
        self,
        batch: SignalBatch,
        *,
        mode: PipelineMode = PipelineMode.GENERIC_VALIDATION_MODE,
        baseline_seconds: int | None = None,
        speed: float = 1.0,
        real_time: bool = True,
    ) -> AsyncIterator[dict[str, object]]:
        if speed <= 0.0:
            raise ValueError("speed must be positive")
        baseline_duration = baseline_seconds or self.config.baseline_seconds
        effective_config = replace(self.config, baseline_seconds=baseline_duration)
        fs = batch.sample_rates_hz.get(
            "ecg_ii",
            next(iter(batch.sample_rates_hz.values()), effective_config.waveform_sample_rate_hz),
        )
        chunk_size = max(1, int(round(fs * effective_config.feature_update_seconds)))
        buffer = RingBuffer(effective_config.buffer_seconds, fs)
        try:
            for start in range(0, batch.timestamps_s.size, chunk_size):
                processing_started = time.perf_counter()
                end = min(start + chunk_size, batch.timestamps_s.size)
                chunk_times = batch.timestamps_s[start:end]
                chunk_signals = {
                    name: values[start:end]
                    for name, values in batch.signals.items()
                    if values.size >= end
                }
                buffer.append(chunk_times, chunk_signals)
                snapshot = buffer.snapshot()
                processed = {name: values.copy() for name, values in snapshot.signals.items()}
                if "ecg_ii" in processed:
                    ecg_high_hz = min(effective_config.filters.ecg_high_hz, fs * 0.45)
                    processed["ecg_ii"] = preprocess_ecg(
                        processed["ecg_ii"],
                        fs,
                        low_hz=effective_config.filters.ecg_low_hz,
                        high_hz=ecg_high_hz,
                        order=effective_config.filters.order,
                        mains_hz=effective_config.filters.mains_hz,
                    )
                if "ppg" in processed:
                    ppg_high_hz = min(effective_config.filters.ppg_high_hz, fs * 0.45)
                    processed["ppg"] = preprocess_ppg(
                        processed["ppg"],
                        fs,
                        low_hz=effective_config.filters.ppg_low_hz,
                        high_hz=ppg_high_hz,
                        order=effective_config.filters.order,
                    )
                feature_signals = {name: values.copy() for name, values in processed.items()}
                if "ppg" in snapshot.signals:
                    # Preserve absolute PPG amplitude for within-patient change features.
                    feature_signals["ppg"] = snapshot.signals["ppg"].copy()
                sample_rates = {name: fs for name in processed}
                baseline_cutoff = snapshot.timestamps_s[0] + baseline_duration
                baseline_mask = snapshot.timestamps_s < baseline_cutoff
                baseline_quality = evaluate_quality(
                    {name: values[baseline_mask] for name, values in processed.items()},
                    sample_rates,
                    effective_config.quality,
                    out_of_order_count=snapshot.out_of_order_count,
                    timestamp_synchronized=(
                        batch.timestamp_synchronized and snapshot.out_of_order_count == 0
                    ),
                )
                baseline = calibrate_baseline(
                    snapshot.timestamps_s,
                    feature_signals,
                    fs,
                    baseline_quality,
                    baseline_seconds=baseline_duration,
                    minimum_fraction=effective_config.baseline_minimum_fraction,
                )
                feature_set = extract_features(
                    snapshot.timestamps_s,
                    feature_signals,
                    baseline,
                    fs,
                    window_seconds=min(
                        60,
                        max(1, int(snapshot.timestamps_s[-1] - snapshot.timestamps_s[0] + 1)),
                    ),
                )
                quality_cutoff = snapshot.timestamps_s[-1] - min(60.0, baseline_duration)
                quality_mask = snapshot.timestamps_s >= quality_cutoff
                quality = evaluate_quality(
                    {name: values[quality_mask] for name, values in processed.items()},
                    sample_rates,
                    effective_config.quality,
                    out_of_order_count=snapshot.out_of_order_count,
                    timestamp_synchronized=(
                        batch.timestamp_synchronized and snapshot.out_of_order_count == 0
                    ),
                    valid_beat_count=feature_set.valid_beat_count,
                )
                if snapshot.gap_fraction > effective_config.quality.maximum_gap_fraction:
                    quality = replace(
                        quality,
                        usable=False,
                        gap_fraction=max(quality.gap_fraction, snapshot.gap_fraction),
                        reasons=tuple(
                            dict.fromkeys(
                                [
                                    *quality.reasons,
                                    "Network or source timestamps contain excessive gaps.",
                                ]
                            )
                        ),
                    )
                risk = compute_research_instability_index(
                    feature_set,
                    quality,
                    baseline,
                    mode,
                    effective_config,
                    data_source=batch.source.dataset,
                    age_group=batch.source.age_group,
                )
                processing_latency_ms = (time.perf_counter() - processing_started) * 1000.0
                timestamp_ms = int(round(float(chunk_times[-1]) * 1000.0))
                values = feature_set.values
                yield {
                    "timestamp_ms": timestamp_ms,
                    "mode": mode.value,
                    "source": {
                        "dataset": batch.source.dataset,
                        "case_id": batch.source.case_id,
                        "is_synthetic": batch.source.is_synthetic,
                        "attribution": batch.source.attribution,
                        "data_type": batch.source.data_type,
                    },
                    "patient_context": {
                        "ds_status": batch.source.ds_status,
                        "age_group": batch.source.age_group,
                    },
                    "signals": {
                        "ecg_ii": _waveform_values(chunk_signals.get("ecg_ii")),
                        "ppg": _waveform_values(chunk_signals.get("ppg")),
                        "abp": _waveform_values(chunk_signals.get("abp")),
                        "hr_bpm": _last_value(chunk_signals.get("hr_bpm")),
                        "sbp_mm_hg": _last_value(chunk_signals.get("sbp_mm_hg")),
                        "dbp_mm_hg": _last_value(chunk_signals.get("dbp_mm_hg")),
                        "map_mm_hg": _last_value(chunk_signals.get("map_mm_hg")),
                        "spo2_pct": _last_value(chunk_signals.get("spo2_pct")),
                        "etco2_mm_hg": _last_value(chunk_signals.get("etco2_mm_hg")),
                    },
                    "quality": {
                        "ecg_sqi": quality.ecg_sqi,
                        "ppg_sqi": quality.ppg_sqi,
                        "abp_sqi": quality.abp_sqi,
                        "usable": quality.usable,
                        "unavailable_signals": list(quality.unavailable_signals),
                        "reasons": list(quality.reasons),
                        "gap_fraction": quality.gap_fraction,
                        "timestamp_synchronized": quality.timestamp_synchronized,
                    },
                    "baseline": {
                        "calibrated": baseline.calibrated,
                        "progress": baseline.progress,
                        "confidence": baseline.confidence,
                        "reasons": list(baseline.reasons),
                    },
                    "features": {
                        "delta_hr_pct": values.get("delta_hr_pct"),
                        "hr_slope_bpm_min": values.get("hr_slope_bpm_min"),
                        "rmssd_ms": values.get("rmssd_ms"),
                        "sdnn_ms": values.get("sdnn_ms"),
                        "ppg_amp_delta_pct": values.get("ppg_amp_delta_pct"),
                        "map_slope_mm_hg_min": values.get("map_slope_mm_hg_min"),
                        "ptt_ms": values.get("ptt_ms"),
                    },
                    "risk": {
                        "name": "Research Instability Index",
                        "score": risk.score,
                        "level": risk.level.value,
                        "valid": risk.valid,
                        "horizon_seconds": risk.horizon_seconds,
                        "confidence": risk.confidence,
                        "reasons": list(risk.reasons),
                        "model_version": risk.model_version,
                        "population_validated_on": risk.population_validated_on,
                        "limitations": list(risk.limitations),
                    },
                    "transport": {
                        "source_latency_ms": batch.latency_ms,
                        "processing_latency_ms": processing_latency_ms,
                        "data_gap": snapshot.gap_fraction > 0.0,
                        "out_of_order_count": snapshot.out_of_order_count,
                        "synchronization_error_ms": batch.synchronization_error_ms,
                    },
                    "provenance": {
                        "raw": batch.provenance,
                        "processed": {
                            "ecg_ii": effective_config.config_version,
                            "ppg": effective_config.config_version,
                        },
                    },
                    "disclaimer": DISCLAIMER,
                }
                if real_time and end < batch.timestamps_s.size:
                    await asyncio.sleep(effective_config.feature_update_seconds / speed)
        finally:
            buffer.clear()
