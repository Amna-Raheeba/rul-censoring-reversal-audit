from rul_audit.censoring import RATES, REGIMES
from rul_audit.evaluate import headline_numbers, run_evaluation, run_single_seed


def test_single_seed_structure():
    result = run_single_seed(101, rates=(0.3,), regimes=("random",))
    assert result["seed"] == 101
    assert len(result["rows"]) == 1
    row = result["rows"][0]
    assert row["regime"] == "random"
    assert 0.0 <= row["achieved_rate"] <= 1.0
    assert set(result["truth_scores"].keys()) == {
        "mean_life", "linear_trend", "exponential_trend",
        "recent_slope", "knn_trajectory",
    }


def test_single_seed_full_grid_size():
    result = run_single_seed(102)
    assert len(result["rows"]) == len(RATES) * len(REGIMES)


def test_evaluation_aggregation():
    evaluation = run_evaluation(seeds=(101, 102), rates=(0.5,),
                                regimes=("fixed_horizon",))
    assert evaluation["n_seeds"] == 2
    assert len(evaluation["conditions"]) == 1
    cond = evaluation["conditions"][0]
    assert cond["reversal_rate"] in (0.0, 0.5, 1.0)
    assert cond["mean_kendall_tau"] <= 1.0


def test_headline_numbers_keys():
    evaluation = run_evaluation(seeds=(101, 102), rates=(0.5,),
                                regimes=("fixed_horizon", "random",
                                          "failure_dependent"))
    headline = headline_numbers(evaluation)
    assert "worst_condition" in headline
    assert "mean_reversal_failure_dependent" in headline
    assert "mean_reversal_random" in headline
    for key, value in headline.items():
        if key == "worst_condition":
            continue
        assert isinstance(value, dict) or isinstance(value, float)
