"""Notebook 01 - demo run.

Runs the audit for a single demo fleet (seed 7) and prints the truth
leaderboard plus every naive leaderboard under censoring. Runnable as
a plain script: python notebooks/01_demo_run.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rul_audit.evaluate import run_single_seed
from rul_audit.report import render_single_seed_report


def main():
    result = run_single_seed(7)
    print(render_single_seed_report(result))
    reversals = [r for r in result["rows"] if r["reversal"]]
    print("Reversals in this fleet: %d of %d conditions"
          % (len(reversals), len(result["rows"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
