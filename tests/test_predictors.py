from rul_audit.predictors import PREDICTOR_NAMES, all_predictors


def test_five_predictor_families():
    assert len(all_predictors()) == 5
    assert len(set(PREDICTOR_NAMES)) == 5


def test_all_predict_positive_rul(fitted_predictors, test_fleet):
    for predictor in fitted_predictors:
        for traj in test_fleet[:5]:
            if traj.failure_time > 80:
                pred = predictor.predict(traj, 80)
                assert pred is not None
                assert pred >= 1.0


def test_predictions_are_capped(fitted_predictors, test_fleet):
    for predictor in fitted_predictors:
        cap = predictor.cap
        for traj in test_fleet:
            for age in (40, 80, 120):
                if traj.failure_time > age:
                    pred = predictor.predict(traj, age)
                    assert pred <= cap


def test_mean_life_uses_training_mean(fitted_predictors, test_fleet):
    mean_pred = [p for p in fitted_predictors if p.name == "mean_life"][0]
    traj = [t for t in test_fleet if t.failure_time > 40][0]
    assert mean_pred.predict(traj, 40) == mean_pred.mean_failure - 40


def test_exponential_beats_linear_on_fast_units(fitted_predictors, test_fleet):
    from rul_audit.models import rmse
    by_name = dict((p.name, p) for p in fitted_predictors)
    fast = [t for t in test_fleet if t.group == "fast" and t.failure_time > 80]
    exp_err = rmse([(by_name["exponential_trend"].predict(t, 80),
                     t.true_rul(80)) for t in fast])
    lin_err = rmse([(by_name["linear_trend"].predict(t, 80),
                     t.true_rul(80)) for t in fast])
    assert exp_err < lin_err


def test_knn_skips_training_units_dead_at_age(fitted_predictors, test_fleet):
    knn = [p for p in fitted_predictors if p.name == "knn_trajectory"][0]
    traj = [t for t in test_fleet if t.failure_time > 120][0]
    pred = knn.predict(traj, 120)
    assert pred is not None and pred >= 1.0


def test_predictor_names_match_panel():
    names = [p.name for p in all_predictors()]
    assert names == PREDICTOR_NAMES
