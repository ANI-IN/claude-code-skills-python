"""Behavior checks for the evaluation module.

These pass even though evaluate.py contains planted mistakes. Green tests
check that code runs and returns the right shape of answer; they do not
prove the reported numbers are trustworthy.
"""

from __future__ import annotations

import numpy as np
import pytest
from numpy.typing import NDArray

from failure_model.evaluate import THRESHOLDS, EvaluationResult, evaluate, main

SensorLog = tuple[NDArray[np.float64], NDArray[np.int64]]


def test_evaluate_returns_a_result(sensor_log: SensorLog) -> None:
    X, y = sensor_log
    result = evaluate(X, y)
    assert isinstance(result, EvaluationResult)
    assert result.threshold in THRESHOLDS
    assert 0.0 <= result.accuracy <= 1.0


def test_main_prints_threshold_and_accuracy(capsys: pytest.CaptureFixture[str]) -> None:
    result = main()
    output = capsys.readouterr().out
    assert f"Decision threshold: {result.threshold:.1f}" in output
    assert f"Test accuracy: {result.accuracy:.3f}" in output
