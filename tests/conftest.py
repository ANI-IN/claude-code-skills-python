"""Shared fixtures."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

from failure_model.data import load_sensor_log

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def sensor_log() -> tuple[NDArray[np.float64], NDArray[np.int64]]:
    return load_sensor_log()


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT
