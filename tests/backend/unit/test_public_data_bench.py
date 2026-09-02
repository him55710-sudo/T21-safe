from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from t21_engine.evaluation.public_data_bench import (
    DEFAULT_PUBLIC_CASES,
    run_public_data_bench,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "wfdb_bidmc_synthetic"
EXPECTED_SHA256 = {
    "bidmc01.hea": "5267d168d1d7527767feeb609120fc0c072146c01e99f921409f420562e8ac6e",
    "bidmc01.dat": "7ea84b78a0a97e88018b90def1d180f622889bfd2930bfffbe54e536ab8fd0d1",
}


@pytest.fixture
def mock_wfdb(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    calls: dict[str, object] = {}

    def rdheader(record_name: str, **kwargs: object) -> SimpleNamespace:
        calls["header"] = (record_name, kwargs)
        return SimpleNamespace(fs=10.0)

    def rdrecord(record_name: str, **kwargs: object) -> SimpleNamespace:
        calls["record"] = (record_name, kwargs)
        samples = int(kwargs.get("sampto", 20))
        return SimpleNamespace(
            fs=10.0,
            p_signal=np.linspace(0.0, 1.0, samples, dtype=np.float64)[:, None],
            sig_name=["PLETH"],
        )

    monkeypatch.setitem(
        sys.modules, "wfdb", SimpleNamespace(rdheader=rdheader, rdrecord=rdrecord)
    )
    return calls


@pytest.mark.asyncio
async def test_bidmc_local_fixture_passes_with_checksums_and_wfdb_io(
    mock_wfdb: dict[str, object],
) -> None:
    report = await run_public_data_bench(
        local_sample=FIXTURE,
        expected_sha256=EXPECTED_SHA256,
        seed=17,
        duration_seconds=1.0,
    )

    assert DEFAULT_PUBLIC_CASES == ("wfdb:bidmc01",)
    assert report["schema_version"] == "public-data-auto-bench/1.0"
    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["case_ids_attempted"] == ["wfdb:bidmc01"]
    assert report["cases"][0]["sha256"] == EXPECTED_SHA256
    assert report["cases"][0]["failure_reason_code"] is None
    assert report["datasets"][0]["dataset_name"] == "BIDMC PPG and Respiration Dataset"
    assert report["datasets"][0]["dataset_version"] == "1.0.0"
    assert report["datasets"][0]["license_notes"]
    assert "pn_dir" not in mock_wfdb["header"][1]  # type: ignore[index]
    assert "pn_dir" not in mock_wfdb["record"][1]  # type: ignore[index]
    json.dumps(report)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("sample", "checksums", "reason"),
    [
        (Path("does-not-exist"), EXPECTED_SHA256, "MISSING_SAMPLE"),
        (FIXTURE, {**EXPECTED_SHA256, "bidmc01.dat": "0" * 64}, "SHA256_MISMATCH"),
    ],
)
async def test_local_input_failures_are_machine_readable(
    sample: Path, checksums: dict[str, str], reason: str
) -> None:
    report = await run_public_data_bench(local_sample=sample, expected_sha256=checksums)

    assert report["status"] == "FAIL"
    assert report["cases"][0]["failure_reason_code"] == reason


@pytest.mark.asyncio
async def test_wfdb_load_failure_is_machine_readable(
    mock_wfdb: dict[str, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    del mock_wfdb

    def fail_load(record_name: str, **kwargs: object) -> None:
        del record_name, kwargs
        raise OSError("fixture is corrupt")

    monkeypatch.setattr(sys.modules["wfdb"], "rdrecord", fail_load)
    report = await run_public_data_bench(
        local_sample=FIXTURE, expected_sha256=EXPECTED_SHA256
    )

    assert report["status"] == "FAIL"
    assert report["cases"][0]["failure_reason_code"] == "WFDB_LOAD_FAILURE"


@pytest.mark.asyncio
async def test_missing_catalog_metadata_fails_closed_without_loading() -> None:
    report = await run_public_data_bench(case_ids=("wfdb:uncataloged",))

    assert report["status"] == "FAIL"
    assert report["cases"][0]["failure_reason_code"] == "MISSING_PUBLIC_METADATA"


@pytest.mark.asyncio
async def test_same_seed_produces_same_report_fields(mock_wfdb: dict[str, object]) -> None:
    first = await run_public_data_bench(
        local_sample=FIXTURE, expected_sha256=EXPECTED_SHA256, seed=923
    )
    second = await run_public_data_bench(
        local_sample=FIXTURE, expected_sha256=EXPECTED_SHA256, seed=923
    )

    assert first == second


@pytest.mark.asyncio
async def test_path_b_safety_is_local_observe_only() -> None:
    report = await run_public_data_bench()

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
