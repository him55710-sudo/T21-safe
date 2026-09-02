"""Leakage-resistant case-level dataset splits."""

from __future__ import annotations

import numpy as np


def case_level_split(
    case_ids: list[str],
    *,
    seed: int = 20250321,
    train_fraction: float = 0.6,
    validation_fraction: float = 0.2,
) -> dict[str, list[str]]:
    unique = np.asarray(sorted(set(case_ids)), dtype=object)
    rng = np.random.default_rng(seed)
    rng.shuffle(unique)
    train_end = int(round(unique.size * train_fraction))
    validation_end = train_end + int(round(unique.size * validation_fraction))
    return {
        "train": unique[:train_end].tolist(),
        "validation": unique[train_end:validation_end].tolist(),
        "test": unique[validation_end:].tolist(),
    }
