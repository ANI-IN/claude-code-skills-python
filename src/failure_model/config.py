"""Shared settings for the failure model."""

FEATURE_NAMES: tuple[str, ...] = (
    "temperature",
    "vibration",
    "pressure",
    "rotation_speed",
    "torque",
    "tool_wear_minutes",
    "hours_since_service",
    "power_draw",
)
"""Sensor readings recorded for each machine, in column order."""

FAILURE_RATE = 0.04
"""Share of machines that fail within the prediction window."""

N_MACHINES = 2000
"""Number of machines in the generated sensor log."""

DATA_SEED = 7
"""Seed for generating the sensor log, so every learner sees the same data."""

TEST_FRACTION = 0.25
"""Share of machines held out for the final test."""
