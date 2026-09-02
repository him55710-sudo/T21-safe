"""Optional versioned statistical model interface.

The deterministic index remains available when no fitted model is registered.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from t21_engine.types import FeatureSet


class ResearchModel(Protocol):
    def predict_score(self, features: FeatureSet) -> float: ...


@dataclass(frozen=True, slots=True)
class ModelMetadata:
    model_version: str
    feature_schema_version: str
    population_validated_on: str
    calibrated_probability: bool = False
