"""CODEX-120: fail-closed claim pins for the founder meeting one-pager."""

from __future__ import annotations

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
MEETING_ONEPAGER = (
    REPOSITORY_ROOT / "docs" / "founder" / "MEETING_ONEPAGER_PROXY_v0.1_KR.md"
)

REQUIRED_STRINGS = (
    "PARTIALLY_SUPPORTED",
    "STRETCH",
    "clinical_validation",
    "PI_TO_DEFINE",
    "ECG",
    "SQI",
    "HR-event",
)


def test_meeting_onepager_contains_claim_boundary_strings() -> None:
    assert MEETING_ONEPAGER.is_file()
    contents = MEETING_ONEPAGER.read_text(encoding="utf-8")

    for needle in REQUIRED_STRINGS:
        assert needle in contents, f"{MEETING_ONEPAGER}: missing required string {needle!r}"

    assert "BIDMC" in contents or "do-not-run" in contents, (
        f"{MEETING_ONEPAGER}: missing BIDMC/do-not-run wording"
    )
    assert (
        "no FACT" in contents
        or "no clinical FACT" in contents
        or "clinical FACT 아님" in contents
        or ("FACT" in contents and "금지" in contents)
    ), f"{MEETING_ONEPAGER}: missing no-FACT wording"
