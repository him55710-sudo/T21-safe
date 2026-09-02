from __future__ import annotations

import numpy as np
import pytest
from t21_engine.adapters.synthetic_adapter import SyntheticAdapter
from t21_engine.beats.rpeak import detect_r_peaks
from t21_engine.streaming.replay import ReplayPipeline


async def _batch(scenario: str = "stable-baseline"):
    return await SyntheticAdapter().load_case(f"synthetic:{scenario}", duration_seconds=20)


async def _final(batch):  # type: ignore[no-untyped-def]
    final = None
    async for event in ReplayPipeline().events(
        batch,
        baseline_seconds=3,
        speed=1000.0,
        real_time=False,
    ):
        final = event
    assert final is not None
    return final


def _assert_withheld_or_reduced(event: dict[str, object], reference: dict[str, object]) -> None:
    risk = event["risk"]
    reference_risk = reference["risk"]
    assert isinstance(risk, dict)
    assert isinstance(reference_risk, dict)
    assert risk["valid"] is False or float(risk["confidence"]) < float(
        reference_risk["confidence"]
    )


@pytest.mark.asyncio
async def test_ecg_normal_rhythm_and_sudden_hr_decline() -> None:
    stable = await _final(await _batch())
    decline = await _final(await _batch("progressive-hr-decline"))

    assert stable["quality"]["ecg_sqi"] >= 0.55  # type: ignore[index]
    assert stable["risk"]["valid"] is True  # type: ignore[index]
    assert decline["features"]["delta_hr_pct"] < 0  # type: ignore[index]
    assert decline["risk"]["score"] > stable["risk"]["score"]  # type: ignore[index]


@pytest.mark.asyncio
async def test_ecg_noise_flatline_and_missing_data_are_fail_safe() -> None:
    reference = await _final(await _batch())
    for corruption in ("noise", "flatline", "missing"):
        batch = await _batch()
        recent = batch.timestamps_s >= 5.0
        if corruption == "noise":
            batch.signals["ecg_ii"][recent] = np.random.default_rng(7).normal(
                0.0, 4.0, int(recent.sum())
            )
        elif corruption == "flatline":
            batch.signals["ecg_ii"][recent] = 0.0
        else:
            batch.signals.pop("ecg_ii")
            batch.sample_rates_hz.pop("ecg_ii")
        event = await _final(batch)
        _assert_withheld_or_reduced(event, reference)


@pytest.mark.asyncio
async def test_ectopic_beat_candidate_does_not_create_an_unbounded_output() -> None:
    batch = await _batch()
    fs = batch.sample_rates_hz["ecg_ii"]
    candidate_index = int(6.35 * fs)
    batch.signals["ecg_ii"][candidate_index : candidate_index + 2] += 2.5
    beats = detect_r_peaks(batch.signals["ecg_ii"], fs)
    event = await _final(batch)

    assert beats.indices.size > 0
    assert event["risk"]["score"] is None or 0 <= event["risk"]["score"] <= 100  # type: ignore[index,operator]


@pytest.mark.asyncio
async def test_ppg_stable_and_amplitude_decline() -> None:
    stable = await _final(await _batch())
    decline_batch = await _batch()
    decline_batch.signals["ppg"][decline_batch.timestamps_s >= 4.0] *= 0.3
    decline = await _final(decline_batch)

    assert stable["quality"]["ppg_sqi"] >= 0.55  # type: ignore[index]
    assert decline["features"]["ppg_amp_delta_pct"] < 0  # type: ignore[index]
    assert decline["risk"]["score"] >= stable["risk"]["score"]  # type: ignore[index]


@pytest.mark.asyncio
@pytest.mark.parametrize("corruption", ["clipping", "motion", "loss"])
async def test_ppg_artifacts_are_withheld_or_reduce_confidence(corruption: str) -> None:
    reference = await _final(await _batch())
    batch = await _batch()
    recent = batch.timestamps_s >= 5.0
    if corruption == "clipping":
        batch.signals["ppg"][recent] = np.where(
            batch.signals["ppg"][recent] > 0.15, 0.2, 0.0
        )
    elif corruption == "motion":
        batch.signals["ppg"][recent] += np.random.default_rng(11).normal(
            0.0, 2.0, int(recent.sum())
        )
    else:
        batch.signals["ppg"][recent] = np.nan
    event = await _final(batch)
    _assert_withheld_or_reduced(event, reference)


@pytest.mark.asyncio
async def test_abp_stable_and_map_decline() -> None:
    stable = await _final(await _batch())
    decline = await _final(await _batch("progressive-map-decline"))

    assert stable["quality"]["abp_sqi"] >= 0.55  # type: ignore[index]
    assert decline["features"]["map_slope_mm_hg_min"] < 0  # type: ignore[index]
    assert decline["risk"]["score"] > stable["risk"]["score"]  # type: ignore[index]


@pytest.mark.asyncio
@pytest.mark.parametrize("corruption", ["flush", "flatline"])
async def test_abp_artifacts_are_withheld_or_reduce_confidence(corruption: str) -> None:
    reference = await _final(await _batch())
    batch = await _batch()
    recent = batch.timestamps_s >= 5.0
    batch.signals["abp"][recent] = 330.0 if corruption == "flush" else 80.0
    event = await _final(batch)
    _assert_withheld_or_reduced(event, reference)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("condition", "reason_fragment"),
    [
        ("desynchronization", "Timestamp synchronization failed"),
        ("dropout", "source reported a data dropout"),
        ("delayed", "source packet is too delayed"),
        ("out_of_order", "Timestamp synchronization failed"),
    ],
)
async def test_multimodal_transport_failures_withhold_output(
    condition: str, reason_fragment: str
) -> None:
    batch = await _batch()
    if condition == "desynchronization":
        batch.synchronization_error_ms = 250.0
    elif condition == "dropout":
        batch.gap_detected = True
    elif condition == "delayed":
        batch.latency_ms = 1500.0
    else:
        batch.timestamps_s[650], batch.timestamps_s[651] = (
            batch.timestamps_s[651],
            batch.timestamps_s[650],
        )

    event = await _final(batch)
    assert event["risk"]["valid"] is False  # type: ignore[index]
    assert event["risk"]["level"] == "INVALID"  # type: ignore[index]
    assert event["risk"]["score"] is None  # type: ignore[index]
    assert any(
        reason_fragment.lower() in reason.lower()
        for reason in event["risk"]["reasons"]  # type: ignore[index,union-attr]
    )
