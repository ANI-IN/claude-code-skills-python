# Exercises: Build Your First Claude Code Skill

These exercises turn the lesson in [`docs/skills.docx`](../docs/skills.docx)
into short, hands-on steps. Work through them in order. In about 20 minutes you
will write a reusable review skill for machine-learning evaluation code, load
it into Claude Code, run it against a sample with planted mistakes, and then
hand the same review to a read-only subagent.

## How to use these exercises

1. Work through the files in numerical order, starting with
   `01-prerequisites.md`.
2. Each guide tells you what to do and what the step teaches, and most also
   cover what to observe and what to look for.
3. Run every command and prompt exactly as written. Prompts you type into
   Claude Code are in fenced blocks so you can copy them.
4. When a guide points you at the sample code, read it closely. Its mistakes
   are there to be noticed and understood, not repaired.

## The sample you will review

`src/failure_model/evaluate.py` trains a model that predicts machine failures
and reports a test accuracy of about 0.97. It contains four deliberate
evaluation mistakes. Exercise 4 walks you through them, and exercises 5 and 7
run the review.

## Exercise index

| Step | File | What you build or do |
|------|------|----------------------|
| 1 | `01-prerequisites.md` | Install the project, run the tests and the sample. |
| 2 | `02-create-the-skill.md` | Write the `model-eval-review` skill as a single `SKILL.md`. |
| 3 | `03-load-and-verify.md` | Confirm Claude Code has discovered the skill. |
| 4 | `04-read-the-sample.md` | Study the evaluation code and its planted mistakes. |
| 5 | `05-run-the-review.md` | Ask for a review in plain language and read the findings. |
| 6 | `06-pre-approve-read-only-tools.md` | Optional. See what `allowed-tools` does and does not do. |
| 7 | `07-delegate-to-a-subagent.md` | Build a read-only subagent that preloads the skill, and delegate the review. |

## Key takeaways

- A skill is a folder plus a `SKILL.md` file, with `name` and `description`
  frontmatter on top and instructions below.
- The `description` drives matching. Say what the skill does and when to use
  it, in the words people actually type.
- Skills load on demand, only when a request matches. `CLAUDE.md` loads in
  every conversation.
- `allowed-tools` pre-approves tools while a skill is active. It does not
  block other tools.
- A custom subagent can preload skills with its `skills` field, and its
  `tools` field is a strict allowlist. Together they give you a consistent,
  truly read-only reviewer that runs in its own context.
- Define a standard once, and it applies the same way for everyone who has
  the skill.

## Troubleshooting

| Symptom | Resolution |
|---|---|
| Skill not listed | Run `skillcheck` on the folder. The file must be named exactly `SKILL.md` and sit inside a named folder, not loose in `skills/`. |
| Skill does not activate | The `description` does not overlap with how you phrased the request. Add the words you actually use. |
| Wrong skill activates | Two descriptions are too similar. Make them more distinct. |
| Changes not taking effect | Run `/reload-skills`, or restart Claude Code. A skills folder created after the session started is not watched until you do. |
| Subagent not found | Run `skillcheck` on the agent file. If `~/.claude/agents` did not exist when the session started, restart Claude Code. |
| `test_teaching_sample.py` fails | The sample was changed. Restore it with `git checkout -- src/failure_model/evaluate.py`. |

## Where to go next

- Move the skill into this repository's `.claude/skills/` folder and commit
  it, so everyone who clones the project gets it. The `solution/model-eval-review`
  branch shows the result.
- Keep `SKILL.md` short and move detail into a `references/` folder, such as a
  full guide to choosing metrics for imbalanced data, linked from `SKILL.md`
  so it loads only when needed. This is progressive disclosure.
- Write a second skill for another task you repeat, such as an experiment
  report template, a model card, or a data-quality checklist.
