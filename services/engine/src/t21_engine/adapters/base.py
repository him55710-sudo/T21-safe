"""Adapter interface and public case metadata."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any

from t21_engine.types import SignalBatch


@dataclass(frozen=True, slots=True)
class CaseDescriptor:
    case_id: str
    title: str
    source: str
    data_type: str
    available_signals: tuple[str, ...]
    is_synthetic: bool
    ds_status: str
    clinical_use_allowed: bool
    attribution: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DataAdapter(ABC):
    @abstractmethod
    async def list_cases(self) -> list[CaseDescriptor]:
        """Return cases without loading full waveform data."""

    @abstractmethod
    async def load_case(
        self,
        case_id: str,
        *,
        duration_seconds: float | None = None,
    ) -> SignalBatch:
        """Load signals that exist; optional signals must not fail the whole request."""
