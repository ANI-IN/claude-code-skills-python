# Exercise 6: Pre-approve Read-only Tools (Optional)

## Goal

Learn what the `allowed-tools` field does, and just as important, what it
does not do.

## What to do

1. Add `allowed-tools` to the frontmatter of
   `~/.claude/skills/model-eval-review/SKILL.md`. Leave the body unchanged:

   ```markdown
   ---
   name: model-eval-review
   description: Reviews Python machine-learning evaluation code for results
     that look better than they are. Use when reviewing how a model is
     evaluated, checking metrics, thresholds, or train/test splits, or when
     the user asks to review ML, scikit-learn, or model-evaluation code.
   allowed-tools: Read, Grep, Glob
   ---
   ```

2. Check it, then run the review from exercise 5 again:

   ```bash
   skillcheck ~/.claude/skills/model-eval-review
   ```

## What to observe

- While the skill is active, Claude can use Read, Grep, and Glob without
  asking you for permission each time. A review that reads several files
  runs with fewer interruptions.
- `allowed-tools` **pre-approves** the tools it lists. It does **not** block
  the others. Every other tool is still available, and your normal permission
  settings still decide whether Claude must ask before using it.
- So this field makes a review smoother. It does not make a review
  read-only. Exercise 7 shows how to get a guarantee.

## What to look for

- Only the frontmatter changed. The instructions below the second `---` are
  exactly the same.
- Omit `allowed-tools` entirely and the skill pre-approves nothing. Claude
  uses your normal permission settings for every tool.

## Learning outcome

You know that `allowed-tools` pre-approves the tools a skill needs so it runs
without repeated prompts, and that it is not a restriction.
