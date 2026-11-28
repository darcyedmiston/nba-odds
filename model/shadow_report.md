# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 22 (2026-11-05 to 2026-11-26)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 8511 | 161 | 50.7 | 1.91 | -4.1 | -6.6 to -1.6 | Not met |
| R1 Under above bias-adjusted AU consensus | 3085 | 161 | 47.4 | 2.02 | -5.0 | -8.6 to -1.3 | Not met |
| R2 R1 and the model agrees | 1018 | 158 | 48.3 | 2.00 | -4.3 | -9.9 to +1.3 | Not met |
| R2 capped, 1 per player, 2 per game | 308 | 158 | 49.7 | 2.09 | +2.9 | -8.8 to +14.5 | Not met |
| S1 best AU price above reference price by 2%+ | 895 | 159 | 49.6 | 1.99 | -2.9 | -9.4 to +3.9 | Not met |
| S1 capped, 1 per player, 2 per game | 309 | 159 | 49.5 | 2.03 | -1.3 | -12.2 to +9.8 | Not met |

Under hit rate minus de-vigged AU market: +0.16 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 6876 props across 161 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68789 | | |
| AU minus Over bias | 0.68973 | +0.00184 | +0.00022 to +0.00351 |
| Reference, all | 0.68837 | +0.00048 | -0.00051 to +0.00140 |
| AU and reference, 50/50 | 0.68796 | +0.00007 | -0.00042 to +0.00053 |
| Same blend + 5% model | 0.68793 | +0.00004 | -0.00047 to +0.00052 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 7985 | 0.68767 | 0.68753 |
| Novig, ProphetX, Polymarket | 8294 | 0.68851 | 0.68761 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 70 | 17 | 42 | 11 | +0.00 |
| Diff 3 | 177 | 28 | 125 | 24 | +0.01 |
