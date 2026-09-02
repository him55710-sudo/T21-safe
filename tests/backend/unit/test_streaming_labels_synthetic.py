from __future__ import annotations

import numpy as np
import pytest
from t21_engine.adapters.synthetic_adapter import SCENARIOS, SyntheticAdapter
from t21_engine.evaluation.labels import hypotension_candidate
from t21_engine.evaluation.metrics import binary_metrics, bootstrap_confidence_interval
from t21_engine.streaming.ring_buffer import RingBuffer
from t21_engine.types import SignalBatch, SourceMetadata


def test_ring_buffer_sorts_out_of_order_and_enforces_capacity() -> None:
    buffer = RingBuffer(capacity_seconds=2.0, sample_rate_hz=2.0)
    buffer.append(
        np.asarray([0.0, 1.0, 0.5], dtype=np.float64),
        {"ecg_ii": np.asarray([0.0, 2.0, 1.0], dtype=np.float64)},
    )
    buffer.append(
        np.asarray([1.5, 2.0], dtype=np.float64),
        {"ecg_ii": np.asarray([3.0, 4.0], dtype=np.float64)},
    )
    snapshot = buffer.snapshot()

    assert np.all(np.diff(snapshot.timestamps_s) > 0.0)
    assert len(buffer) == 4
    assert snapshot.out_of_order_count >= 1


def test_generic_hypotension_candidate_requires_sustained_duration() -> None:
    timestamps = np.arange(0.0, 120.0, 1.0, dtype=np.float64)
    map_values = np.full_like(timestamps, 80.0)
    map_values[10:80] = 60.0

    labels = hypotension_candidate(timestamps, map_values)

    assert labels[10:80].all()
    assert not labels[:10].any()
    assert not labels[80:].any()


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", SCENARIOS)
async def test_all_synthetic_scenarios_are_labeled_and_deterministic(
    scenario: str,
) -> None:
    adapter = SyntheticAdapter(seed=7)
    first = await adapter.load_case(f"synthetic:{scenario}", duration_seconds=10)
    second = await adapter.load_case(f"synthetic:{scenario}", duration_seconds=10)

    assert first.source.is_synthetic
    assert first.source.ds_status == "synthetic_not_applicable"
    assert np.allclose(
        first.signals["ecg_ii"], second.signals["ecg_ii"], equal_nan=True
    )


def test_evaluation_metrics_and_bootstrap_are_reproducible() -> None:
    labels = np.asarray([0, 0, 1, 1], dtype=np.int64)
    scores = np.asarray([5.0, 20.0, 80.0, 95.0], dtype=np.float64)

    metrics = binary_metrics(labels, scores, threshold=50.0, observed_hours=2.0)
    interval = bootstrap_confidence_interval(labels, scores, iterations=100, seed=7)

    assert metrics["auroc"] == pytest.approx(1.0)
    assert metrics["sensitivity"] == pytest.approx(1.0)
    assert metrics["specificity"] == pytest.approx(1.0)
    assert interval is not None
    assert 0.0 <= interval[0] <= interval[1] <= 1.0


def test_signal_batch_rejects_misaligned_signal_lengths() -> None:
    with pytest.raises(ValueError, match="align"):
        SignalBatch(
            timestamps_s=np.asarray([0.0, 1.0], dtype=np.float64),
            signals={"ecg_ii": np.asarray([0.0], dtype=np.float64)},
            sample_rates_hz={"ecg_ii": 1.0},
            source=SourceMetadata("test", "case", True),
        )


def test_signal_batch_rejects_invalid_transport_measurements() -> None:
    with pytest.raises(ValueError, match="latency_ms"):
        SignalBatch(
            timestamps_s=np.asarray([0.0], dtype=np.float64),
            signals={"ecg_ii": np.asarray([0.0], dtype=np.float64)},
            sample_rates_hz={"ecg_ii": 1.0},
            source=SourceMetadata("test", "case", True),
            latency_ms=-1.0,
        )
    with pytest.raises(ValueError, match="synchronization_error_ms"):
        SignalBatch(
            timestamps_s=np.asarray([0.0], dtype=np.float64),
            signals={"ecg_ii": np.asarray([0.0], dtype=np.float64)},
            sample_rates_hz={"ecg_ii": 1.0},
            source=SourceMetadata("test", "case", True),
            synchronization_error_ms=float("nan"),
        )
