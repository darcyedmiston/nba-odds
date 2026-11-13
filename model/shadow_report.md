# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 9 (2026-11-05 to 2026-11-13)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 3606 | 67 | 52.1 | 1.91 | -1.6 | -5.7 to +2.3 | Not met |
| R1 Under above bias-adjusted AU consensus | 1349 | 67 | 48.9 | 2.01 | -2.7 | -7.7 to +2.0 | Not met |
| R2 R1 and the model agrees | 406 | 65 | 50.7 | 1.99 | -0.4 | -8.9 to +8.0 | Not met |
| R2 capped, 1 per player, 2 per game | 125 | 65 | 53.6 | 2.09 | +11.8 | -4.9 to +29.4 | Not met |
| S1 best AU price above reference price by 2%+ | 368 | 67 | 52.7 | 1.99 | +4.1 | -6.5 to +14.8 | Not met |
| S1 capped, 1 per player, 2 per game | 133 | 67 | 48.9 | 2.03 | -2.8 | -20.6 to +15.3 | Not met |

Under hit rate minus de-vigged AU market: +1.48 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 2775 props across 67 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68728 | | |
| AU minus Over bias | 0.68724 | -0.00004 | -0.00253 to +0.00256 |
| Reference, all | 0.68635 | -0.00093 | -0.00231 to +0.00046 |
| AU and reference, 50/50 | 0.68666 | -0.00062 | -0.00131 to +0.00007 |
| Same blend + 5% model | 0.68660 | -0.00068 | -0.00144 to +0.00005 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 3382 | 0.68618 | 0.68661 |
| Novig, ProphetX, Polymarket | 3493 | 0.68584 | 0.68676 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 42 | 10 | 27 | 5 | +0.07 |
| Diff 3 | 55 | 7 | 39 | 9 | -0.06 |
