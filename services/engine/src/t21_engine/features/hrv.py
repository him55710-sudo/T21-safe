"""Time-domain and optional frequency-domain HRV research features."""

from __future__ import annotations

import math

import numpy as np
from scipy.signal import welch

from t21_engine.types import BeatSeries, FloatArray


def rr_intervals_ms(beats: BeatSeries) -> FloatArray:
    rr = np.diff(beats.times_s) * 1000.0
    return rr[(rr >= 300.0) & (rr <= 2000.0)].astype(np.float64)


def sample_entropy(values: FloatArray, *, dimension: int = 2) -> float | None:
    samples = np.asarray(values, dtype=np.float64)
    samples = samples[np.isfinite(samples)]
    if samples.size < dimension + 3:
        return None
    tolerance = 0.2 * float(np.std(samples))
    if tolerance <= 1e-12:
        return 0.0

    def matches(length: int) -> int:
        count = 0
        for index in range(samples.size - length):
            template = samples[index : index + length]
            candidates = np.lib.stride_tricks.sliding_window_view(samples[index + 1 :], length)
            if candidates.size:
                count += int(np.sum(np.max(np.abs(candidates - template), axis=1) <= tolerance))
        return count

    count_m = matches(dimension)
    count_m_plus = matches(dimension + 1)
    if count_m == 0 or count_m_plus == 0:
        return None
    return float(-math.log(count_m_plus / count_m))


def time_domain_hrv(rr_ms: FloatArray) -> dict[str, float | None]:
    rr = np.asarray(rr_ms, dtype=np.float64)
    rr = rr[np.isfinite(rr)]
    if rr.size < 2:
        return {
            "rr_mean_ms": None,
            "rmssd_ms": None,
            "sdnn_ms": None,
            "poincare_sd1_ms": None,
            "poincare_sd2_ms": None,
            "sample_entropy": None,
        }
    differences = np.diff(rr)
    sdnn = float(np.std(rr, ddof=1)) if rr.size >= 2 else None
    rmssd = float(np.sqrt(np.mean(differences**2))) if differences.size else None
    sd_diff = float(np.std(differences, ddof=1)) if differences.size >= 2 else 0.0
    sd1 = sd_diff / np.sqrt(2.0)
    sd2_term = max(0.0, 2.0 * float(np.var(rr, ddof=1)) - 0.5 * sd_diff**2)
    return {
        "rr_mean_ms": float(np.mean(rr)),
        "rmssd_ms": rmssd,
        "sdnn_ms": sdnn,
        "poincare_sd1_ms": float(sd1),
        "poincare_sd2_ms": float(np.sqrt(sd2_term)),
        "sample_entropy": sample_entropy(rr),
    }


def frequency_domain_hrv(
    beats: BeatSeries,
    *,
    minimum_window_seconds: float = 180.0,
) -> tuple[dict[str, float | None], str | None]:
    if beats.times_s.size < 20 or float(np.ptp(beats.times_s)) < minimum_window_seconds:
        return {"lf_power": None, "hf_power": None, "lf_hf_ratio": None}, (
            "LF/HF requires at least 180 seconds and 20 valid beats; it is optional and "
            "not used by the core index."
        )
    rr_seconds = np.diff(beats.times_s)
    rr_times = beats.times_s[1:]
    valid = (rr_seconds >= 0.3) & (rr_seconds <= 2.0)
    if valid.sum() < 20:
        return {"lf_power": None, "hf_power": None, "lf_hf_ratio": None}, (
            "LF/HF was withheld because too few physiologically plausible RR intervals remained."
        )
    rr_seconds = rr_seconds[valid]
    rr_times = rr_times[valid]
    uniform_times = np.arange(rr_times[0], rr_times[-1], 0.25)
    interpolated = np.interp(uniform_times, rr_times, rr_seconds)
    frequencies, powers = welch(
        interpolated - np.mean(interpolated), fs=4.0, nperseg=min(256, interpolated.size)
    )
    lf_mask = (frequencies >= 0.04) & (frequencies < 0.15)
    hf_mask = (frequencies >= 0.15) & (frequencies <= 0.4)
    lf_power = float(np.trapezoid(powers[lf_mask], frequencies[lf_mask])) if lf_mask.any() else 0.0
    hf_power = float(np.trapezoid(powers[hf_mask], frequencies[hf_mask])) if hf_mask.any() else 0.0
    return (
        {
            "lf_power": lf_power,
            "hf_power": hf_power,
            "lf_hf_ratio": lf_power / hf_power if hf_power > 1e-12 else None,
        },
        "LF/HF is exploratory and may be confounded by respiration; "
        "it is not a core decision feature.",
    )
