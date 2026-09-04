"""CODEX-129: fail-closed meeting one-pager link pins for hospital demo docs."""

from __future__ import annotations

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
FOUNDER_DOCS = REPOSITORY_ROOT / "docs" / "founder"
MEETING_ONEPAGER_POINTER = "MEETING_ONEPAGER_PROXY_v0.1_KR.md"

REQUIRED_LINKING_DOCS = (
    "HOSPITAL_DEMO_RUNBOOK_KR.md",
    "HOSPITAL_DEMO_ONBOARDING_KR.md",
    "EXPORT_MANIFEST_PHI_FALSE_KR.md",
)


def test_hospital_demo_docs_link_to_meeting_onepager() -> None:
    for filename in REQUIRED_LINKING_DOCS:
        path = FOUNDER_DOCS / filename
        assert path.is_file(), f"required founder doc missing: {path}"

        contents = path.read_text(encoding="utf-8")
        assert MEETING_ONEPAGER_POINTER in contents, (
            f"{path}: missing pointer to {MEETING_ONEPAGER_POINTER}"
        )
