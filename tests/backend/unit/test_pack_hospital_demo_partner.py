"""CODEX-085: thin checks for partner pack script."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY_ROOT / "scripts" / "pack_hospital_demo_partner.sh"


def test_pack_script_exists_and_executable() -> None:
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_mode & 0o111


def test_pack_script_bash_syntax() -> None:
    completed = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_pack_script_excludes_waveforms_and_includes_docs() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "export-manifest-phi-false-1p.md" in text
    assert "never copy shadow JSONL" in text.lower()
    assert "includes_waveforms" in text
    assert "clinical_validation" in text
    assert "zipfile" in text
