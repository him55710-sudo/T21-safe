from __future__ import annotations

import numpy as np
import pytest
from t21_engine.adapters.synthetic_adapter import SyntheticAdapter
from t21_engine.streaming.replay import ReplayPipeline


async def _final_event(batch, *, baseline_seconds: int):  # type: ignore[no-untyped-def]
    final = None
    async for event in ReplayPipeline().events(
        batch,
        baseline_seconds=baseline_seconds,
        speed=1000.0,
        real_time=False,
    ):
        final = event
    assert final is not None
    return final


@pytest.mark.asyncio
async def test_synthetic_replay_reaches_valid_sse_payload() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    final = await _final_event(batch, baseline_seconds=3)

    assert final["baseline"]["calibrated"] is True
    assert final["quality"]["usable"] is True
    assert final["risk"]["valid"] is True
    assert final["risk"]["name"] == "Research Instability Index"


@pytest.mark.asyncio
async def test_missing_ppg_degrades_but_does_not_crash() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    batch.signals.pop("ppg")
    batch.sample_rates_hz.pop("ppg")
    final = await _final_event(batch, baseline_seconds=3)

    assert "ppg" in final["quality"]["unavailable_signals"]
    assert final["quality"]["usable"] is True
    assert final["risk"]["valid"] is True


@pytest.mark.asyncio
async def test_low_sqi_withholds_risk() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    batch.signals["ecg_ii"][:] = 0.0
    batch.signals["ppg"][:] = np.nan
    final = await _final_event(batch, baseline_seconds=3)

    assert final["quality"]["usable"] is False
    assert final["risk"]["valid"] is False
    assert final["risk"]["score"] is None
    assert final["risk"]["level"] == "INVALID"


@pytest.mark.asyncio
async def test_incomplete_baseline_withholds_risk() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=2
    )
    final = await _final_event(batch, baseline_seconds=5)

    assert final["baseline"]["calibrated"] is False
    assert final["risk"]["valid"] is False
    assert final["risk"]["score"] is None


@pytest.mark.asyncio
async def test_timestamp_synchronization_failure_withholds_risk() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    batch.timestamp_synchronized = False
    batch.synchronization_error_ms = 250.0
    final = await _final_event(batch, baseline_seconds=3)

    assert final["quality"]["timestamp_synchronized"] is False
    assert final["risk"]["valid"] is False
    assert final["risk"]["score"] is None
    assert any("Timestamp" in reason for reason in final["risk"]["reasons"])


@pytest.mark.asyncio
async def test_excessive_timestamp_gap_withholds_risk() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    keep = (batch.timestamps_s < 4.0) | (batch.timestamps_s >= 6.0)
    batch.timestamps_s = batch.timestamps_s[keep]
    batch.signals = {name: values[keep] for name, values in batch.signals.items()}

    final = await _final_event(batch, baseline_seconds=3)

    assert final["transport"]["data_gap"] is True
    assert final["quality"]["gap_fraction"] > 0.15
    assert final["risk"]["valid"] is False
    assert final["risk"]["score"] is None
    assert any("excessive gaps" in reason for reason in final["risk"]["reasons"])


@pytest.mark.asyncio
async def test_out_of_order_samples_are_normalized_and_withhold_risk() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    batch.timestamps_s[[350, 351]] = batch.timestamps_s[[351, 350]]

    final = await _final_event(batch, baseline_seconds=3)

    assert final["transport"]["out_of_order_count"] >= 1
    assert final["quality"]["timestamp_synchronized"] is False
    assert final["risk"]["valid"] is False
    assert final["risk"]["score"] is None
    assert any("Timestamp" in reason for reason in final["risk"]["reasons"])
