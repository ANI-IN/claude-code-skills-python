"""Split a Markdown file into YAML frontmatter and body."""

from __future__ import annotations

from typing import Any

import yaml


class FrontmatterError(ValueError):
    """The file has no frontmatter block, or the block is not valid YAML."""


def parse(text: str) -> tuple[dict[str, Any], str]:
    """Return ``(frontmatter, body)`` for a file that starts with ``---``.

    The frontmatter is the YAML between the opening ``---`` line and the next
    ``---`` line. Everything after the closing line is the body.
    """
    lines = text.removeprefix("\ufeff").splitlines()
    if not lines or lines[0].rstrip() != "---":
        raise FrontmatterError("file must start with a '---' frontmatter line")

    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip() == "---":
            closing = index
            break
    else:
        raise FrontmatterError("frontmatter has no closing '---' line")

    try:
        data = yaml.safe_load("\n".join(lines[1:closing]))
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"frontmatter is not valid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter must be a set of 'key: value' fields")

    body = "\n".join(lines[closing + 1 :])
    return data, body
