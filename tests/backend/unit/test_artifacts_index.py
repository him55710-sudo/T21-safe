from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_INDEX = REPOSITORY_ROOT / "docs" / "benchmarks" / "ARTIFACTS_INDEX.md"
PUBLIC_DATA_REPORT = (
    REPOSITORY_ROOT / "docs" / "benchmarks" / "PUBLIC_DATA_REPORT_V1.md"
)


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


def test_public_data_report_freeze_labels_and_boundaries_are_explicit() -> None:
    report = PUBLIC_DATA_REPORT.read_text(encoding="utf-8")
    index = ARTIFACTS_INDEX.read_text(encoding="utf-8")

    for contents in (report, index):
        assert "v1.0-pre-VitalDB" in contents
        assert "2026-09-02 UTC" in contents
        assert "clinical_validation=false" in contents
        assert "VitalDB" in contents
        assert "CapnoBase" in contents
        assert "PulseDB" in contents
        assert "PENDING" in contents
        assert "operational_proxy_ok" in contents

    assert "No DS clinical claims" in index
    assert "DS clinical claims:** none" in report
