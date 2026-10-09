# Exercise 2: Create the Skill

## Goal

Write the `model-eval-review` skill from scratch. This is the heart of the
lesson. You define a review standard once, as a single file, and Claude
applies it whenever a request fits.

## The problem it solves

Every ML engineer has seen a model that scored 97% in a notebook and failed in
production. The cause is rarely the model. It is usually the evaluation: a
threshold tuned on the test set, accuracy reported on badly imbalanced data,
no baseline to compare against. These mistakes are easy to make and easy to
miss in review, and explaining them to Claude from scratch on every review is
exactly the repetition a skill removes.

## What to do

1. A skill is a folder that contains a `SKILL.md` file. The folder name must
   match the skill name. Create the folder:

   ```bash
   mkdir -p ~/.claude/skills/model-eval-review
   ```

2. Create `~/.claude/skills/model-eval-review/SKILL.md` with this content:

   ```markdown
   ---
   name: model-eval-review
   description: Reviews Python machine-learning evaluation code for results
     that look better than they are. Use when reviewing how a model is
     evaluated, checking metrics, thresholds, or train/test splits, or when
     the user asks to review ML, scikit-learn, or model-evaluation code.
   ---
   When reviewing model-evaluation code, check for the issues below.
   Report each finding with file and line, severity (High / Medium / Low),
   and a recommended fix.

   ## Evaluation checklist
   1. Test set used for decisions: hyperparameters, the decision threshold,
      or the model choice picked by scoring on the same test set that is
      then reported.
   2. Misleading metrics: accuracy alone on imbalanced classes. Expect
      precision, recall, and F1 for the rare class, or PR-AUC.
   3. No baseline: results not compared with a trivial model, such as one
      that always predicts the majority class.
   4. Unreproducible numbers: no fixed random_state or seed for the split,
      the model, or NumPy.
   5. Evaluating on training data: metrics computed on rows the model was
      trained on.

   ## Output format
   Group findings by severity, highest first. Close with a one-line verdict:
   "Results can be trusted" or "Blockers found: N High-severity issues".
   ```

3. Check the file for structural mistakes before you load it:

   ```bash
   skillcheck ~/.claude/skills/model-eval-review
   ```

   You should see `PASS`. `skillcheck` ships with this project. It catches
   the problems that most often stop a skill from loading, such as a misnamed
   file, a missing field, or a name that does not match its folder.

## What to observe

- The file has two parts. The frontmatter between the two `---` lines holds
  the `name` and `description`. Everything below the second `---` is the
  instruction set Claude follows once the skill is active.
- The `description` is what Claude matches your request against when it
  decides whether to use the skill. It answers two questions: what the skill
  does, and when to use it. Its wording includes the words an engineer would
  actually type, such as *evaluation*, *metrics*, *threshold*, and
  *scikit-learn*.

## What to look for

- Each checklist item names a concrete mistake, not a vague goal. "Accuracy
  alone on imbalanced classes" can be checked line by line. "Make sure the
  evaluation is good" cannot.
- The output format is fixed: severity order, file and line, a fix, and a
  one-line verdict. That is what makes every review look the same, whoever
  asks for it.

## Learning outcome

You can create a skill as a folder plus a `SKILL.md` file. You know that the
`name` identifies it, the `description` decides when it activates, and the
body is the instruction set Claude applies.
