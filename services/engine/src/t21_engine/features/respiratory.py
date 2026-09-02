"""Optional respiratory trend features."""

from __future__ import annotations

import numpy as np

from t21_engine.features.blood_pressure import slope_per_minute
from t21_engine.types import FloatArray


def extract_respiratory_features(
    timestamps_s: FloatArray,
    signals: dict[str, FloatArray],
) -> dict[str, float | None]:
    output: dict[str, float | None] = {
        "current_spo2_pct": None,
        "spo2_slope_pct_min": None,
        "current_etco2_mm_hg": None,
        "etco2_slope_mm_hg_min": None,
        "respiratory_rate_bpm": None,
    }
    for name, current_key, slope_key in (
        ("spo2_pct", "current_spo2_pct", "spo2_slope_pct_min"),
        ("etco2_mm_hg", "current_etco2_mm_hg", "etco2_slope_mm_hg_min"),
    ):
        values = signals.get(name)
        if values is not None and np.isfinite(values).any():
            output[current_key] = float(np.nanmedian(values[-100:]))
            output[slope_key] = slope_per_minute(timestamps_s, values)
    respiratory = signals.get("resp_bpm")
    if respiratory is not None and np.isfinite(respiratory).any():
        output["respiratory_rate_bpm"] = float(np.nanmedian(respiratory[-100:]))
    return output
