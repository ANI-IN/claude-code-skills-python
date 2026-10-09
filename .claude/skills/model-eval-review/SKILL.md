---
name: model-eval-review
description: Reviews Python machine-learning evaluation code for results
  that look better than they are. Use when reviewing how a model is
  evaluated, checking metrics, thresholds, or train/test splits, or when
  the user asks to review ML, scikit-learn, or model-evaluation code.
allowed-tools: Read, Grep, Glob
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
