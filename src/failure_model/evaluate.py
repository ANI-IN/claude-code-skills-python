"""Train the failure model and report how well it works.

Teaching sample for the skill demo. This module contains deliberate
evaluation mistakes for the model-eval-review skill to find. Do not fix it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from failure_model.config import TEST_FRACTION
from failure_model.data import load_sensor_log

THRESHOLDS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)


@dataclass(frozen=True)
class EvaluationResult:
    threshold: float
    accuracy: float


def evaluate(X: NDArray[np.float64], y: NDArray[np.int64]) -> EvaluationResult:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_FRACTION)

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    scores = model.predict_proba(X_test)[:, 1]

    best_threshold, best_accuracy = THRESHOLDS[0], 0.0
    for threshold in THRESHOLDS:
        predictions = (scores >= threshold).astype(np.int64)
        accuracy = float(np.mean(predictions == y_test))
        if accuracy > best_accuracy:
            best_threshold, best_accuracy = threshold, accuracy

    return EvaluationResult(threshold=best_threshold, accuracy=best_accuracy)


def main() -> EvaluationResult:
    X, y = load_sensor_log()
    result = evaluate(X, y)
    print(f"Decision threshold: {result.threshold:.1f}")
    print(f"Test accuracy: {result.accuracy:.3f}")
    return result


if __name__ == "__main__":
    main()
