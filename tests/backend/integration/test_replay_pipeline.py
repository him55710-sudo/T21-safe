from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from t21_engine.adapters.synthetic_adapter import SyntheticAdapter
from t21_engine.config import PipelineConfig
from t21_engine.streaming.export_manifest import build_export_manifest
from t21_engine.streaming.local_capture_writer import LocalCaptureJsonlWriter
from t21_engine.streaming.replay import ReplayPipeline
from t21_engine.types import SignalBatch, SourceMetadata


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
async def test_synthetic_replay_can_emit_local_observe_only_shadow_capture() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    final = None
    async for event in ReplayPipeline().events(
        batch,
        baseline_seconds=3,
        speed=1000.0,
        real_time=False,
        shadow_session_id="shadow-synthetic-001",
    ):
        final = event

    assert final is not None
    capture = final["shadow_capture"]
    assert capture["session"]["storage_scope"] == "LOCAL_ONLY"
    assert capture["session"]["contains_phi"] is False
    assert capture["waveform_persistence"] == "NONE"
    assert capture["controls"] == {
        "actuation": False,
        "dosing": False,
        "closed_loop": False,
        "drug_advice": False,
        "emr_write": False,
    }
    assert capture["quality_gate"]["baseline_bypass"] is False
    assert capture["feature_windows"]
    assert all(
        window["evidence_status"] == "RESEARCH_HYPOTHESIS"
        and window["clinical_decision_thresholds"] == "PI_TO_DEFINE"
        for window in capture["feature_windows"]
    )
    assert not any(
        name in capture for name in ("signals", "waveforms", "raw_waveforms")
    )

    manifest = build_export_manifest(
        export_id="synthetic-export-001",
        session_id=capture["session"]["session_id"],
        event_ids=(capture["event_id"],),
    )
    assert manifest["storage_scope"] == "LOCAL_ONLY"
    assert manifest["mode"] == "OBSERVE_ONLY_SHADOW"
    assert manifest["includes_waveforms"] is False
    assert manifest["includes_phi"] is False
    assert manifest["controls"] == capture["controls"]


@pytest.mark.asyncio
async def test_synthetic_shadow_capture_writes_and_reads_back_from_local_jsonl(
    tmp_path: Path,
) -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    final = None
    async for event in ReplayPipeline().events(
        batch,
        baseline_seconds=3,
        speed=1000.0,
        real_time=False,
        shadow_session_id="shadow-synthetic-jsonl-001",
        local_capture_dir=tmp_path,
        write_export_manifest=True,
    ):
        final = event

    assert final is not None
    capture = final["shadow_capture"]
    writer = LocalCaptureJsonlWriter(tmp_path)

    lines = [
        json.loads(line)
        for line in writer.path.read_text(encoding="utf-8").splitlines()
    ]
    captures = lines[:-1]
    manifest = lines[-1]
    assert captures
    assert captures[-1] == capture
    assert all(item["mode"] == "OBSERVE_ONLY_SHADOW" for item in captures)
    assert all(item["session"]["contains_phi"] is False for item in captures)
    assert all(item["waveform_persistence"] == "NONE" for item in captures)
    assert all(
        not any(key in item for key in ("signals", "waveforms")) for item in captures
    )
    assert all(
        all(value is False for value in item["controls"].values()) for item in captures
    )
    assert manifest["event_ids"] == [item["event_id"] for item in captures]
    assert manifest["storage_scope"] == "LOCAL_ONLY"
    assert manifest["includes_waveforms"] is False
    assert manifest["includes_phi"] is False
    assert all(value is False for value in manifest["controls"].values())


@pytest.mark.asyncio
async def test_replay_local_capture_rejects_cloud_uri() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )

    with pytest.raises(ValueError, match="must not use a URI scheme"):
        await anext(
            ReplayPipeline().events(
                batch,
                baseline_seconds=3,
                speed=1000.0,
                real_time=False,
                shadow_session_id="shadow-synthetic-cloud-001",
                local_capture_dir="s3://research-captures",
            )
        )


@pytest.mark.asyncio
async def test_shadow_capture_rejects_non_synthetic_replay() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    batch.source = SourceMetadata(
        dataset="Public research data",
        case_id="public-case-001",
        is_synthetic=False,
    )

    with pytest.raises(ValueError, match="limited to synthetic/local replay"):
        await anext(
            ReplayPipeline().events(
                batch,
                baseline_seconds=3,
                speed=1000.0,
                real_time=False,
                shadow_session_id="shadow-public-001",
            )
        )


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
async def test_synchronization_error_above_configured_tolerance_withholds_risk() -> (
    None
):
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    batch.timestamp_synchronized = True
    batch.synchronization_error_ms = 101.0

    final = await _final_event(batch, baseline_seconds=3)

    assert final["quality"]["timestamp_synchronized"] is False
    assert final["transport"]["synchronization_error_ms"] == 101.0
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


@pytest.mark.asyncio
async def test_completed_baseline_does_not_slide_with_short_ring_buffer() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    changed = batch.timestamps_s >= 4.0
    batch.signals["hr_bpm"][changed] = 48.0
    batch.signals["map_mm_hg"][changed] = 54.0
    pipeline = ReplayPipeline(PipelineConfig(baseline_seconds=3, buffer_seconds=4))

    final = None
    async for event in pipeline.events(
        batch,
        baseline_seconds=3,
        speed=1000.0,
        real_time=False,
    ):
        final = event

    assert final is not None
    assert final["baseline"]["calibrated"] is True
    assert final["features"]["delta_hr_pct"] == pytest.approx(-100.0 / 3.0, abs=1.0)
    assert final["risk"]["valid"] is True
    assert final["risk"]["score"] is not None
    assert final["risk"]["score"] >= 50.0


@pytest.mark.asyncio
async def test_failed_initial_baseline_does_not_retry_on_later_samples() -> None:
    batch = await SyntheticAdapter().load_case(
        "synthetic:stable-baseline", duration_seconds=8
    )
    keep = (batch.timestamps_s < 1.0) | (batch.timestamps_s >= 3.0)
    batch.timestamps_s = batch.timestamps_s[keep]
    batch.signals = {name: values[keep] for name, values in batch.signals.items()}
    pipeline = ReplayPipeline(PipelineConfig(baseline_seconds=3, buffer_seconds=3))

    final = None
    async for event in pipeline.events(
        batch,
        baseline_seconds=3,
        speed=1000.0,
        real_time=False,
    ):
        final = event

    assert final is not None
    assert final["baseline"]["calibrated"] is False
    assert any("coverage" in reason for reason in final["baseline"]["reasons"])
    assert final["risk"]["valid"] is False
    assert final["risk"]["score"] is None


@pytest.mark.asyncio
async def test_empty_signal_batch_fails_closed() -> None:
    """CODEX-074: ReplayPipeline rejects empty timestamps fail-closed."""
    batch = SignalBatch(
        timestamps_s=np.asarray([], dtype=np.float64),
        signals={"ecg_ii": np.asarray([], dtype=np.float64)},
        sample_rates_hz={"ecg_ii": 100.0},
        source=SourceMetadata(
            dataset="Synthetic",
            case_id="empty-batch",
            is_synthetic=True,
        ),
    )
    with pytest.raises(ValueError, match="at least one sample"):
        await anext(
            ReplayPipeline().events(
                batch,
                baseline_seconds=3,
                speed=1000.0,
                real_time=False,
            )
        )


@pytest.mark.asyncio
async def test_signal_batch_without_signals_fails_closed() -> None:
    """CODEX-074: ReplayPipeline rejects batches with no signal channels."""
    batch = SignalBatch(
        timestamps_s=np.asarray([0.0, 0.01], dtype=np.float64),
        signals={},
        sample_rates_hz={},
        source=SourceMetadata(
            dataset="Synthetic",
            case_id="no-signals",
            is_synthetic=True,
        ),
    )
    with pytest.raises(ValueError, match="at least one signal"):
        await anext(
            ReplayPipeline().events(
                batch,
                baseline_seconds=3,
                speed=1000.0,
                real_time=False,
            )
        )
