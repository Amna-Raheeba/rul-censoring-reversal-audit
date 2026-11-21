"""Leaderboard scoring: naive (drop censored) vs the uncensored truth.

For a fixed panel of predictors and a fixed case list, the audit scores
every predictor twice:

- truth scores use every case (the complete-data leaderboard, only
  computable because the fleet is synthetic and failure times are
  known);
- naive scores use only cases from units that were NOT censored — the
  common drop-censored practice.

The headline objects are the rank-reversal indicator (does the naive
winner differ from the truth winner?), the naive winner's true-RMSE
penalty, and the Kendall tau between the two rankings.
"""

from .models import kendall_tau, rank_order, rmse


def score_panel(predictors, cases, lookup, keep_units=None):
    """RMSE per predictor over cases whose unit is in keep_units.

    keep_units=None keeps every case (the truth scoring).
    """
    scores = {}
    for predictor in predictors:
        pairs = []
        for case in cases:
            if keep_units is not None and case.unit_id not in keep_units:
                continue
            traj = lookup[case.unit_id]
            pred = predictor.predict(traj, case.age)
            if pred is not None:
                pairs.append((pred, case.true_rul))
        scores[predictor.name] = rmse(pairs)
    return scores


def compare_leaderboards(truth_scores, naive_scores):
    """Compare a naive leaderboard against the truth leaderboard."""
    truth_order = rank_order(truth_scores)
    naive_order = rank_order(naive_scores)
    truth_winner = truth_order[0]
    naive_winner = naive_order[0]
    reversal = naive_winner != truth_winner
    best_true = truth_scores[truth_winner]
    winner_true = truth_scores[naive_winner]
    if best_true and best_true == best_true and best_true > 0:
        penalty = (winner_true - best_true) / best_true
    else:
        penalty = 0.0
    rank_shift = {}
    for name in truth_scores:
        rank_shift[name] = naive_order.index(name) - truth_order.index(name)
    return {
        "truth_order": truth_order,
        "naive_order": naive_order,
        "truth_winner": truth_winner,
        "naive_winner": naive_winner,
        "reversal": reversal,
        "winner_true_rmse_penalty": penalty,
        "kendall_tau": kendall_tau(truth_order, naive_order),
        "rank_shift": rank_shift,
        "truth_scores": truth_scores,
        "naive_scores": naive_scores,
    }
