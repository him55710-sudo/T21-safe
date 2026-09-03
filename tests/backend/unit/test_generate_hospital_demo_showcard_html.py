"""CODEX-089: thin checks for hospital demo HTML show-card generator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY_ROOT / "scripts" / "generate_hospital_demo_showcard_html.py"


def _load():
    spec = importlib.util.spec_from_file_location("gen_showcard_html", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _report() -> dict:
    return {
        "status": "PASS",
        "path": "Path B",
        "intended_use": "RESEARCH_USE_ONLY",
        "mode": "OBSERVE_ONLY_SHADOW",
        "synthetic_only": True,
        "contains_phi": False,
        "clinical_validation": False,
        "case_id": "synthetic:hospital-stable",
        "duration_seconds": 12.0,
        "seed": 1,
        "alignment_qc": {"status": "PASS", "checked_channels": ["ecg_ii"]},
        "replay_qc": {
            "events_processed": 3,
            "quality_usable": True,
            "baseline_calibrated": True,
            "timestamp_synchronized": True,
        },
        "local_export": {
            "includes_phi": False,
            "includes_waveforms": False,
            "content_scope": "SHADOW_CAPTURE_METADATA_ONLY",
            "jsonl_path": "/tmp/shadow-capture.jsonl",
        },
    }


def test_html_showcard_script_exists() -> None:
    assert SCRIPT.is_file()


def test_html_showcard_fail_closed_on_clinical_true() -> None:
    mod = _load()
    bad = _report()
    bad["clinical_validation"] = True
    with pytest.raises(ValueError, match="clinical_validation=false"):
        mod.render_showcard_html(bad)


def test_html_showcard_writes_browser_document(tmp_path: Path) -> None:
    mod = _load()
    report_path = tmp_path / "hospital-demo-report.json"
    report_path.write_text(json.dumps(_report()), encoding="utf-8")
    out = tmp_path / "showcard.html"
    assert mod.main([str(report_path), "-o", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in text
    assert "clinical_validation" in text
    assert "False" in text or "false" in text
    assert "waveform" not in text.lower() or "No waveforms" in text or "Raw waveforms" in text
    assert "<img" not in text.lower()
    assert "@media print" in text
    assert "Research Use Only" in text
    assert "not a clinical device" in text
    assert "cleared device" not in text.lower()
