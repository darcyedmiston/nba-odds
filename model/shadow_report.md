# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 20 (2026-11-05 to 2026-11-24)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 7868 | 149 | 50.9 | 1.91 | -3.8 | -6.3 to -1.3 | Not met |
| R1 Under above bias-adjusted AU consensus | 2867 | 149 | 47.4 | 2.02 | -5.1 | -8.9 to -1.3 | Not met |
| R2 R1 and the model agrees | 954 | 146 | 47.8 | 2.00 | -5.3 | -11.0 to +0.9 | Not met |
| R2 capped, 1 per player, 2 per game | 285 | 146 | 48.1 | 2.10 | -0.0 | -11.5 to +12.6 | Not met |
| S1 best AU price above reference price by 2%+ | 809 | 147 | 50.3 | 1.99 | -1.5 | -8.1 to +5.5 | Not met |
| S1 capped, 1 per player, 2 per game | 285 | 147 | 49.1 | 2.03 | -2.2 | -13.9 to +9.7 | Not met |

Under hit rate minus de-vigged AU market: +0.31 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 6358 props across 149 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68824 | | |
| AU minus Over bias | 0.69004 | +0.00180 | +0.00014 to +0.00351 |
| Reference, all | 0.68864 | +0.00040 | -0.00066 to +0.00133 |
| AU and reference, 50/50 | 0.68827 | +0.00003 | -0.00049 to +0.00050 |
| Same blend + 5% model | 0.68823 | -0.00001 | -0.00054 to +0.00050 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 7388 | 0.68780 | 0.68768 |
| Novig, ProphetX, Polymarket | 7670 | 0.68810 | 0.68767 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 66 | 16 | 40 | 10 | +0.00 |
| Diff 3 | 154 | 24 | 109 | 21 | +0.01 |
