"""Calibration placeholders that never claim unperformed probability calibration."""

from __future__ import annotations


def uncalibrated_index(score: float) -> float:
    """Return a bounded research index, not a clinical probability."""
    return min(100.0, max(0.0, float(score)))
