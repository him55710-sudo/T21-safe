"""In-memory replay sessions with deterministic cleanup."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from t21_engine.adapters import (
    DataAdapter,
    LocalFixtureAdapter,
    SyntheticAdapter,
    VitalDBAdapter,
    WFDBAdapter,
)
from t21_engine.types import PipelineMode, SignalBatch


@dataclass(slots=True)
class ReplaySession:
    session_id: str
    batch: SignalBatch
    speed: float
    baseline_seconds: int
    mode: PipelineMode
    claimed: bool = False
    created_monotonic: float = 0.0


class SessionManager:
    def __init__(
        self,
        *,
        fixture_path: Path,
        vitaldb_base_url: str,
        vitaldb_timeout_seconds: float,
        offline_mode: bool = True,
        session_ttl_seconds: float = 900.0,
    ) -> None:
        local = LocalFixtureAdapter(fixture_path)
        self._synthetic = SyntheticAdapter()
        self._local = local
        self._vitaldb = VitalDBAdapter(
            base_url=vitaldb_base_url,
            timeout_seconds=vitaldb_timeout_seconds,
            fallback=local,
        )
        self._wfdb = WFDBAdapter()
        self._offline_mode = offline_mode
        online_adapters: tuple[DataAdapter, ...] = (
            () if offline_mode else (self._vitaldb, self._wfdb)
        )
        self.adapters: tuple[DataAdapter, ...] = (self._synthetic, self._local, *online_adapters)
        self._sessions: dict[str, ReplaySession] = {}
        self._lock = asyncio.Lock()
        self._session_ttl_seconds = session_ttl_seconds

    async def list_cases(self) -> list[dict[str, object]]:
        cases: list[dict[str, object]] = []
        for adapter in self.adapters:
            cases.extend(case.to_dict() for case in await adapter.list_cases())
        return cases

    async def create(
        self,
        case_id: str,
        *,
        speed: float,
        baseline_seconds: int,
        mode: PipelineMode,
    ) -> ReplaySession:
        adapter = self._adapter_for(case_id)
        if case_id.startswith("synthetic:"):
            duration = max(float(baseline_seconds + 60), 30.0)
        elif case_id == "vitaldb:public-live":
            # The live API caps its own window at 60 s, while its local fallback can
            # still honor the full offline baseline request.
            duration = float(baseline_seconds + 5)
        elif case_id == "local:fixture":
            duration = float(baseline_seconds + 5)
        else:
            duration = None
        batch = await adapter.load_case(case_id, duration_seconds=duration)
        session = ReplaySession(
            uuid4().hex,
            batch,
            speed,
            baseline_seconds,
            mode,
            created_monotonic=time.monotonic(),
        )
        async with self._lock:
            self._prune_expired_locked()
            self._sessions[session.session_id] = session
        return session

    async def claim(self, session_id: str) -> ReplaySession | None:
        async with self._lock:
            self._prune_expired_locked()
            session = self._sessions.get(session_id)
            if session is None or session.claimed:
                return None
            session.claimed = True
            return session

    async def remove(self, session_id: str) -> None:
        async with self._lock:
            self._sessions.pop(session_id, None)

    def _adapter_for(self, case_id: str) -> DataAdapter:
        if case_id.startswith("synthetic:"):
            return self._synthetic
        if case_id == "local:fixture":
            return self._local
        if self._offline_mode and (case_id == "vitaldb:public-live" or case_id.startswith("wfdb:")):
            raise RuntimeError("network-backed replay is disabled while OFFLINE_MODE=true")
        if case_id == "vitaldb:public-live":
            return self._vitaldb
        if case_id.startswith("wfdb:"):
            return self._wfdb
        raise KeyError(case_id)

    def _prune_expired_locked(self) -> None:
        cutoff = time.monotonic() - self._session_ttl_seconds
        expired = [
            session_id
            for session_id, session in self._sessions.items()
            if not session.claimed and session.created_monotonic < cutoff
        ]
        for session_id in expired:
            self._sessions.pop(session_id, None)
