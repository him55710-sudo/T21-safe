"""Optional reproducible generic-model training demo.

This module is not imported by the real-time pipeline. Install the ``training`` extra
to use it. Outputs are generic non-DS research artifacts only.
"""

from __future__ import annotations

import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from t21_engine.evaluation.metrics import binary_metrics
from t21_engine.evaluation.splits import case_level_split
from t21_engine.model_registry import register_research_model


@dataclass(frozen=True, slots=True)
class TrainingConfig:
    seed: int = 20250321
    feature_schema_version: str = "features-v0.1"
    model_version: str = "generic-logistic-demo-v0.1"
    threshold_candidates: tuple[float, ...] = tuple(np.linspace(0.1, 0.9, 17))


def _indices_for_cases(case_ids: np.ndarray, selected: list[str]) -> np.ndarray:
    return np.flatnonzero(np.isin(case_ids, np.asarray(selected, dtype=object)))


def _class_balance(labels: np.ndarray) -> dict[str, int]:
    return {
        "negative": int(np.sum(labels == 0)),
        "positive": int(np.sum(labels == 1)),
    }


def _validation_threshold(
    labels: np.ndarray, probabilities: np.ndarray, candidates: tuple[float, ...]
) -> float:
    best_threshold = 0.5
    best_score = -1.0
    for threshold in candidates:
        predictions = probabilities >= threshold
        positive = labels == 1
        negative = labels == 0
        sensitivity = float(np.mean(predictions[positive])) if positive.any() else 0.0
        specificity = float(np.mean(~predictions[negative])) if negative.any() else 0.0
        youden = sensitivity + specificity - 1.0
        if youden > best_score:
            best_score = youden
            best_threshold = threshold
    return float(best_threshold)


def train_logistic_demo(
    features: np.ndarray,
    labels: np.ndarray,
    case_ids: list[str],
    *,
    feature_names: list[str],
    dataset_version: str,
    dataset_checksum: str,
    output_path: Path | None = None,
    registry_path: Path | None = None,
    config: TrainingConfig | None = None,
) -> dict[str, Any]:
    """Fit and evaluate a small generic demo with strict case-level separation."""
    try:
        import joblib
        import sklearn
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise RuntimeError("install t21-engine[training] to run the training demo") from exc

    resolved = config or TrainingConfig()
    matrix = np.asarray(features, dtype=np.float64)
    truth = np.asarray(labels, dtype=np.int64)
    cases = np.asarray(case_ids, dtype=object)
    if matrix.ndim != 2 or matrix.shape[0] != truth.size or truth.size != cases.size:
        raise ValueError("features, labels, and case_ids must align")
    if matrix.shape[1] != len(feature_names):
        raise ValueError("feature_names must match the feature matrix columns")
    if not dataset_version or not dataset_checksum:
        raise ValueError("dataset version and checksum are required")

    splits = case_level_split(case_ids, seed=resolved.seed)
    indices = {name: _indices_for_cases(cases, selected) for name, selected in splits.items()}
    if any(index.size == 0 for index in indices.values()):
        raise ValueError("at least one case is required in train, validation, and test")
    train_labels = truth[indices["train"]]
    if np.unique(train_labels).size < 2:
        raise ValueError("training split must contain both classes")

    estimator = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    random_state=resolved.seed,
                    class_weight="balanced",
                    max_iter=1000,
                ),
            ),
        ]
    )
    estimator.fit(matrix[indices["train"]], train_labels)
    validation_probabilities = np.asarray(
        estimator.predict_proba(matrix[indices["validation"]])[:, 1], dtype=np.float64
    )
    validation_labels = truth[indices["validation"]]
    calibrator = None
    calibration_method = "NOT_EVALUATED: validation split has only one class"
    if np.unique(validation_labels).size == 2:
        calibrator = LogisticRegression(random_state=resolved.seed, max_iter=1000)
        validation_logits = np.log(
            np.clip(validation_probabilities, 1e-6, 1.0 - 1e-6)
            / np.clip(1.0 - validation_probabilities, 1e-6, 1.0)
        ).reshape(-1, 1)
        calibrator.fit(validation_logits, validation_labels)
        validation_probabilities = np.asarray(
            calibrator.predict_proba(validation_logits)[:, 1], dtype=np.float64
        )
        calibration_method = "sigmoid calibrator fitted on validation split only"
    threshold = _validation_threshold(
        validation_labels, validation_probabilities, resolved.threshold_candidates
    )
    raw_test_probabilities = np.asarray(
        estimator.predict_proba(matrix[indices["test"]])[:, 1], dtype=np.float64
    )
    if calibrator is not None:
        test_logits = np.log(
            np.clip(raw_test_probabilities, 1e-6, 1.0 - 1e-6)
            / np.clip(1.0 - raw_test_probabilities, 1e-6, 1.0)
        ).reshape(-1, 1)
        test_probabilities = np.asarray(
            calibrator.predict_proba(test_logits)[:, 1], dtype=np.float64
        )
    else:
        test_probabilities = raw_test_probabilities
    test_metrics = binary_metrics(
        truth[indices["test"]], test_probabilities * 100.0, threshold=threshold * 100.0
    )
    training_environment = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scikit_learn": sklearn.__version__,
        "joblib": joblib.__version__,
    }
    report: dict[str, Any] = {
        "model_version": resolved.model_version,
        "feature_schema_version": resolved.feature_schema_version,
        "feature_names": feature_names,
        "dataset_version": dataset_version,
        "dataset_checksum": dataset_checksum,
        "deterministic_seed": resolved.seed,
        "split_unit": "case",
        "splits": splits,
        "class_balance": {name: _class_balance(truth[index]) for name, index in indices.items()},
        "threshold_tuned_on": "validation",
        "selected_threshold": threshold,
        "test_metrics": test_metrics,
        "training_environment": training_environment,
        "population": "generic non-DS research data only",
        "ds_validated": False,
        "pediatric_validated": False,
        "calibration": calibration_method,
        "clinical_probability_claimed": False,
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "estimator": estimator,
                "calibrator": calibrator,
                "threshold": threshold,
                "metadata": report,
            },
            output_path,
        )
        if registry_path is not None:
            register_research_model(
                registry_path,
                {
                    "model_id": resolved.model_version,
                    "model_version": resolved.model_version,
                    "type": "logistic_regression_demo",
                    "artifact": str(output_path),
                    "feature_schema_version": resolved.feature_schema_version,
                    "dataset_version": dataset_version,
                    "dataset_checksum": dataset_checksum,
                    "training_environment": training_environment,
                    "clinical_validation": False,
                    "ds_validated": False,
                    "pediatric_validated": False,
                    "calibrated_probability": False,
                    "population_validated_on": "generic non-DS research data only",
                    "status": "research_only",
                },
            )
    elif registry_path is not None:
        raise ValueError("output_path is required when registry_path is provided")
    return report
