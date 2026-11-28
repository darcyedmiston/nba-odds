# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 23 (2026-11-05 to 2026-11-28)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 9173 | 172 | 50.9 | 1.91 | -3.8 | -6.2 to -1.4 | Not met |
| R1 Under above bias-adjusted AU consensus | 3286 | 172 | 47.7 | 2.02 | -4.4 | -7.9 to -0.8 | Not met |
| R2 R1 and the model agrees | 1079 | 169 | 48.9 | 2.00 | -2.7 | -8.1 to +2.9 | Not met |
| R2 capped, 1 per player, 2 per game | 329 | 169 | 50.8 | 2.10 | +5.7 | -5.9 to +17.5 | Not met |
| S1 best AU price above reference price by 2%+ | 996 | 170 | 49.6 | 1.99 | -2.9 | -8.8 to +3.5 | Not met |
| S1 capped, 1 per player, 2 per game | 331 | 170 | 50.5 | 2.03 | +0.2 | -10.0 to +11.0 | Not met |

Under hit rate minus de-vigged AU market: +0.34 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 7433 props across 172 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68768 | | |
| AU minus Over bias | 0.68940 | +0.00172 | +0.00016 to +0.00329 |
| Reference, all | 0.68823 | +0.00055 | -0.00040 to +0.00137 |
| AU and reference, 50/50 | 0.68778 | +0.00010 | -0.00037 to +0.00051 |
| Same blend + 5% model | 0.68774 | +0.00005 | -0.00043 to +0.00051 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 8617 | 0.68753 | 0.68732 |
| Novig, ProphetX, Polymarket | 8942 | 0.68819 | 0.68734 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 74 | 18 | 45 | 11 | +0.03 |
| Diff 3 | 181 | 28 | 129 | 24 | +0.01 |
