"""CODEX-054: thin checks for scripts/verify_path_b_mcp.sh."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY_ROOT / "scripts" / "verify_path_b_mcp.sh"


def test_verify_path_b_mcp_script_exists_and_executable() -> None:
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_mode & 0o111


def test_verify_path_b_mcp_bash_syntax() -> None:
    completed = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_verify_path_b_mcp_help_banner_mentions_ruo() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "clinical_validation=false" in text
    assert "Path B" in text or "RUO" in text
    assert "smoke_dual_mcp.py" in text
    assert "generate_mcp_tool_catalog.py" in text
    assert "t21_engine.demo" in text


def test_verify_path_b_mcp_fails_closed_on_tool_catalog_drift() -> None:
    """CODEX-061: deliberate TOOL_CATALOG drift makes git diff --exit-code fail (script step 3)."""
    script = SCRIPT.read_text(encoding="utf-8")
    assert "git diff --exit-code" in script
    assert "docs/mcp/TOOL_CATALOG.md" in script

    catalog = REPOSITORY_ROOT / "docs" / "mcp" / "TOOL_CATALOG.md"
    original = catalog.read_text(encoding="utf-8")
    try:
        catalog.write_text(original + "\n<!-- deliberate-drift CODEX-061 -->\n", encoding="utf-8")
        completed = subprocess.run(
            ["git", "diff", "--exit-code", "--", "docs/mcp/TOOL_CATALOG.md"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode != 0
    finally:
        catalog.write_text(original, encoding="utf-8")
