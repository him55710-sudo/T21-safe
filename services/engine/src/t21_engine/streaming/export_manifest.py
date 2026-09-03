"""Local-only manifests for synthetic shadow-capture metadata exports."""

from __future__ import annotations

from t21_engine.types import ExportManifest


def build_export_manifest(
    *,
    export_id: str,
    session_id: str,
    event_ids: tuple[str, ...],
    includes_waveforms: bool = False,
    includes_phi: bool = False,
    is_synthetic: bool = True,
) -> dict[str, object]:
    """Build an observe-only manifest; unsafe export requests fail closed."""
    manifest = ExportManifest(
        export_id=export_id,
        session_id=session_id,
        event_ids=event_ids,
        includes_waveforms=includes_waveforms,
        includes_phi=includes_phi,
        is_synthetic=is_synthetic,
    )
    controls = manifest.controls
    return {
        "schema_version": manifest.schema_version,
        "clinical_validation": manifest.clinical_validation,
        "synthetic_only": manifest.synthetic_only,
        "export_id": manifest.export_id,
        "session_id": manifest.session_id,
        "event_ids": list(manifest.event_ids),
        "storage_scope": manifest.storage_scope,
        "content_scope": manifest.content_scope,
        "mode": manifest.mode,
        "is_synthetic": manifest.is_synthetic,
        "includes_waveforms": manifest.includes_waveforms,
        "includes_phi": manifest.includes_phi,
        "controls": {
            "actuation": controls.actuation,
            "dosing": controls.dosing,
            "closed_loop": controls.closed_loop,
            "drug_advice": controls.drug_advice,
            "emr_write": controls.emr_write,
        },
    }


__all__ = ["build_export_manifest"]
