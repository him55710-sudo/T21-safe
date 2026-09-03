"""Regenerate the visibly synthetic Fantasia-style ECG fixture matrix and manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
FS = 100
SAMPLES = 60 * FS
RECORDS = {
    "f1o01": (90, 100, 110, 100),
    "synthetic02": (80, 95, 105, 90),
    "synthetic03": (105, 115, 95, 110),
}


def main() -> None:
    names: list[str] = []
    for record, intervals in RECORDS.items():
        ecg = np.zeros(SAMPLES, dtype="<i2")
        peak = 50
        index = 0
        while peak < SAMPLES:
            ecg[peak] = 1000
            if peak > 0:
                ecg[peak - 1] = 250
            if peak + 1 < SAMPLES:
                ecg[peak + 1] = 250
            peak += intervals[index % len(intervals)]
            index += 1
        (ROOT / f"{record}.dat").write_bytes(ecg.tobytes())
        (ROOT / f"{record}.hea").write_text(
            f"{record} 1 {FS} {SAMPLES}\n"
            f"{record}.dat 16 1000(0)/mV 16 0 0 0 0 ECG\n"
            "# Synthetic fixture-equivalent generated for offline CI; "
            "NOT real Fantasia bytes.\n",
            encoding="ascii",
        )
        (ROOT / f"{record}.synthetic-metadata.json").write_text(
            json.dumps(
                {
                    "format": "synthetic_fantasia_metadata_v1",
                    "synthetic": True,
                    "contains_real_fantasia_metadata": False,
                    "age_metadata_available": False,
                    "age_band": "PI_TO_DEFINE",
                    "age_group": "PI_TO_DEFINE",
                    "note": (
                        "Placeholder only; no age was assigned and no age effect "
                        "may be inferred from this synthetic fixture."
                    ),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        names.extend(
            (f"{record}.dat", f"{record}.hea", f"{record}.synthetic-metadata.json")
        )
    manifest = {
        "dataset_name": "Fantasia Database",
        "dataset_version": "1.0.0",
        "license_note": (
            "Synthetic fixture-equivalent only; NOT real Fantasia or PhysioNet bytes. "
            "The public Fantasia dataset is distributed under the Open Data Commons "
            "Attribution License v1.0."
        ),
        "authorization": "operational_proxy_ok",
        "clinical_validation": False,
        "sample_kind": "synthetic_fixture_equivalent",
        "records": list(RECORDS),
        "files": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in names
        },
    }
    (ROOT / "sha256-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
