"""Replay one already-downloaded WFDB sample through the deterministic pipeline."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from t21_engine.adapters.wfdb_adapter import WFDBAdapter
from t21_engine.streaming.replay import ReplayPipeline
from t21_engine.types import PipelineMode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Load one local WFDB record and print a compact research-only replay summary."
        )
    )
    parser.add_argument("--sample", required=True, type=Path, help="local .hea file")
    parser.add_argument(
        "--limit",
        required=True,
        type=float,
        help="maximum source seconds to replay (1-60)",
    )
    parser.add_argument(
        "--baseline-seconds",
        type=int,
        default=3,
        help="technical baseline duration for this bounded check (3-30)",
    )
    return parser.parse_args()


async def replay_sample(sample: Path, limit: float, baseline_seconds: int) -> dict[str, object]:
    header = sample.resolve()
    if header.suffix.lower() != ".hea" or not header.is_file():
        raise ValueError("--sample must be an existing local .hea file")
    if not 1.0 <= limit <= 60.0:
        raise ValueError("--limit must be between 1 and 60 seconds")
    if not 3 <= baseline_seconds <= 30 or baseline_seconds >= limit:
        raise ValueError("--baseline-seconds must be 3-30 and shorter than --limit")

    adapter = WFDBAdapter({"wfdb:local-sample": (str(header.with_suffix("")), None)})
    batch = await adapter.load_case("wfdb:local-sample", duration_seconds=limit)
    final: dict[str, object] | None = None
    event_count = 0
    async for event in ReplayPipeline().events(
        batch,
        mode=PipelineMode.GENERIC_VALIDATION_MODE,
        baseline_seconds=baseline_seconds,
        speed=1000.0,
        real_time=False,
    ):
        final = event
        event_count += 1
    if final is None:
        raise ValueError("sample produced no replay events")

    risk = final["risk"]
    quality = final["quality"]
    assert isinstance(risk, dict)
    assert isinstance(quality, dict)
    return {
        "research_use_only": True,
        "source": str(header),
        "samples": int(batch.timestamps_s.size),
        "signals": sorted(batch.signals),
        "events": event_count,
        "quality_usable": quality["usable"],
        "risk_valid": risk["valid"],
        "risk_level": risk["level"],
        "limitations": risk["limitations"],
    }


def main() -> int:
    args = parse_args()
    try:
        result = asyncio.run(replay_sample(args.sample, args.limit, args.baseline_seconds))
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"replay_wfdb_sample: {exc}") from exc
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
