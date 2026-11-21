"""Command-line interface.

Usage:
    python -m rul_audit demo
    python -m rul_audit evaluate --out results_dir
"""

import argparse
import csv
import json
import os
import sys

from .evaluate import headline_numbers, run_evaluation, run_single_seed
from .report import render_evaluation_summary, render_single_seed_report


def _jsonable(obj):
    if isinstance(obj, dict):
        return dict((k, _jsonable(v)) for k, v in obj.items())
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, float):
        return round(obj, 6)
    return obj


def cmd_demo(args):
    result = run_single_seed(7)
    sys.stdout.write(render_single_seed_report(result))
    sys.stdout.write("\n")
    return 0


def cmd_evaluate(args):
    evaluation = run_evaluation()
    headline = headline_numbers(evaluation)
    out_dir = args.out
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    slim = {
        "seeds": evaluation["seeds"],
        "n_seeds": evaluation["n_seeds"],
        "truth_winner_counts": evaluation["truth_winner_counts"],
        "conditions": evaluation["conditions"],
        "headline": headline,
    }
    with open(os.path.join(out_dir, "evaluation.json"), "w") as fh:
        json.dump(_jsonable(slim), fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "evaluation.csv"), "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["regime", "target_rate", "achieved_rate",
                         "reversal_rate", "mean_winner_penalty",
                         "mean_kendall_tau", "n_seeds"])
        for cond in evaluation["conditions"]:
            writer.writerow([
                cond["regime"],
                "%.1f" % cond["target_rate"],
                "%.4f" % cond["mean_achieved_rate"],
                "%.4f" % cond["reversal_rate"],
                "%.4f" % cond["mean_winner_penalty"],
                "%.4f" % cond["mean_kendall_tau"],
                cond["n_seeds"],
            ])
    with open(os.path.join(out_dir, "evaluation_summary.md"), "w") as fh:
        fh.write(render_evaluation_summary(evaluation, headline))
    with open(os.path.join(out_dir, "HEADLINE.md"), "w") as fh:
        fh.write("# Headline results\n\n")
        fh.write("Worst condition: %s at target censoring rate %.1f - "
                 "rank-reversal rate %.3f across %d seeds, mean winner "
                 "true-RMSE penalty %.1f%%.\n\n"
                 % (headline["worst_condition"]["regime"],
                    headline["worst_condition"]["target_rate"],
                    headline["worst_condition"]["reversal_rate"],
                    evaluation["n_seeds"],
                    100.0 * headline["worst_condition"]["mean_winner_penalty"]))
        fh.write("Mean reversal rate under failure-dependent censoring: "
                 "%.3f. Under random (non-informative) censoring: %.3f.\n"
                 % (headline["mean_reversal_failure_dependent"],
                    headline["mean_reversal_random"]))
    sys.stdout.write("Wrote evaluation results to %s\n" % out_dir)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="rul_audit")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("demo")
    eval_parser = sub.add_parser("evaluate")
    eval_parser.add_argument("--out", default="results")
    args = parser.parse_args(argv)
    if args.command == "demo":
        return cmd_demo(args)
    if args.command == "evaluate":
        return cmd_evaluate(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
