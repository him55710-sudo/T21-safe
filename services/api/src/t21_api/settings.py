"""Environment-backed API settings without secrets or patient identifiers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _allowed_origins() -> tuple[str, ...]:
    configured = os.getenv("T21_ALLOWED_ORIGINS")
    if configured:
        return tuple(item.strip() for item in configured.split(",") if item.strip())
    return ("http://localhost:3000", "http://127.0.0.1:3000")


@dataclass(frozen=True, slots=True)
class Settings:
    version: str = "0.2.0"
    fixture_path: Path = Path(
        os.getenv(
            "T21_FIXTURE_PATH",
            str(Path(__file__).resolve().parents[4] / "tests/backend/fixtures/local_waveform.csv"),
        )
    )
    vitaldb_base_url: str = os.getenv("T21_VITALDB_BASE_URL", "https://api.vitaldb.net")
    vitaldb_timeout_seconds: float = float(os.getenv("T21_VITALDB_TIMEOUT_SECONDS", "12"))
    offline_mode: bool = _env_flag("OFFLINE_MODE", True)
    allowed_origins: tuple[str, ...] = _allowed_origins()
