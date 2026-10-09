# Exercise 5: Run the Review

## Goal

Ask for a review in plain language and watch the skill activate on its own and
apply the checklist.

## What to do

In Claude Code, started from the project root, ask:

```
Review the model evaluation in src/failure_model/evaluate.py
```

## What to observe

- You did not name the skill. Claude matched your words, *review*, *model*,
  and *evaluation*, against the skill's description and chose
  `model-eval-review` itself. The terminal shows the skill loading, for
  example `Skill(model-eval-review)`. Depending on your permission settings,
  Claude Code may ask you to approve it first.
- Once loaded, Claude follows the checklist and groups its findings by
  severity, highest first. Expect it to flag the threshold chosen on the test
  set, the accuracy-only reporting, and the missing baseline, usually as
  High, and the unseeded split and model, usually as Medium. Each finding has
  a file and line and a recommended fix, and the review ends with a one-line
  verdict such as "Blockers found: 3 High-severity issues".
- The exact wording and severities vary between runs, and Claude may add a
  related observation that is not on the checklist, such as a split that is
  not stratified. The structure does not vary.

## What to look for

- Match each finding to the checklist item it came from. That is how you
  confirm the skill applied your standard rather than improvising.
- Check that the review did not report checklist item 5. The model is scored
  on held-out rows, so there is nothing to flag.
- The review reports and explains. It does not change the file. Exercises 6
  and 7 look at how to keep it that way.

## Try a variation

Ask the same thing in different words:

```
Can I trust the accuracy number in evaluate.py?
```

If the skill does not activate for a phrasing you would really use, the
description is missing those words. Add them to the description and try again.
This is the most common way to fix a skill that does not trigger.

## Why this matters

The standard is now defined once. Every engineer who has this skill gets the
same review, in the same format, every time, without anyone having to
remember the checklist.

## Learning outcome

You have seen a skill activate from a natural request, apply a shared
checklist, and produce a consistent, severity-ordered review.
