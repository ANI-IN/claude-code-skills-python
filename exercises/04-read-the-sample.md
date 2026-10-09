# Exercise 4: Read the Sample

## Goal

Study the code the skill will review, and decide for yourself whether its
reported accuracy can be trusted.

## The scenario

A team is building a predictive-maintenance model. Each row of the sensor log
is one machine: temperature, vibration, pressure, rotation speed, torque, tool
wear, hours since the last service, and power draw. The label says whether the
machine failed within the next seven days. Failures are rare, about 4% of
machines, and missing one is expensive.

A teammate has written `src/failure_model/evaluate.py`, which trains a random
forest and reports how well it works. It prints a test accuracy of about 0.97.
Before that number goes into a slide, it needs a review.

## What to do

Open `src/failure_model/evaluate.py` and read it closely. Then open
`src/failure_model/data.py` and `src/failure_model/config.py` to see where
the data comes from.

## What to look for

The module contains four deliberate evaluation mistakes. Try to find them
before you read on. Then compare with this list:

1. **The threshold is chosen on the test set.** The loop tries seven
   decision thresholds, scores each one against `y_test`, and keeps the best.
   The accuracy it then reports is measured on the same rows that picked the
   threshold, so it is optimistic. A validation split or cross-validation on
   the training rows should choose the threshold. This matches checklist
   item 1.
2. **Accuracy is the only metric.** With about 4% failures, accuracy is
   dominated by the machines that do not fail. It says nothing about how many
   failures the model catches. This matches checklist item 2.
3. **There is no baseline.** A "model" that always predicts *no failure* is
   right about 96% of the time on this data. Run
   `pytest tests/test_data.py -k no_failure` to see that test. Without that
   comparison, 0.97 sounds impressive when it is barely better than doing
   nothing. Measured with recall, this model catches well under half of the
   machines that actually fail. This matches checklist item 3.
4. **Nothing is seeded.** Neither `train_test_split` nor
   `RandomForestClassifier` has a `random_state`, so the threshold and
   accuracy change from run to run. You may have seen this in exercise 1.
   This matches checklist item 4.

Checklist item 5, evaluating on training data, is not present. The model is
scored on held-out rows. A good review should not invent a finding for it.

## Important: do not fix these issues

These mistakes are planted on purpose. They give the skill something real to
find. Leave the file as it is. `tests/test_teaching_sample.py` fails if they
are fixed. If that happens, restore the file with
`git checkout -- src/failure_model/evaluate.py`.

Notice also that `tests/test_evaluate.py` passes. It checks that the code runs
and returns a threshold and an accuracy. Green tests do not prove that the
reported numbers mean anything, which is why a review standard is worth
having.

## Learning outcome

You can read evaluation code and map specific lines to specific risks, and
you understand why an impressive accuracy on imbalanced data needs a second
look.
