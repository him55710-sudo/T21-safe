"""HYP-01 PROXY: MIT-BIH abs vs relative bradycardia-definition sensitivity scaffold.

PROXY_ECG_BENCHMARK only. clinical_validation=false. Thresholds are PI_TO_DEFINE.
Not DS / peri-op / clinical validation. No pooled instability score.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from t21_engine.adapters.wfdb_adapter import WFDB_CATALOG
from t21_engine.evaluation.mitbih_beat_bench import (
    DEFAULT_RECORD,
    SYNTHETIC_ANNOTATION_SUFFIX,
    _default_sample_root,
    _load_annotations,
)

SCHEMA_VERSION = "mitbih-brady-def-sensitivity/1.0"
CATALOG_CASE_ID = "wfdb:mitdb-100"
ROLE_TAG = "PROXY_ECG_BENCHMARK"
HYPOTHESIS_ID = "HYP-01"


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
        "thresholds": {
            "absolute_hr_bpm": "PI_TO_DEFINE",
            "relative_drop_fraction": "PI_TO_DEFINE",
            "note": "No clinical cutoffs hardcoded; sensitivity waits on PI_TO_DEFINE.",
        },
        "dataset": {
            "catalog_case_id": CATALOG_CASE_ID,
            "dataset_name": metadata.dataset_name,
            "dataset_version": metadata.dataset_version,
            "master_verified_proxy": metadata.public_bench_enabled,
            "usage": "PROXY_FIXTURE_ONLY",
        },
        "prohibited_claims": ["DS", "peri_op", "clinical_bradycardia_cutoff", "pooled_instability_score"],
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
            "hypothesis": {
                "id": HYPOTHESIS_ID,
                "status": "HYPOTHESIS",
                "human_review_required": True,
                "statement": (
                    "Absolute vs relative HR/bradycardia-style definitions may differ in "
                    "sensitivity on MIT-BIH PROXY annotations — not a clinical claim."
                ),
            },
        }
    )
    return payload


def _rr_from_annotations(samples: np.ndarray, fs: float) -> np.ndarray:
    if samples.size < 2 or fs <= 0:
        return np.asarray([], dtype=np.float64)
    ordered = np.sort(samples.astype(np.float64))
    rr_ms = np.diff(ordered) * 1000.0 / fs
    return rr_ms[(rr_ms >= 300.0) & (rr_ms <= 2000.0)]


def run_mitbih_brady_def_sensitivity(
    sample_root: str | Path | None = None,
    *,
    record: str = DEFAULT_RECORD,
    absolute_hr_bpm: float | None = None,
    relative_drop_fraction: float | None = None,
) -> dict[str, Any]:
    """Scaffold FACT/INTERPRETATION/HYPOTHESIS for abs vs rel definition sensitivity.

    Numeric thresholds default to PI_TO_DEFINE (None). Optional probe values may be
    passed for engineering tests only and are never labeled clinical cutoffs.
    """
    metadata = WFDB_CATALOG[CATALOG_CASE_ID]
    if not metadata.public_bench_enabled:
        return _failure("DATASET_NOT_PROMOTED", record)
    root = Path(sample_root).resolve() if sample_root is not None else _default_sample_root()
    if root is None or not root.is_dir():
        return _failure("MISSING_SAMPLE", record)
    record_base = root / record
    if not record_base.with_suffix(".hea").is_file():
        return _failure("MISSING_SAMPLE", record)
    try:
        annotations, annotation_source = _load_annotations(record_base)
    except FileNotFoundError:
        return _failure("MISSING_ANNOTATIONS", record)
    except (ImportError, OSError, TypeError, ValueError):
        return _failure("ANNOTATION_LOAD_FAILURE", record)

    # WFDB header line 1: record nsig fs nsamp ...
    fs = None
    hea = record_base.with_suffix(".hea").read_text(encoding="utf-8", errors="replace")
    first = next((ln.strip() for ln in hea.splitlines() if ln.strip() and not ln.startswith("#")), "")
    parts = first.split()
    if len(parts) >= 3:
        try:
            fs = float(parts[2])
        except ValueError:
            fs = None
    if fs is None or fs <= 0:
        syn = record_base.with_suffix(SYNTHETIC_ANNOTATION_SUFFIX)
        if syn.is_file():
            payload = json.loads(syn.read_text(encoding="utf-8"))
            fs = float(payload.get("sample_rate_hz") or 0.0) or None
    if fs is None or fs <= 0:
        return _failure("INVALID_SAMPLE_RATE", record)

    rr_ms = _rr_from_annotations(annotations, float(fs))
    if rr_ms.size == 0:
        return _failure("INSUFFICIENT_RR_INTERVALS", record)
    hr_bpm = 60000.0 / rr_ms
    fact = {
        "record": record,
        "annotation_source": annotation_source,
        "annotated_beats": int(annotations.size),
        "rr_interval_count": int(rr_ms.size),
        "sample_rate_hz": float(fs),
        "hr_bpm_mean": float(np.mean(hr_bpm)),
        "hr_bpm_min": float(np.min(hr_bpm)),
        "hr_bpm_max": float(np.max(hr_bpm)),
        "layer": "FACT",
    }

    thresholds_ready = absolute_hr_bpm is not None and relative_drop_fraction is not None
    interpretation: dict[str, Any]
    if not thresholds_ready:
        interpretation = {
            "layer": "INTERPRETATION",
            "status": "UNAVAILABLE",
            "reason": "PI_TO_DEFINE",
            "abs_vs_rel_concordance": None,
            "engineering_probe_only": False,
            "note": "Abs/rel sensitivity comparison deferred until PI defines thresholds.",
        }
    else:
        # Engineering probe path only — values are not clinical cutoffs.
        baseline = float(np.median(hr_bpm[: max(1, hr_bpm.size // 3)]))
        abs_flags = hr_bpm < float(absolute_hr_bpm)
        rel_flags = hr_bpm < (baseline * (1.0 - float(relative_drop_fraction)))
        both = int(np.sum(abs_flags & rel_flags))
        abs_only = int(np.sum(abs_flags & ~rel_flags))
        rel_only = int(np.sum(~abs_flags & rel_flags))
        interpretation = {
            "layer": "INTERPRETATION",
            "status": "PASS",
            "reason": None,
            "engineering_probe_only": True,
            "clinical_cutoff": "PI_TO_DEFINE",
            "probe_absolute_hr_bpm": float(absolute_hr_bpm),
            "probe_relative_drop_fraction": float(relative_drop_fraction),
            "baseline_hr_bpm_median_first_third": baseline,
            "abs_positive_intervals": int(np.sum(abs_flags)),
            "rel_positive_intervals": int(np.sum(rel_flags)),
            "abs_and_rel": both,
            "abs_only": abs_only,
            "rel_only": rel_only,
            "abs_vs_rel_concordance": (
                both / max(1, both + abs_only + rel_only)
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
            "hypothesis": {
                "id": HYPOTHESIS_ID,
                "status": "HYPOTHESIS",
                "human_review_required": True,
                "statement": (
                    "Absolute vs relative HR/bradycardia-style definitions may differ in "
                    "sensitivity on MIT-BIH PROXY annotations — not a clinical claim."
                ),
            },
        }
    )
    return payload


__all__ = ["run_mitbih_brady_def_sensitivity"]
