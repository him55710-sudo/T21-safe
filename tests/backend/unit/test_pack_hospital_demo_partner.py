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
    assert "never copy shadow jsonl" in text.lower()
    assert "includes_waveforms" in text
    assert "clinical_validation" in text
    assert "zipfile" in text
    assert "generate_hospital_demo_showcard_html.py" in text
    assert "showcard.html" in text
    assert "research-node-one-pager.md" in text
    assert "safety-local-first-1p.md" in text
    assert "research-overview-2p.md" in text
    assert (
        'cp docs/founder/MEETING_ONEPAGER_PROXY_v0.1_KR.md "${STAGING}/docs/"'
        in text
    )
