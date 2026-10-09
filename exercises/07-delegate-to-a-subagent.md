# Exercise 7: Delegate to a Read-only Subagent

## Goal

Build a custom subagent that preloads your skill and is truly read-only, then
hand it the review.

## Why a subagent

So far the skill has run inline, in your main conversation. Every file it read
and every search it made stayed in your context. A subagent runs in its own,
isolated context window and returns only its final answer, so your
conversation stays clean.

Two facts about subagents matter for skills:

- **A subagent starts clean.** It does not see your conversation history or
  the skills you already used in the main conversation.
- **The `skills` field preloads skills.** The full content of every skill
  listed there is injected into the subagent's context when it starts, so it
  does not have to discover the skill on its own. The built-in subagents,
  such as Explore and Plan, do not preload skills. Only custom subagents can.

A subagent also gives you what `allowed-tools` could not: its `tools` field is
a strict allowlist. A subagent with only Read, Grep, and Glob cannot edit
files, write files, or run commands.

## What to do

1. Create the personal agents folder:

   ```bash
   mkdir -p ~/.claude/agents
   ```

2. Create `~/.claude/agents/model-eval-reviewer.md` with this content:

   ```markdown
   ---
   name: model-eval-reviewer
   description: Reviews Python model-evaluation code in its own context and
     reports findings without changing files. Use when asked to delegate an
     ML evaluation review, or to have a subagent check how a model's
     metrics, thresholds, or splits were computed.
   tools: Read, Grep, Glob
   model: sonnet
   skills: model-eval-review
   ---
   You are a reviewer for machine-learning evaluation code. Read the files
   you are given and apply the preloaded model-eval-review checklist to
   them. Report your findings in that skill's output format, with the file
   and line for each one. You are read-only: describe fixes, never apply
   them.
   ```

   You can also ask Claude to write the file for you. Either way, it is a
   Markdown file with frontmatter on top and the subagent's system prompt
   below.

3. Check it. `skillcheck` also confirms that the skill it lists exists:

   ```bash
   skillcheck ~/.claude/agents/model-eval-reviewer.md
   ```

4. Claude Code notices new agent files within a few seconds. If
   `~/.claude/agents` did not exist when your session started, restart
   Claude Code. Then delegate the review:

   ```
   Use the model-eval-reviewer subagent to review src/failure_model/evaluate.py
   ```

   You can also type `@` and pick `model-eval-reviewer` from the list.

## What to observe

- Claude hands the task to `model-eval-reviewer`. The subagent reads the file
  in its own context and returns a review in the skill's format, with the
  same checklist, severity order, and verdict as exercise 5.
- Your main conversation shows the request and the returned review. It does
  not show every file read and search the subagent made along the way.
- Test the restriction by asking the subagent itself to make a change:

  ```
  Use the model-eval-reviewer subagent to apply the fixes to src/failure_model/evaluate.py
  ```

  The subagent reports that it cannot, because it has no Edit or Write tool.
  Claude, in your main conversation, may then offer to make the edits itself.
  Decline: the main conversation is not restricted, and the sample must keep
  its mistakes. If the file does get changed, restore it with
  `git checkout -- src/failure_model/evaluate.py`.

## What to look for

- `skills: model-eval-review` is what puts the checklist in the subagent's
  context. Every delegated review applies the same standard, without relying
  on how the request is worded.
- `tools: Read, Grep, Glob` is what makes it read-only, by construction rather
  than by instruction.
- The `skills` field controls what is preloaded, not what is allowed. Without
  it, a subagent that has the Skill tool can still find and load skills while
  it works. To stop a subagent from using skills at all, leave `Skill` out of
  its `tools` list.

## Learning outcome

You can create a custom subagent that preloads a skill, restrict it to
read-only tools, and delegate a review to it. You know when to run a skill
inline and when to hand it to a subagent.
