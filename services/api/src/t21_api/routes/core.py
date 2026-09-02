"""Health, cases, replay, analysis, and evidence routes."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import numpy as np
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from t21_engine.streaming.replay import ReplayPipeline
from t21_engine.types import SignalBatch, SourceMetadata

from t21_api.schemas import (
    AnalyzeWindowRequest,
    CaseResponse,
    EvidenceResponse,
    HealthResponse,
    ReplayRequest,
    ReplayResponse,
    StreamEvent,
)

router = APIRouter()


def _manager(request: Request):  # type: ignore[no-untyped-def]
    return request.app.state.session_manager


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.get("/v1/cases", response_model=list[CaseResponse])
async def cases(request: Request) -> list[CaseResponse]:
    return [CaseResponse.model_validate(case) for case in await _manager(request).list_cases()]


@router.post("/v1/replays", response_model=ReplayResponse, status_code=201)
async def create_replay(payload: ReplayRequest, request: Request) -> ReplayResponse:
    try:
        session = await _manager(request).create(
            payload.case_id,
            speed=payload.speed,
            baseline_seconds=payload.baseline_seconds,
            mode=payload.mode,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="case not found") from exc
    except (ConnectionError, FileNotFoundError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=f"case unavailable: {exc}") from exc
    return ReplayResponse(
        session_id=session.session_id,
        stream_url=f"/v1/stream/{session.session_id}",
    )


@router.get("/v1/stream/{session_id}")
async def stream_replay(session_id: str, request: Request) -> StreamingResponse:
    manager = _manager(request)
    session = await manager.claim(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found or already consumed")
    pipeline = ReplayPipeline()

    async def event_frames() -> AsyncIterator[str]:
        try:
            async for event in pipeline.events(
                session.batch,
                mode=session.mode,
                baseline_seconds=session.baseline_seconds,
                speed=session.speed,
                real_time=True,
            ):
                validated = StreamEvent.model_validate(event)
                yield (
                    "event: signal\ndata: "
                    + json.dumps(
                        validated.model_dump(mode="json"),
                        separators=(",", ":"),
                        allow_nan=False,
                    )
                    + "\n\n"
                )
        finally:
            await manager.remove(session_id)

    return StreamingResponse(
        event_frames(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/v1/analyze-window", response_model=StreamEvent)
async def analyze_window(payload: AnalyzeWindowRequest) -> StreamEvent:
    timestamps = np.asarray(payload.timestamps_s, dtype=np.float64)
    signals = {
        name: np.asarray(
            [value if value is not None else np.nan for value in values], dtype=np.float64
        )
        for name, values in payload.signals.items()
    }
    batch = SignalBatch(
        timestamps_s=timestamps,
        signals=signals,
        sample_rates_hz={name: payload.sample_rate_hz for name in signals},
        source=SourceMetadata(
            dataset="User-provided de-identified analysis window",
            case_id="batch-window",
            is_synthetic=False,
            ds_status=payload.ds_status,
            age_group=payload.age_group,
            attribution="Ephemeral request body; not persisted.",
        ),
        provenance={name: "raw:ephemeral_api_request" for name in signals},
    )
    final_event: dict[str, object] | None = None
    pipeline = ReplayPipeline()
    async for event in pipeline.events(
        batch,
        mode=payload.mode,
        baseline_seconds=payload.baseline_seconds,
        speed=1000.0,
        real_time=False,
    ):
        final_event = event
    if final_event is None:
        raise HTTPException(status_code=422, detail="window contains no samples")
    return StreamEvent.model_validate(final_event)


@router.get("/v1/evidence", response_model=EvidenceResponse)
async def evidence() -> EvidenceResponse:
    return EvidenceResponse.model_validate(
        {
            "model_version": "rii-v0.1",
            "feature_schema_version": "features-v0.1",
            "clinical_validation": False,
            "items": [
                {
                    "evidence_id": "vitaldb-2022",
                    "feature_or_model": "public waveform adapter and generic validation",
                    "citation": (
                        "Lee HC et al. VitalDB, a high-fidelity multi-parameter vital signs "
                        "database in surgical patients. Scientific Data, 2022."
                    ),
                    "url": "https://doi.org/10.1038/s41597-022-01411-5",
                    "applicability": "Adult perioperative signal-processing research.",
                    "limitation": "Does not establish DS or pediatric clinical performance.",
                },
                {
                    "evidence_id": "physionet-waveform-sources",
                    "feature_or_model": "optional WFDB adapters",
                    "citation": (
                        "PhysioNet BIDMC PPG, Pulse Transit Time PPG, and MIMIC-IV "
                        "Waveform Database source records."
                    ),
                    "url": "https://physionet.org/about/database/",
                    "applicability": "Generic signal-processing interoperability research.",
                    "limitation": (
                        "Source-specific licenses and citations apply; no DS performance claim."
                    ),
                },
                {
                    "evidence_id": "rii-config-v0.1",
                    "feature_or_model": "Research Instability Index",
                    "citation": (
                        "Version-pinned transparent engineering hypothesis in this repository."
                    ),
                    "url": "",
                    "applicability": "Research visualization and software verification only.",
                    "limitation": "Not trained or calibrated as a clinical probability.",
                },
            ],
        }
    )
