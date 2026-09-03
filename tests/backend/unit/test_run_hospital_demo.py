"""CODEX-079: thin checks for scripts/run_hospital_demo.sh."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY_ROOT / "scripts" / "run_hospital_demo.sh"


def test_run_hospital_demo_script_exists_and_executable() -> None:
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_mode & 0o111


def test_run_hospital_demo_bash_syntax() -> None:
    completed = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_run_hospital_demo_banner_mentions_ruo_and_phi_false() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "clinical_validation=false" in text
    assert "PHI" in text or "includes_phi" in text
    assert "t21_engine.demo" in text
    assert "export-manifest/1.0" in text
    assert "VitalDB" in text or "synthetic" in text.lower()
