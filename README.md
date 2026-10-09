# Claude Code Skills: A Python ML Project

A small, hands-on project that teaches how to build and use Claude Code
**skills**. You write a reusable review skill for machine-learning evaluation
code, watch it activate on its own when you ask for a review, and then hand the
same review to a read-only **subagent** that preloads the skill.

It is written for early-career software and AI/ML engineers. The code is small,
but it is organized like a real Python project: a `src/` package layout, type
hints checked by mypy, linting with Ruff, and a pytest suite.

## 1. Project Overview

A skill is a Markdown file that teaches Claude how to handle a task once.
Claude keeps only each skill's name and description in context, and loads the
full instructions when a request matches. If you find yourself explaining the
same thing to Claude again and again, that is a skill waiting to be written.

The use case here is one every ML engineer meets: **a model that looks great
in evaluation and disappoints in production**. The sample code is a
predictive-maintenance model. It reads a sensor log, one row per machine, and
predicts whether the machine will fail in the next seven days. Failures are
rare, about 4% of machines. The evaluation script reports a test accuracy of
about 0.97, and the lesson is about whether that number can be trusted.

You build two things:

- **`model-eval-review`**, a personal skill with a five-point checklist for
  evaluation code: test-set reuse, misleading metrics, missing baselines,
  unreproducible numbers, and scoring on training data.
- **`model-eval-reviewer`**, a custom subagent that preloads the skill and can
  only read files, so the review runs in its own context and cannot change
  anything.

The project ships with:

- The `failure_model` package under `src/`, the code under review.
- `skillcheck`, a small command-line checker for skill folders and subagent
  files, so you can catch structural mistakes before you load them.
- The full lesson in [`docs/skills.docx`](docs/skills.docx): concepts, the
  skills and subagents guide, and the walkthrough.
- Step-by-step exercises under [`exercises/`](exercises/).

## 2. Intentional Flaws

**`src/failure_model/evaluate.py` is flawed on purpose. Do not fix it.** The
flaws give the skill something real to find. The file says so in its
docstring, but it does not list them, so the review has to find them from the
code.

It contains four planted evaluation mistakes:

1. **The decision threshold is chosen on the test set**, and the reported
   accuracy is measured on the same rows.
2. **Accuracy is the only metric**, on data where about 4% of rows are
   failures.
3. **There is no baseline.** A model that always predicts *no failure* scores
   about 0.96 on this data.
4. **Nothing is seeded**, so the threshold and accuracy change between runs.

Try the review in exercise 5 before you compare against this list.

The test suite passes with these flaws in place. `tests/test_evaluate.py` only
checks that the code runs and returns a threshold and an accuracy, which is
part of the lesson: green tests do not prove that reported metrics mean
anything. `tests/test_teaching_sample.py` does the opposite job. It fails if
the planted mistakes are removed, so the lesson cannot be broken by accident.

## 3. Branches

| Branch | Contents |
|---|---|
| `main` | The starting point. No skill or subagent is included. Do the exercises here. |
| `solution/model-eval-review` | The finished result: the skill in `.claude/skills/model-eval-review/` and the subagent in `.claude/agents/model-eval-reviewer.md`, committed at project level. Compare against it after you finish. |

## 4. Prerequisites

- Python 3.10 or newer. Check with `python3 --version`. If your `python3` is
  older, install a newer Python and create the virtual environment with it by
  name, for example `python3.12 -m venv .venv`.
- Git.
- [Claude Code](https://code.claude.com/docs/en/overview) installed, so that
  `claude` is available in your terminal.

## 5. Setup

```bash
git clone https://github.com/ANI-IN/claude-code-skills-python.git
cd claude-code-skills-python

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

This installs the project in editable mode with its runtime dependencies
(NumPy, scikit-learn, PyYAML) and the development tools (pytest, Ruff, mypy).
It also puts the `skillcheck` command on your path.

## 6. Commands

| Task | Command |
|---|---|
| Run the tests | `pytest` |
| Lint | `ruff check .` |
| Check formatting | `ruff format --check .` |
| Type check | `mypy` |
| Run the sample evaluation | `python -m failure_model.evaluate` |
| Check a skill or subagent file | `skillcheck PATH [PATH ...]` |

On `main`, `pytest` reports `42 passed, 3 skipped`. The three skipped tests
check the committed skill and subagent files, which exist only on the solution
branch, where all 45 run and pass.

## 7. Project Structure

```text
claude-code-skills-python/
├── CLAUDE.md                    Project conventions Claude reads every session
├── README.md                    This file
├── pyproject.toml               Package metadata, dependencies, and tool settings
├── .gitignore
├── docs/
│   └── skills.docx              The full lesson: concepts and walkthrough
├── src/
│   ├── failure_model/
│   │   ├── config.py            Feature names, failure rate, seed, test fraction
│   │   ├── data.py              Generates the sensor log (works offline)
│   │   └── evaluate.py          Evaluation with planted mistakes. The skill reviews this
│   └── skillcheck/
│       ├── checks.py            Rules for SKILL.md files and subagent files
│       ├── frontmatter.py       Splits a Markdown file into YAML frontmatter and body
│       └── cli.py               The skillcheck command
├── tests/
│   ├── test_data.py             Sensor log shape, failure rate, and the no-skill baseline
│   ├── test_evaluate.py         Runs the evaluation. Passes despite the flaws
│   ├── test_teaching_sample.py  Fails if the planted mistakes are fixed
│   ├── test_skillcheck.py       Unit tests for the checker
│   └── test_lesson_files.py     Validates the skill and subagent shown in the exercises
└── exercises/
    ├── README.md                Index, key takeaways, troubleshooting
    ├── 01-prerequisites.md
    ├── 02-create-the-skill.md
    ├── 03-load-and-verify.md
    ├── 04-read-the-sample.md
    ├── 05-run-the-review.md
    ├── 06-pre-approve-read-only-tools.md
    └── 07-delegate-to-a-subagent.md
```

## 8. Running the Demos

Start Claude Code from the project root:

```bash
claude
```

Each step maps to an exercise in `exercises/`, where you will find the full
detail.

### Step 1: create and check the skill

Create `~/.claude/skills/model-eval-review/SKILL.md` with the content in
[exercise 2](exercises/02-create-the-skill.md), then check it:

```bash
skillcheck ~/.claude/skills/model-eval-review
```

### Step 2: confirm Claude Code sees it

```text
What skills do you have available?
```

`model-eval-review` should be listed. If `~/.claude/skills` did not exist when
the session started, run `/reload-skills` first. See
[exercise 3](exercises/03-load-and-verify.md).

### Demo A: run the review inline

```text
Review the model evaluation in src/failure_model/evaluate.py
```

Claude matches the request to the skill's description, loads it, and returns
findings grouped by severity, each with a file, line, and fix, and a closing
verdict. See [exercise 5](exercises/05-run-the-review.md).

### Demo B: delegate to a read-only subagent

Create `~/.claude/agents/model-eval-reviewer.md` from
[exercise 7](exercises/07-delegate-to-a-subagent.md), then:

```text
Use the model-eval-reviewer subagent to review src/failure_model/evaluate.py
```

The subagent preloads the skill, reviews the file in its own context with only
Read, Grep, and Glob, and returns the same structured review.

## 9. Exercises

Start with [exercises/README.md](exercises/README.md), then work through the
numbered files in order:

1. Prerequisites.
2. Create the skill.
3. Load and verify.
4. Read the sample.
5. Run the review.
6. Pre-approve read-only tools (optional).
7. Delegate to a read-only subagent.

Each guide states what to do, what to observe, what to look for, and the
learning outcome. Every prompt is quoted exactly so you can copy it.

## 10. Additional Notes

- **Personal or project skill.** The exercises build a personal skill in
  `~/.claude/skills`, which follows you into every project. To share it with a
  team, put it in the repository's `.claude/skills/` folder and commit it, as
  the solution branch does.
- **The description is the trigger.** Claude matches requests against it. If
  a skill does not activate, add the words you would actually type.
- **`allowed-tools` pre-approves; it does not restrict.** It lets a skill use
  the listed tools without asking, and leaves every other tool available. For a
  hard limit, use a subagent's `tools` field.
- **Skills in subagents.** A subagent starts with a fresh context and does not
  see the skills you used in the main conversation. List skills in its
  `skills` field to preload them. Built-in subagents do not preload skills.
- **Progressive disclosure.** Keep `SKILL.md` short, under about 500 lines, and
  move detailed material into `references/` files that Claude reads only when
  needed.
- **Scope.** This is a teaching project, not production software. The sensor
  log is generated, so the project runs offline and every learner sees the same
  data.
