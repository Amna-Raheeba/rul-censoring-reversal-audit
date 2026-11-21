"""Reproduction guard: the stored headline must be reproducible.

Runs the real scripts/reproduce_results.py entry point, which re-runs
the evaluation on the stored seed set and compares the headline
against results/evaluation.json within tolerance.
"""

import importlib.util
import os

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts",
                      "reproduce_results.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("reproduce_results",
                                                  SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stored_headline_file_exists_and_is_valid():
    import json
    path = os.path.join(os.path.dirname(__file__), "..", "results",
                        "evaluation.json")
    with open(path) as fh:
        payload = json.load(fh)
    headline = payload["headline"]
    assert 0.0 <= headline["mean_reversal_failure_dependent"] <= 1.0
    assert 0.0 <= headline["mean_reversal_random"] <= 1.0
    assert headline["worst_condition"]["reversal_rate"] >= 0.9


def test_reproduce_within_tolerance():
    module = _load_module()
    assert module.main() == 0
