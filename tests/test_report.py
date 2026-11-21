from rul_audit.evaluate import headline_numbers, run_evaluation, run_single_seed
from rul_audit.report import (
    render_evaluation_summary,
    render_single_seed_report,
)


def test_single_seed_report_contents():
    result = run_single_seed(7, rates=(0.5,), regimes=("random",))
    text = render_single_seed_report(result)
    assert "seed 7" in text
    assert "Uncensored truth leaderboard" in text
    assert "random" in text


def test_evaluation_summary_contents():
    evaluation = run_evaluation(seeds=(101, 102), rates=(0.5,),
                                regimes=("random", "failure_dependent",
                                          "fixed_horizon"))
    headline = headline_numbers(evaluation)
    text = render_evaluation_summary(evaluation, headline)
    assert "Evaluation summary" in text
    assert "Reversal rate" in text
    assert "failure_dependent" in text
