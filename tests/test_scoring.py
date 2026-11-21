from rul_audit.models import build_cases
from rul_audit.scoring import compare_leaderboards, score_panel


def test_score_panel_all_cases(fitted_predictors, test_fleet):
    cases, lookup = build_cases(test_fleet)
    scores = score_panel(fitted_predictors, cases, lookup)
    assert set(scores.keys()) == set(p.name for p in fitted_predictors)
    assert all(v > 0 for v in scores.values())


def test_score_panel_keep_subset(fitted_predictors, test_fleet):
    cases, lookup = build_cases(test_fleet)
    keep = set(t.unit_id for t in test_fleet[:10])
    scores = score_panel(fitted_predictors, cases, lookup, keep)
    assert all(v > 0 for v in scores.values())


def test_compare_no_reversal_when_identical():
    scores = {"a": 1.0, "b": 2.0, "c": 3.0}
    comp = compare_leaderboards(scores, dict(scores))
    assert comp["reversal"] is False
    assert comp["winner_true_rmse_penalty"] == 0.0
    assert comp["kendall_tau"] == 1.0


def test_compare_detects_reversal():
    truth = {"a": 1.0, "b": 2.0}
    naive = {"a": 5.0, "b": 4.0}
    comp = compare_leaderboards(truth, naive)
    assert comp["reversal"] is True
    assert comp["naive_winner"] == "b"
    assert comp["truth_winner"] == "a"
    assert abs(comp["winner_true_rmse_penalty"] - 1.0) < 1e-9


def test_compare_rank_shift():
    truth = {"a": 1.0, "b": 2.0, "c": 3.0}
    naive = {"a": 2.0, "b": 1.0, "c": 3.0}
    comp = compare_leaderboards(truth, naive)
    assert comp["rank_shift"]["a"] == 1
    assert comp["rank_shift"]["b"] == -1
    assert comp["rank_shift"]["c"] == 0
