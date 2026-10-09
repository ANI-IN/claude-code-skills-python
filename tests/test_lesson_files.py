"""Check that the skill and subagent shown in the exercises are valid.

The exercises are the source learners copy from, so a typo there breaks the
lesson. These tests extract each example and run skillcheck on it. On the
solution branch they also check the committed files under .claude/.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from skillcheck import check_agent, check_skill
from skillcheck.frontmatter import parse

ROOT = Path(__file__).resolve().parent.parent
EXERCISES = ROOT / "exercises"
SKILL_NAME = "model-eval-review"
AGENT_NAME = "model-eval-reviewer"


def markdown_block(exercise: str) -> str:
    """Return the first fenced ```markdown block in an exercise, dedented."""
    text = (EXERCISES / exercise).read_text(encoding="utf-8")
    match = re.search(r"^( *)```markdown\n(.*?)^\1```", text, re.DOTALL | re.MULTILINE)
    assert match, f"no markdown block in {exercise}"
    indent = len(match.group(1))
    return "\n".join(line[indent:] for line in match.group(2).splitlines()) + "\n"


@pytest.fixture
def skill_file(tmp_path: Path) -> Path:
    path = tmp_path / "skills" / SKILL_NAME / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(markdown_block("02-create-the-skill.md"), encoding="utf-8")
    return path


def test_exercise_skill_is_valid(skill_file: Path) -> None:
    assert check_skill(skill_file) == []


def test_exercise_06_only_adds_allowed_tools(skill_file: Path) -> None:
    original, _ = parse(skill_file.read_text(encoding="utf-8"))
    updated, _ = parse(markdown_block("06-pre-approve-read-only-tools.md"))
    assert updated.pop("allowed-tools") == "Read, Grep, Glob"
    assert updated == original


def test_exercise_agent_is_valid(skill_file: Path, tmp_path: Path) -> None:
    agent = tmp_path / "agents" / f"{AGENT_NAME}.md"
    agent.parent.mkdir()
    agent.write_text(markdown_block("07-delegate-to-a-subagent.md"), encoding="utf-8")
    assert check_agent(agent, skills_dirs=[skill_file.parent.parent]) == []

    fields, _ = parse(agent.read_text(encoding="utf-8"))
    assert fields["skills"] == SKILL_NAME
    assert fields["tools"] == "Read, Grep, Glob"


COMMITTED_SKILLS = sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
COMMITTED_AGENTS = sorted((ROOT / ".claude" / "agents").glob("*.md"))


@pytest.mark.parametrize("path", COMMITTED_SKILLS, ids=lambda p: p.parent.name)
def test_committed_skill_is_valid(path: Path) -> None:
    assert check_skill(path) == []


@pytest.mark.parametrize("path", COMMITTED_AGENTS, ids=lambda p: p.stem)
def test_committed_agent_is_valid(path: Path) -> None:
    assert check_agent(path, skills_dirs=[ROOT / ".claude" / "skills"]) == []


@pytest.mark.parametrize("path", COMMITTED_SKILLS, ids=lambda p: p.parent.name)
def test_committed_skill_matches_the_exercises(path: Path) -> None:
    committed, committed_body = parse(path.read_text(encoding="utf-8"))
    expected, expected_body = parse(markdown_block("06-pre-approve-read-only-tools.md"))
    _, exercise_body = parse(markdown_block("02-create-the-skill.md"))
    assert committed == expected
    assert committed_body.strip() == exercise_body.strip()
