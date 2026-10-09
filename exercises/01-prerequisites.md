# Exercise 1: Prerequisites

## Goal

Get the project running on your machine so the rest of the walkthrough goes
smoothly.

## What to do

1. Confirm Claude Code is installed. The `claude` command should start an
   interactive session in your terminal.
2. Confirm you have Python 3.10 or newer:

   ```bash
   python3 --version
   ```

3. Clone the project, create a virtual environment, and install it with the
   development tools:

   ```bash
   git clone https://github.com/ANI-IN/claude-code-skills-python.git
   cd claude-code-skills-python

   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate

   pip install -e ".[dev]"
   ```

4. Run the test suite and the sample evaluation:

   ```bash
   pytest
   python -m failure_model.evaluate
   ```

## What to observe

- `pytest` passes. Three tests are reported as skipped. They check the
  finished skill and subagent files, which do not exist on `main` until you
  build them.
- The evaluation prints a decision threshold and a test accuracy, usually
  between 0.95 and 0.98. Remember that number. Exercise 4 asks whether it means
  anything.
- Run the evaluation a second time. The numbers can change. That is a clue
  too.

## Personal Skill

This lesson builds a **personal** skill. It lives in your home directory under
`~/.claude/skills` and is available in every project you open, not just this
one. The project folder is only where you run the review.

## Learning outcome

You have a working Python environment for the project, and you know the
difference between the project you work in and the home-directory folder
where a personal skill is stored.
