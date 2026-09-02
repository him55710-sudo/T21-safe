from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from t21_engine.demo import main, run_demo


def test_demo_module_is_importable() -> None:
    module = importlib.import_module("t21_engine.demo")

    assert callable(module.main)


def test_demo_module_entrypoint_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "t21_engine.demo", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "--output-dir" in result.stdout
    assert "synthetic Path B / RUO research node demo" in result.stdout


@pytest.mark.asyncio
async def test_demo_happy_path_writes_shadow_jsonl_and_manifest(tmp_path: Path) -> None:
    report = await run_demo(output_dir=tmp_path)

    assert report["status"] == "PASS"
    assert report["clinical_validation"] is False
    assert report["synthetic_only"] is True
    assert report["alignment_qc"]["status"] == "PASS"
    assert report["replay_qc"]["events_processed"] > 0

    output = tmp_path / "shadow-capture.jsonl"
    records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    captures, manifest = records[:-1], records[-1]
    assert captures
    assert all(item["waveform_persistence"] == "NONE" for item in captures)
    assert all(item["session"]["contains_phi"] is False for item in captures)
    assert manifest["event_ids"] == [item["event_id"] for item in captures]
    assert manifest["includes_waveforms"] is False
    assert manifest["includes_phi"] is False


def test_demo_cli_rejects_cloud_output_uri_fail_closed(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--output-dir", "s3://research-node-demo"]) == 2

    failure = json.loads(capsys.readouterr().err)
    assert failure["status"] == "FAIL_CLOSED"
    assert failure["clinical_validation"] is False
    assert "must not use a URI scheme" in failure["error"]
