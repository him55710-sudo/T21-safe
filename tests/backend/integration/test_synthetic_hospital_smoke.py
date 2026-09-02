from __future__ import annotations

import pytest
from t21_engine.adapters.synthetic_hospital_case import SyntheticHospitalAdapter
from t21_engine.streaming.export_manifest import build_export_manifest
from t21_engine.streaming.replay import ReplayPipeline


@pytest.mark.asyncio
async def test_synthetic_hospital_case_replay_and_export_manifest_smoke() -> None:
    adapter = SyntheticHospitalAdapter(seed=19)
    batch = await adapter.load_case("synthetic:hospital-stable", duration_seconds=12.0)
    final = None
    async for event in ReplayPipeline().events(
        batch,
        baseline_seconds=3,
        speed=1000.0,
        real_time=False,
        shadow_session_id="synthetic-hospital-shadow-001",
    ):
        final = event

    assert final is not None
    capture = final["shadow_capture"]
    assert capture["session"]["is_synthetic"] is True
    assert capture["session"]["contains_phi"] is False
    assert capture["mode"] == "OBSERVE_ONLY_SHADOW"
    manifest = build_export_manifest(
        export_id="synthetic-hospital-export-001",
        session_id=capture["session"]["session_id"],
        event_ids=(capture["event_id"],),
    )
    assert manifest["is_synthetic"] is True
    assert manifest["includes_waveforms"] is False
    assert manifest["includes_phi"] is False
