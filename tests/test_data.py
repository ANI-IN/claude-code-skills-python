from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from failure_model.config import FEATURE_NAMES, N_MACHINES
from failure_model.data import load_sensor_log

SensorLog = tuple[NDArray[np.float64], NDArray[np.int64]]


def test_shape_matches_config(sensor_log: SensorLog) -> None:
    X, y = sensor_log
    assert X.shape == (N_MACHINES, len(FEATURE_NAMES))
    assert y.shape == (N_MACHINES,)


def test_labels_are_binary(sensor_log: SensorLog) -> None:
    _, y = sensor_log
    assert set(np.unique(y)) == {0, 1}


def test_failures_are_rare(sensor_log: SensorLog) -> None:
    _, y = sensor_log
    assert 0.02 < y.mean() < 0.08


def test_same_seed_gives_same_log() -> None:
    X1, y1 = load_sensor_log(n_machines=200, seed=3)
    X2, y2 = load_sensor_log(n_machines=200, seed=3)
    np.testing.assert_array_equal(X1, X2)
    np.testing.assert_array_equal(y1, y2)


def test_predicting_no_failure_scores_high_accuracy(sensor_log: SensorLog) -> None:
    """A model that never predicts a failure still looks accurate.

    This is why accuracy alone says little on imbalanced data.
    """
    _, y = sensor_log
    always_no_failure = np.zeros_like(y)
    assert np.mean(always_no_failure == y) > 0.92
