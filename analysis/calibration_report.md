# Calibration-by-side test (2026-11-06 to 2026-11-16, walk-forward)

Out-of-sample props: 8728 over 11 days; training window = all earlier days (min 7). 1-unit flat stakes at the logged best price. No-vig fair price available for 61% of rows (median overround of best-price pairs 1.042).

## Probability accuracy (Brier, lower = better)

| Source | Brier |
|---|---|
| Raw model prob | 0.2541 |
| Calibrated (by side) | 0.2495 |
| Implied 1/odds | 0.2468 |
| No-vig fair (rows with both sides) | 0.2469 |

## Selection rules, out of sample

| Rule | n | Hit % | Units | ROI % |
|---|---|---|---|---|
| Current: Diff 3+ Overs | 139 | 48.9 | -16.4 | -11.8 |
| Current tiers, both sides | 611 | 53.0 | -25.2 | -4.1 |
| Over: calibrated > implied + 0.00 | 766 | 46.9 | -27.4 | -3.6 |
| Over: calibrated > implied + 0.03 | 399 | 49.1 | +12.3 | +3.1 |
| Over: calibrated > implied + 0.05 | 237 | 49.4 | +14.7 | +6.2 |
| Over: calibrated > no-vig fair + 0.00 | 945 | 45.6 | -56.7 | -6.0 |
| Over: calibrated > no-vig fair + 0.03 | 541 | 46.8 | -6.3 | -1.2 |
| Over: calibrated > no-vig fair + 0.05 | 304 | 48.7 | +14.4 | +4.7 |
| Under: calibrated > implied + 0.00 | 3007 | 53.7 | +31.3 | +1.0 |
| Under: calibrated > implied + 0.03 | 1692 | 51.6 | -23.6 | -1.4 |
| Under: calibrated > implied + 0.05 | 836 | 48.9 | -43.6 | -5.2 |
| Under: calibrated > no-vig fair + 0.00 | 2032 | 53.2 | +38.6 | +1.9 |
| Under: calibrated > no-vig fair + 0.03 | 1569 | 51.6 | -8.1 | -0.5 |
| Under: calibrated > no-vig fair + 0.05 | 1158 | 50.8 | -24.7 | -2.1 |
| Both: calibrated > implied + 0.00 | 3773 | 52.3 | +3.9 | +0.1 |
| Both: calibrated > implied + 0.03 | 2091 | 51.1 | -11.3 | -0.5 |
| Both: calibrated > implied + 0.05 | 1073 | 49.0 | -28.9 | -2.7 |
| Both: calibrated > no-vig fair + 0.00 | 2977 | 50.8 | -18.1 | -0.6 |
| Both: calibrated > no-vig fair + 0.03 | 2110 | 50.4 | -14.4 | -0.7 |
| Both: calibrated > no-vig fair + 0.05 | 1462 | 50.3 | -10.3 | -0.7 |

## Reliability of calibrated probabilities (out of sample)

| Side | Bucket | n | Mean calibrated | Actual hit |
|---|---|---|---|---|
| Over | (0.0, 0.45] | 529 | 0.366 | 0.452 |
| Over | (0.45, 0.5] | 2462 | 0.475 | 0.482 |
| Over | (0.5, 0.55] | 1008 | 0.527 | 0.526 |
| Over | (0.55, 0.6] | 261 | 0.563 | 0.544 |
| Over | (0.6, 0.65] | 56 | 0.629 | 0.661 |
| Over | (0.65, 1.0] | 48 | 0.721 | 0.521 |
| Under | (0.0, 0.45] | 90 | 0.361 | 0.500 |
| Under | (0.45, 0.5] | 628 | 0.485 | 0.475 |
| Under | (0.5, 0.55] | 846 | 0.528 | 0.566 |
| Under | (0.55, 0.6] | 2109 | 0.570 | 0.554 |
| Under | (0.6, 0.65] | 531 | 0.624 | 0.584 |
| Under | (0.65, 1.0] | 160 | 0.729 | 0.556 |

## By day (best no-vig rule vs current)

| Day | Current Diff3+ Overs units | Both: cal > fair + 0.03 units (n) |
|---|---|---|
| 2026-11-06 | +1.3 (4) | -10.7 (63) |
| 2026-11-07 | +0.3 (18) | +10.8 (246) |
| 2026-11-08 | -10.3 (14) | -10.8 (183) |
| 2026-11-09 | +3.6 (13) | +12.7 (214) |
| 2026-11-10 | -2.5 (15) | -8.1 (216) |
| 2026-11-11 | +3.5 (11) | +12.3 (187) |
| 2026-11-12 | +0.7 (14) | +40.7 (298) |
| 2026-11-13 | -1.7 (7) | -13.9 (117) |
| 2026-11-14 | -2.3 (18) | -9.0 (270) |
| 2026-11-15 | -6.3 (10) | -32.8 (131) |
| 2026-11-16 | -2.7 (15) | -5.7 (185) |

Caveats: one season, 18 days; settled at best book including possibly stale one-book lines; best-price Over/Under pairs from different books understate the vig, so 'fair' is optimistic. Analysis only - no change to model.py, weights, thresholds or stakes.

## Does the model add information beyond the market? (logistic regression, all settled rows with both sides priced, n = 9,724)

win ~ logit(no-vig fair) + logit(model_prob)

| Sample | Market coef (se) | Model coef (se) | p(model) | Constant |
|---|---|---|---|---|
| Overs (n 4,862) | 1.015 (0.158) | -0.068 (0.092) | 0.46 | -0.093 |
| All (n 9,724) | 1.129 (0.109) | -0.103 (0.065) | 0.11 | 0.000 |

Reading: once the no-vig price is known, model probability carries no extra information (coefficient ~0, wrong sign).
The Over constant of -0.093 logits (~2.3 pp) means Overs land below their no-vig fair probability across the board - a market-wide Over bias, not a model edge.
