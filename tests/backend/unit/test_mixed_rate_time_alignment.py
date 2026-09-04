"""Deterministic pure-Python mixed-rate alignment helpers (plan support).

Supports docs/research/FAULT_INJECTION_MIXED_RATE_PLAN.md.
No production RII/PROXY/threshold changes; no new third-party deps.
"""

from __future__ import annotations

from typing import Sequence


def nearest_previous_sample(
    master_times: Sequence[float],
    secondary_times: Sequence[float],
    secondary_values: Sequence[float],
    *,
    max_skew_s: float | None = None,
) -> list[float | None]:
    """Align secondary values onto master timestamps (nearest previous sample).

    For each master time t, pick the latest secondary sample with time <= t.
    If none exists, or if (t - chosen_time) > max_skew_s when set, return None.
    """
    if len(secondary_times) != len(secondary_values):
        raise ValueError("secondary_times and secondary_values length mismatch")
    if any(secondary_times[i] > secondary_times[i + 1] for i in range(len(secondary_times) - 1)):
        raise ValueError("secondary_times must be non-decreasing")

    out: list[float | None] = []
    j = -1
    n = len(secondary_times)
    for t in master_times:
        while j + 1 < n and secondary_times[j + 1] <= t:
            j += 1
        if j < 0:
            out.append(None)
            continue
        skew = t - secondary_times[j]
        if max_skew_s is not None and skew > max_skew_s:
            out.append(None)
        else:
            out.append(secondary_values[j])
    return out


def test_nearest_previous_aligns_mixed_rate_streams() -> None:
    # Master @ 4 Hz over 1s; secondary @ 1 Hz
    master = [0.00, 0.25, 0.50, 0.75, 1.00]
    secondary_t = [0.0, 1.0]
    secondary_v = [10.0, 20.0]
    aligned = nearest_previous_sample(master, secondary_t, secondary_v)
    assert aligned == [10.0, 10.0, 10.0, 10.0, 20.0]


def test_nearest_previous_respects_max_skew_and_leading_gap() -> None:
    master = [0.0, 0.5, 1.5]
    secondary_t = [0.4, 1.0]
    secondary_v = [1.0, 2.0]
    # Leading master tick has no previous secondary sample
    aligned = nearest_previous_sample(master, secondary_t, secondary_v, max_skew_s=0.2)
    assert aligned[0] is None
    # t=0.5 uses sample at 0.4 (skew 0.1 <= 0.2)
    assert aligned[1] == 1.0
    # t=1.5 uses sample at 1.0 but skew 0.5 > 0.2 -> reject
    assert aligned[2] is None
