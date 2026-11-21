# Evaluation summary

Seeds: 20 (101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120). Predictors: 5 families. Censoring regimes: fixed_horizon, random, failure_dependent. Target censoring rates: 0.1-0.7.

Truth-winner counts across seeds: exponential_trend x1, knn_trajectory x19

| Regime | Target rate | Achieved rate | Reversal rate | Mean winner penalty | Mean Kendall tau |
|---|---|---|---|---|---|
| fixed_horizon | 0.1 | 0.092 | 0.150 | 1.8% | 0.970 |
| fixed_horizon | 0.2 | 0.192 | 0.400 | 5.4% | 0.920 |
| fixed_horizon | 0.3 | 0.292 | 0.600 | 8.9% | 0.860 |
| fixed_horizon | 0.4 | 0.392 | 0.850 | 14.6% | 0.820 |
| fixed_horizon | 0.5 | 0.492 | 0.950 | 17.6% | 0.810 |
| fixed_horizon | 0.6 | 0.592 | 0.950 | 17.6% | 0.810 |
| fixed_horizon | 0.7 | 0.692 | 0.950 | 17.6% | 0.810 |
| random | 0.1 | 0.135 | 0.100 | 0.6% | 0.980 |
| random | 0.2 | 0.203 | 0.250 | 2.1% | 0.950 |
| random | 0.3 | 0.300 | 0.350 | 3.4% | 0.930 |
| random | 0.4 | 0.401 | 0.550 | 6.4% | 0.890 |
| random | 0.5 | 0.501 | 0.650 | 9.2% | 0.870 |
| random | 0.6 | 0.598 | 0.700 | 10.6% | 0.860 |
| random | 0.7 | 0.702 | 0.900 | 16.4% | 0.820 |
| failure_dependent | 0.1 | 0.097 | 0.050 | 0.1% | 0.990 |
| failure_dependent | 0.2 | 0.202 | 0.100 | 0.4% | 0.980 |
| failure_dependent | 0.3 | 0.301 | 0.250 | 2.3% | 0.950 |
| failure_dependent | 0.4 | 0.399 | 0.300 | 2.8% | 0.940 |
| failure_dependent | 0.5 | 0.501 | 0.400 | 4.7% | 0.920 |
| failure_dependent | 0.6 | 0.599 | 0.650 | 10.4% | 0.870 |
| failure_dependent | 0.7 | 0.700 | 0.800 | 13.9% | 0.840 |

Worst condition: fixed_horizon at target rate 0.5 - reversal rate 0.950, mean winner penalty 17.6%.

Mean reversal rate, failure-dependent censoring: 0.364. Mean reversal rate, random (non-informative) censoring: 0.500.
