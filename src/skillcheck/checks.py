"""Structural checks for skill folders and subagent files.

Skill rules follow the Agent Skills specification (https://agentskills.io),
which Claude Code reads. The checks catch the problems that most often stop
a skill or subagent from loading: a misnamed file, a missing or malformed
field, or a name that does not match its folder.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from skillcheck.frontmatter import FrontmatterError, parse

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_LINES = 500
TRIGGER_HINTS = ("use when", "use for", "use this when", "use whenever")


@dataclass(frozen=True)
class Finding:
    """One problem found in a file. Errors fail the check; warnings do not."""

    path: Path
    level: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper()}: {self.path}: {self.message}"


def check_path(path: Path, skills_dirs: list[Path] | None = None) -> list[Finding]:
    """Check a skill folder, a ``SKILL.md`` file, or a subagent ``.md`` file."""
    # Absolute, so "." and ".." have real folder names. Symlinks are kept as
    # they are, because the folder name is what Claude Code sees.
    path = Path(os.path.abspath(path))
    if path.is_dir() and path.name.lower() != "skill.md":
        return check_skill(path / "SKILL.md")
    if not path.exists():
        return [Finding(path, "error", "path does not exist")]
    if path.name.lower() == "skill.md":
        return check_skill(path)
    return check_agent(path, skills_dirs)


def check_skill(path: Path) -> list[Finding]:
    """Check one ``SKILL.md`` file and the folder that holds it."""
    path = Path(os.path.abspath(path))
    folder = path.parent
    # On case-insensitive file systems (macOS, Windows) "SKILL.md" also finds
    # "skill.md", so compare against the name actually stored on disk.
    try:
        actual = _stored_name(path)
    except OSError as exc:
        return [Finding(folder, "error", f"cannot read folder: {_reason(exc)}")]
    if actual is None:
        return [Finding(folder, "error", "folder has no SKILL.md file")]
    if actual != "SKILL.md":
        path = folder / actual
        return [
            Finding(
                path, "error", f"file must be named exactly SKILL.md, not {path.name}"
            )
        ]
    if folder.name == "skills" and folder.parent.name == ".claude":
        return [
            Finding(
                path,
                "error",
                "SKILL.md must sit inside a named folder, not loose in skills/",
            )
        ]

    if path.is_dir():
        return [Finding(path, "error", "expected a file but found a folder")]
    try:
        text = _read(path)
        fields, body = parse(text)
    except (OSError, UnicodeDecodeError, FrontmatterError) as exc:
        return [Finding(path, "error", _describe(exc))]

    findings = _check_name(path, fields)
    name = fields.get("name")
    if isinstance(name, str) and name != folder.name:
        findings.append(
            Finding(
                path,
                "error",
                f"name '{name}' must match the folder name '{folder.name}'",
            )
        )

    findings += _check_description(path, fields, MAX_DESCRIPTION_LENGTH)
    findings += _check_tool_list(path, fields, "allowed-tools")

    if not body.strip():
        findings.append(
            Finding(path, "warning", "no instructions below the frontmatter")
        )
    line_count = len(text.splitlines())
    if line_count > MAX_SKILL_LINES:
        findings.append(
            Finding(
                path,
                "warning",
                f"{line_count} lines; keep SKILL.md under {MAX_SKILL_LINES} and "
                "move detail into references/",
            )
        )
    return findings


def check_agent(path: Path, skills_dirs: list[Path] | None = None) -> list[Finding]:
    """Check one subagent file, such as ``.claude/agents/<name>.md``.

    Each skill listed in the ``skills`` field is looked up in ``skills_dirs``.
    When none are given, the project's ``.claude/skills`` next to the agents
    folder and the personal ``~/.claude/skills`` are searched.
    """
    path = Path(os.path.abspath(path))
    if path.suffix != ".md":
        return [Finding(path, "error", "subagent files must use the .md extension")]
    if path.is_dir():
        return [Finding(path, "error", "expected a file but found a folder")]

    try:
        fields, body = parse(_read(path))
    except (OSError, UnicodeDecodeError, FrontmatterError) as exc:
        return [Finding(path, "error", _describe(exc))]

    findings = _check_name(path, fields)
    findings += _check_description(path, fields, limit=None)
    findings += _check_tool_list(path, fields, "tools")

    skills = _as_list(fields.get("skills"))
    if skills is None:
        findings.append(_list_type_error(path, "skills"))
        skills = []

    search = _unique(skills_dirs if skills_dirs is not None else _default_dirs(path))
    for skill in skills:
        if not NAME_PATTERN.fullmatch(skill):
            findings.append(
                Finding(path, "error", f"skills entry {skill!r} is not a valid name")
            )
        elif not any(_has_skill(folder, skill) for folder in search):
            where = ", ".join(str(folder) for folder in search) or "no folders"
            findings.append(
                Finding(path, "warning", f"skill '{skill}' not found in {where}")
            )

    if not body.strip():
        findings.append(
            Finding(path, "warning", "no system prompt below the frontmatter")
        )
    return findings


def _check_name(path: Path, fields: dict[str, Any]) -> list[Finding]:
    name = fields.get("name")
    if name is None:
        return [Finding(path, "error", "missing required field 'name'")]
    if not isinstance(name, str):
        return [
            Finding(
                path,
                "error",
                f"name {name!r} must be text; put it in quotes if YAML reads it "
                "as a number or true/false",
            )
        ]
    if not NAME_PATTERN.fullmatch(name):
        return [
            Finding(
                path,
                "error",
                f"name {name!r} must use lowercase letters, numbers, "
                "and single hyphens",
            )
        ]
    if len(name) > MAX_NAME_LENGTH:
        return [
            Finding(path, "error", f"name is longer than {MAX_NAME_LENGTH} characters")
        ]
    return []


def _check_description(
    path: Path, fields: dict[str, Any], limit: int | None
) -> list[Finding]:
    description = fields.get("description")
    if description is None:
        return [Finding(path, "error", "missing required field 'description'")]
    if not isinstance(description, str) or not description.strip():
        return [Finding(path, "error", "'description' must be a non-empty string")]
    if limit is not None and len(description) > limit:
        return [
            Finding(
                path,
                "error",
                f"description is {len(description)} characters; the limit is {limit}",
            )
        ]
    when_to_use = fields.get("when_to_use")
    trigger_text = description.lower()
    if isinstance(when_to_use, str):
        trigger_text += " " + when_to_use.lower()
    if not any(hint in trigger_text for hint in TRIGGER_HINTS):
        return [
            Finding(
                path,
                "warning",
                "description does not say when to use it; add a 'Use when ...' "
                "sentence with the words people actually type",
            )
        ]
    return []


def _check_tool_list(path: Path, fields: dict[str, Any], key: str) -> list[Finding]:
    if key in fields and _as_list(fields[key]) is None:
        return [_list_type_error(path, key)]
    return []


def _list_type_error(path: Path, key: str) -> Finding:
    return Finding(path, "error", f"'{key}' must be a comma-separated string or a list")


def _as_list(value: Any) -> list[str] | None:
    """Normalize a comma-separated string or a list of strings.

    Returns ``None`` when the value has the wrong type.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return [item.strip() for item in value]
    return None


def _default_dirs(agent_path: Path) -> list[Path]:
    folders = [Path.home() / ".claude" / "skills"]
    if agent_path.parent.name == "agents":
        folders.insert(0, agent_path.parent.parent / "skills")
    return folders


def _unique(folders: list[Path]) -> list[Path]:
    unique: dict[Path, Path] = {}
    for folder in folders:
        unique.setdefault(folder.resolve(), folder)
    return list(unique.values())


def _has_skill(folder: Path, name: str) -> bool:
    """True if ``folder/name/SKILL.md`` exists with exactly that spelling."""
    try:
        return (
            _stored_name(folder / name) == name
            and _stored_name(folder / name / "SKILL.md") == "SKILL.md"
        )
    except OSError:
        return False


def _stored_name(path: Path) -> str | None:
    """Return the file name as stored on disk, matching case if possible.

    Returns ``None`` when no entry in the folder matches, ignoring case.
    """
    if not path.parent.is_dir():
        return None
    names = [entry.name for entry in path.parent.iterdir()]
    if path.name in names:
        return path.name
    wanted = path.name.lower()
    return next((name for name in names if name.lower() == wanted), None)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _describe(exc: Exception) -> str:
    if isinstance(exc, FrontmatterError):
        return str(exc)
    if isinstance(exc, UnicodeDecodeError):
        return "file is not valid UTF-8 text"
    if isinstance(exc, IsADirectoryError):
        return "expected a file but found a folder"
    return f"cannot read file: {_reason(exc)}"


def _reason(exc: Exception) -> str:
    if isinstance(exc, OSError) and exc.strerror:
        return exc.strerror
    return str(exc)
