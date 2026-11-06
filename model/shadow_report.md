# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 2 (2026-11-05 to 2026-11-06)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 895 | 16 | 50.9 | 1.92 | -3.3 | -9.2 to +3.4 | Not met |
| R1 Under above bias-adjusted AU consensus | 356 | 16 | 49.7 | 2.00 | -1.1 | -10.2 to +6.9 | Not met |
| R2 R1 and the model agrees | 94 | 16 | 51.1 | 1.98 | -0.5 | -16.6 to +18.0 | Not met |
| R2 capped, 1 per player, 2 per game | 30 | 16 | 53.3 | 2.08 | +12.2 | -18.2 to +44.3 | Not met |
| S1 best AU price above reference price by 2%+ | 87 | 16 | 60.9 | 2.00 | +20.1 | -4.6 to +44.7 | Not met |
| S1 capped, 1 per player, 2 per game | 32 | 16 | 59.4 | 2.01 | +15.9 | -24.3 to +54.9 | Not met |

Under hit rate minus de-vigged AU market: +0.46 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 660 props across 16 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68848 | | |
| AU minus Over bias | 0.68935 | +0.00086 | -0.00338 to +0.00560 |
| Reference, all | 0.68748 | -0.00100 | -0.00316 to +0.00097 |
| AU and reference, 50/50 | 0.68783 | -0.00065 | -0.00172 to +0.00032 |
| Same blend + 5% model | 0.68794 | -0.00055 | -0.00153 to +0.00047 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 831 | 0.68754 | 0.68865 |
| Novig, ProphetX, Polymarket | 853 | 0.68587 | 0.68766 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 15 | 4 | 8 | 3 | +0.00 |
| Diff 3 | 14 | 1 | 8 | 5 | -0.25 |
