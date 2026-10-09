from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from skillcheck import Finding, check_agent, check_path, check_skill
from skillcheck.cli import main
from skillcheck.frontmatter import FrontmatterError, parse

Capture = pytest.CaptureFixture[str]

GOOD_SKILL = """\
---
name: weekly-report
description: Writes the weekly experiment report. Use when the user asks
  for a weekly report or a summary of this week's training runs.
---
Summarize each run in one line.
"""

GOOD_AGENT = """\
---
name: report-writer
description: Drafts reports in its own context. Use when asked to delegate
  a report.
tools: Read, Grep, Glob
skills: weekly-report
---
You write reports.
"""


def write_skill(base: Path, folder: str, text: str) -> Path:
    path = base / folder / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    return path


def levels(findings: list[Finding]) -> list[str]:
    return [finding.level for finding in findings]


# --- frontmatter ---------------------------------------------------------


def test_parse_splits_fields_and_body() -> None:
    fields, body = parse(GOOD_SKILL)
    assert fields["name"] == "weekly-report"
    assert "training runs" in fields["description"]
    assert body.strip() == "Summarize each run in one line."


@pytest.mark.parametrize(
    "text",
    [
        "no frontmatter here",
        "---\nname: x\n",
        "---\n: : bad yaml [\n---\n",
        "---\n- a\n---\n",
    ],
)
def test_parse_rejects_malformed_frontmatter(text: str) -> None:
    with pytest.raises(FrontmatterError):
        parse(text)


# --- skills --------------------------------------------------------------


def test_valid_skill_has_no_findings(tmp_path: Path) -> None:
    path = write_skill(tmp_path, "weekly-report", GOOD_SKILL)
    assert check_skill(path) == []
    assert check_path(path.parent) == []


def test_folder_without_skill_md(tmp_path: Path) -> None:
    (tmp_path / "empty").mkdir()
    assert levels(check_path(tmp_path / "empty")) == ["error"]


def test_wrong_file_name_case(tmp_path: Path) -> None:
    path = tmp_path / "weekly-report" / "skill.md"
    path.parent.mkdir()
    path.write_text(GOOD_SKILL, encoding="utf-8")
    [finding] = check_path(path)
    assert "exactly SKILL.md" in finding.message


def test_skill_loose_in_skills_root(tmp_path: Path) -> None:
    path = write_skill(tmp_path / ".claude", "skills", GOOD_SKILL)
    [finding] = check_skill(path)
    assert "named folder" in finding.message


def test_name_must_match_folder(tmp_path: Path) -> None:
    path = write_skill(tmp_path, "weekly", GOOD_SKILL)
    [finding] = check_skill(path)
    assert "must match the folder name" in finding.message


@pytest.mark.parametrize("name", ["Weekly-Report", "weekly_report", "-weekly", "a--b"])
def test_invalid_names(tmp_path: Path, name: str) -> None:
    text = GOOD_SKILL.replace("name: weekly-report", f"name: {name}")
    path = write_skill(tmp_path, name, text)
    assert "error" in levels(check_skill(path))


def test_name_too_long(tmp_path: Path) -> None:
    name = "a" * 65
    path = write_skill(tmp_path, name, GOOD_SKILL.replace("weekly-report", name))
    [finding] = check_skill(path)
    assert "longer than 64" in finding.message


def test_missing_name(tmp_path: Path) -> None:
    text = GOOD_SKILL.replace("name: weekly-report\n", "")
    path = write_skill(tmp_path, "weekly-report", text)
    [finding] = check_skill(path)
    assert "'name'" in finding.message


def test_missing_description(tmp_path: Path) -> None:
    text = "---\nname: weekly-report\n---\nBody.\n"
    path = write_skill(tmp_path, "weekly-report", text)
    [finding] = check_skill(path)
    assert "'description'" in finding.message


def test_description_too_long(tmp_path: Path) -> None:
    text = f"---\nname: weekly-report\ndescription: Use when {'x' * 1100}\n---\nBody.\n"
    path = write_skill(tmp_path, "weekly-report", text)
    [finding] = check_skill(path)
    assert "limit is 1024" in finding.message


def test_description_without_trigger_is_a_warning(tmp_path: Path) -> None:
    text = "---\nname: weekly-report\ndescription: Writes reports.\n---\nBody.\n"
    path = write_skill(tmp_path, "weekly-report", text)
    assert levels(check_skill(path)) == ["warning"]


def test_allowed_tools_must_be_string_or_list(tmp_path: Path) -> None:
    text = GOOD_SKILL.replace("---\nSummarize", "allowed-tools: 3\n---\nSummarize")
    path = write_skill(tmp_path, "weekly-report", text)
    [finding] = check_skill(path)
    assert "'allowed-tools'" in finding.message


def test_empty_body_and_long_file_are_warnings(tmp_path: Path) -> None:
    empty = write_skill(tmp_path, "weekly-report", GOOD_SKILL.split("Summarize")[0])
    assert levels(check_skill(empty)) == ["warning"]

    long_text = GOOD_SKILL + "line\n" * 600
    long = write_skill(tmp_path / "other", "weekly-report", long_text)
    [finding] = check_skill(long)
    assert finding.level == "warning" and "references/" in finding.message


# --- subagents -----------------------------------------------------------


def make_project(tmp_path: Path) -> Path:
    claude = tmp_path / ".claude"
    write_skill(claude / "skills", "weekly-report", GOOD_SKILL)
    agent = claude / "agents" / "report-writer.md"
    agent.parent.mkdir(parents=True)
    agent.write_text(GOOD_AGENT, encoding="utf-8")
    return agent


def test_valid_agent_finds_project_skill(tmp_path: Path) -> None:
    agent = make_project(tmp_path)
    assert check_agent(agent) == []
    assert check_path(agent) == []


def test_agent_with_unknown_skill_warns(tmp_path: Path) -> None:
    agent = make_project(tmp_path)
    text = GOOD_AGENT.replace("weekly-report", "missing-skill")
    agent.write_text(text, encoding="utf-8")
    [finding] = check_agent(agent, skills_dirs=[tmp_path / ".claude" / "skills"])
    assert finding.level == "warning" and "missing-skill" in finding.message


def test_agent_skills_as_yaml_list(tmp_path: Path) -> None:
    agent = make_project(tmp_path)
    agent.write_text(
        GOOD_AGENT.replace("skills: weekly-report", "skills:\n  - weekly-report"),
        encoding="utf-8",
    )
    assert check_agent(agent) == []


def test_agent_requires_name_and_description(tmp_path: Path) -> None:
    agent = tmp_path / "bad.md"
    agent.write_text("---\ntools: Read\n---\nPrompt.\n", encoding="utf-8")
    assert levels(check_agent(agent, skills_dirs=[])) == ["error", "error"]


def test_agent_must_be_markdown(tmp_path: Path) -> None:
    agent = tmp_path / "agent.txt"
    agent.write_text(GOOD_AGENT, encoding="utf-8")
    assert levels(check_path(agent)) == ["error"]


# --- command line --------------------------------------------------------


def test_cli_passes_and_fails(tmp_path: Path, capsys: Capture) -> None:
    good = write_skill(tmp_path, "weekly-report", GOOD_SKILL).parent
    assert main([str(good)]) == 0
    assert "PASS" in capsys.readouterr().out

    bad = write_skill(tmp_path, "wrong-folder", GOOD_SKILL).parent
    assert main([str(good), str(bad)]) == 1
    assert "ERROR" in capsys.readouterr().out


def test_cli_reports_missing_path(tmp_path: Path, capsys: Capture) -> None:
    assert main([str(tmp_path / "nope.md")]) == 1
    assert "does not exist" in capsys.readouterr().out


# --- regressions ---------------------------------------------------------


def test_indented_frontmatter_is_rejected(tmp_path: Path) -> None:
    indented = "".join(f"   {line}\n" for line in GOOD_SKILL.splitlines())
    path = write_skill(tmp_path, "weekly-report", indented)
    [finding] = check_skill(path)
    assert "must start with a '---'" in finding.message


def test_byte_order_mark_and_trailing_spaces_are_accepted(tmp_path: Path) -> None:
    text = "﻿" + GOOD_SKILL.replace("---\n", "---  \n")
    path = write_skill(tmp_path, "weekly-report", text)
    assert check_skill(path) == []


def test_lowercase_file_name_is_caught_through_the_folder(tmp_path: Path) -> None:
    path = tmp_path / "weekly-report" / "skill.md"
    path.parent.mkdir()
    path.write_text(GOOD_SKILL, encoding="utf-8")
    [finding] = check_path(path.parent)
    assert "exactly SKILL.md" in finding.message


def test_non_string_description(tmp_path: Path) -> None:
    text = "---\nname: weekly-report\ndescription: 42\n---\nBody.\n"
    path = write_skill(tmp_path, "weekly-report", text)
    [finding] = check_skill(path)
    assert "non-empty string" in finding.message


def test_unreadable_files_give_findings_not_tracebacks(tmp_path: Path) -> None:
    binary = tmp_path / "weekly-report" / "SKILL.md"
    binary.parent.mkdir()
    binary.write_bytes(b"\xff\xfe\x00bad")
    [finding] = check_skill(binary)
    assert "UTF-8" in finding.message

    folder_named_like_a_file = tmp_path / "other" / "agent.md"
    folder_named_like_a_file.mkdir(parents=True)
    [finding] = check_agent(folder_named_like_a_file, skills_dirs=[])
    assert "folder" in finding.message


def test_personal_agent_searches_each_folder_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    agent = tmp_path / ".claude" / "agents" / "report-writer.md"
    agent.parent.mkdir(parents=True)
    agent.write_text(GOOD_AGENT, encoding="utf-8")
    [finding] = check_agent(agent)
    assert finding.message.count(str(Path(".claude") / "skills")) == 1


def test_cli_counts_warnings(tmp_path: Path, capsys: Capture) -> None:
    text = "---\nname: weekly-report\ndescription: Writes reports.\n---\nBody.\n"
    folder = write_skill(tmp_path, "weekly-report", text).parent
    assert main([str(folder)]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == f"PASS: {folder} (1 warning)"


def test_cli_expands_skills_dir(tmp_path: Path, capsys: Capture) -> None:
    agent = make_project(tmp_path)
    assert main([str(agent), "--skills-dir", str(tmp_path / ".claude" / "skills")]) == 0
    assert capsys.readouterr().out.strip() == f"PASS: {agent}"


def test_relative_paths_use_the_real_folder_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = write_skill(tmp_path, "weekly-report", GOOD_SKILL).parent
    monkeypatch.chdir(folder)
    assert check_path(Path(".")) == []
    assert check_path(Path("SKILL.md")) == []
    monkeypatch.chdir(folder / "..")
    assert check_path(Path("weekly-report")) == []


@pytest.mark.skipif(
    sys.platform == "win32" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="needs POSIX permissions and a non-root user",
)
def test_unreadable_folders_give_findings_not_tracebacks(tmp_path: Path) -> None:
    agent = make_project(tmp_path)
    skill_folder = tmp_path / ".claude" / "skills" / "weekly-report"
    skills_root = skill_folder.parent
    skill_folder.chmod(0)
    try:
        [finding] = check_path(skill_folder)
        assert "cannot read folder" in finding.message
    finally:
        skill_folder.chmod(0o755)
    skills_root.chmod(0)
    try:
        [finding] = check_agent(agent, skills_dirs=[skills_root])
        assert finding.level == "warning"
    finally:
        skills_root.chmod(0o755)


def test_duplicate_keys_are_rejected(tmp_path: Path) -> None:
    text = GOOD_SKILL.replace("---\nSummarize", "description: Again.\n---\nSummarize")
    path = write_skill(tmp_path, "weekly-report", text)
    [finding] = check_skill(path)
    assert "more than once" in finding.message


def test_name_that_yaml_reads_as_a_number(tmp_path: Path) -> None:
    text = GOOD_SKILL.replace("name: weekly-report", "name: 123")
    path = write_skill(tmp_path, "123", text)
    [finding] = check_skill(path)
    assert "must be text" in finding.message


def test_when_to_use_counts_as_a_trigger(tmp_path: Path) -> None:
    text = (
        "---\nname: weekly-report\ndescription: Writes reports.\n"
        "when_to_use: Use when the user asks for the weekly report.\n---\nBody.\n"
    )
    path = write_skill(tmp_path, "weekly-report", text)
    assert check_skill(path) == []


def test_skill_named_skills_is_allowed(tmp_path: Path) -> None:
    text = GOOD_SKILL.replace("name: weekly-report", "name: skills")
    path = write_skill(tmp_path / ".claude" / "skills", "skills", text)
    assert check_skill(path) == []


@pytest.mark.parametrize("entry", ["Weekly-Report", "weekly-report/"])
def test_agent_skill_entries_must_be_valid_names(tmp_path: Path, entry: str) -> None:
    agent = make_project(tmp_path)
    agent.write_text(GOOD_AGENT.replace("skills: weekly-report", f"skills: {entry}"))
    [finding] = check_agent(agent, skills_dirs=[tmp_path / ".claude" / "skills"])
    assert finding.level == "error" and "not a valid name" in finding.message


def test_agent_skill_lookup_is_case_sensitive(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    write_skill(skills, "Weekly-Report", GOOD_SKILL)
    agent = tmp_path / "report-writer.md"
    agent.write_text(GOOD_AGENT, encoding="utf-8")
    [finding] = check_agent(agent, skills_dirs=[skills])
    assert finding.level == "warning" and "not found" in finding.message
