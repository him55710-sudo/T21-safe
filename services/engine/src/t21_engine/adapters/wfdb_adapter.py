"""Optional WFDB record adapter.

The dependency is imported lazily so the deterministic synthetic/local demo has no
runtime dependency on WFDB or a network connection.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from t21_engine.adapters.base import CaseDescriptor, DataAdapter
from t21_engine.types import SignalBatch, SourceMetadata


@dataclass(frozen=True, slots=True)
class WFDBCatalogMetadata:
    title: str
    available_signals: tuple[str, ...]
    attribution: str
    dataset_name: str = ""
    dataset_version: str = ""
    license_notes: str = ""


WFDB_CATALOG = {
    "wfdb:bidmc01": WFDBCatalogMetadata(
        title="BIDMC PPG and Respiration record bidmc01",
        available_signals=("ECG_II", "PPG", "RESP"),
        attribution=(
            "BIDMC PPG and Respiration Dataset v1.0.0, PhysioNet; "
            "Open Data Commons Attribution License v1.0; DOI 10.13026/C2208R."
        ),
        dataset_name="BIDMC PPG and Respiration Dataset",
        dataset_version="1.0.0",
        license_notes="Open Data Commons Attribution License v1.0; cite DOI 10.13026/C2208R.",
    ),
    "wfdb:mitdb-100": WFDBCatalogMetadata(
        title="MIT-BIH Arrhythmia Database record 100",
        available_signals=("ECG",),
        attribution=(
            "MIT-BIH Arrhythmia Database v1.0.0, PhysioNet; Open Data Commons "
            "Attribution License v1.0; DOI 10.13026/C2F305."
        ),
        dataset_name="MIT-BIH Arrhythmia Database",
        dataset_version="1.0.0",
        license_notes="Open Data Commons Attribution License v1.0; cite DOI 10.13026/C2F305.",
    ),
    "wfdb:ptt-s10-sit": WFDBCatalogMetadata(
        title="Pulse Transit Time PPG record s10_sit",
        available_signals=("ECG_II", "PPG"),
        attribution=(
            "Mehrgardt et al., Pulse Transit Time PPG Dataset v1.1.0, PhysioNet; "
            "DOI 10.13026/g3me-rt62; source release license applies."
        ),
    ),
    "wfdb:mimic4-preview": WFDBCatalogMetadata(
        title="MIMIC-IV Waveform Database preview record 83411188",
        available_signals=("record-dependent",),
        attribution=(
            "Moody et al., MIMIC-IV Waveform Database v0.1.0, PhysioNet; "
            "Open Data Commons Open Database License v1.0; DOI 10.13026/a2mw-f949."
        ),
    ),
}


class WFDBAdapter(DataAdapter):
    def __init__(self, records: dict[str, tuple[str, str | None]] | None = None) -> None:
        self.records = records or {
            "wfdb:bidmc01": ("bidmc01", "bidmc/1.0.0"),
            "wfdb:mitdb-100": ("100", "mitdb/1.0.0"),
            "wfdb:ptt-s10-sit": ("s10_sit", "pulse-transit-time-ppg/1.1.0"),
            "wfdb:mimic4-preview": (
                "83411188",
                "mimic4wdb/0.1.0/waves/p100/p10039708/83411188",
            ),
        }

    async def list_cases(self) -> list[CaseDescriptor]:
        cases: list[CaseDescriptor] = []
        for case_id, (record, _database) in self.records.items():
            metadata = WFDB_CATALOG.get(
                case_id,
                WFDBCatalogMetadata(
                    title=f"WFDB record {record}",
                    available_signals=("record-dependent",),
                    attribution=(
                        "Custom WFDB record; caller must retain the source-specific "
                        "license and citation metadata."
                    ),
                ),
            )
            cases.append(
                CaseDescriptor(
                    case_id=case_id,
                    title=metadata.title,
                    source="PhysioNet/WFDB",
                    data_type="public waveform record",
                    available_signals=metadata.available_signals,
                    is_synthetic=False,
                    ds_status="unknown_or_non_ds",
                    clinical_use_allowed=False,
                    attribution=metadata.attribution,
                )
            )
        return cases

    async def load_case(
        self,
        case_id: str,
        *,
        duration_seconds: float | None = None,
    ) -> SignalBatch:
        if case_id not in self.records:
            raise KeyError(f"unknown WFDB record: {case_id}")
        metadata = WFDB_CATALOG.get(
            case_id,
            WFDBCatalogMetadata(
                title=f"WFDB record {case_id}",
                available_signals=("record-dependent",),
                attribution=(
                    "Custom WFDB record; caller must retain the source-specific license "
                    "and citation metadata."
                ),
            ),
        )
        try:
            import wfdb
        except ImportError as exc:
            raise RuntimeError("WFDB support requires the 'wfdb' optional dependency") from exc

        record_name, database = self.records[case_id]
        source_path = Path(record_name)
        pn_dir = None if source_path.exists() else database
        kwargs: dict[str, Any] = {"pn_dir": pn_dir} if pn_dir else {}
        if duration_seconds is not None:
            header = wfdb.rdheader(record_name, **kwargs)
            kwargs["sampto"] = int(duration_seconds * float(header.fs))
        record = wfdb.rdrecord(record_name, **kwargs)
        fs = float(record.fs)
        matrix = np.asarray(record.p_signal, dtype=np.float64)
        timestamps = np.arange(matrix.shape[0], dtype=np.float64) / fs
        signals: dict[str, np.ndarray[Any, np.dtype[np.float64]]] = {}
        for column, raw_name in enumerate(record.sig_name):
            normalized = str(raw_name).strip().lower().rstrip(",")
            if normalized in {"ii", "mlii", "ecg", "ekg", "ecg_ii"}:
                canonical = "ecg_ii"
            elif normalized == "pleth" or normalized.startswith("ppg"):
                canonical = "ppg"
            elif normalized in {"abp", "art", "bp"}:
                canonical = "abp"
            elif "resp" in normalized:
                canonical = "resp"
            else:
                canonical = None
            if canonical and canonical not in signals:
                signals[canonical] = matrix[:, column]
        if not signals:
            raise ValueError("WFDB record has no supported signal names")
        return SignalBatch(
            timestamps_s=timestamps,
            signals=signals,
            sample_rates_hz={name: fs for name in signals},
            source=SourceMetadata(
                dataset=f"WFDB/{database or 'local'}",
                case_id=case_id,
                is_synthetic=False,
                ds_status="unknown_or_non_ds",
                clinical_use_allowed=False,
                attribution=metadata.attribution,
                data_type="public waveform record",
            ),
            provenance={name: f"raw:wfdb:{record_name}" for name in signals},
        )
