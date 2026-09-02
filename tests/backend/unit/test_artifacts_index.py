from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_INDEX = REPOSITORY_ROOT / "docs" / "benchmarks" / "ARTIFACTS_INDEX.md"


def test_artifacts_index_exists_and_lists_required_sections() -> None:
    contents = ARTIFACTS_INDEX.read_text(encoding="utf-8")

    required_headers = {
        "## DEMO runner",
        "## MIT-BIH beat table",
        "## BIDMC align / respiration",
        "## Fantasia HRV / age-stability PROXY",
        "## Baseline 180 / 300",
        "## SQI missingness",
        "## PUBLIC_DATA_REPORT_V1",
        "## PI pack",
    }

    assert required_headers <= set(contents.splitlines())
