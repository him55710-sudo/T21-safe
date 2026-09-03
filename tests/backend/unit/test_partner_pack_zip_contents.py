"""CODEX-098: partner zip must include showcard.html and available business 1-pagers."""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PACK_SCRIPT = REPOSITORY_ROOT / "scripts" / "pack_hospital_demo_partner.sh"

# Fail-closed: these must exist in-repo and appear in the partner zip docs/.
REQUIRED_BUSINESS_ONE_PAGERS = (
    "docs/business/export-manifest-phi-false-1p.md",
    "docs/business/research-node-one-pager.md",
    "docs/business/research-overview-2p.md",
    "docs/business/safety-local-first-1p.md",
)


def test_required_business_one_pagers_exist_in_repo() -> None:
    missing = [p for p in REQUIRED_BUSINESS_ONE_PAGERS if not (REPOSITORY_ROOT / p).is_file()]
    assert not missing, f"required partner 1-pagers missing from repo: {missing}"


def test_partner_zip_includes_showcard_html_and_business_one_pagers(
    tmp_path: Path,
) -> None:
    demo_dir = tmp_path / "demo"
    pack_dir = tmp_path / "pack"
    demo_dir.mkdir()
    # Minimal demo report + export gates so pack does not need a full replay if we
    # pre-seed; pack will run demo when report missing — prefer full pack path.
    completed = subprocess.run(
        ["bash", str(PACK_SCRIPT), str(demo_dir), str(pack_dir)],
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
    zip_path = pack_dir / "t21-hospital-demo-partner-pack.zip"
    assert zip_path.is_file(), zip_path
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    assert "reports/showcard.html" in names, names
    assert "reports/showcard.md" in names, names
    for rel in REQUIRED_BUSINESS_ONE_PAGERS:
        basename = Path(rel).name
        assert f"docs/{basename}" in names, f"missing {basename} in zip; have={sorted(names)}"
