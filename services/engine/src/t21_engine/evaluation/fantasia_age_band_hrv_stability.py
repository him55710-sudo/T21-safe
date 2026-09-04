"""HYP-07 PROXY: Fantasia age-band HRV feature reproducibility / engine QA.

PROXY_HRV_AGE_STABILITY only. clinical_validation=false.
Time-domain preferred; LF/HF is not a balance index here.
Age-band clinical claims stay PI_TO_DEFINE / HUMAN_REVIEW_REQUIRED.
Not a test of RQ-003 induction mechanisms.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from t21_engine.adapters.wfdb_adapter import WFDB_CATALOG
from t21_engine.beats.rpeak import detect_r_peaks
from t21_engine.features.hrv import rr_intervals_ms, time_domain_hrv

SCHEMA_VERSION = "fantasia-age-band-hrv-stability/1.0"
CATALOG_CASE_ID = "wfdb:fantasia-f1o01"
DEFAULT_RECORDS = ("f1o01", "synthetic02", "synthetic03")
ROLE_TAG = "PROXY_HRV_AGE_STABILITY"
HYPOTHESIS_ID = "HYP-07"
METRIC_NAMES = ("rr_mean_ms", "rmssd_ms", "sdnn_ms", "poincare_sd1_ms", "poincare_sd2_ms")


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _default_sample_root() -> Path | None:
    repository = _repository_root()
    for relative in (
        Path("data/public/fantasia/1.0.0"),
        Path("tests/backend/fixtures/wfdb_fantasia_synthetic"),
    ):
        candidate = repository / relative
        if candidate.is_dir():
            return candidate.resolve()
    return None


def _base_meta() -> dict[str, Any]:
    metadata = WFDB_CATALOG[CATALOG_CASE_ID]
    return {
        "schema_version": SCHEMA_VERSION,
        "hypothesis_id": HYPOTHESIS_ID,
        "role_tag": ROLE_TAG,
        "clinical_validation": False,
        "research_use_only": True,
        "network_required": False,
        "proxy_not_ds": True,
        "age_unavailable": True,
        "lf_hf_as_balance_index": False,
        "thresholds": {
            "age_band_cutoffs": "PI_TO_DEFINE",
            "stability_tolerance": "PI_TO_DEFINE",
            "note": "Age bands and clinical stability cutoffs stay PI_TO_DEFINE; engine QA only.",
        },
        "dataset": {
            "catalog_case_id": CATALOG_CASE_ID,
            "dataset_name": metadata.dataset_name,
            "dataset_version": metadata.dataset_version,
            "master_verified_proxy": metadata.public_bench_enabled,
            "usage": "PROXY_FIXTURE_ONLY",
        },
        "prohibited_claims": [
            "DS",
            "peri_op",
            "clinical_age_effect",
            "RQ003_causation",
            "lf_hf_balance_index",
            "pooled_instability_score",
            "dosing",
            "closed_loop",
        ],
    }


def _hypothesis() -> dict[str, Any]:
    return {
        "id": HYPOTHESIS_ID,
        "status": "HYPOTHESIS",
        "human_review_required": True,
        "rq003_note": (
            "Resting age HRV ≠ sevo induction autonomic mechanism (NOT causation)."
        ),
        "statement": (
            "Fantasia multi-record time-domain HRV differences provide a PROXY stress "
            "surface for autonomic feature pipelines — engine QA only, not age-effect "
            "or induction-mechanism claims."
        ),
    }


def _failure(reason: str, records: tuple[str, ...] | list[str]) -> dict[str, Any]:
    payload = _base_meta()
    payload.update(
        {
            "status": "FAIL",
            "failure_reason_code": reason,
            "records": [
                {"record": record, "status": "FAIL", "failure_reason_code": reason}
                for record in records
            ],
            "fact": None,
            "interpretation": None,
            "hypothesis": _hypothesis(),
        }
    )
    return payload


def _verify_fixture(root: Path) -> str | None:
    manifest_path = root / "sha256-manifest.json"
    if not manifest_path.is_file():
        return "MISSING_MANIFEST"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("sample_kind") != "synthetic_fixture_equivalent":
            return "INVALID_FIXTURE_PROVENANCE"
        files = manifest["files"]
        if not isinstance(files, dict) or not files:
            return "INVALID_FIXTURE_PROVENANCE"
        for name, expected in files.items():
            path = root / str(name)
            if not path.is_file():
                return "MISSING_SAMPLE"
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != str(expected).lower().removeprefix("sha256:"):
                return "SHA256_MISMATCH"
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return "INVALID_FIXTURE_PROVENANCE"
    return None


def _age_metadata(root: Path, record: str) -> dict[str, Any]:
    path = root / f"{record}.synthetic-metadata.json"
    if not path.is_file():
        return {
            "status": "UNAVAILABLE",
            "reason": "PI_TO_DEFINE",
            "age_metadata_available": False,
            "age_band": "PI_TO_DEFINE",
            "age_group": "PI_TO_DEFINE",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return {
            "status": "FAIL",
            "reason": "INVALID_AGE_METADATA",
            "age_metadata_available": False,
            "age_band": None,
            "age_group": None,
        }
    available = payload.get("age_metadata_available") is True
    if not available:
        return {
            "status": "UNAVAILABLE",
            "reason": "PI_TO_DEFINE",
            "age_metadata_available": False,
            "age_band": str(payload.get("age_band") or "PI_TO_DEFINE"),
            "age_group": str(payload.get("age_group") or "PI_TO_DEFINE"),
        }
    return {
        "status": "AVAILABLE",
        "reason": None,
        "age_metadata_available": True,
        "age_band": payload.get("age_band"),
        "age_group": payload.get("age_group"),
    }


def _evaluate_record(root: Path, record: str) -> dict[str, Any]:
    try:
        import wfdb

        waveform = wfdb.rdrecord(str(root / record))
        fs = float(waveform.fs)
        matrix = np.asarray(waveform.p_signal, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[1] < 1 or not np.isfinite(matrix).all() or fs <= 0:
            raise ValueError("invalid waveform")
        beats = detect_r_peaks(matrix[:, 0], fs)
        rr = rr_intervals_ms(beats)
    except (ImportError, OSError, RuntimeError, TypeError, ValueError):
        return {
            "record": record,
            "status": "FAIL",
            "failure_reason_code": "WFDB_LOAD_FAILURE",
        }
    if rr.size < 12:
        return {
            "record": record,
            "status": "FAIL",
            "failure_reason_code": "INSUFFICIENT_RR_INTERVALS",
        }
    full = time_domain_hrv(rr)
    repeated = time_domain_hrv(rr.copy())
    age = _age_metadata(root, record)
    if age["status"] == "FAIL":
        return {
            "record": record,
            "status": "FAIL",
            "failure_reason_code": str(age["reason"]),
            "age_metadata": age,
        }
    return {
        "record": record,
        "status": "PASS",
        "failure_reason_code": None,
        "sample_rate_hz": fs,
        "rr_interval_count": int(rr.size),
        "time_domain_hrv": {name: full[name] for name in METRIC_NAMES},
        "deterministic_recompute_exact": full == repeated,
        "age_metadata": age,
    }


def run_fantasia_age_band_hrv_stability(
    sample_root: str | Path | None = None,
    *,
    records: tuple[str, ...] | list[str] = DEFAULT_RECORDS,
) -> dict[str, Any]:
    """Multi-record Fantasia time-domain HRV engine QA (age clinical claims withheld)."""
    metadata = WFDB_CATALOG[CATALOG_CASE_ID]
    record_tuple = tuple(records)
    if not metadata.public_bench_enabled:
        return _failure("DATASET_NOT_PROMOTED", record_tuple)
    root = Path(sample_root).resolve() if sample_root is not None else _default_sample_root()
    if root is None or not root.is_dir():
        return _failure("MISSING_SAMPLE", record_tuple)
    provenance_failure = _verify_fixture(root)
    if provenance_failure is not None:
        return _failure(provenance_failure, record_tuple)
    for record in record_tuple:
        if not (root / f"{record}.hea").is_file():
            return _failure("MISSING_SAMPLE", record_tuple)

    rows = [_evaluate_record(root, record) for record in record_tuple]
    if any(row["status"] != "PASS" for row in rows):
        reason = next(
            str(row["failure_reason_code"]) for row in rows if row["status"] != "PASS"
        )
        payload = _base_meta()
        payload.update(
            {
                "status": "FAIL",
                "failure_reason_code": reason,
                "records": rows,
                "fact": None,
                "interpretation": None,
                "hypothesis": _hypothesis(),
            }
        )
        return payload

    metric_spreads: dict[str, float | None] = {}
    for name in METRIC_NAMES:
        values = [float(row["time_domain_hrv"][name]) for row in rows]
        if not values:
            metric_spreads[name] = None
        else:
            metric_spreads[name] = float(max(values) - min(values))

    age_available = any(row["age_metadata"]["age_metadata_available"] for row in rows)
    distinct_bands = {
        str(row["age_metadata"].get("age_band"))
        for row in rows
        if row["age_metadata"].get("age_metadata_available")
    }
    if not age_available:
        age_stability = {
            "status": "UNAVAILABLE",
            "reason": "PI_TO_DEFINE",
            "age_metadata_available": False,
            "distinct_age_bands": [],
            "note": "Synthetic fixtures withhold age bands; no clinical age effect inferred.",
        }
    elif len(distinct_bands) < 2:
        age_stability = {
            "status": "UNAVAILABLE",
            "reason": "INSUFFICIENT_AGE_GROUPS",
            "age_metadata_available": True,
            "distinct_age_bands": sorted(distinct_bands),
            "note": "Need ≥2 age bands for between-band stability; clinical cutoffs PI_TO_DEFINE.",
        }
    else:
        age_stability = {
            "status": "ENGINEERING_ONLY",
            "reason": None,
            "age_metadata_available": True,
            "distinct_age_bands": sorted(distinct_bands),
            "note": (
                "Age labels present for engine QA only — not RQ-003 causation or "
                "clinical age-effect claims."
            ),
        }

    fact = {
        "layer": "FACT",
        "records_evaluated": len(rows),
        "per_record": [
            {
                "record": row["record"],
                "rr_interval_count": row["rr_interval_count"],
                "sample_rate_hz": row["sample_rate_hz"],
                "time_domain_hrv": row["time_domain_hrv"],
                "deterministic_recompute_exact": row["deterministic_recompute_exact"],
                "age_metadata": row["age_metadata"],
            }
            for row in rows
        ],
        "preferred_feature_domain": "time_domain",
        "lf_hf_as_balance_index": False,
    }
    interpretation = {
        "layer": "INTERPRETATION",
        "status": "PASS",
        "reason": None,
        "engineering_probe_only": True,
        "clinical_cutoff": "PI_TO_DEFINE",
        "engine_qa": {
            "all_deterministic_recompute_exact": all(
                row["deterministic_recompute_exact"] for row in rows
            ),
            "cross_record_time_domain_absolute_spread": metric_spreads,
            "stability_tolerance": "PI_TO_DEFINE",
        },
        "age_stability": age_stability,
        "note": (
            "Cross-record time-domain spreads are engine QA stress signals only; "
            "not clinical age-band claims."
        ),
    }

    payload = _base_meta()
    payload.update(
        {
            "age_unavailable": not age_available,
            "status": "PASS",
            "failure_reason_code": None,
            "records": rows,
            "fact": fact,
            "interpretation": interpretation,
            "hypothesis": _hypothesis(),
        }
    )
    return payload


__all__ = ["run_fantasia_age_band_hrv_stability"]
