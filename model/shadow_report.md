# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 18 (2026-11-05 to 2026-11-22)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 6985 | 132 | 51.1 | 1.91 | -3.2 | -5.9 to -0.5 | Not met |
| R1 Under above bias-adjusted AU consensus | 2568 | 132 | 47.7 | 2.02 | -4.5 | -8.3 to -0.6 | Not met |
| R2 R1 and the model agrees | 845 | 129 | 47.1 | 2.00 | -6.8 | -12.5 to -0.6 | Not met |
| R2 capped, 1 per player, 2 per game | 252 | 129 | 47.6 | 2.09 | -0.9 | -13.7 to +12.4 | Not met |
| S1 best AU price above reference price by 2%+ | 677 | 130 | 50.7 | 1.98 | -0.8 | -8.4 to +7.0 | Not met |
| S1 capped, 1 per player, 2 per game | 251 | 130 | 49.8 | 2.02 | -1.3 | -14.3 to +12.0 | Not met |

Under hit rate minus de-vigged AU market: +0.58 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 5620 props across 132 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68823 | | |
| AU minus Over bias | 0.68973 | +0.00150 | -0.00026 to +0.00328 |
| Reference, all | 0.68837 | +0.00014 | -0.00097 to +0.00113 |
| AU and reference, 50/50 | 0.68814 | -0.00009 | -0.00065 to +0.00041 |
| Same blend + 5% model | 0.68818 | -0.00005 | -0.00062 to +0.00048 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 6552 | 0.68770 | 0.68759 |
| Novig, ProphetX, Polymarket | 6799 | 0.68766 | 0.68767 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 64 | 16 | 39 | 9 | +0.02 |
| Diff 3 | 131 | 19 | 93 | 19 | -0.01 |
