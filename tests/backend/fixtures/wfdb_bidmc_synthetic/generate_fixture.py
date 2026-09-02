"""Regenerate the visibly synthetic BIDMC-style three-signal fixture."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
FS = 25
SAMPLES = 60 * FS


def main() -> None:
    sample = np.arange(SAMPLES)
    ecg = np.zeros(SAMPLES, dtype=np.int16)
    ppg = np.zeros(SAMPLES, dtype=np.float64)
    for peak in range(FS // 2, SAMPLES, FS):
        ecg[peak] = 1000
        for offset, amplitude in ((3, 200), (4, 600), (5, 900), (6, 600), (7, 200)):
            if peak + offset < SAMPLES:
                ppg[peak + offset] += amplitude
    resp = np.rint(800 * np.sin(2 * np.pi * sample / (5 * FS))).astype(np.int16)
    matrix = np.column_stack((ecg, np.rint(ppg).astype(np.int16), resp))
    with (ROOT / "bidmc01.dat").open("wb") as handle:
        for row in matrix:
            handle.write(struct.pack("<hhh", *(int(value) for value in row)))


if __name__ == "__main__":
    main()
