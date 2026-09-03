"""CODEX-090: thin checks for hospital demo chain script."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY_ROOT / "scripts" / "run_hospital_demo_chain.sh"


def test_chain_script_exists_and_executable() -> None:
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_mode & 0o111


def test_chain_script_bash_syntax() -> None:
    completed = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_chain_script_orders_demo_showcard_pack() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "run_hospital_demo.sh" in text
    assert "generate_hospital_demo_showcard_html.py" in text
    assert "pack_hospital_demo_partner.sh" in text
    assert "clinical_validation=false" in text
    demo_i = text.index("run_hospital_demo.sh")
    html_i = text.index("generate_hospital_demo_showcard_html.py")
    pack_i = text.index("pack_hospital_demo_partner.sh")
    assert demo_i < html_i < pack_i
