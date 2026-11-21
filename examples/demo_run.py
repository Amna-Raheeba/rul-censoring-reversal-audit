"""Example: run the audit on one small fleet and print the report."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rul_audit.evaluate import run_single_seed
from rul_audit.report import render_single_seed_report


def main():
    result = run_single_seed(7)
    print(render_single_seed_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
