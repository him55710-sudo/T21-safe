from __future__ import annotations

import numpy as np
import pytest
from t21_engine.evaluation.splits import patient_level_split
from t21_engine.evaluation.training import train_logistic_demo


def test_patient_level_split_is_deterministic_and_disjoint() -> None:
    patient_ids = ["p1", "p1", "p2", "p3", "p4", "p4", "p5", "p6"]

    first = patient_level_split(patient_ids, seed=42)
    second = patient_level_split(patient_ids, seed=42)

    assert first == second
    train = set(first["train"])
    validation = set(first["validation"])
    test = set(first["test"])
    assert train.isdisjoint(validation)
    assert train.isdisjoint(test)
    assert validation.isdisjoint(test)
    assert train | validation | test == set(patient_ids)


@pytest.mark.parametrize(
    ("train_fraction", "validation_fraction"),
    [(0.0, 0.2), (1.0, 0.2), (0.6, 0.0), (0.8, 0.2)],
)
def test_patient_level_split_rejects_invalid_fractions(
    train_fraction: float, validation_fraction: float
) -> None:
    with pytest.raises(ValueError):
        patient_level_split(
            ["p1", "p2", "p3"],
            train_fraction=train_fraction,
            validation_fraction=validation_fraction,
        )


def test_training_rejects_non_finite_features_before_fitting() -> None:
    features = np.asarray([[1.0], [np.nan], [3.0]], dtype=np.float64)
    labels = np.asarray([0, 1, 0], dtype=np.int64)

    with pytest.raises(ValueError, match="imputation pipeline"):
        train_logistic_demo(
            features,
            labels,
            ["p1", "p2", "p3"],
            feature_names=["feature"],
            dataset_version="synthetic-test-v1",
            dataset_checksum="0" * 64,
        )
