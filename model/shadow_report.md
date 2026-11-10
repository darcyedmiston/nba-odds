# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 6 (2026-11-05 to 2026-11-10)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 2552 | 47 | 51.6 | 1.91 | -2.4 | -7.3 to +2.7 | Not met |
| R1 Under above bias-adjusted AU consensus | 959 | 47 | 48.9 | 2.01 | -2.7 | -8.8 to +3.1 | Not met |
| R2 R1 and the model agrees | 266 | 45 | 48.9 | 1.99 | -4.5 | -14.8 to +6.1 | Not met |
| R2 capped, 1 per player, 2 per game | 87 | 45 | 51.7 | 2.08 | +7.4 | -10.3 to +24.9 | Not met |
| S1 best AU price above reference price by 2%+ | 262 | 47 | 53.1 | 1.99 | +4.3 | -9.1 to +17.0 | Not met |
| S1 capped, 1 per player, 2 per game | 94 | 47 | 53.2 | 2.03 | +4.6 | -16.9 to +24.7 | Not met |

Under hit rate minus de-vigged AU market: +1.03 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 1915 props across 47 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68733 | | |
| AU minus Over bias | 0.68738 | +0.00005 | -0.00323 to +0.00321 |
| Reference, all | 0.68685 | -0.00048 | -0.00222 to +0.00129 |
| AU and reference, 50/50 | 0.68693 | -0.00040 | -0.00127 to +0.00049 |
| Same blend + 5% model | 0.68698 | -0.00035 | -0.00125 to +0.00059 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 2375 | 0.68654 | 0.68719 |
| Novig, ProphetX, Polymarket | 2460 | 0.68634 | 0.68684 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 34 | 9 | 21 | 4 | +0.09 |
| Diff 3 | 39 | 5 | 28 | 6 | -0.04 |
