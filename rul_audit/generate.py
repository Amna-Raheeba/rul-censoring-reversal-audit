"""Seeded synthetic run-to-failure degradation fleet generator.

Each unit's true (noiseless) degradation grows exponentially,
d(t) = d0 * exp(rate * t), and the unit fails when d crosses 1.0, so the
true failure time is known exactly: T = ln(1 / d0) / rate. The observed
signal is the true degradation plus Gaussian noise, sampled every
OBSERVATION_STEP cycles.

The fleet mixes two sub-populations:

- "fast" units degrade quickly (short lives);
- "slow" units degrade slowly (long lives).

That mixture is what makes censoring dangerous: any censoring regime
that removes one sub-population more than the other silently changes
which units the leaderboard is scored on.
"""

import math
import random

from .models import FAILURE_THRESHOLD, OBSERVATION_STEP, Trajectory

FAST_RATE_RANGE = (0.011, 0.019)
SLOW_RATE_RANGE = (0.0038, 0.0075)
D0_RANGE = (0.015, 0.12)
NOISE_SIGMA = 0.009
FAST_FRACTION = 0.45


def failure_time_for(d0, rate):
    return math.log(FAILURE_THRESHOLD / d0) / rate


def generate_fleet(seed, n_units=120):
    """Generate a complete run-to-failure fleet. Deterministic per seed."""
    rng = random.Random(seed)
    trajectories = []
    for i in range(n_units):
        if rng.random() < FAST_FRACTION:
            group = "fast"
            rate = rng.uniform(FAST_RATE_RANGE[0], FAST_RATE_RANGE[1])
        else:
            group = "slow"
            rate = rng.uniform(SLOW_RATE_RANGE[0], SLOW_RATE_RANGE[1])
        d0 = rng.uniform(D0_RANGE[0], D0_RANGE[1])
        t_fail = failure_time_for(d0, rate)
        times = []
        signal = []
        t = 0
        while t <= t_fail:
            true_d = d0 * math.exp(rate * t)
            observed = true_d + rng.gauss(0.0, NOISE_SIGMA)
            if observed < 0.001:
                observed = 0.001
            times.append(t)
            signal.append(observed)
            t += OBSERVATION_STEP
        trajectories.append(
            Trajectory("U%03d" % i, group, d0, rate, t_fail, times, signal)
        )
    return trajectories
