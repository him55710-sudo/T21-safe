"""Deterministic, offline-friendly smoke bench for cataloged public waveforms."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from t21_engine.adapters.base import DataAdapter
from t21_engine.adapters.wfdb_adapter import WFDB_CATALOG, WFDBCatalogMetadata
from t21_engine.types import SignalBatch

DEFAULT_PUBLIC_CASES = ("wfdb:mitdb-100", "wfdb:bidmc01")


def _public_metadata(metadata: WFDBCatalogMetadata | None) -> dict[str, str] | None:
    if metadata is None:
        return None
    fields = {
        "dataset_name": metadata.dataset_name.strip(),
        "dataset_version": metadata.dataset_version.strip(),
        "license_notes": metadata.license_notes.strip(),
        "attribution": metadata.attribution.strip(),
    }
    return fields if all(fields.values()) else None


def _smoke_failure(batch: SignalBatch) -> str | None:
    if not batch.signals:
        return "NO_SUPPORTED_SIGNALS"
    if batch.timestamps_s.size < 2 or not np.all(np.diff(batch.timestamps_s) > 0.0):
        return "INVALID_TIMESTAMPS"
    if any(values.size != batch.timestamps_s.size for values in batch.signals.values()):
        return "MISALIGNED_SIGNAL"
    if any(not np.isfinite(values).all() for values in batch.signals.values()):
        return "NONFINITE_SIGNAL"
    if not batch.source.attribution.strip():
        return "MISSING_SOURCE_ATTRIBUTION"
    return None


async def run_public_data_bench(
    adapter: DataAdapter,
    *,
    case_ids: Sequence[str] = DEFAULT_PUBLIC_CASES,
    seed: int = 20250321,
    duration_seconds: float = 10.0,
) -> dict[str, Any]:
    """Run a waveform integrity smoke bench; this does not calculate clinical output."""
    ordered_ids = list(case_ids)
    np.random.default_rng(seed).shuffle(ordered_ids)
    cases: list[dict[str, Any]] = []
    datasets: dict[tuple[str, str], dict[str, str]] = {}

    for case_id in ordered_ids:
        metadata = _public_metadata(WFDB_CATALOG.get(case_id))
        if metadata is None:
            cases.append(
                {
                    "case_id": case_id,
                    "status": "FAIL",
                    "failure_reason_code": "MISSING_PUBLIC_METADATA",
                }
            )
            continue
        datasets[(metadata["dataset_name"], metadata["dataset_version"])] = metadata
        try:
            batch = await adapter.load_case(case_id, duration_seconds=duration_seconds)
            reason = _smoke_failure(batch)
        except (KeyError, OSError, RuntimeError, ValueError) as exc:
            reason = "INPUT_LOAD_FAILED"
            # Exception text may contain local paths or source-record contents; do not export it.
            del exc
        cases.append(
            {
                "case_id": case_id,
                "status": "FAIL" if reason else "PASS",
                "failure_reason_code": reason,
            }
        )

    passed = bool(cases) and all(case["status"] == "PASS" for case in cases)
    return {
        "schema_version": "public-data-auto-bench/1.0",
        "status": "PASS" if passed else "FAIL",
        "seed": seed,
        "datasets": sorted(datasets.values(), key=lambda item: item["dataset_name"]),
        "case_ids_attempted": ordered_ids,
        "cases": cases,
        "clinical_validation": False,
        "research_use_only": True,
        "contains_phi": False,
        "network_required": False,
        "safety": {
            "mode": "LOCAL_OFFLINE_SMOKE_ONLY",
            "clinical_alerts": False,
            "clinical_decision_cutoffs": False,
            "actuation_or_dosing": False,
            "cloud_sinks": False,
            "login_or_rbac": False,
        },
    }
