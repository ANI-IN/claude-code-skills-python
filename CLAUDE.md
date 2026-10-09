# Project
Predictive-maintenance model. A small Python ML codebase that generates a
sensor log, trains a classifier that predicts machine failures, and reports
how well it works. It is used to practice building Claude Code skills.

# Map
- src/failure_model/config.py      feature names, failure rate, data seed, test fraction
- src/failure_model/data.py        generates the sensor log; about 4% of rows are failures
- src/failure_model/evaluate.py    evaluation module under review (see below)
- src/skillcheck/                  checker for SKILL.md and subagent files
- tests/                           pytest suite
- exercises/                       step-by-step lesson guides

# Commands
- Install:    `pip install -e ".[dev]"` (inside a virtual environment)
- Run tests:  `pytest`
- Lint:       `ruff check .` and `ruff format --check .`
- Type check: `mypy`
- Run sample: `python -m failure_model.evaluate`
- Check files: `skillcheck PATH [PATH ...]`

# Code Style
- PEP 8, 4-space indentation, enforced by Ruff.
- Type hints on every function; mypy runs in strict mode.
- Absolute imports from `failure_model` and `skillcheck`; no wildcard imports.

# Teaching Exercise
`src/failure_model/evaluate.py` is the subject of a review exercise and
contains deliberate evaluation mistakes. Do not modify it unless the user
explicitly asks you to. `tests/test_teaching_sample.py` fails if it changes.
