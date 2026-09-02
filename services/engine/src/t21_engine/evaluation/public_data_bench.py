"""Deterministic, offline-friendly smoke bench for cataloged public waveforms."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

from t21_engine.adapters.base import DataAdapter
from t21_engine.adapters.wfdb_adapter import WFDB_CATALOG, WFDBAdapter, WFDBCatalogMetadata
from t21_engine.types import SignalBatch

DEFAULT_PUBLIC_CASES = ("wfdb:bidmc01",)
MANIFEST_FILENAME = "sha256-manifest.json"


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _resolve_default_sample() -> Path | None:
    """Prefer an operator-provided local sample, then the bounded CI fixture."""
    repository = _repository_root()
    candidates = (
        Path("data/public/bidmc/1.0.0"),
        repository / "data/public/bidmc/1.0.0",
        repository / "tests/backend/fixtures/wfdb_bidmc_synthetic",
    )
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen and resolved.is_dir():
            return resolved
        seen.add(resolved)
    return None


def _manifest_sha256(sample_root: Path) -> dict[str, str]:
    manifest_path = sample_root / MANIFEST_FILENAME
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid checksum manifest")
    for field in ("dataset_name", "dataset_version", "license_note"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            raise ValueError("incomplete checksum manifest metadata")
    files = payload.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("invalid checksum manifest files")
    checksums: dict[str, str] = {}
    for name, digest in files.items():
        if (
            not isinstance(name, str)
            or Path(name).name != name
            or not isinstance(digest, str)
            or len(digest.lower().removeprefix("sha256:")) != 64
        ):
            raise ValueError("invalid checksum manifest entry")
        checksums[name] = digest.lower().removeprefix("sha256:")
    return checksums


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _local_record_files(sample: Path) -> tuple[Path, list[Path]]:
    """Resolve one bounded, local WFDB header and its directly referenced data files."""
    header = sample / "bidmc01.hea" if sample.is_dir() else sample
    if header.suffix.lower() != ".hea" or not header.is_file():
        raise FileNotFoundError("local BIDMC sample header is missing")
    lines = [line.split() for line in header.read_text(encoding="utf-8-sig").splitlines()]
    if not lines or len(lines[0]) < 2:
        raise ValueError("invalid WFDB header")
    signal_count = int(lines[0][1])
    if signal_count < 1 or len(lines) < signal_count + 1:
        raise ValueError("invalid WFDB signal declarations")
    parent = header.resolve().parent
    data_files: list[Path] = []
    for fields in lines[1 : signal_count + 1]:
        if not fields:
            raise ValueError("invalid WFDB signal declaration")
        data_file = (parent / fields[0]).resolve()
        if data_file.parent != parent or not data_file.is_file():
            raise FileNotFoundError("local WFDB data file is missing")
        if data_file not in data_files:
            data_files.append(data_file)
    return header.resolve(), [header.resolve(), *data_files]


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
    adapter: DataAdapter | None = None,
    *,
    case_ids: Sequence[str] = DEFAULT_PUBLIC_CASES,
    local_sample: str | Path | None = None,
    expected_sha256: dict[str, str] | None = None,
    seed: int = 20250321,
    duration_seconds: float = 10.0,
) -> dict[str, Any]:
    """Run a waveform integrity smoke bench; this does not calculate clinical output."""
    ordered_ids = list(case_ids)
    np.random.default_rng(seed).shuffle(ordered_ids)
    cases: list[dict[str, Any]] = []
    datasets: dict[tuple[str, str], dict[str, str]] = {}

    local_adapter = adapter
    checksums: dict[str, str] = {}
    local_failure: str | None = None
    resolved_sample = Path(local_sample) if local_sample is not None else _resolve_default_sample()
    if resolved_sample is None:
        local_failure = "MISSING_SAMPLE"
    else:
        try:
            header, files = _local_record_files(resolved_sample)
            checksums = {path.name: _sha256(path) for path in files}
            expected = expected_sha256
            if expected is None:
                expected = _manifest_sha256(header.parent)
            if (
                set(expected) != set(checksums)
                or any(
                    expected[name].lower().removeprefix("sha256:") != digest
                    for name, digest in checksums.items()
                )
            ):
                local_failure = "SHA256_MISMATCH"
            else:
                local_adapter = WFDBAdapter(
                    {"wfdb:bidmc01": (str(header.with_suffix("")), None)}
                )
        except FileNotFoundError:
            local_failure = "MISSING_SAMPLE"
        except (OSError, UnicodeError, ValueError):
            local_failure = "WFDB_LOAD_FAILURE"

    for case_id in ordered_ids:
        metadata = _public_metadata(WFDB_CATALOG.get(case_id))
        if metadata is None:
            cases.append(
                {
                    "case_id": case_id,
                    "status": "FAIL",
                    "failure_reason_code": "MISSING_PUBLIC_METADATA",
                    "sha256": checksums,
                }
            )
            continue
        datasets[(metadata["dataset_name"], metadata["dataset_version"])] = metadata
        reason = local_failure
        if reason is None:
            try:
                if local_adapter is None:
                    raise RuntimeError("no local WFDB adapter")
                batch = await local_adapter.load_case(case_id, duration_seconds=duration_seconds)
                reason = _smoke_failure(batch)
            except (KeyError, OSError, RuntimeError, ValueError) as exc:
                reason = "WFDB_LOAD_FAILURE"
                # Exception text may contain local paths or record contents; do not export it.
                del exc
        cases.append(
            {
                "case_id": case_id,
                "status": "FAIL" if reason else "PASS",
                "failure_reason_code": reason,
                "sha256": checksums,
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
