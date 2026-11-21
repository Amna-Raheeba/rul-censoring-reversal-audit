"""The headline experiment.

For each seed, a fresh test fleet is generated and scored once against
the uncensored truth. Then every (regime, rate) censoring condition is
applied and the naive drop-censored leaderboard is compared with the
truth. Aggregates over seeds give, per regime and rate:

- rank-reversal rate (fraction of seeds where the winner changes);
- mean winner's true-RMSE penalty (how much worse the naive winner
  really is, on the full data);
- mean Kendall tau between the naive and truth rankings.
"""

from .censoring import RATES, REGIMES, apply_censoring, censored_units
from .generate import generate_fleet
from .models import build_cases
from .predictors import all_predictors
from .scoring import compare_leaderboards, score_panel

DEFAULT_SEEDS = tuple(range(101, 121))
TRAIN_SEED = 9001
TRAIN_UNITS = 160
TEST_UNITS = 120


def run_single_seed(seed, rates=RATES, regimes=REGIMES):
    """Full audit for one test fleet. Returns per-condition comparisons."""
    train = generate_fleet(TRAIN_SEED, TRAIN_UNITS)
    predictors = [p.fit(train) for p in all_predictors()]
    test = generate_fleet(seed, TEST_UNITS)
    cases, lookup = build_cases(test)
    truth_scores = score_panel(predictors, cases, lookup)
    rows = []
    for regime in regimes:
        for rate in rates:
            censor = apply_censoring(test, regime, rate, seed)
            dropped = censored_units(test, censor)
            keep = set(t.unit_id for t in test) - dropped
            naive_scores = score_panel(predictors, cases, lookup, keep)
            comp = compare_leaderboards(truth_scores, naive_scores)
            comp["regime"] = regime
            comp["target_rate"] = rate
            comp["achieved_rate"] = len(dropped) / float(len(test))
            comp["n_cases_naive"] = sum(
                1 for c in cases if c.unit_id in keep
            )
            comp["n_cases_truth"] = len(cases)
            rows.append(comp)
    return {
        "seed": seed,
        "truth_scores": truth_scores,
        "rows": rows,
    }


def run_evaluation(seeds=DEFAULT_SEEDS, rates=RATES, regimes=REGIMES):
    """Run the audit over all seeds and aggregate per (regime, rate)."""
    per_seed = [run_single_seed(seed, rates, regimes) for seed in seeds]
    conditions = []
    for regime in regimes:
        for rate in rates:
            rows = []
            for result in per_seed:
                for row in result["rows"]:
                    if row["regime"] == regime and row["target_rate"] == rate:
                        rows.append(row)
            n = len(rows)
            reversals = sum(1 for r in rows if r["reversal"])
            conditions.append({
                "regime": regime,
                "target_rate": rate,
                "n_seeds": n,
                "reversal_rate": reversals / float(n) if n else 0.0,
                "mean_winner_penalty": (
                    sum(r["winner_true_rmse_penalty"] for r in rows) / float(n)
                    if n else 0.0
                ),
                "mean_kendall_tau": (
                    sum(r["kendall_tau"] for r in rows) / float(n)
                    if n else 0.0
                ),
                "mean_achieved_rate": (
                    sum(r["achieved_rate"] for r in rows) / float(n)
                    if n else 0.0
                ),
            })
    truth_wins = {}
    for result in per_seed:
        winner = min(result["truth_scores"],
                     key=lambda k: (result["truth_scores"][k], k))
        truth_wins[winner] = truth_wins.get(winner, 0) + 1
    return {
        "seeds": list(seeds),
        "n_seeds": len(per_seed),
        "conditions": conditions,
        "per_seed": per_seed,
        "truth_winner_counts": truth_wins,
    }


def headline_numbers(evaluation):
    """The small set of numbers quoted in the README and HEADLINE.md."""
    out = {}
    for cond in evaluation["conditions"]:
        key = "%s@%.1f" % (cond["regime"], cond["target_rate"])
        out[key] = {
            "reversal_rate": round(cond["reversal_rate"], 4),
            "mean_winner_penalty": round(cond["mean_winner_penalty"], 4),
            "mean_kendall_tau": round(cond["mean_kendall_tau"], 4),
        }
    worst = None
    for cond in evaluation["conditions"]:
        if worst is None or cond["reversal_rate"] > worst["reversal_rate"]:
            worst = cond
    out["worst_condition"] = {
        "regime": worst["regime"],
        "target_rate": worst["target_rate"],
        "reversal_rate": round(worst["reversal_rate"], 4),
        "mean_winner_penalty": round(worst["mean_winner_penalty"], 4),
    }
    fd = [c for c in evaluation["conditions"]
          if c["regime"] == "failure_dependent"]
    rnd = [c for c in evaluation["conditions"] if c["regime"] == "random"]
    out["mean_reversal_failure_dependent"] = round(
        sum(c["reversal_rate"] for c in fd) / float(len(fd)), 4)
    out["mean_reversal_random"] = round(
        sum(c["reversal_rate"] for c in rnd) / float(len(rnd)), 4)
    return out
