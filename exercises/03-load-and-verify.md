# Exercise 3: Load and Verify

## Goal

Confirm that Claude Code has discovered the skill you just wrote.

## What to do

1. Start Claude Code from the project root:

   ```bash
   claude
   ```

   If Claude Code was already running when you created `~/.claude/skills` for
   the first time, run `/reload-skills` or restart it. Claude Code watches
   skill folders that existed when the session started, so edits to an
   existing skill are picked up without a restart.

2. Ask:

   ```
   What skills do you have available?
   ```

## What to observe

- `model-eval-review` appears in the list, with its description.
- Claude keeps only each skill's `name` and `description` in context until a
  request matches. Seeing the skill listed confirms it was discovered, even
  though its full instructions are not loaded yet.

## If the skill does not appear

- Run `skillcheck ~/.claude/skills/model-eval-review` and fix any `ERROR`.
- The file must be named exactly `SKILL.md`, with uppercase "SKILL" and
  lowercase "md", and it must sit inside a named folder rather than loose in
  `skills/`.
- Run `/reload-skills`, or restart Claude Code.

## Learning outcome

You know where Claude Code discovers personal skills, that only the `name` and
`description` are held in context until a request matches, and how to confirm
a skill is registered.
