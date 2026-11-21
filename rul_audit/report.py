"""Markdown report rendering for one audit run."""

from .models import rank_order


def render_single_seed_report(result):
    """Human-readable report for one seed's audit."""
    lines = []
    lines.append("# RUL Censoring-Reversal Audit - seed %d" % result["seed"])
    lines.append("")
    lines.append("## Uncensored truth leaderboard (RMSE, lower is better)")
    lines.append("")
    truth = result["truth_scores"]
    for idx, name in enumerate(rank_order(truth)):
        lines.append("%d. %s - %.2f" % (idx + 1, name, truth[name]))
    lines.append("")
    lines.append("## Naive leaderboards under censoring")
    lines.append("")
    lines.append("| Regime | Target rate | Achieved rate | Naive winner | "
                 "Truth winner | Reversal | Winner true-RMSE penalty | "
                 "Kendall tau |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for row in result["rows"]:
        lines.append(
            "| %s | %.1f | %.3f | %s | %s | %s | %.1f%% | %.2f |" % (
                row["regime"],
                row["target_rate"],
                row["achieved_rate"],
                row["naive_winner"],
                row["truth_winner"],
                "YES" if row["reversal"] else "no",
                100.0 * row["winner_true_rmse_penalty"],
                row["kendall_tau"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_evaluation_summary(evaluation, headline):
    """Summary markdown for the full multi-seed evaluation."""
    lines = []
    lines.append("# Evaluation summary")
    lines.append("")
    lines.append("Seeds: %d (%s). Predictors: 5 families. Censoring "
                 "regimes: fixed_horizon, random, failure_dependent. "
                 "Target censoring rates: 0.1-0.7."
                 % (evaluation["n_seeds"],
                    ", ".join(str(s) for s in evaluation["seeds"])))
    lines.append("")
    lines.append("Truth-winner counts across seeds: %s"
                 % ", ".join(
                     "%s x%d" % (k, v)
                     for k, v in sorted(
                         evaluation["truth_winner_counts"].items())))
    lines.append("")
    lines.append("| Regime | Target rate | Achieved rate | Reversal rate | "
                 "Mean winner penalty | Mean Kendall tau |")
    lines.append("|---|---|---|---|---|---|")
    for cond in evaluation["conditions"]:
        lines.append(
            "| %s | %.1f | %.3f | %.3f | %.1f%% | %.3f |" % (
                cond["regime"],
                cond["target_rate"],
                cond["mean_achieved_rate"],
                cond["reversal_rate"],
                100.0 * cond["mean_winner_penalty"],
                cond["mean_kendall_tau"],
            )
        )
    lines.append("")
    lines.append("Worst condition: %s at target rate %.1f - reversal rate "
                 "%.3f, mean winner penalty %.1f%%."
                 % (headline["worst_condition"]["regime"],
                    headline["worst_condition"]["target_rate"],
                    headline["worst_condition"]["reversal_rate"],
                    100.0 * headline["worst_condition"]["mean_winner_penalty"]))
    lines.append("")
    lines.append("Mean reversal rate, failure-dependent censoring: %.3f. "
                 "Mean reversal rate, random (non-informative) censoring: "
                 "%.3f."
                 % (headline["mean_reversal_failure_dependent"],
                    headline["mean_reversal_random"]))
    lines.append("")
    return "\n".join(lines)
