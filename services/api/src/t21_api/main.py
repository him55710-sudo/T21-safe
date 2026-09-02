"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from t21_api.routes.core import router
from t21_api.settings import Settings
from t21_api.streaming.sessions import SessionManager


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings()
    app = FastAPI(
        title="T21 Safe Research Signal API",
        version=resolved.version,
        description=(
            "Research Use Only / Shadow Mode. Not for diagnosis, treatment, dosing, "
            "or clinical monitoring."
        ),
    )
    app.state.session_manager = SessionManager(
        fixture_path=resolved.fixture_path,
        vitaldb_base_url=resolved.vitaldb_base_url,
        vitaldb_timeout_seconds=resolved.vitaldb_timeout_seconds,
    )
    app.include_router(router)
    return app


app = create_app()
