"""Seeded right-censoring regimes.

A censoring regime assigns every test unit a censoring time C. A unit
with C < T is *censored*: in real PHM benchmarks its failure is never
observed. The naive scoring practice audited here drops censored units
from the test set entirely.

Three regimes, each calibrated (by deterministic bisection on the
fleet itself) to hit a target censoring rate:

- fixed_horizon: every unit shares one horizon C = H. Units that
  outlive the study are censored, so the naive test set keeps only
  short-lived units.
- random: C drawn independently of the unit's degradation (the
  non-informative control condition).
- failure_dependent: at each observation step the unit may be pulled
  for preventive maintenance with a hazard that grows with its current
  degradation level. Fast degraders are censored most — the informative
  case that real fleets produce.
"""

import random

from .models import OBSERVATION_STEP

REGIMES = ("fixed_horizon", "random", "failure_dependent")
RATES = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)


def _fraction_censored(trajectories, censor_times):
    n = len(trajectories)
    if n == 0:
        return 0.0
    count = 0
    for traj in trajectories:
        if censor_times[traj.unit_id] < traj.failure_time:
            count += 1
    return count / float(n)


def _fixed_horizon(trajectories, target_rate):
    lifetimes = sorted(t.failure_time for t in trajectories)
    n = len(lifetimes)
    # Horizon at the (1 - rate) quantile of lifetimes: units living
    # longer than the horizon are censored.
    idx = int((1.0 - target_rate) * n)
    if idx >= n:
        idx = n - 1
    horizon = lifetimes[idx]
    return dict((t.unit_id, horizon) for t in trajectories)


def _random(trajectories, seed, target_rate):
    rng = random.Random(seed * 7919 + 13)
    draws = dict((t.unit_id, rng.random()) for t in trajectories)

    def build(scale):
        return dict(
            (t.unit_id, draws[t.unit_id] * scale) for t in trajectories
        )

    lo, hi = 1.0, max(t.failure_time for t in trajectories) * 3.0
    best = build(hi)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        candidate = build(mid)
        frac = _fraction_censored(trajectories, candidate)
        best = candidate
        if abs(frac - target_rate) < 0.01:
            break
        if frac < target_rate:
            # Too few censored: shrink the scale so censoring times
            # fall earlier.
            hi = mid
        else:
            lo = mid
    return best


def _failure_dependent(trajectories, seed, target_rate):
    rng = random.Random(seed * 104729 + 7)
    # One uniform draw per (unit, step), fixed before calibration so the
    # bisection only moves the hazard scale, never the randomness.
    draws = {}
    for traj in trajectories:
        steps = len(traj.signal)
        draws[traj.unit_id] = [rng.random() for _ in range(steps)]

    def build(hazard):
        censor = {}
        for traj in trajectories:
            c_time = float("inf")
            for step_idx, level in enumerate(traj.signal):
                p = hazard * level * level
                if p > 0.95:
                    p = 0.95
                if draws[traj.unit_id][step_idx] < p:
                    c_time = step_idx * OBSERVATION_STEP
                    break
            censor[traj.unit_id] = c_time
        return censor

    lo, hi = 0.0, 2.0
    best = build(hi)
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        candidate = build(mid)
        frac = _fraction_censored(trajectories, candidate)
        best = candidate
        if abs(frac - target_rate) < 0.01:
            break
        if frac < target_rate:
            lo = mid
        else:
            hi = mid
    return best


def apply_censoring(trajectories, regime, target_rate, seed):
    """Return {unit_id: censor_time} calibrated to the target rate."""
    if regime == "fixed_horizon":
        return _fixed_horizon(trajectories, target_rate)
    if regime == "random":
        return _random(trajectories, seed, target_rate)
    if regime == "failure_dependent":
        return _failure_dependent(trajectories, seed, target_rate)
    raise ValueError("unknown regime: %s" % regime)


def censored_units(trajectories, censor_times):
    """Set of unit ids censored under the given censoring times."""
    out = set()
    for traj in trajectories:
        if censor_times[traj.unit_id] < traj.failure_time:
            out.add(traj.unit_id)
    return out
