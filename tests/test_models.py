import math

from rul_audit.generate import generate_fleet
from rul_audit.models import build_cases, kendall_tau, rank_order, rmse


def test_rmse_perfect():
    assert rmse([(3.0, 3.0), (5.0, 5.0)]) == 0.0


def test_rmse_known_value():
    assert abs(rmse([(0.0, 3.0), (0.0, 4.0)]) - math.sqrt(12.5)) < 1e-9


def test_rmse_empty_is_nan():
    assert math.isnan(rmse([]))


def test_rank_order_ascending():
    scores = {"b": 2.0, "a": 1.0, "c": 3.0}
    assert rank_order(scores) == ["a", "b", "c"]


def test_rank_order_ties_by_name():
    scores = {"b": 1.0, "a": 1.0}
    assert rank_order(scores) == ["a", "b"]


def test_kendall_tau_identical():
    assert kendall_tau(["a", "b", "c"], ["a", "b", "c"]) == 1.0


def test_kendall_tau_reversed():
    assert kendall_tau(["a", "b", "c"], ["c", "b", "a"]) == -1.0


def test_kendall_tau_single_swap():
    tau = kendall_tau(["a", "b", "c"], ["b", "a", "c"])
    assert abs(tau - (1.0 / 3.0)) < 1e-9


def test_build_cases_skips_dead_units():
    fleet = generate_fleet(13, 30)
    cases, lookup = build_cases(fleet)
    for case in cases:
        assert lookup[case.unit_id].failure_time > case.age
        assert abs(case.true_rul - (lookup[case.unit_id].failure_time - case.age)) < 1e-9


def test_build_cases_ages():
    fleet = generate_fleet(13, 30)
    cases, _ = build_cases(fleet, ages=(40,))
    assert all(c.age == 40 for c in cases)


def test_history_length():
    traj = generate_fleet(15, 1)[0]
    times, signal = traj.history(40)
    assert times[-1] == 40
    assert len(times) == len(signal) == 9


def test_signal_at_matches_history():
    traj = generate_fleet(15, 1)[0]
    _times, signal = traj.history(80)
    assert traj.signal_at(80) == signal[-1]


def test_case_key():
    fleet = generate_fleet(17, 5)
    cases, _ = build_cases(fleet)
    keys = set(c.key() for c in cases)
    assert len(keys) == len(cases)
