"""Thin unit tests for MCP tool catalog generator (CODEX-039)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPOSITORY_ROOT / "scripts" / "generate_mcp_tool_catalog.py"
ENGINE_SOURCE = REPOSITORY_ROOT / "services" / "engine" / "src"

FANTASIA_TOOL_NAMES = (
    "list_records",
    "load_sample",
    "run_hrv_proxy_bench",
)
RESEARCH_TOOL_NAMES = (
    "list_demo_presets",
    "list_local_shadow_exports",
    "export_shadow_summary",
    "run_synthetic_demo",
    "run_time_align_qc",
    "run_mitbih_beat_bench",
    "run_bidmc_align_resp_bench",
    "run_sqi_missingness_impact",
    "run_baseline_window_sensitivity",
)


def _load_generator():
    engine_src = str(ENGINE_SOURCE)
    if engine_src not in sys.path:
        sys.path.insert(0, engine_src)
    spec = importlib.util.spec_from_file_location(
        "generate_mcp_tool_catalog", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_render_catalog_includes_both_servers_tools_and_ruo_banner() -> None:
    module = _load_generator()
    markdown = module.render_catalog()

    assert "clinical_validation=false" in markdown
    assert "RUO" in markdown
    assert "Path B" in markdown
    assert "fantasia-proxy" in markdown
    assert "research-node" in markdown
    assert "auto-generated" in markdown.lower() or "auto-generated" in markdown

    for name in FANTASIA_TOOL_NAMES:
        assert name in markdown
    for name in RESEARCH_TOOL_NAMES:
        assert name in markdown


def test_main_writes_catalog_under_docs_mcp(tmp_path: Path, monkeypatch) -> None:
    module = _load_generator()
    out = tmp_path / "TOOL_CATALOG.md"
    monkeypatch.setattr(module, "OUTPUT_PATH", out)

    assert module.main() == 0
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "clinical_validation=false" in text
    assert "list_records" in text
    assert "run_synthetic_demo" in text
    assert "list_demo_presets" in text
