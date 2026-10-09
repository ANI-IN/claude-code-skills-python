"""Load the sensor log used to train and evaluate the failure model."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from sklearn.datasets import make_classification

from failure_model.config import DATA_SEED, FAILURE_RATE, FEATURE_NAMES, N_MACHINES


def load_sensor_log(
    n_machines: int = N_MACHINES, seed: int = DATA_SEED
) -> tuple[NDArray[np.float64], NDArray[np.int64]]:
    """Return sensor readings ``X`` and failure labels ``y``.

    The log is generated rather than downloaded, so the project works offline.
    Each row is one machine. ``y`` is 1 when the machine failed within seven
    days of the reading and 0 otherwise. Failures are rare: about
    ``FAILURE_RATE`` of rows are positive.
    """
    X, y = make_classification(
        n_samples=n_machines,
        n_features=len(FEATURE_NAMES),
        n_informative=4,
        n_redundant=2,
        weights=[1.0 - FAILURE_RATE],
        flip_y=0.01,
        class_sep=0.8,
        random_state=seed,
    )
    return X.astype(np.float64), y.astype(np.int64)
