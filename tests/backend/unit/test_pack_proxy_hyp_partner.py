"""CODEX-108: PROXY HYP partner pack (docs + JSON/MD only)."""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY_ROOT / "scripts" / "pack_proxy_hyp_partner.sh"


def test_pack_proxy_hyp_script_exists_and_syntax() -> None:
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_mode & 0o111
    completed = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_pack_proxy_hyp_banner_gates() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "METHODS_CRITIQUE" in text or "Auditor DSCS" in text
    assert "PARTIALLY_SUPPORTED" in text or "METHODS_CRITIQUE" in text
    assert "No waveforms" in text or "no waveforms" in text.lower()
    assert "PROXY_HYP_RESULTS_KR.md" in text
    assert "BIDMC" in text
    assert "clinical_validation" in text


def test_pack_proxy_hyp_zip_contents(tmp_path: Path) -> None:
    bench = tmp_path / "bench"
    pack = tmp_path / "pack"
    completed = subprocess.run(
        ["bash", str(SCRIPT), str(bench), str(pack)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={
            **dict(**{k: v for k, v in __import__("os").environ.items()}),
            "PYTHONPATH": str(REPOSITORY_ROOT / "services" / "engine" / "src"),
        },
    )
    assert completed.returncode == 0, completed.stdout + "\n" + completed.stderr
    zip_path = pack / "t21-proxy-hyp-partner-pack.zip"
    assert zip_path.is_file()
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        readme = zf.read("README.md").decode("utf-8")
    assert "README.md" in names
    assert "reports/proxy-hyp-bench-report.json" in names
    assert "reports/proxy-hyp-bench-results.md" in names
    assert "docs/PROXY_HYP_RESULTS_KR.md" in names
    assert "docs/ARTIFACTS_INDEX.md" in names
    assert not any(n.endswith((".dat", ".hea", ".jsonl")) for n in names), names
    assert "PARTIALLY_SUPPORTED" in readme
    assert "METHODS_CRITIQUE" in readme or "Auditor DSCS" in readme
    head = readme.split("## Contents")[0]
    assert "PARTIALLY_SUPPORTED" in head
    assert "BIDMC" in readme
