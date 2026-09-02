"""One-command, synthetic-only research node demonstration.

This entry point intentionally reuses the hospital fixture and replay shadow
path. It is not a clinical monitor and does not accept patient data.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from t21_engine.adapters.synthetic_hospital_case import build_synthetic_hospital_case
from t21_engine.streaming.replay import ReplayPipeline

DEFAULT_DURATION_SECONDS = 12.0
DEFAULT_BASELINE_SECONDS = 3
DEFAULT_SEED = 20250321
DEFAULT_SESSION_ID = "synthetic-research-node-demo"


async def run_demo(
    *,
    duration_seconds: float = DEFAULT_DURATION_SECONDS,
    baseline_seconds: int = DEFAULT_BASELINE_SECONDS,
    seed: int = DEFAULT_SEED,
    output_dir: str | Path | None = None,
) -> dict[str, object]:
    """Run alignment/QC and deterministic replay, optionally writing metadata."""
    case = build_synthetic_hospital_case(duration_s=duration_seconds, seed=seed)
    alignment = case.quality_report()
    if alignment.status != "PASS":
        codes = ", ".join(reason.code for reason in alignment.reasons)
        raise ValueError(f"synthetic hospital alignment failed closed: {codes}")

    batch = case.to_signal_batch()
    final_event: dict[str, object] | None = None
    event_count = 0
    async for event in ReplayPipeline().events(
        batch,
        baseline_seconds=baseline_seconds,
        real_time=False,
        shadow_session_id=DEFAULT_SESSION_ID if output_dir is not None else None,
        local_capture_dir=output_dir,
        write_export_manifest=output_dir is not None,
    ):
        final_event = event
        event_count += 1

    if final_event is None:
        raise RuntimeError("synthetic replay produced no events")

    quality = final_event["quality"]
    baseline = final_event["baseline"]
    assert isinstance(quality, dict)
    assert isinstance(baseline, dict)
    report: dict[str, object] = {
        "mission": "CODEX-010",
        "status": "PASS",
        "path": "Path B",
        "intended_use": "RESEARCH_USE_ONLY",
        "mode": "OBSERVE_ONLY_SHADOW",
        "synthetic_only": True,
        "contains_phi": False,
        "clinical_validation": False,
        "case_id": case.case_id,
        "duration_seconds": duration_seconds,
        "seed": seed,
        "alignment_qc": alignment.to_dict(),
        "replay_qc": {
            "events_processed": event_count,
            "timestamp_synchronized": quality["timestamp_synchronized"],
            "quality_usable": quality["usable"],
            "quality_reasons": quality["reasons"],
            "baseline_calibrated": baseline["calibrated"],
        },
        "local_export": None,
    }
    if output_dir is not None:
        report["local_export"] = {
            "jsonl_path": str(Path(output_dir).expanduser().resolve() / "shadow-capture.jsonl"),
            "content_scope": "SHADOW_CAPTURE_METADATA_ONLY",
            "includes_waveforms": False,
            "includes_phi": False,
            "manifest_appended": True,
        }
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the local synthetic Path B / RUO research node demo."
    )
    parser.add_argument(
        "--output-dir",
        help="Optional local directory for shadow metadata JSONL and its ExportManifest.",
    )
    parser.add_argument("--duration-seconds", type=float, default=DEFAULT_DURATION_SECONDS)
    parser.add_argument("--baseline-seconds", type=int, default=DEFAULT_BASELINE_SECONDS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = asyncio.run(
            run_demo(
                duration_seconds=args.duration_seconds,
                baseline_seconds=args.baseline_seconds,
                seed=args.seed,
                output_dir=args.output_dir,
            )
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "mission": "CODEX-010",
                    "status": "FAIL_CLOSED",
                    "clinical_validation": False,
                    "synthetic_only": True,
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main", "run_demo"]
