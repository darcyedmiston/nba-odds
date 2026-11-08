# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 4 (2026-11-05 to 2026-11-08)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 1771 | 32 | 51.7 | 1.91 | -2.3 | -8.5 to +4.2 | Not met |
| R1 Under above bias-adjusted AU consensus | 642 | 32 | 49.8 | 2.01 | -0.7 | -8.1 to +6.1 | Not met |
| R2 R1 and the model agrees | 172 | 31 | 48.3 | 1.99 | -5.1 | -18.3 to +8.0 | Not met |
| R2 capped, 1 per player, 2 per game | 60 | 31 | 50.0 | 2.09 | +6.1 | -15.1 to +27.9 | Not met |
| S1 best AU price above reference price by 2%+ | 175 | 32 | 54.9 | 2.00 | +9.2 | -6.7 to +24.6 | Not met |
| S1 capped, 1 per player, 2 per game | 64 | 32 | 57.8 | 2.04 | +16.0 | -10.2 to +42.1 | Not met |

Under hit rate minus de-vigged AU market: +1.13 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 1316 props across 32 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68739 | | |
| AU minus Over bias | 0.68770 | +0.00032 | -0.00371 to +0.00409 |
| Reference, all | 0.68768 | +0.00029 | -0.00179 to +0.00253 |
| AU and reference, 50/50 | 0.68738 | -0.00001 | -0.00104 to +0.00110 |
| Same blend + 5% model | 0.68754 | +0.00016 | -0.00094 to +0.00131 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 1648 | 0.68593 | 0.68665 |
| Novig, ProphetX, Polymarket | 1709 | 0.68729 | 0.68629 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 23 | 5 | 15 | 3 | +0.04 |
| Diff 3 | 30 | 3 | 21 | 6 | -0.10 |
