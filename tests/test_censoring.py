import pytest

from rul_audit.censoring import (
    REGIMES,
    apply_censoring,
    censored_units,
)
from rul_audit.generate import generate_fleet


@pytest.fixture(scope="module")
def fleet():
    return generate_fleet(101, 120)


def test_regimes_listed():
    assert set(REGIMES) == {"fixed_horizon", "random", "failure_dependent"}


@pytest.mark.parametrize("regime", list(REGIMES))
@pytest.mark.parametrize("rate", [0.1, 0.3, 0.5, 0.7])
def test_calibration_hits_target_rate(fleet, regime, rate):
    censor = apply_censoring(fleet, regime, rate, 101)
    achieved = len(censored_units(fleet, censor)) / float(len(fleet))
    assert abs(achieved - rate) <= 0.05


def test_censoring_deterministic(fleet):
    a = apply_censoring(fleet, "random", 0.4, 101)
    b = apply_censoring(fleet, "random", 0.4, 101)
    assert a == b


def test_censoring_seed_changes_outcome(fleet):
    a = apply_censoring(fleet, "random", 0.4, 101)
    b = apply_censoring(fleet, "random", 0.4, 202)
    assert a != b


def test_fixed_horizon_same_for_all_units(fleet):
    censor = apply_censoring(fleet, "fixed_horizon", 0.5, 101)
    assert len(set(censor.values())) == 1


def test_fixed_horizon_censors_only_long_lived(fleet):
    censor = apply_censoring(fleet, "fixed_horizon", 0.5, 101)
    dropped = censored_units(fleet, censor)
    horizon = list(censor.values())[0]
    for traj in fleet:
        if traj.unit_id in dropped:
            assert traj.failure_time > horizon
        else:
            assert traj.failure_time <= horizon


def test_failure_dependent_censors_slow_more_than_fast(fleet):
    # Measured property of the regime: long-lived units accumulate the
    # most exposure to the degradation hazard.
    censor = apply_censoring(fleet, "failure_dependent", 0.5, 101)
    dropped = censored_units(fleet, censor)
    fast = [t for t in fleet if t.group == "fast"]
    slow = [t for t in fleet if t.group == "slow"]
    fast_rate = sum(1 for t in fast if t.unit_id in dropped) / float(len(fast))
    slow_rate = sum(1 for t in slow if t.unit_id in dropped) / float(len(slow))
    assert slow_rate > fast_rate


def test_unknown_regime_raises(fleet):
    with pytest.raises(ValueError):
        apply_censoring(fleet, "not_a_regime", 0.5, 101)


def test_censor_times_cover_all_units(fleet):
    censor = apply_censoring(fleet, "random", 0.3, 101)
    assert set(censor.keys()) == set(t.unit_id for t in fleet)
