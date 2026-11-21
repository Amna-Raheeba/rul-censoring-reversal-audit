# RUL Censoring-Reversal Audit - seed 7

## Uncensored truth leaderboard (RMSE, lower is better)

1. knn_trajectory - 136.49
2. exponential_trend - 154.89
3. mean_life - 217.53
4. recent_slope - 414.90
5. linear_trend - 503.38

## Naive leaderboards under censoring

| Regime | Target rate | Achieved rate | Naive winner | Truth winner | Reversal | Winner true-RMSE penalty | Kendall tau |
|---|---|---|---|---|---|---|---|
| fixed_horizon | 0.1 | 0.092 | knn_trajectory | knn_trajectory | no | 0.0% | 1.00 |
| fixed_horizon | 0.2 | 0.192 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| fixed_horizon | 0.3 | 0.292 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| fixed_horizon | 0.4 | 0.392 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| fixed_horizon | 0.5 | 0.492 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| fixed_horizon | 0.6 | 0.592 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| fixed_horizon | 0.7 | 0.692 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| random | 0.1 | 0.142 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| random | 0.2 | 0.192 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| random | 0.3 | 0.300 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| random | 0.4 | 0.400 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| random | 0.5 | 0.492 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| random | 0.6 | 0.600 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| random | 0.7 | 0.692 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| failure_dependent | 0.1 | 0.100 | knn_trajectory | knn_trajectory | no | 0.0% | 1.00 |
| failure_dependent | 0.2 | 0.200 | knn_trajectory | knn_trajectory | no | 0.0% | 1.00 |
| failure_dependent | 0.3 | 0.308 | knn_trajectory | knn_trajectory | no | 0.0% | 1.00 |
| failure_dependent | 0.4 | 0.400 | knn_trajectory | knn_trajectory | no | 0.0% | 1.00 |
| failure_dependent | 0.5 | 0.500 | knn_trajectory | knn_trajectory | no | 0.0% | 1.00 |
| failure_dependent | 0.6 | 0.608 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
| failure_dependent | 0.7 | 0.700 | exponential_trend | knn_trajectory | YES | 13.5% | 0.80 |
