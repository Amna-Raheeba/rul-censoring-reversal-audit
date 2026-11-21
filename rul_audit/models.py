"""Core data types for the RUL censoring-reversal audit.

A Trajectory is one unit's complete run-to-failure degradation record.
The ground truth failure time is always known in this audit, because the
fleet is synthetic: censoring is applied afterwards, as an evaluation
condition, never to the stored trajectory itself.
"""

import math

FAILURE_THRESHOLD = 1.0
OBSERVATION_STEP = 5
PREDICTION_AGES = (40, 80, 120)


class Trajectory(object):
    """One unit's complete run-to-failure degradation trajectory."""

    def __init__(self, unit_id, group, d0, rate, failure_time, times, signal):
        self.unit_id = unit_id
        self.group = group
        self.d0 = d0
        self.rate = rate
        self.failure_time = failure_time
        self.times = list(times)
        self.signal = list(signal)

    def signal_at(self, age):
        """Observed (noisy) degradation signal at the given age."""
        idx = int(age // OBSERVATION_STEP)
        if idx < 0:
            idx = 0
        if idx >= len(self.signal):
            idx = len(self.signal) - 1
        return self.signal[idx]

    def history(self, age):
        """(times, signal) pairs observed up to and including age."""
        n = int(age // OBSERVATION_STEP) + 1
        return self.times[:n], self.signal[:n]

    def true_rul(self, age):
        return self.failure_time - age

    def to_dict(self):
        return {
            "unit_id": self.unit_id,
            "group": self.group,
            "d0": round(self.d0, 6),
            "rate": round(self.rate, 6),
            "failure_time": round(self.failure_time, 3),
        }


class Case(object):
    """One RUL prediction task: a unit observed at one prediction age."""

    def __init__(self, unit_id, age, true_rul):
        self.unit_id = unit_id
        self.age = age
        self.true_rul = true_rul

    def key(self):
        return "%s@%d" % (self.unit_id, self.age)


def build_cases(trajectories, ages=PREDICTION_AGES):
    """One case per (unit, age) for every unit still alive at that age."""
    cases = []
    lookup = {}
    for traj in trajectories:
        lookup[traj.unit_id] = traj
        for age in ages:
            if traj.failure_time > age:
                cases.append(Case(traj.unit_id, age, traj.true_rul(age)))
    return cases, lookup


def rmse(pairs):
    """Root mean squared error over (predicted, true) pairs."""
    if not pairs:
        return float("nan")
    total = 0.0
    for pred, true in pairs:
        total += (pred - true) * (pred - true)
    return math.sqrt(total / len(pairs))


def rank_order(scores):
    """Predictor names sorted by ascending score (best first)."""
    return sorted(scores.keys(), key=lambda name: (scores[name], name))


def kendall_tau(order_a, order_b):
    """Kendall tau between two full rankings of the same items."""
    pos_b = {}
    for idx, name in enumerate(order_b):
        pos_b[name] = idx
    seq = [pos_b[name] for name in order_a]
    n = len(seq)
    if n < 2:
        return 1.0
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            if seq[i] < seq[j]:
                concordant += 1
            elif seq[i] > seq[j]:
                discordant += 1
    total = concordant + discordant
    if total == 0:
        return 1.0
    return (concordant - discordant) / float(total)
