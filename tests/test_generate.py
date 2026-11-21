import math

from rul_audit.generate import failure_time_for, generate_fleet


def test_deterministic_per_seed():
    a = generate_fleet(42, 20)
    b = generate_fleet(42, 20)
    assert [t.failure_time for t in a] == [t.failure_time for t in b]
    assert [t.signal for t in a] == [t.signal for t in b]


def test_different_seeds_differ():
    a = generate_fleet(1, 20)
    b = generate_fleet(2, 20)
    assert [t.failure_time for t in a] != [t.failure_time for t in b]


def test_fleet_size():
    assert len(generate_fleet(3, 30)) == 30


def test_failure_time_formula():
    for traj in generate_fleet(5, 25):
        expected = math.log(1.0 / traj.d0) / traj.rate
        assert abs(traj.failure_time - expected) < 1e-9


def test_groups_present():
    groups = set(t.group for t in generate_fleet(7, 120))
    assert groups == {"fast", "slow"}


def test_fast_units_die_sooner_on_average():
    fleet = generate_fleet(7, 120)
    fast = [t.failure_time for t in fleet if t.group == "fast"]
    slow = [t.failure_time for t in fleet if t.group == "slow"]
    assert sum(fast) / len(fast) < sum(slow) / len(slow)


def test_signal_reaches_failure_region():
    for traj in generate_fleet(9, 15):
        assert traj.signal[-1] > 0.5


def test_signal_positive_and_monotone_in_expectation():
    for traj in generate_fleet(11, 10):
        assert all(s > 0 for s in traj.signal)
        assert traj.signal[-1] > traj.signal[0]


def test_failure_time_for_helper():
    assert failure_time_for(0.05, 0.01) == math.log(20.0) / 0.01
