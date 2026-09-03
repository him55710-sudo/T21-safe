from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_dual_mcp_smoke_script() -> None:
    repository_root = Path(__file__).parents[3]
    completed = subprocess.run(
        [sys.executable, "scripts/smoke_dual_mcp.py"],
        text=True,
        capture_output=True,
        cwd=repository_root,
        timeout=30,
        check=True,
    )

    assert completed.stderr == ""
    assert "clinical_validation=false" in completed.stdout
    assert "PASS fantasia-proxy:" in completed.stdout
    assert "PASS research-node:" in completed.stdout
