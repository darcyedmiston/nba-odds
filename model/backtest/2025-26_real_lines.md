# Model v4 against real closing AU lines, 2025-26

291 games with props; train before 2026-02-01 (174 games), holdout from 2026-02-01 (117 games). Lines are 5 min before tip. D5 is 0 (no historical injury status). D7 has no totals or spreads.

## 1. Does the model add to the market?

`logit(win) = a + b*logit(de-vigged market) + c*logit(model)`, Overs at the most common line, errors clustered by game. c near 0 means no added information.

| Set | Props | a | b (market) | c (model) | c 95% CI | c p-value |
|---|---|---|---|---|---|---|
| Train | 13140 | -0.075 | 1.005 | +0.149 | +0.050 to +0.249 | 0.003 |
| Holdout | 8243 | -0.066 | 0.977 | +0.028 | -0.120 to +0.176 | 0.710 |

## 2. Holdout accuracy (lower is better)

| Forecast | Log-loss | Brier |
|---|---|---|
| De-vigged market | 0.68494 | 0.24603 |
| Model alone | 0.70561 | 0.25511 |
| Coin flip | 0.69315 | 0.25000 |
| Market + model (fit on train) | 0.68486 | 0.24599 |
| Market + D1-D8 (regularised, fit on train) | 0.68419 | 0.24566 |

Fitted on train only; not applied to the model:

| Input | Coefficient |
|---|---|
| market | +1.013 |
| D1 | -0.024 |
| D2 | +0.021 |
| D3 | +0.029 |
| D4 | +0.033 |
| D5 | +0.000 |
| D6 | +0.023 |
| D7 | +0.018 |
| D8 | -0.036 |

## 3. Holdout calibration: model probability

| Bucket | Props | Avg model | Avg market | Hit % |
|---|---|---|---|---|
| (0.0, 0.4] | 1926 | 31.9 | 45.6 | 43.9 |
| (0.4, 0.45] | 1160 | 42.6 | 47.3 | 45.1 |
| (0.45, 0.5] | 1561 | 47.7 | 48.7 | 45.9 |
| (0.5, 0.55] | 1550 | 52.5 | 50.3 | 48.3 |
| (0.55, 0.6] | 1144 | 57.3 | 51.8 | 51.2 |
| (0.6, 0.65] | 615 | 62.2 | 53.3 | 51.4 |
| (0.65, 0.7] | 213 | 67.0 | 53.8 | 55.4 |
| (0.7, 1.0] | 74 | 73.5 | 53.3 | 64.9 |

## 4. Tier ROI at the best closing price (flat $10)

Before the 2-per-game cap. CI is a bootstrap by game.

| Set / side / tier | Props | Games | Hit % | ROI % | ROI 95% CI |
|---|---|---|---|---|---|
| train / Over / Diff 4 | 261 | 82 | 52.5 | -2.9 | -14.6 to +9.3 |
| train / Over / Diff 3 | 1263 | 164 | 52.3 | -3.3 | -8.7 to +2.4 |
| train / Over / Watchlist | 2344 | 174 | 52.7 | -0.5 | -4.6 to +3.4 |
| train / Over / Pass | 9272 | 174 | 46.4 | -10.1 | -12.3 to -7.7 |
| train / Under / Diff 4 | 504 | 117 | 58.3 | +6.4 | -3.7 to +16.0 |
| train / Under / Diff 3 | 1825 | 171 | 58.2 | +5.9 | +0.8 to +10.8 |
| train / Under / Watchlist | 2334 | 174 | 56.5 | +3.0 | -1.3 to +7.3 |
| train / Under / Pass | 8477 | 174 | 55.7 | -0.0 | -2.2 to +2.2 |
| holdout / Over / Diff 4 | 150 | 49 | 58.7 | +8.9 | -7.9 to +25.3 |
| holdout / Over / Diff 3 | 726 | 101 | 49.2 | -9.8 | -17.9 to -2.0 |
| holdout / Over / Watchlist | 1325 | 110 | 52.2 | -3.0 | -8.6 to +2.5 |
| holdout / Over / Pass | 6042 | 117 | 48.1 | -7.4 | -10.5 to -4.4 |
| holdout / Under / Diff 4 | 485 | 80 | 56.7 | +4.1 | -7.5 to +16.1 |
| holdout / Under / Diff 3 | 1200 | 108 | 52.2 | -4.2 | -10.6 to +1.4 |
| holdout / Under / Watchlist | 1323 | 117 | 55.0 | +0.2 | -5.5 to +6.2 |
| holdout / Under / Pass | 5235 | 117 | 56.5 | +1.3 | -1.6 to +4.3 |

## 5. Added checks on the same holdout

Benchmarks added after section 2 to read it correctly. No model settings were chosen from them.

| Comparison (holdout log-loss, negative favours the first) | Difference | 95% CI by game |
|---|---|---|
| Market + intercept vs raw de-vigged market | -0.00043 | -0.00154 to +0.00072 |
| Market + D1-D8 vs market + intercept | -0.00032 | -0.00133 to +0.00069 |

| Set / side, every prop at best closing price | Props | Hit % | ROI % | ROI 95% CI |
|---|---|---|---|---|
| Train / Over | 13,140 | 48.2 | -7.6 | -9.6 to -5.5 |
| Train / Under | 13,140 | 56.3 | +1.6 | -0.3 to +3.4 |
| Holdout / Over | 8,243 | 49.1 | -6.6 | -9.1 to -4.1 |
| Holdout / Under | 8,243 | 55.6 | +0.5 | -1.8 to +3.0 |

Diff 3+ Overs at best price: train -3.2% (n=1,524, -8.3 to +1.9), holdout -6.6% (n=876, -14.6 to +1.4).

Overs at the most common line hit below the de-vigged market in both sets: 46.6% vs 48.7% (train), 47.3% vs 49.0% (holdout).

The holdout has now been used. Further tuning needs new data, such as the rest of 2025-26 or live 2026-27 results.
