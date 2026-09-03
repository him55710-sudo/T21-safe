"""CODEX-113: fail-closed pins for Auditor DUAL-GATE strings in founder docs."""

from __future__ import annotations

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PROXY_KR = REPOSITORY_ROOT / "docs" / "founder" / "PROXY_HYP_RESULTS_KR.md"
ARTIFACTS_INDEX = REPOSITORY_ROOT / "docs" / "benchmarks" / "ARTIFACTS_INDEX.md"

REQUIRED_STRINGS = (
    "PARTIALLY_SUPPORTED",
    "STRETCH",
    "neg-control-QA",
    "do-not-run",
    "clinical_validation",
    "PI_TO_DEFINE",
    "BIDMC",
    "Airway",
    "no FACT",  # may appear as "no clinical FACT" or "clinical FACT 아님"
)


def _assert_required(contents: str, path: Path) -> None:
    lowered = contents
    # Allow Korean "clinical FACT 아님" as equivalent to no FACT
    if "no FACT" not in lowered and "clinical FACT 아님" not in lowered and "no clinical FACT" not in lowered:
        raise AssertionError(f"{path}: missing no-FACT wording")
    for needle in REQUIRED_STRINGS:
        if needle == "no FACT":
            continue
        if needle == "neg-control-QA":
            assert (
                "neg-control-QA" in lowered or "neg-control" in lowered
            ), f"{path}: missing {needle}"
            continue
        if needle == "do-not-run":
            assert (
                "do-not-run" in lowered or "do-not-run" in lowered.lower()
            ), f"{path}: missing do-not-run"
            # also accept Korean 금지 with BIDMC/Airway already required
            continue
        assert needle in lowered, f"{path}: missing required string {needle!r}"


def test_proxy_hyp_results_kr_contains_auditor_dual_gate_strings() -> None:
    assert PROXY_KR.is_file()
    contents = PROXY_KR.read_text(encoding="utf-8")
    _assert_required(contents, PROXY_KR)
    # Near-top: Auditor section before landing SHA
    assert contents.index("Auditor") < contents.index("랜딩 SHA")
    assert contents.index("PARTIALLY_SUPPORTED") < contents.index("랜딩 SHA")


def test_artifacts_index_contains_auditor_dual_gate_strings() -> None:
    assert ARTIFACTS_INDEX.is_file()
    contents = ARTIFACTS_INDEX.read_text(encoding="utf-8")
    _assert_required(contents, ARTIFACTS_INDEX)
    assert "PARTIALLY_SUPPORTED" in contents
    assert "PROXY Analysis Plan" in contents
