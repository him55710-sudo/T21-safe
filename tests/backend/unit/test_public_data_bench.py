from __future__ import annotations

import json

import numpy as np
import pytest

from t21_engine.adapters.base import CaseDescriptor, DataAdapter
from t21_engine.evaluation.public_data_bench import run_public_data_bench
from t21_engine.types import SignalBatch, SourceMetadata


class FixtureAdapter(DataAdapter):
    def __init__(self, *, corrupt_case: str | None = None) -> None:
        self.corrupt_case = corrupt_case

    async def list_cases(self) -> list[CaseDescriptor]:
        return []

    async def load_case(
        self, case_id: str, *, duration_seconds: float | None = None
    ) -> SignalBatch:
        del duration_seconds
        if case_id == self.corrupt_case:
            raise OSError("fixture is missing or corrupt")
        sample_rate = 10.0
        timestamps = np.arange(20, dtype=np.float64) / sample_rate
        return SignalBatch(
            timestamps_s=timestamps,
            signals={"ecg_ii": np.sin(timestamps)},
            sample_rates_hz={"ecg_ii": sample_rate},
            source=SourceMetadata(
                dataset="offline public fixture",
                case_id=case_id,
                is_synthetic=True,
                attribution="Synthetic stand-in for an attributed public catalog record.",
            ),
            provenance={"ecg_ii": "fixture:generated"},
        )


@pytest.mark.asyncio
async def test_report_shape_and_public_metadata() -> None:
    report = await run_public_data_bench(FixtureAdapter(), seed=17)

    assert report["schema_version"] == "public-data-auto-bench/1.0"
    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["contains_phi"] is False
    assert set(report["case_ids_attempted"]) == {"wfdb:mitdb-100", "wfdb:bidmc01"}
    assert {item["dataset_name"] for item in report["datasets"]} == {
        "MIT-BIH Arrhythmia Database",
        "BIDMC PPG and Respiration Dataset",
    }
    assert all(item["dataset_version"] == "1.0.0" for item in report["datasets"])
    metadata_complete = [
        item["license_notes"] and item["attribution"] for item in report["datasets"]
    ]
    assert all(metadata_complete)
    assert all(case["failure_reason_code"] is None for case in report["cases"])
    json.dumps(report)


@pytest.mark.asyncio
async def test_missing_or_corrupt_input_produces_machine_readable_fail() -> None:
    report = await run_public_data_bench(
        FixtureAdapter(corrupt_case="wfdb:bidmc01"),
        case_ids=("wfdb:bidmc01",),
    )

    assert report["status"] == "FAIL"
    assert report["cases"] == [
        {
            "case_id": "wfdb:bidmc01",
            "status": "FAIL",
            "failure_reason_code": "INPUT_LOAD_FAILED",
        }
    ]


@pytest.mark.asyncio
async def test_missing_catalog_metadata_fails_closed_without_loading() -> None:
    unknown_cases = ("wfdb:uncataloged",)
    report = await run_public_data_bench(FixtureAdapter(), case_ids=unknown_cases)

    assert report["status"] == "FAIL"
    assert report["cases"][0]["failure_reason_code"] == "MISSING_PUBLIC_METADATA"


@pytest.mark.asyncio
async def test_same_seed_produces_same_report_fields() -> None:
    first = await run_public_data_bench(FixtureAdapter(), seed=923)
    second = await run_public_data_bench(FixtureAdapter(), seed=923)

    assert first == second


@pytest.mark.asyncio
async def test_path_b_safety_is_local_observe_only() -> None:
    report = await run_public_data_bench(FixtureAdapter())

    assert report["network_required"] is False
    assert report["contains_phi"] is False
    assert report["safety"] == {
        "mode": "LOCAL_OFFLINE_SMOKE_ONLY",
        "clinical_alerts": False,
        "clinical_decision_cutoffs": False,
        "actuation_or_dosing": False,
        "cloud_sinks": False,
        "login_or_rbac": False,
    }
