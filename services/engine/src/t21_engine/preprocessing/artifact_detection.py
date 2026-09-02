"""Simple, auditable artifact candidates used by signal quality metrics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from t21_engine.types import FloatArray


@dataclass(frozen=True, slots=True)
class ArtifactSummary:
    missing_fraction: float
    flatline_fraction: float
    clipping_fraction: float
    abrupt_change_fraction: float
    implausible_fraction: float = 0.0


def flatline_fraction(values: FloatArray, *, tolerance: float = 1e-6) -> float:
    samples = np.asarray(values, dtype=np.float64)
    if samples.size < 2:
        return 1.0
    differences = np.diff(samples)
    finite = np.isfinite(differences)
    return 1.0 if not finite.any() else float(np.mean(np.abs(differences[finite]) <= tolerance))


def clipping_fraction(values: FloatArray, *, tolerance_fraction: float = 1e-4) -> float:
    samples = np.asarray(values, dtype=np.float64)
    finite = samples[np.isfinite(samples)]
    if finite.size < 3:
        return 1.0
    span = float(np.ptp(finite))
    if span <= 1e-12:
        return 1.0
    tolerance = span * tolerance_fraction
    at_extreme = (np.abs(finite - finite.min()) <= tolerance) | (
        np.abs(finite - finite.max()) <= tolerance
    )
    return float(np.mean(at_extreme))


def abrupt_change_fraction(values: FloatArray, *, z_threshold: float = 8.0) -> float:
    differences = np.diff(np.asarray(values, dtype=np.float64))
    finite = differences[np.isfinite(differences)]
    if finite.size < 3:
        return 1.0
    median = float(np.median(finite))
    mad = float(np.median(np.abs(finite - median)))
    if mad <= 1e-12:
        return 0.0
    robust_z = np.abs(finite - median) / (1.4826 * mad)
    return float(np.mean(robust_z > z_threshold))


def relative_roughness(values: FloatArray) -> float:
    """Return median adjacent change relative to the robust waveform span."""
    samples = np.asarray(values, dtype=np.float64)
    finite = samples[np.isfinite(samples)]
    if finite.size < 3:
        return 1.0
    span = float(np.percentile(finite, 99) - np.percentile(finite, 1))
    if span <= 1e-12:
        return 1.0
    adjacent = np.diff(samples)
    adjacent = adjacent[np.isfinite(adjacent)]
    if not adjacent.size:
        return 1.0
    return float(np.median(np.abs(adjacent)) / span)


def summarize_artifacts(
    values: FloatArray,
    *,
    plausible_range: tuple[float, float] | None = None,
) -> ArtifactSummary:
    samples = np.asarray(values, dtype=np.float64)
    missing = float(np.mean(~np.isfinite(samples))) if samples.size else 1.0
    implausible = 0.0
    if plausible_range is not None:
        finite = samples[np.isfinite(samples)]
        if finite.size:
            low, high = plausible_range
            implausible = float(np.mean((finite < low) | (finite > high)))
        else:
            implausible = 1.0
    return ArtifactSummary(
        missing_fraction=missing,
        flatline_fraction=flatline_fraction(samples),
        clipping_fraction=clipping_fraction(samples),
        abrupt_change_fraction=abrupt_change_fraction(samples),
        implausible_fraction=implausible,
    )
