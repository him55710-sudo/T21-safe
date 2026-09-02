"""Bounded, timestamp-normalizing multi-signal ring buffer."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from t21_engine.types import FloatArray


@dataclass(frozen=True, slots=True)
class RingBufferSnapshot:
    timestamps_s: FloatArray
    signals: dict[str, FloatArray]
    out_of_order_count: int
    gap_fraction: float


class RingBuffer:
    def __init__(self, capacity_seconds: float, sample_rate_hz: float) -> None:
        if capacity_seconds <= 0 or sample_rate_hz <= 0:
            raise ValueError("capacity_seconds and sample_rate_hz must be positive")
        self.capacity_samples = max(1, int(np.ceil(capacity_seconds * sample_rate_hz)))
        self.sample_rate_hz = sample_rate_hz
        self._timestamps = np.asarray([], dtype=np.float64)
        self._signals: dict[str, FloatArray] = {}
        self.out_of_order_count = 0

    def append(self, timestamps_s: FloatArray, signals: dict[str, FloatArray]) -> None:
        timestamps = np.asarray(timestamps_s, dtype=np.float64)
        if timestamps.ndim != 1:
            raise ValueError("timestamps must be one-dimensional")
        if not timestamps.size:
            return
        for name, values in signals.items():
            if np.asarray(values).shape != timestamps.shape:
                raise ValueError(f"signal {name} does not align with timestamps")
        local_reversals = int(np.count_nonzero(np.diff(timestamps) <= 0.0))
        boundary_reversal = int(
            bool(self._timestamps.size and timestamps[0] <= self._timestamps[-1])
        )
        self.out_of_order_count += local_reversals + boundary_reversal

        previous_size = self._timestamps.size
        combined_timestamps = np.concatenate((self._timestamps, timestamps))
        all_names = set(self._signals) | set(signals)
        combined_signals: dict[str, FloatArray] = {}
        for name in all_names:
            old_values = self._signals.get(name, np.full(previous_size, np.nan, dtype=np.float64))
            new_values = np.asarray(
                signals.get(name, np.full(timestamps.size, np.nan)), dtype=np.float64
            )
            combined_signals[name] = np.concatenate((old_values, new_values))

        order = np.argsort(combined_timestamps, kind="stable")
        ordered_timestamps = combined_timestamps[order]
        ordered_signals = {name: values[order] for name, values in combined_signals.items()}
        _, reverse_unique = np.unique(ordered_timestamps[::-1], return_index=True)
        keep = np.sort(ordered_timestamps.size - 1 - reverse_unique)
        ordered_timestamps = ordered_timestamps[keep]
        ordered_signals = {name: values[keep] for name, values in ordered_signals.items()}
        if ordered_timestamps.size > self.capacity_samples:
            start = ordered_timestamps.size - self.capacity_samples
            ordered_timestamps = ordered_timestamps[start:]
            ordered_signals = {name: values[start:] for name, values in ordered_signals.items()}
        self._timestamps = ordered_timestamps.astype(np.float64)
        self._signals = {
            name: np.asarray(values, dtype=np.float64) for name, values in ordered_signals.items()
        }

    def snapshot(self, window_seconds: float | None = None) -> RingBufferSnapshot:
        if not self._timestamps.size:
            return RingBufferSnapshot(
                np.asarray([], dtype=np.float64), {}, self.out_of_order_count, 1.0
            )
        start = 0
        if window_seconds is not None:
            if window_seconds <= 0:
                raise ValueError("window_seconds must be positive")
            cutoff = self._timestamps[-1] - window_seconds
            start = int(np.searchsorted(self._timestamps, cutoff, side="left"))
        timestamps = self._timestamps[start:].copy()
        signals = {name: values[start:].copy() for name, values in self._signals.items()}
        expected_interval = 1.0 / self.sample_rate_hz
        if timestamps.size < 2:
            gap_fraction = 1.0
        else:
            missing_intervals = np.maximum(0.0, np.diff(timestamps) / expected_interval - 1.0).sum()
            expected_samples = timestamps.size + missing_intervals
            gap_fraction = float(missing_intervals / max(1.0, expected_samples))
        return RingBufferSnapshot(timestamps, signals, self.out_of_order_count, gap_fraction)

    def clear(self) -> None:
        self._timestamps = np.asarray([], dtype=np.float64)
        self._signals.clear()
        self.out_of_order_count = 0

    def __len__(self) -> int:
        return int(self._timestamps.size)
