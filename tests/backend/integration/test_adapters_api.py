from __future__ import annotations

import json
from pathlib import Path

import httpx
import numpy as np
import pytest
from fastapi.testclient import TestClient
from t21_api.main import app, create_app
from t21_api.schemas import AnalyzeWindowRequest, StreamEvent
from t21_api.settings import Settings
from t21_api.streaming.sessions import SessionManager
from t21_engine.adapters.local_fixture_adapter import LocalFixtureAdapter
from t21_engine.adapters.vitaldb_adapter import VitalDBAdapter
from t21_engine.adapters.wfdb_adapter import WFDBAdapter
from t21_engine.types import PipelineMode

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/local_waveform.csv"


@pytest.mark.asyncio
async def test_local_fixture_replay_adapter() -> None:
    batch = await LocalFixtureAdapter(FIXTURE).load_case("local:fixture")

    assert batch.timestamps_s.size == 40
    assert {"ecg_ii", "ppg", "abp", "map_mm_hg"} <= batch.signals.keys()
    assert batch.source.is_synthetic is True
    assert batch.source.ds_status == "synthetic_not_applicable"
    assert batch.source.clinical_use_allowed is False


@pytest.mark.asyncio
async def test_local_fixture_can_repeat_for_an_offline_baseline() -> None:
    batch = await LocalFixtureAdapter(FIXTURE).load_case(
        "local:fixture", duration_seconds=8
    )

    assert batch.timestamps_s.size == 80
    assert batch.timestamps_s[-1] == pytest.approx(7.9)
    assert np.array_equal(batch.signals["ecg_ii"][:40], batch.signals["ecg_ii"][40:])
    assert batch.source.is_synthetic is True
    assert all(
        "cyclic synthetic repetition" in value for value in batch.provenance.values()
    )


@pytest.mark.asyncio
async def test_vitaldb_network_failure_uses_explicit_local_fallback() -> None:
    async def fail(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="offline")

    client = httpx.AsyncClient(transport=httpx.MockTransport(fail))
    try:
        adapter = VitalDBAdapter(
            client=client,
            fallback=LocalFixtureAdapter(FIXTURE),
            timeout_seconds=0.1,
        )
        batch = await adapter.load_case("vitaldb:public-live", duration_seconds=3)
    finally:
        await client.aclose()

    assert batch.source.dataset == "Local synthetic fixture"
    assert batch.source.is_synthetic is True
    assert "fallback_reason" in batch.provenance
    assert batch.latency_ms > 0.0


@pytest.mark.asyncio
async def test_default_vitaldb_failure_fallback_covers_the_requested_baseline() -> None:
    manager = SessionManager(
        fixture_path=FIXTURE,
        vitaldb_base_url="http://127.0.0.1:9",
        vitaldb_timeout_seconds=0.05,
        offline_mode=False,
    )

    session = await manager.create(
        "vitaldb:public-live",
        speed=1000.0,
        baseline_seconds=180,
        mode=PipelineMode.GENERIC_VALIDATION_MODE,
    )

    assert session.batch.source.dataset == "Local synthetic fixture"
    assert session.batch.source.is_synthetic is True
    assert session.batch.timestamps_s.size == 1850
    assert "fallback_reason" in session.batch.provenance
    assert all(
        "cyclic synthetic repetition" in value
        for name, value in session.batch.provenance.items()
        if name != "fallback_reason"
    )


@pytest.mark.asyncio
async def test_wfdb_catalog_retains_source_attribution_and_license() -> None:
    cases = await WFDBAdapter().list_cases()

    assert {case.case_id for case in cases} == {
        "wfdb:bidmc01",
        "wfdb:ptt-s10-sit",
        "wfdb:mimic4-preview",
    }
    assert all("PhysioNet" in case.attribution for case in cases)
    assert all("DOI" in case.attribution for case in cases)


def test_api_health_cases_synthetic_sse_and_schema() -> None:
    settings = Settings(
        fixture_path=FIXTURE,
        vitaldb_timeout_seconds=0.1,
        offline_mode=False,
    )
    with TestClient(create_app(settings)) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok", "mode": "research", "version": "0.2.0"}

        cases = client.get("/v1/cases")
        assert cases.status_code == 200
        public_case = next(
            case for case in cases.json() if case["case_id"] == "vitaldb:public-live"
        )
        assert public_case["ds_status"] == "unknown_or_non_ds"
        assert public_case["clinical_use_allowed"] is False

        created = client.post(
            "/v1/replays",
            json={
                "case_id": "synthetic:stable-baseline",
                "speed": 1000.0,
                "baseline_seconds": 3,
            },
        )
        assert created.status_code == 201
        stream = client.get(created.json()["stream_url"])
        assert stream.status_code == 200
        data_lines = [
            line.removeprefix("data: ")
            for line in stream.text.splitlines()
            if line.startswith("data: ")
        ]
        assert data_lines
        final = StreamEvent.model_validate(json.loads(data_lines[-2]))
        assert final.risk.valid
        assert final.risk.data_source == "T21 synthetic generator"
        assert final.disclaimer.startswith("Research prototype")


def test_local_fixture_sse_and_replay_session_is_single_use() -> None:
    with TestClient(create_app(Settings(fixture_path=FIXTURE))) as client:
        created = client.post(
            "/v1/replays",
            json={"case_id": "local:fixture", "speed": 1000.0, "baseline_seconds": 3},
        )
        url = created.json()["stream_url"]
        first = client.get(url)
        second = client.get(url)

    assert first.status_code == 200
    assert "event: signal" in first.text
    assert "event: end" in first.text
    assert second.status_code == 404


def test_offline_mode_hides_and_rejects_network_backed_cases() -> None:
    with TestClient(
        create_app(Settings(fixture_path=FIXTURE, offline_mode=True))
    ) as client:
        cases = client.get("/v1/cases")
        assert cases.status_code == 200
        assert all(
            not case["case_id"].startswith(("vitaldb:", "wfdb:"))
            for case in cases.json()
        )

        blocked = client.post(
            "/v1/replays",
            json={
                "case_id": "vitaldb:public-live",
                "speed": 1000.0,
                "baseline_seconds": 3,
            },
        )
        assert blocked.status_code == 503
        assert "OFFLINE_MODE=true" in blocked.json()["detail"]


def test_local_fixture_default_baseline_reaches_a_valid_research_index() -> None:
    with TestClient(create_app(Settings(fixture_path=FIXTURE))) as client:
        created = client.post(
            "/v1/replays",
            json={"case_id": "local:fixture", "speed": 1000.0},
        )
        stream = client.get(created.json()["stream_url"])
        data_lines = [
            line.removeprefix("data: ")
            for line in stream.text.splitlines()
            if line.startswith("data: ")
        ]
        final = StreamEvent.model_validate(json.loads(data_lines[-2]))

    assert final.source.is_synthetic is True
    assert final.baseline.calibrated is True
    assert final.risk.valid is True
    assert final.risk.score is not None


def test_committed_openapi_and_event_schema_match_runtime_models() -> None:
    contracts = Path(__file__).resolve().parents[3] / "contracts"
    committed_openapi = json.loads(
        (contracts / "openapi.json").read_text(encoding="utf-8")
    )
    committed_event = json.loads(
        (contracts / "event.schema.json").read_text(encoding="utf-8")
    )
    runtime_event = StreamEvent.model_json_schema()
    runtime_event["$id"] = "https://t21-safe.local/contracts/event.schema.json"
    runtime_event["$schema"] = "https://json-schema.org/draft/2020-12/schema"

    assert committed_openapi == app.openapi()
    assert committed_event == runtime_event


def test_analyze_window_rejects_non_coarse_age_text() -> None:
    with TestClient(create_app(Settings(fixture_path=FIXTURE))) as client:
        response = client.post(
            "/v1/analyze-window",
            json={
                "timestamps_s": [0.0, 1.0],
                "signals": {"hr_bpm": [72.0, 72.0]},
                "sample_rate_hz": 1.0,
                "baseline_seconds": 3,
                "age_group": "11 years 3 months",
            },
        )

    assert response.status_code == 422


def test_analyze_window_rejects_non_finite_or_noncanonical_input() -> None:
    with pytest.raises(ValueError, match="finite number"):
        AnalyzeWindowRequest.model_validate(
            {
                "timestamps_s": [0.0, float("nan")],
                "signals": {"hr_bpm": [72.0, 72.0]},
                "sample_rate_hz": 1.0,
            }
        )
    with pytest.raises(ValueError, match="unsupported signal names"):
        AnalyzeWindowRequest.model_validate(
            {
                "timestamps_s": [0.0, 1.0],
                "signals": {"free_text_history": [1.0, 1.0]},
                "sample_rate_hz": 1.0,
            }
        )
    with pytest.raises(ValueError, match="at least one canonical signal"):
        AnalyzeWindowRequest.model_validate(
            {
                "timestamps_s": [0.0, 1.0],
                "signals": {},
                "sample_rate_hz": 1.0,
            }
        )


def test_docker_image_points_to_the_copied_offline_fixture() -> None:
    repository_root = Path(__file__).resolve().parents[3]
    dockerfile = (repository_root / "services/api/Dockerfile").read_text(
        encoding="utf-8"
    )

    assert "COPY tests/backend/fixtures /app/tests/backend/fixtures" in dockerfile
    assert (
        "T21_FIXTURE_PATH=/app/tests/backend/fixtures/local_waveform.csv" in dockerfile
    )
