from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from t21_engine.evaluation.training import train_logistic_demo
from t21_engine.model_registry import load_registry, register_research_model


def _empty_registry(path: Path) -> None:
    path.write_text(
        json.dumps({"schema_version": "1.0", "active_model": None, "models": []}),
        encoding="utf-8",
    )


def test_generic_training_demo_is_reproducible_and_registers_safe_metadata(
    tmp_path: Path,
) -> None:
    case_ids = [f"synthetic-case-{index:02d}" for index in range(30)]
    labels = np.asarray([index % 2 for index in range(30)], dtype=np.int64)
    rng = np.random.default_rng(20250321)
    features = np.column_stack(
        (
            labels + rng.normal(0.0, 0.15, labels.size),
            rng.normal(0.0, 1.0, labels.size),
        )
    ).astype(np.float64)
    artifact_path = tmp_path / "generic-demo.joblib"
    registry_path = tmp_path / "model_registry.yaml"
    _empty_registry(registry_path)

    report = train_logistic_demo(
        features,
        labels,
        case_ids,
        feature_names=["candidate_signal", "noise_control"],
        dataset_version="synthetic-training-fixture-v1",
        dataset_checksum="sha256:" + "a" * 64,
        output_path=artifact_path,
        registry_path=registry_path,
    )
    repeated = train_logistic_demo(
        features,
        labels,
        case_ids,
        feature_names=["candidate_signal", "noise_control"],
        dataset_version="synthetic-training-fixture-v1",
        dataset_checksum="sha256:" + "a" * 64,
    )
    registry = load_registry(registry_path)
    entry = registry["models"][0]

    assert artifact_path.exists()
    assert report["splits"] == repeated["splits"]
    assert report["selected_threshold"] == repeated["selected_threshold"]
    assert set(report["splits"]["train"]).isdisjoint(report["splits"]["validation"])
    assert set(report["splits"]["train"]).isdisjoint(report["splits"]["test"])
    assert set(report["splits"]["validation"]).isdisjoint(report["splits"]["test"])
    assert report["threshold_tuned_on"] == "validation"
    assert report["clinical_probability_claimed"] is False
    assert {"python", "platform", "numpy", "scikit_learn", "joblib"} <= report[
        "training_environment"
    ].keys()
    assert entry["status"] == "research_only"
    assert entry["clinical_validation"] is False
    assert entry["ds_validated"] is False
    assert entry["pediatric_validated"] is False
    assert entry["calibrated_probability"] is False


def test_registry_rejects_calibrated_or_population_claims(tmp_path: Path) -> None:
    registry_path = tmp_path / "model_registry.yaml"
    _empty_registry(registry_path)
    entry = {
        "model_id": "unsafe-demo",
        "model_version": "unsafe-demo-v1",
        "type": "logistic_regression_demo",
        "artifact": "unsafe-demo.joblib",
        "feature_schema_version": "features-v0.1",
        "dataset_version": "synthetic-v1",
        "dataset_checksum": "sha256:" + "b" * 64,
        "training_environment": {"python": "test"},
        "clinical_validation": False,
        "ds_validated": False,
        "pediatric_validated": False,
        "calibrated_probability": True,
        "population_validated_on": "generic non-DS research data only",
        "status": "research_only",
    }

    with pytest.raises(ValueError, match="calibrated-probability"):
        register_research_model(registry_path, entry)

    entry["calibrated_probability"] = False
    entry["population_validated_on"] = "unsupported population claim"
    with pytest.raises(ValueError, match="generic non-DS"):
        register_research_model(registry_path, entry)
