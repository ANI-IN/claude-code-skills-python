"""Guard the lesson: fail if the planted mistakes in evaluate.py are fixed.

The review exercises need something real to find. If one of these tests
fails, the sample was changed. Restore it with ``git checkout -- src``.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SAMPLE = Path(__file__).resolve().parent.parent / "src/failure_model/evaluate.py"


@pytest.fixture(scope="module")
def tree() -> ast.Module:
    return ast.parse(SAMPLE.read_text(encoding="utf-8"))


def _calls(tree: ast.Module) -> list[ast.Call]:
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call)]


def _call_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def test_threshold_is_still_chosen_on_the_test_labels(tree: ast.Module) -> None:
    loops = [node for node in ast.walk(tree) if isinstance(node, ast.For)]
    assert loops, "the threshold loop is gone"
    names_in_loops = {
        node.id
        for loop in loops
        for node in ast.walk(loop)
        if isinstance(node, ast.Name)
    }
    assert "y_test" in names_in_loops


def test_accuracy_is_still_the_only_metric() -> None:
    source = SAMPLE.read_text(encoding="utf-8").lower()
    for metric in ("precision", "recall", "f1", "roc_auc", "average_precision"):
        assert metric not in source, f"{metric} was added to the sample"


def test_there_is_still_no_baseline() -> None:
    source = SAMPLE.read_text(encoding="utf-8")
    assert "DummyClassifier" not in source
    assert "baseline" not in source.lower()


def test_split_and_model_are_still_unseeded(tree: ast.Module) -> None:
    for call in _calls(tree):
        if _call_name(call) in {"train_test_split", "RandomForestClassifier"}:
            keywords = {keyword.arg for keyword in call.keywords}
            assert "random_state" not in keywords
