"""Command line entry point: ``skillcheck PATH [PATH ...]``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from skillcheck.checks import check_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skillcheck",
        description=(
            "Check Claude Code skill folders and subagent files for problems "
            "that stop them from loading."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="a skill folder, a SKILL.md file, or a subagent .md file",
    )
    parser.add_argument(
        "--skills-dir",
        action="append",
        type=Path,
        dest="skills_dirs",
        help=(
            "folder to search for skills listed in a subagent's 'skills' field "
            "(repeatable; defaults to .claude/skills and ~/.claude/skills)"
        ),
    )
    args = parser.parse_args(argv)

    failed = False
    for path in args.paths:
        path = path.expanduser()
        findings = check_path(path, args.skills_dirs)
        errors = [f for f in findings if f.level == "error"]
        for finding in findings:
            print(finding)
        if errors:
            failed = True
        else:
            print(f"PASS: {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
