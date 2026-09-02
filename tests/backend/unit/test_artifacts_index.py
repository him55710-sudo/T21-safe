"""Existence checks for the research artifacts index."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
INDEX = REPO_ROOT / "docs" / "benchmarks" / "RESEARCH_ARTIFACTS_INDEX.md"

REQUIRED_HEADERS = (
    "## DEMO runner",
    "## MIT-BIH beat table",
    "## BIDMC align / respiration",
    "## Baseline 180 / 300",
    "## SQI missingness",
    "## PUBLIC_DATA_REPORT_V1",
    "## PI pack",
)


def test_research_artifacts_index_exists_with_required_sections() -> None:
    assert INDEX.is_file()
    text = INDEX.read_text(encoding="utf-8")
    assert "clinical_validation=false" in text
    assert "PROXY" in text
    for header in REQUIRED_HEADERS:
        assert header in text, f"missing section: {header}"
