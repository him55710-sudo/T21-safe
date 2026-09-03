"""CODEX-083: thin checks for hospital demo show-card generator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY_ROOT / "scripts" / "generate_hospital_demo_showcard.py"


def _load():
    spec = importlib.util.spec_from_file_location("gen_showcard", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_showcard_script_exists() -> None:
    assert SCRIPT.is_file()


def test_render_showcard_requires_phi_false_gates() -> None:
    mod = _load()
    bad = {
        "status": "PASS",
        "clinical_validation": True,
        "contains_phi": False,
        "synthetic_only": True,
    }
    with pytest.raises(ValueError, match="clinical_validation=false"):
        mod.render_showcard(bad)


def test_render_showcard_happy_path_markdown(tmp_path: Path) -> None:
    mod = _load()
    report = {
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
            "jsonl_path": str(tmp_path / "shadow-capture.jsonl"),
        },
    }
    card = mod.render_showcard(report)
    assert "clinical_validation" in card
    assert "`False`" in card or "`false`" in card.lower()
    assert "PHI-false" in card
    assert "VitalDB" in card
    out = tmp_path / "card.md"
    (tmp_path / "r.json").write_text(json.dumps(report), encoding="utf-8")
    assert mod.main([str(tmp_path / "r.json"), "-o", str(out)]) == 0
    assert out.is_file()
    assert "Show Card" in out.read_text(encoding="utf-8")
