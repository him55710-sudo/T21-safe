"""End-to-end deterministic replay pipeline producing API-ready events."""

from __future__ import annotations

import asyncio
import os
import time
from collections.abc import AsyncIterator
from dataclasses import replace

import numpy as np

from t21_engine.baseline.calibration import calibrate_baseline
from t21_engine.config import PipelineConfig
from t21_engine.features import extract_feature_windows
from t21_engine.preprocessing.filters import preprocess_abp, preprocess_ecg, preprocess_ppg
from t21_engine.quality.quality_gate import evaluate_quality
from t21_engine.risk.deterministic_index import compute_research_instability_index
from t21_engine.streaming.export_manifest import build_export_manifest
from t21_engine.streaming.local_capture_writer import LocalCaptureJsonlWriter
from t21_engine.streaming.ring_buffer import RingBuffer
from t21_engine.streaming.shadow_capture import build_shadow_capture
from t21_engine.types import BaselineState, PipelineMode, QualityResult, SignalBatch

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


def _apply_timestamp_gap_gate(
    quality: QualityResult,
    gap_fraction: float,
    maximum_gap_fraction: float,
) -> QualityResult:
    if gap_fraction <= maximum_gap_fraction:
        return quality
    return replace(
        quality,
        usable=False,
        gap_fraction=max(quality.gap_fraction, gap_fraction),
        reasons=tuple(
            dict.fromkeys(
                [
                    *quality.reasons,
                    "Network or source timestamps contain excessive gaps.",
                ]
            )
        ),
    )


def _timestamps_synchronized(
    batch: SignalBatch,
    out_of_order_count: int,
    tolerance_ms: float,
) -> bool:
    return (
        batch.timestamp_synchronized
        and batch.synchronization_error_ms <= tolerance_ms
        and out_of_order_count == 0
    )


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
        shadow_session_id: str | None = None,
        local_capture_dir: str | os.PathLike[str] | None = None,
        write_export_manifest: bool = False,
    ) -> AsyncIterator[dict[str, object]]:
        if speed <= 0.0:
            raise ValueError("speed must be positive")
        if local_capture_dir is not None and shadow_session_id is None:
            raise ValueError("local capture requires shadow_session_id")
        if write_export_manifest and local_capture_dir is None:
            raise ValueError("export manifest requires local_capture_dir")
        if shadow_session_id is not None and not batch.source.is_synthetic:
            raise ValueError("shadow capture is limited to synthetic/local replay")
        if batch.timestamps_s.size == 0:
            raise ValueError("signal batch must contain at least one sample")
        if not batch.signals:
            raise ValueError("signal batch must contain at least one signal")
        local_capture_writer = (
            LocalCaptureJsonlWriter(local_capture_dir) if local_capture_dir is not None else None
        )
        captured_event_ids: list[str] = []
        baseline_duration = baseline_seconds or self.config.baseline_seconds
        effective_config = replace(self.config, baseline_seconds=baseline_duration)
        fs = batch.sample_rates_hz.get(
            "ecg_ii",
            next(iter(batch.sample_rates_hz.values()), effective_config.waveform_sample_rate_hz),
        )
        chunk_size = max(1, int(round(fs * effective_config.feature_update_seconds)))
        buffer_seconds = max(
            effective_config.buffer_seconds,
            baseline_duration,
            max(effective_config.feature_windows_seconds, default=0),
        )
        buffer = RingBuffer(buffer_seconds, fs)
        baseline: BaselineState | None = None
        baseline_locked = False
        baseline_start_s: float | None = None
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
                if "abp" in processed:
                    abp_high_hz = min(effective_config.filters.abp_high_hz, fs * 0.45)
                    processed["abp"] = preprocess_abp(
                        processed["abp"],
                        fs,
                        low_hz=effective_config.filters.abp_low_hz,
                        high_hz=abp_high_hz,
                        order=effective_config.filters.order,
                    )
                feature_signals = {name: values.copy() for name, values in processed.items()}
                sample_rates = {name: fs for name in processed}
                timestamps_synchronized = _timestamps_synchronized(
                    batch,
                    snapshot.out_of_order_count,
                    effective_config.quality.synchronization_tolerance_ms,
                )
                if baseline is None or not baseline_locked:
                    if baseline_start_s is None:
                        baseline_start_s = float(snapshot.timestamps_s[0])
                    baseline_cutoff = baseline_start_s + baseline_duration
                    baseline_mask = (snapshot.timestamps_s >= baseline_start_s) & (
                        snapshot.timestamps_s < baseline_cutoff
                    )
                    baseline_quality = evaluate_quality(
                        {name: values[baseline_mask] for name, values in processed.items()},
                        sample_rates,
                        effective_config.quality,
                        out_of_order_count=snapshot.out_of_order_count,
                        timestamp_synchronized=timestamps_synchronized,
                    )
                    baseline_quality = _apply_timestamp_gap_gate(
                        baseline_quality,
                        snapshot.gap_fraction,
                        effective_config.quality.maximum_gap_fraction,
                    )
                    baseline = calibrate_baseline(
                        snapshot.timestamps_s,
                        feature_signals,
                        fs,
                        baseline_quality,
                        baseline_seconds=baseline_duration,
                        minimum_fraction=effective_config.baseline_minimum_fraction,
                        raw_signals=snapshot.signals,
                    )
                    baseline_locked = float(snapshot.timestamps_s[-1]) >= baseline_cutoff
                feature_windows = extract_feature_windows(
                    snapshot.timestamps_s,
                    feature_signals,
                    baseline,
                    fs,
                    windows_seconds=effective_config.feature_windows_seconds,
                    raw_signals=snapshot.signals,
                    hypotension_threshold_mm_hg=(effective_config.risk.hypotension_map_mm_hg),
                )
                primary_window = min(feature_windows, key=lambda window: abs(window - 60))
                feature_set = feature_windows[primary_window]
                quality_cutoff = snapshot.timestamps_s[-1] - min(60.0, baseline_duration)
                quality_mask = snapshot.timestamps_s >= quality_cutoff
                quality = evaluate_quality(
                    {name: values[quality_mask] for name, values in snapshot.signals.items()},
                    sample_rates,
                    effective_config.quality,
                    out_of_order_count=snapshot.out_of_order_count,
                    timestamp_synchronized=timestamps_synchronized,
                    valid_beat_count=feature_set.valid_beat_count,
                )
                quality = _apply_timestamp_gap_gate(
                    quality,
                    snapshot.gap_fraction,
                    effective_config.quality.maximum_gap_fraction,
                )
                if batch.gap_detected:
                    quality = replace(
                        quality,
                        usable=False,
                        reasons=tuple(
                            dict.fromkeys([*quality.reasons, "The source reported a data dropout."])
                        ),
                    )
                if batch.latency_ms > effective_config.quality.maximum_source_latency_ms:
                    quality = replace(
                        quality,
                        usable=False,
                        reasons=tuple(
                            dict.fromkeys(
                                [*quality.reasons, "The source packet is too delayed for scoring."]
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
                event: dict[str, object] = {
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
                        "values": {
                            "hr": baseline.median_hr,
                            "map": baseline.median_map,
                            "ppg_amplitude": baseline.median_ppg_amplitude,
                            "rmssd_ms": baseline.rmssd_ms,
                            "sdnn_ms": baseline.sdnn_ms,
                        },
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
                        "observation_context_seconds": risk.observation_context_seconds,
                        "confidence": risk.confidence,
                        "reasons": list(risk.reasons),
                        "model_version": risk.model_version,
                        "data_source": risk.data_source,
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
                            name: effective_config.config_version
                            for name in ("ecg_ii", "ppg", "abp")
                            if name in processed
                        },
                    },
                    "disclaimer": DISCLAIMER,
                }
                if shadow_session_id is not None:
                    event_id = f"{shadow_session_id}-{timestamp_ms}"
                    shadow_capture = build_shadow_capture(
                        session_id=shadow_session_id,
                        event_id=event_id,
                        subject_id=batch.source.case_id,
                        is_synthetic=batch.source.is_synthetic,
                        baseline_calibrated=baseline.calibrated,
                        quality_config=effective_config.quality,
                        feature_windows=feature_windows,
                        signals=snapshot.signals,
                        sample_rates_hz=sample_rates,
                        out_of_order_count=snapshot.out_of_order_count,
                        timestamp_synchronized=timestamps_synchronized,
                    )
                    event["shadow_capture"] = shadow_capture
                    if local_capture_writer is not None:
                        local_capture_writer.append_capture(shadow_capture)
                        captured_event_ids.append(event_id)
                yield event
                if real_time and end < batch.timestamps_s.size:
                    await asyncio.sleep(effective_config.feature_update_seconds / speed)
            if write_export_manifest:
                assert local_capture_writer is not None
                assert shadow_session_id is not None
                local_capture_writer.append_manifest(
                    build_export_manifest(
                        export_id=f"{shadow_session_id}-export",
                        session_id=shadow_session_id,
                        event_ids=tuple(captured_event_ids),
                    )
                )
        finally:
            buffer.clear()
