"""Environment-backed API settings without secrets or patient identifiers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    version: str = "0.1.0"
    fixture_path: Path = Path(
        os.getenv(
            "T21_FIXTURE_PATH",
            str(Path(__file__).resolve().parents[4] / "tests/backend/fixtures/local_waveform.csv"),
        )
    )
    vitaldb_base_url: str = os.getenv("T21_VITALDB_BASE_URL", "https://api.vitaldb.net")
    vitaldb_timeout_seconds: float = float(os.getenv("T21_VITALDB_TIMEOUT_SECONDS", "12"))
