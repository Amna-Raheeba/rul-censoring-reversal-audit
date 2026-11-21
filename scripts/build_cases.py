"""Build the seeded demo fleet summary stored in data/cases.json.

The stored file is a compact summary (one row per unit) of the demo
fleet (seed 7) plus the audit's case list shape. Full trajectories are
always regenerated deterministically from the seed, never stored.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rul_audit.generate import generate_fleet
from rul_audit.models import PREDICTION_AGES, build_cases


def main():
    fleet = generate_fleet(7, 120)
    cases, _lookup = build_cases(fleet)
    payload = {
        "seed": 7,
        "n_units": len(fleet),
        "prediction_ages": list(PREDICTION_AGES),
        "n_cases": len(cases),
        "units": [t.to_dict() for t in fleet],
    }
    out = os.path.join(os.path.dirname(__file__), "..", "data", "cases.json")
    with open(out, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
    print("Wrote %s (%d units, %d cases)" % (out, len(fleet), len(cases)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
