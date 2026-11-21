# Changelog

## 0.1.0 - 2026-11-21

- Initial release: seeded synthetic run-to-failure fleet generator
  (fast/slow degradation mixture, exponential degradation law, known
  ground-truth failure times).
- Five RUL predictor families: mean life, linear trend, exponential
  trend, recent slope, kNN trajectory matching.
- Three seeded censoring regimes calibrated to target rates of
  10-70%: fixed horizon, random, and failure-dependent
  (degradation-hazard preventive-maintenance removal).
- Leaderboard audit: naive drop-censored scoring vs the uncensored
  truth, with rank-reversal rate, winner's true-RMSE penalty, and
  Kendall tau as the headline objects.
- Streamlit dashboard (3 tabs), CLI demo/evaluate commands, and a
  reproduction script with a headline-drift guard.
