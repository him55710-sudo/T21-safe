"""Generate committed API contracts from the runtime models."""

from __future__ import annotations

import json
from pathlib import Path

from t21_api.main import app
from t21_api.schemas import StreamEvent


def generate(output_directory: Path) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / "openapi.json").write_text(
        json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    event_schema = StreamEvent.model_json_schema()
    event_schema["$id"] = "https://t21-safe.local/contracts/event.schema.json"
    event_schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    (output_directory / "event.schema.json").write_text(
        json.dumps(event_schema, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[4] / "contracts")
