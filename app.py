"""Streamlit dashboard for the RUL Censoring-Reversal Audit.

Three tabs:
1. Leaderboards - the uncensored truth leaderboard vs the naive
   drop-censored leaderboard for a chosen regime and rate.
2. Reversals - every censoring condition for one fleet, with the
   reversal flag, the winner's true-RMSE penalty, and Kendall tau.
3. Evaluation - the aggregated multi-seed headline table.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from rul_audit.censoring import RATES, REGIMES, apply_censoring, censored_units
from rul_audit.evaluate import TRAIN_SEED, TRAIN_UNITS, run_evaluation
from rul_audit.generate import generate_fleet
from rul_audit.models import build_cases, rank_order
from rul_audit.predictors import all_predictors
from rul_audit.scoring import compare_leaderboards, score_panel


@st.cache_data(show_spinner=False)
def load_single_seed(seed):
    train = generate_fleet(TRAIN_SEED, TRAIN_UNITS)
    predictors = [p.fit(train) for p in all_predictors()]
    test = generate_fleet(seed, 120)
    cases, lookup = build_cases(test)
    truth_scores = score_panel(predictors, cases, lookup)
    rows = []
    for regime in REGIMES:
        for rate in RATES:
            censor = apply_censoring(test, regime, rate, seed)
            dropped = censored_units(test, censor)
            keep = set(t.unit_id for t in test) - dropped
            naive_scores = score_panel(predictors, cases, lookup, keep)
            comp = compare_leaderboards(truth_scores, naive_scores)
            comp["regime"] = regime
            comp["target_rate"] = rate
            comp["achieved_rate"] = len(dropped) / float(len(test))
            rows.append(comp)
    return truth_scores, rows


@st.cache_data(show_spinner=False)
def load_evaluation():
    return run_evaluation(seeds=(101, 102, 103, 104, 105))


def leaderboard_rows(scores):
    rows = []
    for idx, name in enumerate(rank_order(scores)):
        rows.append({
            "rank": idx + 1,
            "predictor": name,
            "rmse": round(scores[name], 2),
        })
    return rows


def main():
    st.set_page_config(page_title="RUL Censoring-Reversal Audit")
    st.title("RUL Censoring-Reversal Audit")
    st.write(
        "How right-censoring silently reverses remaining-useful-life "
        "model leaderboards: the naive drop-censored ranking against "
        "the uncensored ground truth, on seeded synthetic fleets."
    )
    seed = st.sidebar.number_input("Fleet seed", value=7, step=1)
    truth_scores, rows = load_single_seed(int(seed))

    tab1, tab2, tab3 = st.tabs(["Leaderboards", "Reversals", "Evaluation"])

    with tab1:
        regime = st.selectbox("Censoring regime", list(REGIMES))
        rate = st.select_slider("Target censoring rate", options=list(RATES))
        chosen = None
        for row in rows:
            if row["regime"] == regime and row["target_rate"] == rate:
                chosen = row
        st.subheader("Uncensored truth leaderboard")
        st.table(leaderboard_rows(truth_scores))
        st.subheader("Naive leaderboard (censored units dropped)")
        st.table(leaderboard_rows(chosen["naive_scores"]))
        if chosen["reversal"]:
            st.error(
                "RANK REVERSAL: naive winner %s is not the true winner "
                "%s. Its true RMSE is %.1f%% worse than the best."
                % (chosen["naive_winner"], chosen["truth_winner"],
                   100.0 * chosen["winner_true_rmse_penalty"]))
        else:
            st.success("No reversal at this condition: the naive winner "
                       "matches the truth winner.")
        st.write("Achieved censoring rate: %.3f" % chosen["achieved_rate"])

    with tab2:
        table = []
        for row in rows:
            table.append({
                "regime": row["regime"],
                "target_rate": row["target_rate"],
                "achieved_rate": round(row["achieved_rate"], 3),
                "naive_winner": row["naive_winner"],
                "reversal": "YES" if row["reversal"] else "no",
                "winner_penalty_pct": round(
                    100.0 * row["winner_true_rmse_penalty"], 1),
                "kendall_tau": round(row["kendall_tau"], 2),
            })
        st.table(table)
        n_rev = sum(1 for r in rows if r["reversal"])
        st.write("Reversals in this fleet: %d of %d conditions"
                 % (n_rev, len(rows)))

    with tab3:
        evaluation = load_evaluation()
        table = []
        for cond in evaluation["conditions"]:
            table.append({
                "regime": cond["regime"],
                "target_rate": cond["target_rate"],
                "reversal_rate": round(cond["reversal_rate"], 3),
                "mean_winner_penalty_pct": round(
                    100.0 * cond["mean_winner_penalty"], 1),
                "mean_kendall_tau": round(cond["mean_kendall_tau"], 3),
            })
        st.table(table)
        st.write("Truth-winner counts across seeds: %s"
                 % evaluation["truth_winner_counts"])


if __name__ == "__main__":
    main()
