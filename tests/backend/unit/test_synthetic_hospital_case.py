from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest
from t21_engine.adapters.synthetic_hospital_case import (
    REQUIRED_CHANNELS,
    SYNTHETIC_HOSPITAL_CASE_ID,
    SyntheticHospitalAdapter,
    build_synthetic_hospital_case,
)


def _codes(case) -> set[str]:  # type: ignore[no-untyped-def]
    return {reason.code for reason in case.quality_report().reasons}


def test_factory_is_deterministic_synthetic_and_time_aligned() -> None:
    first = build_synthetic_hospital_case(duration_s=20.0, seed=7)
    second = build_synthetic_hospital_case(duration_s=20.0, seed=7)

    assert first.case_id == SYNTHETIC_HOSPITAL_CASE_ID
    assert first.synthetic_label == "SYNTHETIC_DATA"
    assert first.contains_phi is False
    assert first.clinical_validation is False
    assert first.mode == "OBSERVE_ONLY_SHADOW"
    assert tuple(first.channels) == REQUIRED_CHANNELS
    assert [stage.name for stage in first.anesthesia_stages] == [
        "preop",
        "induction",
        "maintenance",
        "emergence",
        "PACU",
    ]
    assert first.quality_report().to_dict() == {
        "status": "PASS",
        "reasons": [],
        "checked_channels": sorted(REQUIRED_CHANNELS),
        "clinical_validation": False,
        "synthetic_only": True,
    }
    for name in REQUIRED_CHANNELS:
        assert np.array_equal(
            first.channels[name].timestamps_s, second.channels[name].timestamps_s
        )
        assert np.array_equal(first.channels[name].values, second.channels[name].values)


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("gap", "TIMESTAMP_GAP"),
        ("misalignment", "START_MISALIGNED"),
        ("out_of_order", "OUT_OF_ORDER"),
    ],
)
def test_alignment_smoke_fails_closed_with_machine_codes(
    mutation: str, expected_code: str
) -> None:
    case = build_synthetic_hospital_case(duration_s=20.0)
    channel = case.channels["ppg"]
    timestamps = channel.timestamps_s.copy()
    if mutation == "gap":
        timestamps = np.delete(timestamps, 50)
        values = np.delete(channel.values, 50)
    elif mutation == "misalignment":
        timestamps += 0.1
        values = channel.values
    else:
        timestamps[50:52] = timestamps[50:52][::-1]
        values = channel.values
    channels = dict(case.channels)
    channels["ppg"] = replace(channel, timestamps_s=timestamps, values=values)
    broken = replace(case, channels=channels)

    report = broken.quality_report()
    assert report.status == "FAIL"
    assert expected_code in _codes(broken)
    assert report.clinical_validation is False
    with pytest.raises(ValueError, match="failed closed"):
        broken.to_signal_batch()


def test_missing_channel_fails_closed() -> None:
    case = build_synthetic_hospital_case(duration_s=20.0)
    channels = dict(case.channels)
    del channels["resp"]
    assert "MISSING_CHANNEL" in _codes(replace(case, channels=channels))


@pytest.mark.asyncio
async def test_thin_adapter_produces_replay_compatible_batch() -> None:
    adapter = SyntheticHospitalAdapter(seed=11)
    descriptor = (await adapter.list_cases())[0]
    batch = await adapter.load_case(descriptor.case_id, duration_seconds=12.0)

    assert descriptor.is_synthetic is True
    assert descriptor.clinical_use_allowed is False
    assert batch.source.is_synthetic is True
    assert set(REQUIRED_CHANNELS).issubset(batch.signals)
    assert np.all(np.diff(batch.timestamps_s) > 0.0)
