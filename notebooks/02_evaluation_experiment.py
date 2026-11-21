"""Notebook 02 - the headline evaluation experiment.

Runs the multi-seed audit (a reduced seed set so the notebook finishes
quickly) and prints the aggregated reversal table. The full 20-seed
run behind results/ is: python -m rul_audit evaluate --out results
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rul_audit.evaluate import headline_numbers, run_evaluation
from rul_audit.report import render_evaluation_summary


def main():
    evaluation = run_evaluation(seeds=(101, 102, 103, 104, 105))
    headline = headline_numbers(evaluation)
    print(render_evaluation_summary(evaluation, headline))
    return 0


if __name__ == "__main__":
    sys.exit(main())
