from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from t21_engine.adapters.wfdb_adapter import WFDB_CATALOG
from t21_engine.evaluation.public_data_bench import (
    DEFAULT_PUBLIC_CASES,
    run_public_data_bench,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "wfdb_bidmc_synthetic"
MITDB_FIXTURE = Path(__file__).parents[1] / "fixtures" / "wfdb_mitdb_synthetic"
EXPECTED_SHA256 = {
    "bidmc01.hea": "5267d168d1d7527767feeb609120fc0c072146c01e99f921409f420562e8ac6e",
    "bidmc01.dat": "7ea84b78a0a97e88018b90def1d180f622889bfd2930bfffbe54e536ab8fd0d1",
}
MITDB_EXPECTED_SHA256 = {
    "100.hea": "2f15c8cbb32d8dc5b50c39867ae73299e9d2a30fc2a23222c00c14700f596d86",
    "100.dat": "a047efbd949b1d8d4e2850435d8b05a07db4f2fbc5d6431a538414e09753f097",
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
            sig_name=["MLII" if Path(record_name).name == "100" else "PLETH"],
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
        case_ids=("wfdb:bidmc01",),
        local_sample=FIXTURE,
        expected_sha256=EXPECTED_SHA256,
        seed=17,
        duration_seconds=1.0,
    )

    assert DEFAULT_PUBLIC_CASES == ("wfdb:bidmc01", "wfdb:mitdb-100")
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
async def test_default_fixture_and_manifest_are_resolved(
    mock_wfdb: dict[str, object], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    del mock_wfdb
    monkeypatch.chdir(tmp_path)

    report = await run_public_data_bench(
        case_ids=("wfdb:bidmc01",), seed=17, duration_seconds=1.0
    )

    assert report["status"] == "PASS"
    assert report["cases"][0]["sha256"] == EXPECTED_SHA256


@pytest.mark.asyncio
async def test_default_local_root_is_preferred_and_manifest_verified(
    mock_wfdb: dict[str, object], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    del mock_wfdb
    local_root = tmp_path / "data/public/bidmc/1.0.0"
    local_root.mkdir(parents=True)
    for source in FIXTURE.iterdir():
        (local_root / source.name).write_bytes(source.read_bytes())
    manifest = json.loads((local_root / "sha256-manifest.json").read_text())
    manifest["files"]["bidmc01.dat"] = "0" * 64
    (local_root / "sha256-manifest.json").write_text(json.dumps(manifest))
    monkeypatch.chdir(tmp_path)

    report = await run_public_data_bench(case_ids=("wfdb:bidmc01",))

    assert report["status"] == "FAIL"
    assert report["cases"][0]["failure_reason_code"] == "SHA256_MISMATCH"


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
    report = await run_public_data_bench(
        case_ids=("wfdb:bidmc01",),
        local_sample=sample,
        expected_sha256=checksums,
    )

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
        case_ids=("wfdb:bidmc01",),
        local_sample=FIXTURE,
        expected_sha256=EXPECTED_SHA256,
    )

    assert report["status"] == "FAIL"
    assert report["cases"][0]["failure_reason_code"] == "WFDB_LOAD_FAILURE"


@pytest.mark.asyncio
async def test_missing_catalog_metadata_fails_closed_without_loading() -> None:
    report = await run_public_data_bench(case_ids=("wfdb:uncataloged",))

    assert report["status"] == "FAIL"
    assert report["cases"][0]["failure_reason_code"] == "MISSING_PUBLIC_METADATA"


@pytest.mark.asyncio
async def test_unpromoted_catalog_still_fails_closed() -> None:
    report = await run_public_data_bench(case_ids=("wfdb:ptt-s10-sit",))

    assert report["status"] == "FAIL"
    assert report["cases"][0]["failure_reason_code"] == "DATASET_NOT_PROMOTED"


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


@pytest.mark.asyncio
async def test_mitbih_promoted_fixture_passes_with_checksum(
    mock_wfdb: dict[str, object],
) -> None:
    del mock_wfdb
    report = await run_public_data_bench(
        case_ids=("wfdb:mitdb-100",),
        local_sample=MITDB_FIXTURE,
        expected_sha256=MITDB_EXPECTED_SHA256,
    )

    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["cases"][0]["sha256"] == MITDB_EXPECTED_SHA256
    assert report["cases"][0]["failure_reason_code"] is None
    assert report["datasets"][0]["dataset_name"] == "MIT-BIH Arrhythmia Database"
    assert WFDB_CATALOG["wfdb:mitdb-100"].public_bench_enabled is True
    assert DEFAULT_PUBLIC_CASES == ("wfdb:bidmc01", "wfdb:mitdb-100")


@pytest.mark.asyncio
async def test_default_promoted_fixtures_both_pass(mock_wfdb: dict[str, object]) -> None:
    del mock_wfdb
    report = await run_public_data_bench(seed=17, duration_seconds=1.0)

    assert report["status"] == "PASS"
    assert {case["case_id"] for case in report["cases"]} == set(DEFAULT_PUBLIC_CASES)
    assert all(case["failure_reason_code"] is None for case in report["cases"])
