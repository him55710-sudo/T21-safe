"""Regenerate the visibly synthetic Fantasia-style ECG fixture and manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
FS = 100
SAMPLES = 60 * FS


def main() -> None:
    ecg = np.zeros(SAMPLES, dtype="<i2")
    intervals = (90, 100, 110, 100)
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
    (ROOT / "f1o01.dat").write_bytes(ecg.tobytes())
    names = ("f1o01.dat", "f1o01.hea", "f1o01.synthetic-metadata.json")
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
        "files": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names
        },
    }
    (ROOT / "sha256-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
