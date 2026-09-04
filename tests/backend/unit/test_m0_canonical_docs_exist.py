"""M0 canonical documentation path existence (docs/governance only)."""

from __future__ import annotations

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

# M0-A + M0-B canonical files — pathlib existence only (no content claims).
M0_CANONICAL_DOCS = (
    # M0-A
    "docs/research/SIGNAL_EXTERNAL_VALIDITY_PLAN.md",
    "docs/security/SECURITY_STAGE_MATRIX_D0_D3.md",
    "docs/product/CLINICIAN_COMPREHENSION_PROTOCOL.md",
    "docs/founder/PI_DECISION_PACK_KR.md",
    "docs/governance/RELEASE_TAG_PROCESS.md",
    "docs/model/RII_DISPLAY_HF_OPTIONS.md",
    "docs/governance/TECHNICAL_AND_REPOSITORY_GATES.md",
    ".github/workflows/all-up-required.yml",
    # M0-B
    "docs/business/HOSPITAL_AGGREGATE_FEASIBILITY_QUERY_KR.md",
    "docs/research/SCHEMA_CLOCK_PILOT_ACCEPTANCE.md",
    "docs/governance/DOC_DEDUP_MAP.md",
    "docs/governance/REQUIRED_CI_CHECK_HOWTO.md",
    "docs/governance/FREEZE_DECLARATION_M0.md",
    "docs/research/FIRST_STUDY_PROTOCOL_KR.md",
)


def test_m0_canonical_docs_exist() -> None:
    missing = [
        rel
        for rel in M0_CANONICAL_DOCS
        if not (REPOSITORY_ROOT / rel).is_file()
    ]
    assert not missing, f"missing M0 canonical documentation paths: {missing}"
