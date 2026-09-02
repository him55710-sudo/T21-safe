"""Leakage-resistant patient-level dataset splits."""

from __future__ import annotations

import numpy as np


def patient_level_split(
    patient_ids: list[str],
    *,
    seed: int = 20250321,
    train_fraction: float = 0.6,
    validation_fraction: float = 0.2,
) -> dict[str, list[str]]:
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be between 0 and 1")
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must be between 0 and 1")
    if train_fraction + validation_fraction >= 1.0:
        raise ValueError("train and validation fractions must leave a test partition")
    unique = np.asarray(sorted(set(patient_ids)), dtype=object)
    if unique.size < 3:
        raise ValueError("at least three unique patients are required")
    rng = np.random.default_rng(seed)
    rng.shuffle(unique)
    train_end = int(round(unique.size * train_fraction))
    validation_end = train_end + int(round(unique.size * validation_fraction))
    return {
        "train": unique[:train_end].tolist(),
        "validation": unique[train_end:validation_end].tolist(),
        "test": unique[validation_end:].tolist(),
    }
