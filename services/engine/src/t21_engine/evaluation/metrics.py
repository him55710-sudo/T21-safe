"""Dependency-light binary research metrics with NOT_EVALUATED handling."""

from __future__ import annotations

from typing import Any

import numpy as np


def _rank_auc(labels: np.ndarray, scores: np.ndarray) -> float | None:
    positives = labels == 1
    negatives = labels == 0
    if not positives.any() or not negatives.any():
        return None
    order = np.argsort(scores, kind="stable")
    sorted_scores = scores[order]
    sorted_ranks = np.arange(1, scores.size + 1, dtype=np.float64)
    boundaries = np.flatnonzero(np.diff(sorted_scores) != 0.0) + 1
    starts = np.concatenate((np.asarray([0]), boundaries))
    stops = np.concatenate((boundaries, np.asarray([scores.size])))
    for start, stop in zip(starts, stops, strict=True):
        sorted_ranks[start:stop] = float(np.mean(sorted_ranks[start:stop]))
    ranks = np.empty_like(sorted_ranks)
    ranks[order] = sorted_ranks
    positive_rank_sum = float(ranks[positives].sum())
    return float(
        (positive_rank_sum - positives.sum() * (positives.sum() + 1) / 2.0)
        / (positives.sum() * negatives.sum())
    )


def _average_precision(labels: np.ndarray, scores: np.ndarray) -> float | None:
    positives = int(np.sum(labels == 1))
    if positives == 0:
        return None
    order = np.argsort(-scores, kind="stable")
    ordered_labels = labels[order]
    ordered_scores = scores[order]
    cumulative_true = np.cumsum(ordered_labels == 1)
    cumulative_false = np.cumsum(ordered_labels == 0)
    threshold_ends = np.concatenate(
        (np.flatnonzero(np.diff(ordered_scores) != 0.0), np.asarray([scores.size - 1]))
    )
    true_at_threshold = cumulative_true[threshold_ends]
    false_at_threshold = cumulative_false[threshold_ends]
    precision = true_at_threshold / (true_at_threshold + false_at_threshold)
    recall = true_at_threshold / positives
    recall_increase = np.diff(np.concatenate((np.asarray([0.0]), recall)))
    return float(np.sum(recall_increase * precision))


def binary_metrics(
    labels: np.ndarray,
    scores: np.ndarray,
    *,
    threshold: float = 50.0,
    valid_mask: np.ndarray | None = None,
    observed_hours: float | None = None,
    sqi_failure_mask: np.ndarray | None = None,
    lead_times_seconds: np.ndarray | None = None,
) -> dict[str, Any]:
    raw_truth = np.asarray(labels)
    estimates = np.asarray(scores, dtype=np.float64)
    if raw_truth.ndim != 1 or estimates.ndim != 1:
        return {"status": "NOT_EVALUATED", "reason": "labels and scores must be vectors"}
    if raw_truth.shape != estimates.shape or raw_truth.size == 0:
        return {"status": "NOT_EVALUATED", "reason": "insufficient or misaligned data"}
    if not np.isin(raw_truth, (0, 1)).all():
        return {"status": "NOT_EVALUATED", "reason": "labels must be binary 0/1"}
    truth = raw_truth.astype(np.int64)
    valid = np.ones(truth.shape, dtype=bool)
    if valid_mask is not None:
        valid = np.asarray(valid_mask, dtype=bool)
        if valid.shape != truth.shape:
            return {"status": "NOT_EVALUATED", "reason": "no valid predictions"}
    valid = valid & np.isfinite(estimates)
    if not valid.any():
        return {"status": "NOT_EVALUATED", "reason": "no valid predictions"}
    invalid_rate = 1.0 - float(np.mean(valid))
    truth_valid = truth[valid]
    scores_valid = estimates[valid]
    predictions = scores_valid >= threshold
    tp = int(np.sum(predictions & (truth_valid == 1)))
    tn = int(np.sum(~predictions & (truth_valid == 0)))
    fp = int(np.sum(predictions & (truth_valid == 0)))
    fn = int(np.sum(~predictions & (truth_valid == 1)))

    def divide(numerator: int, denominator: int) -> float | None:
        return numerator / denominator if denominator else None

    calibration_bins: list[dict[str, float | int]] = []
    probabilities = np.clip(scores_valid / 100.0, 0.0, 1.0)
    for lower in np.linspace(0.0, 0.8, 5):
        in_bin = (probabilities >= lower) & (probabilities < lower + 0.2)
        if in_bin.any():
            calibration_bins.append(
                {
                    "mean_index_fraction": float(np.mean(probabilities[in_bin])),
                    "observed_fraction": float(np.mean(truth_valid[in_bin])),
                    "count": int(in_bin.sum()),
                }
            )
    return {
        "status": "EVALUATED",
        "auroc": _rank_auc(truth_valid, scores_valid),
        "auprc": _average_precision(truth_valid, scores_valid),
        "sensitivity": divide(tp, tp + fn),
        "specificity": divide(tn, tn + fp),
        "ppv": divide(tp, tp + fp),
        "npv": divide(tn, tn + fn),
        "false_alarms_per_hour": fp / observed_hours
        if observed_hours and observed_hours > 0
        else None,
        "median_lead_time_seconds": (
            float(np.median(lead_times_seconds))
            if lead_times_seconds is not None and np.asarray(lead_times_seconds).size
            else None
        ),
        "brier_score": float(np.mean((probabilities - truth_valid) ** 2)),
        "calibration_curve": calibration_bins,
        "invalid_prediction_rate": invalid_rate,
        "sqi_failure_rate": (
            float(np.mean(np.asarray(sqi_failure_mask, dtype=bool)))
            if sqi_failure_mask is not None
            else None
        ),
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "limitations": "Index fractions are not calibrated clinical probabilities.",
    }


def bootstrap_confidence_interval(
    labels: np.ndarray,
    scores: np.ndarray,
    *,
    metric: str = "auroc",
    iterations: int = 1000,
    confidence: float = 0.95,
    seed: int = 20250321,
) -> tuple[float, float] | None:
    """Case-independent bootstrap helper; callers must pass one row per case when needed."""
    truth = np.asarray(labels, dtype=np.int64)
    estimates = np.asarray(scores, dtype=np.float64)
    if truth.shape != estimates.shape or truth.size < 2 or iterations <= 0:
        return None
    rng = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(iterations):
        indices = rng.integers(0, truth.size, truth.size)
        if metric == "auroc":
            value = _rank_auc(truth[indices], estimates[indices])
        elif metric == "auprc":
            value = _average_precision(truth[indices], estimates[indices])
        else:
            raise ValueError("metric must be 'auroc' or 'auprc'")
        if value is not None:
            values.append(value)
    if not values:
        return None
    alpha = (1.0 - confidence) / 2.0
    return float(np.quantile(values, alpha)), float(np.quantile(values, 1.0 - alpha))
