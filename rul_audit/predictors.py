"""Five simple RUL predictor families.

Every predictor is fitted on a complete (uncensored) training fleet and
then asked for the remaining useful life of a test unit at a prediction
age, from the observed signal history only. The families are chosen to
disagree about *which units* they are good on:

- mean_life: population average remaining life; blind to the unit.
- linear_trend: straight-line extrapolation of the signal to failure.
  Systematically under-predicts RUL for convex (exponential) growth,
  and the bias is worst on fast degraders.
- exponential_trend: log-linear extrapolation; matches the true
  degradation law and is the strongest family on fast degraders, but
  its extrapolation error compounds over the long horizons of slow
  units.
- recent_slope: straight-line fit on the last few observations only;
  adapts to local behaviour but is noise-sensitive.
- knn_trajectory: matches the unit's current signal level and local
  slope against training trajectories and averages the neighbours'
  remaining lives. In the seeded experiment this is the full-fleet
  truth winner - and the family the naive leaderboards dethrone.
"""

import math

from .models import FAILURE_THRESHOLD

MIN_RUL = 1.0


def _clip(rul, cap=None):
    if rul is None or rul != rul:
        return None
    if rul < MIN_RUL:
        return MIN_RUL
    if cap is not None and rul > cap:
        return cap
    return rul


def _ols(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / float(n)
    my = sum(ys) / float(n)
    sxx = 0.0
    sxy = 0.0
    for x, y in zip(xs, ys):
        sxx += (x - mx) * (x - mx)
        sxy += (x - mx) * (y - my)
    if sxx <= 0:
        return None
    slope = sxy / sxx
    intercept = my - slope * mx
    return slope, intercept


class MeanLifePredictor(object):
    name = "mean_life"

    def fit(self, train):
        self.mean_failure = sum(t.failure_time for t in train) / float(len(train))
        self.cap = 3.0 * self.mean_failure
        return self

    def predict(self, traj, age):
        return _clip(self.mean_failure - age, self.cap)


class LinearTrendPredictor(object):
    name = "linear_trend"

    def fit(self, train):
        self.mean_failure = sum(t.failure_time for t in train) / float(len(train))
        self.cap = 3.0 * self.mean_failure
        return self

    def predict(self, traj, age):
        times, signal = traj.history(age)
        fit = _ols([float(t) for t in times], signal)
        if fit is None:
            return _clip(self.mean_failure - age, self.cap)
        slope, intercept = fit
        if slope <= 1e-9:
            return _clip(self.mean_failure - age, self.cap)
        t_hit = (FAILURE_THRESHOLD - intercept) / slope
        return _clip(t_hit - age, self.cap)


class ExponentialTrendPredictor(object):
    name = "exponential_trend"

    def fit(self, train):
        self.mean_failure = sum(t.failure_time for t in train) / float(len(train))
        self.cap = 3.0 * self.mean_failure
        return self

    def predict(self, traj, age):
        times, signal = traj.history(age)
        logged = [math.log(max(s, 1e-6)) for s in signal]
        fit = _ols([float(t) for t in times], logged)
        if fit is None:
            return _clip(self.mean_failure - age, self.cap)
        slope, intercept = fit
        if slope <= 1e-9:
            return _clip(self.mean_failure - age, self.cap)
        t_hit = (math.log(FAILURE_THRESHOLD) - intercept) / slope
        return _clip(t_hit - age, self.cap)


class RecentSlopePredictor(object):
    name = "recent_slope"
    window = 5

    def fit(self, train):
        self.mean_failure = sum(t.failure_time for t in train) / float(len(train))
        self.cap = 3.0 * self.mean_failure
        return self

    def predict(self, traj, age):
        times, signal = traj.history(age)
        times = times[-self.window:]
        signal = signal[-self.window:]
        fit = _ols([float(t) for t in times], signal)
        if fit is None:
            return _clip(self.mean_failure - age, self.cap)
        slope, intercept = fit
        if slope <= 1e-9:
            return _clip(self.mean_failure - age, self.cap)
        t_hit = (FAILURE_THRESHOLD - intercept) / slope
        return _clip(t_hit - age, self.cap)


class KnnTrajectoryPredictor(object):
    name = "knn_trajectory"
    k = 5

    def fit(self, train):
        self.train = list(train)
        self.mean_failure = sum(t.failure_time for t in train) / float(len(train))
        self.cap = 3.0 * self.mean_failure
        return self

    def _level_and_slope(self, traj, age):
        times, signal = traj.history(age)
        level = math.log(max(signal[-1], 1e-6))
        if len(signal) >= 3:
            fit = _ols([float(t) for t in times[-3:]],
                       [math.log(max(s, 1e-6)) for s in signal[-3:]])
            slope = fit[0] if fit else 0.0
        else:
            slope = 0.0
        return level, slope

    def predict(self, traj, age):
        level, slope = self._level_and_slope(traj, age)
        scored = []
        for other in self.train:
            if other.failure_time <= age:
                continue
            o_level, o_slope = self._level_and_slope(other, age)
            dist = abs(level - o_level) + 0.5 * abs(slope - o_slope)
            scored.append((dist, other.failure_time - age))
        if not scored:
            return _clip(self.mean_failure - age, self.cap)
        scored.sort(key=lambda pair: pair[0])
        neighbours = scored[:self.k]
        total_w = 0.0
        total = 0.0
        for dist, rul in neighbours:
            w = 1.0 / (1.0 + dist)
            total_w += w
            total += w * rul
        return _clip(total / total_w, self.cap)


def all_predictors():
    return [
        MeanLifePredictor(),
        LinearTrendPredictor(),
        ExponentialTrendPredictor(),
        RecentSlopePredictor(),
        KnnTrajectoryPredictor(),
    ]


PREDICTOR_NAMES = [p.name for p in all_predictors()]
