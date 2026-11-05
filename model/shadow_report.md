# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 1 (2026-11-05 to 2026-11-05)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 775 | 14 | 51.0 | 1.92 | -3.2 | -9.6 to +4.2 | Not met |
| R1 Under above bias-adjusted AU consensus | 315 | 14 | 50.5 | 2.00 | +0.3 | -8.4 to +8.8 | Not met |
| R2 R1 and the model agrees | 76 | 14 | 55.3 | 1.98 | +7.6 | -8.7 to +25.3 | Not met |
| R2 capped, 1 per player, 2 per game | 26 | 14 | 53.8 | 2.10 | +14.0 | -22.0 to +50.4 | Not met |
| S1 best AU price above reference price by 2%+ | 73 | 14 | 61.6 | 2.01 | +22.6 | -6.1 to +49.1 | Not met |
| S1 capped, 1 per player, 2 per game | 28 | 14 | 53.6 | 2.03 | +5.6 | -36.7 to +48.2 | Not met |

Under hit rate minus de-vigged AU market: +0.44 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 561 props across 14 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68861 | | |
| AU minus Over bias | 0.68905 | +0.00045 | -0.00481 to +0.00588 |
| Reference, all | 0.68778 | -0.00083 | -0.00330 to +0.00140 |
| AU and reference, 50/50 | 0.68805 | -0.00056 | -0.00178 to +0.00055 |
| Same blend + 5% model | 0.68790 | -0.00071 | -0.00177 to +0.00047 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 720 | 0.68805 | 0.68901 |
| Novig, ProphetX, Polymarket | 733 | 0.68658 | 0.68813 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 15 | 4 | 8 | 3 | +0.00 |
| Diff 3 | 12 | 1 | 7 | 4 | -0.21 |
