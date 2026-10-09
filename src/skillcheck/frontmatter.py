"""Split a Markdown file into YAML frontmatter and body."""

from __future__ import annotations

from typing import Any

import yaml


class FrontmatterError(ValueError):
    """The file has no frontmatter block, or the block is not valid YAML."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """A safe YAML loader that rejects a key written twice."""


def _construct_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    seen: set[Any] = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise FrontmatterError(f"frontmatter sets '{key}' more than once")
        seen.add(key)
    return loader.construct_mapping(node, deep=deep)


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


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
        data = yaml.load("\n".join(lines[1:closing]), Loader=_UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"frontmatter is not valid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter must be a set of 'key: value' fields")

    body = "\n".join(lines[closing + 1 :])
    return data, body
