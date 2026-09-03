"""CODEX-104/105: thin checks for scripts/run_proxy_hyp_benches.sh."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY_ROOT / "scripts" / "run_proxy_hyp_benches.sh"


def test_run_proxy_hyp_benches_script_exists_and_executable() -> None:
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_mode & 0o111


def test_run_proxy_hyp_benches_bash_syntax() -> None:
    completed = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_run_proxy_hyp_benches_banner_gates() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "clinical_validation=false" in text
    assert "BIDMC" in text
    assert "proxy_hyp_bench_runner" in text
    assert "HYP-01" in text
    assert "no network" in text.lower() or "network" in text.lower()


def test_run_proxy_hyp_benches_full_local(tmp_path: Path) -> None:
    out = tmp_path / "proxy-out"
    completed = subprocess.run(
        ["bash", str(SCRIPT), str(out)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={
            **dict(**{k: v for k, v in __import__("os").environ.items()}),
            "PYTHONPATH": str(REPOSITORY_ROOT / "services" / "engine" / "src"),
        },
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert (out / "proxy-hyp-bench-report.json").is_file()
    assert (out / "proxy-hyp-bench-results.md").is_file()
