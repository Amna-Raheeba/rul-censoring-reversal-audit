# RUL Censoring-Reversal Audit

## 1. What this is

A stress-audit that shows how **right-censoring silently reverses
remaining-useful-life (RUL) model leaderboards** in PHM benchmarks.

Most PHM test sets contain units that never failed during the study —
they were still running, or were pulled for preventive maintenance.
The common scoring practice is to **drop those censored units** and
rank models on the failures that remain. This tool measures what that
practice does to the ranking itself: it takes complete run-to-failure
fleets (where the true RUL of every unit is known), applies seeded
censoring regimes, re-scores a panel of RUL predictors the naive way,
and compares the naive leaderboard against the uncensored truth.

The headline object is the **rank-reversal rate**: how often the naive
leaderboard's winner is not the true winner — plus the winner's
true-RMSE penalty (how much worse the crowned model really is) and the
Kendall tau between the two rankings.

## 2. The novel mechanism

1. Generate a complete run-to-failure fleet with a seeded synthetic
   degradation generator (Section 4). Ground-truth failure times are
   known exactly, so the uncensored leaderboard is computable — the
   thing real benchmarks can never check.
2. Apply a ladder of **controlled censoring regimes** at target rates
   of 10–70% (Section 5), each calibrated by deterministic bisection
   on the fleet itself.
3. Score a panel of five predictor families (Section 6) twice: on all
   cases (truth) and on uncensored units only (naive, drop-censored).
4. Report, per regime and rate: rank-reversal rate, winner's
   true-RMSE penalty, and Kendall tau, aggregated over 20 seeded
   fleets.

No existing tool measures leaderboard fragility to censoring as the
primary output (Section 3).

## 3. Prior art and the differentiator

- **Survival / IPCW evaluation** (Uno's C-index, IPCW-weighted
  metrics) *corrects* a metric for censoring. It assumes the corrected
  metric is the answer; it never asks whether the published ranking
  flips.
- **The 2026 VRLA battery benchmark** and **PHM-Europe 2024
  censored-data LSTM/Transformer work** *handle* censoring inside a
  model or a metric, on data where the uncensored truth is unknown.
- **C-MAPSS-style benchmarks** ship with censored test units and are
  routinely scored by dropping or truncating them, unaudited.

**Differentiator:** this is an *audit of rankings*, not a model and
not a corrected metric. It works on complete data where the truth is
known, varies the censoring regime and rate as controlled factors,
and reports reversal rate / winner penalty / ranking correlation as
the primary outputs.

## 4. The fleet generator

- Each unit's true degradation grows exponentially,
  `d(t) = d0 * exp(rate * t)`, and the unit fails when `d` crosses
  1.0, so `T = ln(1 / d0) / rate` exactly.
- The observed signal is the true degradation plus Gaussian noise
  (sigma 0.009), sampled every 5 cycles.
- The fleet mixes two sub-populations: **fast** degraders (45%, short
  lives) and **slow** degraders (55%, long lives), with a wide spread
  of initial degradation `d0`. That mixture is what makes censoring
  dangerous: any regime that removes one sub-population more than the
  other silently changes which units the leaderboard is scored on.
- Prediction cases: every unit still alive at ages 40, 80, and 120
  cycles contributes one RUL prediction case (359 cases per 120-unit
  fleet).

## 5. The censoring regimes

Each regime assigns every unit a censoring time `C`; a unit with
`C < T` is censored, and naive scoring drops it entirely. Each regime
is calibrated to hit the target rate on the fleet being censored.

1. **fixed_horizon** — one shared study horizon (the lifetime
   quantile for the target rate). Deterministically truncates the
   retained fleet's lifetimes: only short-lived units remain.
2. **random** — censoring times drawn independently of the unit
   (uniform, scale bisected to the target rate). The textbook
   "non-informative" control — which, measured here, is **not** safe
   for drop-censored leaderboards: a random censoring clock still
   removes long-lived units more often, because they live longer
   under it. Measured on one 120-unit fleet at a 50% target rate:
   random censoring removed 66% of slow units vs 20% of fast units;
   the failure-dependent regime removed 64% vs 23%.
3. **failure_dependent** — at each observation step the unit may be
   pulled for preventive maintenance with hazard proportional to the
   square of its current degradation level. Long-lived units
   accumulate the most exposure to this hazard, so the retained fleet
   skews short-lived — measurably, though less sharply than under a
   fixed horizon.

## 6. The predictor panel

Five simple families, fitted on a separate complete training fleet:

| Predictor | Idea | Behaviour |
|---|---|---|
| `mean_life` | population average remaining life | blind to the unit |
| `linear_trend` | straight-line extrapolation to failure | under-predicts on convex growth; worst on fast units |
| `exponential_trend` | log-linear extrapolation | matches the true law; best on fast units, error compounds on long slow horizons |
| `recent_slope` | linear fit on the last 5 observations | adapts locally, noise-sensitive |
| `knn_trajectory` | match current level + local slope to training trajectories, average neighbours' RUL | the full-fleet truth winner (19 of 20 seeds) — and the family the naive leaderboards dethrone |

All predictions are clipped to `[1, 3 x mean training life]`, as any
deployed predictor would be.

## 7. Measured headline results

Full run: 20 seeded fleets (seeds 101–120), 120 test units each,
5 predictors, 3 regimes x 7 target rates. Reproduction:
`python -m rul_audit evaluate --out results`.

- **Truth winner:** `knn_trajectory` on 19 of 20 fleets.
- **Fixed horizon is the most destructive regime.** Reversal rate
  rises from 0.15 at 10% censoring to **0.95 at 50–70% censoring**;
  the naive winner's true RMSE is **17.6% worse** than the true
  winner's; Kendall tau falls to 0.81.
- **Random censoring is not a safe control.** Reversal rate climbs
  from 0.10 (10%) to **0.90 (70%)**, mean 0.50 across rates — a random
  censoring *time* still selects on survival, because long-lived
  units spend longer exposed to the clock.
- **Failure-dependent (preventive-maintenance) censoring** reverses
  the winner in 5% of fleets at 10% censoring and **80% at 70%**,
  mean 0.36 across rates, with winner penalties up to 13.9%.
- The naive winner, when the ranking reverses, is almost always
  `exponential_trend`: it is genuinely the best model *on the
  retained short-lived-heavy fleet* — the leaderboard is not noisy,
  it is answering a different question.

Full table: `results/evaluation_summary.md`. Machine-readable:
`results/evaluation.json` / `results/evaluation.csv`.

## 8. How to run

```bash
pip install -r requirements.txt        # stdlib only at runtime
python -m rul_audit demo               # one fleet (seed 7), all conditions
python -m rul_audit evaluate --out results   # the 20-seed headline run
python scripts/reproduce_results.py    # drift-guarded reproduction
python notebooks/01_demo_run.py
python notebooks/02_evaluation_experiment.py
streamlit run app.py                   # dashboard: Leaderboards / Reversals / Evaluation
pytest -q
```

## 9. Repository layout

```
rul_audit/        package: generator, predictors, censoring, scoring, audit
data/             seeded demo fleet summary (seed 7)
examples/         one demo case + a sample audit report
notebooks/        runnable .py notebooks (demo + evaluation experiment)
scripts/          build_cases.py, reproduce_results.py (drift guard)
results/          evaluation.json / .csv / summary + HEADLINE.md
tests/            pytest suite
app.py            Streamlit dashboard (3 tabs)
```

## 10. Honest limits

- **Synthetic data only.** The fleets come from a seeded exponential
  degradation generator with two sub-populations, not from C-MAPSS or
  field data. The audit measures the *evaluation practice*, and the
  reversal rates are properties of this generator and predictor
  panel — the qualitative claim (drop-censored leaderboards are
  censoring artifacts) is what transfers, not the exact percentages.
- **Simple predictors.** Five deliberately small families, no deep
  learning. A stronger panel might be more or less fragile; the audit
  harness accepts any predictor with `fit`/`predict`.
- **One prediction protocol.** Cases at ages 40/80/120 with
  unit-level drop-censored scoring. Case-level censoring (dropping
  only post-censoring observations) is a milder practice and would
  show smaller effects.
- **Regime ordering is empirical, not a theorem.** Fixed horizon >
  random > failure-dependent in reversal severity *on this
  generator*, because what matters is how sharply the retained
  fleet's lifetime mix is skewed — a differently shaped hazard could
  reorder them.

## 11. Author and license

Author: Amna Raheeba. MIT license (see `LICENSE`).
