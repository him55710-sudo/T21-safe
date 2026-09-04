"""HYP-03 PROXY: Fantasia short-window HRV / LF-HF negative-control scaffold.

PROXY_HRV_AGE_STABILITY only. clinical_validation=false.
LF/HF is never primary. RQ-004 remains HYPOTHESIS / gap.
Thresholds for clinical transfer stay PI_TO_DEFINE. No peri-op / DS claims.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from t21_engine.adapters.wfdb_adapter import WFDB_CATALOG
from t21_engine.beats.rpeak import detect_r_peaks
from t21_engine.features.hrv import frequency_domain_hrv, rr_intervals_ms, time_domain_hrv
from t21_engine.types import BeatSeries

SCHEMA_VERSION = "fantasia-short-window-hrv-lfhf/1.0"
CATALOG_CASE_ID = "wfdb:fantasia-f1o01"
DEFAULT_RECORD = "f1o01"
ROLE_TAG = "PROXY_HRV_AGE_STABILITY"
HYPOTHESIS_ID = "HYP-03"
# Engineering window lengths only — not clinical ultra-short / 5-min protocol cutoffs.
DEFAULT_ULTRA_SHORT_SECONDS = (20.0, 30.0)
TASK_FORCE_LFHF_MIN_SECONDS = 180.0
METRIC_NAMES = ("rr_mean_ms", "rmssd_ms", "sdnn_ms")


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
        "lf_hf_primary": False,
        "neg_control_qa": True,
        "thresholds": {
            "ultra_short_window_seconds": "PI_TO_DEFINE",
            "reference_window_seconds": "PI_TO_DEFINE",
            "task_force_lfhf_min_seconds": TASK_FORCE_LFHF_MIN_SECONDS,
            "note": "Window cutoffs for clinical transfer stay PI_TO_DEFINE; LF/HF never primary.",
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
            "lf_hf_primary_endpoint",
            "resting_hrv_to_peri_op_biomarker",
            "pooled_instability_score",
            "RQ004_as_FACT",
        ],
    }


def _failure(reason: str, record: str) -> dict[str, Any]:
    payload = _base_meta()
    payload.update(
        {
            "status": "FAIL",
            "failure_reason_code": reason,
            "records": [{"record": record, "status": "FAIL", "failure_reason_code": reason}],
            "fact": None,
            "interpretation": None,
            "hypothesis": _hypothesis(),
        }
    )
    return payload


def _hypothesis() -> dict[str, Any]:
    return {
        "id": HYPOTHESIS_ID,
        "status": "HYPOTHESIS",
        "human_review_required": True,
        "rq004_status": "HYPOTHESIS",
        "rq004_note": (
            "Resting HRV PROXY → peri-op DS remains a gap (RQ-004); do not promote to FACT."
        ),
        "statement": (
            "Ultra-short vs longer Fantasia windows can expose LF/HF instability consistent "
            "with Task Force / methods constraints — PROXY methods stress only, not a "
            "peri-op biomarker claim."
        ),
    }


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


def _slice_beats(beats: BeatSeries, start_s: float, end_s: float) -> BeatSeries:
    mask = (beats.times_s >= start_s) & (beats.times_s < end_s)
    return BeatSeries(
        indices=beats.indices[mask],
        times_s=beats.times_s[mask],
        confidence=beats.confidence,
        kind=beats.kind,
    )


def run_fantasia_short_window_hrv_lfhf(
    sample_root: str | Path | None = None,
    *,
    record: str = DEFAULT_RECORD,
    ultra_short_seconds: tuple[float, ...] = DEFAULT_ULTRA_SHORT_SECONDS,
    engineering_probe_lfhf: bool = True,
) -> dict[str, Any]:
    """FACT/INTERPRETATION/HYPOTHESIS scaffold for short-window HRV LF/HF negative control."""
    metadata = WFDB_CATALOG[CATALOG_CASE_ID]
    if not metadata.public_bench_enabled:
        return _failure("DATASET_NOT_PROMOTED", record)
    root = Path(sample_root).resolve() if sample_root is not None else _default_sample_root()
    if root is None or not root.is_dir() or not (root / f"{record}.hea").is_file():
        return _failure("MISSING_SAMPLE", record)
    provenance_failure = _verify_fixture(root)
    if provenance_failure is not None:
        return _failure(provenance_failure, record)
    try:
        import wfdb

        waveform = wfdb.rdrecord(str(root / record))
        fs = float(waveform.fs)
        matrix = np.asarray(waveform.p_signal, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[1] < 1 or not np.isfinite(matrix).all() or fs <= 0:
            raise ValueError("invalid waveform")
        beats = detect_r_peaks(matrix[:, 0], fs)
        rr = rr_intervals_ms(beats)
        duration_s = float(matrix.shape[0] / fs)
    except (ImportError, OSError, RuntimeError, TypeError, ValueError):
        return _failure("WFDB_LOAD_FAILURE", record)
    if rr.size < 12 or beats.times_s.size < 13:
        return _failure("INSUFFICIENT_RR_INTERVALS", record)

    window_facts: list[dict[str, Any]] = []
    for length in ultra_short_seconds:
        if length <= 0 or length > duration_s:
            continue
        sliced = _slice_beats(beats, 0.0, float(length))
        window_rr = rr_intervals_ms(sliced)
        if window_rr.size < 4:
            window_facts.append(
                {
                    "window_seconds": float(length),
                    "status": "FAIL",
                    "failure_reason_code": "INSUFFICIENT_RR_INTERVALS",
                    "rr_interval_count": int(window_rr.size),
                }
            )
            continue
        td = time_domain_hrv(window_rr)
        lfhf, lfhf_note = frequency_domain_hrv(
            sliced, minimum_window_seconds=TASK_FORCE_LFHF_MIN_SECONDS
        )
        window_facts.append(
            {
                "window_seconds": float(length),
                "status": "PASS",
                "failure_reason_code": None,
                "rr_interval_count": int(window_rr.size),
                "time_domain_hrv": {name: td[name] for name in METRIC_NAMES},
                "lf_hf_task_force_gate": {
                    "minimum_window_seconds": TASK_FORCE_LFHF_MIN_SECONDS,
                    "lf_power": lfhf["lf_power"],
                    "hf_power": lfhf["hf_power"],
                    "lf_hf_ratio": lfhf["lf_hf_ratio"],
                    "withheld": lfhf["lf_hf_ratio"] is None,
                    "note": lfhf_note,
                    "primary": False,
                },
            }
        )

    full_td = time_domain_hrv(rr)
    full_lfhf, full_note = frequency_domain_hrv(
        beats, minimum_window_seconds=TASK_FORCE_LFHF_MIN_SECONDS
    )
    fact = {
        "layer": "FACT",
        "record": record,
        "sample_rate_hz": fs,
        "record_duration_seconds": duration_s,
        "rr_interval_count": int(rr.size),
        "time_domain_hrv_full": {name: full_td[name] for name in METRIC_NAMES},
        "lf_hf_task_force_gate_full": {
            "minimum_window_seconds": TASK_FORCE_LFHF_MIN_SECONDS,
            "lf_power": full_lfhf["lf_power"],
            "hf_power": full_lfhf["hf_power"],
            "lf_hf_ratio": full_lfhf["lf_hf_ratio"],
            "withheld": full_lfhf["lf_hf_ratio"] is None,
            "note": full_note,
            "primary": False,
        },
        "ultra_short_windows": window_facts,
        "reference_5min_window": {
            "status": "UNAVAILABLE" if duration_s < 300.0 else "AVAILABLE",
            "reason": "PI_TO_DEFINE" if duration_s < 300.0 else None,
            "note": (
                "Task Force ~5-min reference not present on this local PROXY fixture "
                "duration; clinical protocol length remains PI_TO_DEFINE."
                if duration_s < 300.0
                else "Full record meets or exceeds 300s engineering length."
            ),
        },
    }

    # Engineering probe: force short-window LF/HF with lowered gate to illustrate instability.
    interpretation: dict[str, Any]
    if not engineering_probe_lfhf:
        interpretation = {
            "layer": "INTERPRETATION",
            "status": "UNAVAILABLE",
            "reason": "PI_TO_DEFINE",
            "engineering_probe_only": False,
            "lf_hf_primary": False,
            "neg_control_qa": True,
            "note": "Short-window LF/HF probe skipped; Task Force withhold remains FACT.",
        }
    else:
        probe_ratios: list[float | None] = []
        probe_rows: list[dict[str, Any]] = []
        for length in ultra_short_seconds:
            if length <= 0 or length > duration_s:
                continue
            sliced = _slice_beats(beats, 0.0, float(length))
            # Lowered gate is engineering-only — never a clinical primary endpoint.
            metrics, note = frequency_domain_hrv(sliced, minimum_window_seconds=float(length))
            ratio = metrics["lf_hf_ratio"]
            probe_ratios.append(ratio if isinstance(ratio, (int, float)) else None)
            probe_rows.append(
                {
                    "window_seconds": float(length),
                    "lf_hf_ratio": ratio,
                    "lf_power": metrics["lf_power"],
                    "hf_power": metrics["hf_power"],
                    "note": note,
                }
            )
        valid = [float(v) for v in probe_ratios if v is not None and np.isfinite(v)]
        if len(valid) >= 2 and max(valid) > 1e-12:
            rel_spread = (max(valid) - min(valid)) / max(valid)
        else:
            rel_spread = None
        interpretation = {
            "layer": "INTERPRETATION",
            "status": "PASS",
            "reason": None,
            "engineering_probe_only": True,
            "lf_hf_primary": False,
            "neg_control_qa": True,
            "clinical_cutoff": "PI_TO_DEFINE",
            "probe_lf_hf_by_window": probe_rows,
            "probe_lf_hf_relative_spread": rel_spread,
            "note": (
                "Lowered-gate LF/HF probe illustrates short-window instability risk; "
                "LF/HF remains non-primary and RQ-004 stays HYPOTHESIS."
            ),
        }

    payload = _base_meta()
    payload.update(
        {
            "status": "PASS",
            "failure_reason_code": None,
            "records": [{"record": record, "status": "PASS", "failure_reason_code": None}],
            "fact": fact,
            "interpretation": interpretation,
            "hypothesis": _hypothesis(),
        }
    )
    return payload


__all__ = ["run_fantasia_short_window_hrv_lfhf"]
