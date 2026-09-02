"""Contract-compatible shadow-mode API shim for product integration tests.

This deterministic shim is owned by product-ui under infra. It is not a clinical
model and must be replaced by services/api at integration time.
"""

from __future__ import annotations

import asyncio
import json
import math
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

DISCLAIMER = "Research prototype; not for diagnosis, treatment, dosing, or clinical monitoring."

app = FastAPI(title="T21 Safe contract shim", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ReplayRequest(BaseModel):
    case_id: str
    patient_context: dict[str, Any] = Field(default_factory=dict)


SESSIONS: dict[str, ReplayRequest] = {}


CASES = [
    {
        "id": "progressive_instability",
        "name": "Progressive instability",
        "kind": "SYNTHETIC",
        "description": "Stable calibration followed by sustained HR, MAP, and PPG amplitude decline.",
        "attribution": "T21 Safe deterministic synthetic generator",
        "license": "Project test fixture — no patient data",
        "verified_ds": False,
    },
    {
        "id": "stable_case",
        "name": "Stable physiology",
        "kind": "SYNTHETIC",
        "description": "Stable baseline and high signal quality.",
        "attribution": "T21 Safe deterministic synthetic generator",
        "license": "Project test fixture — no patient data",
        "verified_ds": False,
    },
    {
        "id": "artifact_case",
        "name": "ECG motion artifact",
        "kind": "SYNTHETIC",
        "description": "Signal artifact suppresses index display.",
        "attribution": "T21 Safe deterministic synthetic generator",
        "license": "Project test fixture — no patient data",
        "verified_ds": False,
    },
    {
        "id": "missing_signal_case",
        "name": "Missing PPG signal",
        "kind": "SYNTHETIC",
        "description": "PPG is absent and operation is degraded.",
        "attribution": "T21 Safe deterministic synthetic generator",
        "license": "Project test fixture — no patient data",
        "verified_ds": False,
    },
    {
        "id": "recovery_case",
        "name": "Deterioration and recovery",
        "kind": "SYNTHETIC",
        "description": "Temporary deterioration returns toward baseline.",
        "attribution": "T21 Safe deterministic synthetic generator",
        "license": "Project test fixture — no patient data",
        "verified_ds": False,
    },
]


def samples(shape: str, timestamp_ms: int) -> list[float]:
    output: list[float] = []
    phase = timestamp_ms // 20
    for index in range(320):
        x = (index + phase) % 50
        if shape == "ecg":
            qrs = -0.25 if x == 3 else 1.0 if x == 4 else -0.4 if x == 5 else 0.0
            output.append(round(qrs + math.sin((index + phase) / 8) * 0.08, 4))
        elif shape == "ppg":
            output.append(round(max(0.0, math.sin((x / 50) * math.pi * 2)) ** 2 * 0.9, 4))
        else:
            output.append(round(65 + max(0.0, math.sin((x / 50) * math.pi * 2)) ** 1.5 * 42, 3))
    return output


def make_frame(case_id: str, timestamp_ms: int, patient_context: dict[str, Any]) -> dict[str, Any]:
    progress = min(1.0, timestamp_ms / 180_000)
    calibrated = progress >= 1
    elapsed = max(0, timestamp_ms - 180_000)
    effect = min(1.0, elapsed / 220_000) if case_id == "progressive_instability" else 0.0
    if case_id == "recovery_case":
        effect = max(0.0, 1 - abs(elapsed - 120_000) / 150_000)
    artifact = case_id == "artifact_case" and timestamp_ms >= 220_000
    missing_ppg = case_id == "missing_signal_case"
    usable = not artifact and not missing_ppg
    score: int | None = None
    level = "BASELINE"
    confidence = 0.0
    reasons = ["Baseline calibration is still in progress."]
    if calibrated and not usable:
        level = "INVALID"
        confidence = 0.16 if artifact else 0.28
        reasons = ["ECG motion artifact", "Signal quality is insufficient."] if artifact else ["PPG signal is unavailable", "Composite input requirements are not met."]
    elif calibrated:
        score = 18
        if case_id == "progressive_instability":
            score = min(82, round(18 + elapsed / 3_200))
        elif case_id == "recovery_case":
            score = max(22, min(80, round(20 + elapsed / 2_000 if elapsed < 120_000 else 80 - (elapsed - 120_000) / 2_300)))
        level = "ELEVATED" if score >= 65 else "WATCH" if score >= 38 else "STABLE"
        confidence = 0.88
        reasons = ["Heart rate is declining from baseline.", "MAP trend is declining.", "PPG amplitude is reduced."] if score >= 38 else ["Signals remain near the calibrated baseline."]
    hr = round(76 - effect * 18)
    map_value = round(82 - effect * 25)
    ppg_amplitude = round(0.92 - effect * 0.42, 2)
    mode = "DS_HYPOTHESIS_MODE" if patient_context.get("dsStatus") == "confirmed by clinical record" else "GENERIC_VALIDATION_MODE"
    return {
        "timestamp_ms": timestamp_ms,
        "mode": mode,
        "source": {"scenario_id": case_id, "synthetic": True, "api": "infra-contract-shim"},
        "patient_context": patient_context,
        "signals": {
            "ecg": {"value": hr, "unit": "bpm", "samples": samples("ecg", timestamp_ms), "sample_rate_hz": 250, "available": True},
            "ppg": {"value": None if missing_ppg else ppg_amplitude, "unit": "a.u.", "samples": [] if missing_ppg else samples("ppg", timestamp_ms), "sample_rate_hz": 100, "available": not missing_ppg},
            "abp": {"value": map_value, "unit": "mmHg", "samples": samples("abp", timestamp_ms), "sample_rate_hz": 125, "available": True},
            "spo2": {"value": 97, "unit": "%", "samples": [], "available": True},
            "etco2": {"value": 36, "unit": "mmHg", "samples": [], "available": True},
        },
        "quality": {
            "usable": usable,
            "reasons": ["ECG motion artifact"] if artifact else ["PPG absent"] if missing_ppg else [],
            "overall": 0.18 if artifact else 0.58 if missing_ppg else 0.94,
            "by_signal": {"ECG": 0.18 if artifact else 0.96, "PPG": 0 if missing_ppg else 0.92, "ABP": 0.95},
        },
        "baseline": {
            "calibrated": calibrated,
            "progress": progress,
            "stable": True,
            "values": {"hr": 76, "map": 82, "ppg_amplitude": 0.92, "rmssd": 31, "sdnn": 42},
            "confidence": 0.91 if calibrated else progress * 0.91,
            "failure_reasons": [],
        },
        "features": {
            "hr": hr, "hr_slope": round(-effect * 1.8, 1), "map": map_value,
            "map_slope": round(-effect * 2.4, 1), "ppg_amplitude": None if missing_ppg else ppg_amplitude,
            "rmssd": round(31 - effect * 9), "sdnn": round(42 - effect * 11), "spo2": 97,
            "etco2": 36, "respiratory_rate": 14, "beat_confidence": 0.18 if artifact else 0.96,
            "ptt": None if missing_ppg else round(228 + effect * 16),
        },
        "risk": {
            "name": "Research Instability Index", "score": score, "level": level, "valid": score is not None,
            "confidence": confidence, "reasons": reasons, "population_validated_on": "non-DS research data only",
        },
        "events": [{"id": "baseline", "timestamp_ms": 0, "type": "BASELINE", "label": "Baseline calibration"}],
        "disclaimer": DISCLAIMER,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "t21-safe-contract-shim"}


@app.get("/v1/cases")
def cases() -> list[dict[str, Any]]:
    return CASES


@app.post("/v1/replays")
def start_replay(payload: ReplayRequest) -> dict[str, str]:
    if payload.case_id not in {item["id"] for item in CASES}:
        raise HTTPException(status_code=404, detail="Unknown research case")
    session_id = str(uuid4())
    SESSIONS[session_id] = payload
    return {"session_id": session_id}


@app.get("/v1/stream/{session_id}")
async def stream(session_id: str, request: Request) -> StreamingResponse:
    replay = SESSIONS.get(session_id)
    if replay is None:
        raise HTTPException(status_code=404, detail="Unknown replay session")

    async def events():
        timestamp_ms = 0
        while timestamp_ms <= 600_000 and not await request.is_disconnected():
            yield f"data: {json.dumps(make_frame(replay.case_id, timestamp_ms, replay.patient_context))}\n\n"
            timestamp_ms += 20_000
            await asyncio.sleep(0.5)

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/v1/analyze-window")
def analyze_window(frame: dict[str, Any]) -> dict[str, Any]:
    return frame


@app.get("/v1/evidence")
def evidence() -> dict[str, Any]:
    return {
        "model_version": "rii-demo-deterministic-v0.3.0",
        "feature_schema": "t21-safe-feature-schema-v0.2",
        "data_source": "Synthetic contract shim",
        "source_population": "Non-DS research data only; synthetic scenarios are not a population",
        "ds_data_availability": "No DS-specific calibration or validation cohort is included in this build.",
        "known_limitations": [
            "Research thresholds are demonstration values.",
            "Signal loss can invalidate index output.",
            "This shim must be replaced by the versioned Session 2 backend at integration.",
        ],
        "evidence_id": "EVD-T21S-UI-0003",
        "dataset_license": "Synthetic fixtures contain no patient data",
        "model_card_url": "/docs/model-card.html",
        "protocol_url": "/docs/research-protocol.html",
    }
