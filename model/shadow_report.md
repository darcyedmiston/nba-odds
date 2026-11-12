# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 8 (2026-11-05 to 2026-11-12)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 3380 | 63 | 52.3 | 1.91 | -1.1 | -5.2 to +3.0 | Not met |
| R1 Under above bias-adjusted AU consensus | 1252 | 63 | 49.2 | 2.01 | -2.1 | -7.2 to +2.9 | Not met |
| R2 R1 and the model agrees | 365 | 61 | 51.2 | 1.99 | +0.7 | -8.7 to +10.8 | Not met |
| R2 capped, 1 per player, 2 per game | 117 | 61 | 55.6 | 2.09 | +15.9 | -2.0 to +33.3 | Not met |
| S1 best AU price above reference price by 2%+ | 350 | 63 | 53.4 | 1.99 | +5.3 | -5.6 to +16.7 | Not met |
| S1 capped, 1 per player, 2 per game | 125 | 63 | 49.6 | 2.02 | -1.6 | -20.1 to +17.6 | Not met |

Under hit rate minus de-vigged AU market: +1.71 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 2590 props across 63 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68708 | | |
| AU minus Over bias | 0.68658 | -0.00050 | -0.00304 to +0.00204 |
| Reference, all | 0.68598 | -0.00110 | -0.00249 to +0.00034 |
| AU and reference, 50/50 | 0.68637 | -0.00071 | -0.00141 to +0.00001 |
| Same blend + 5% model | 0.68632 | -0.00076 | -0.00152 to +0.00004 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 3167 | 0.68614 | 0.68661 |
| Novig, ProphetX, Polymarket | 3273 | 0.68565 | 0.68669 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 42 | 10 | 27 | 5 | +0.07 |
| Diff 3 | 49 | 7 | 34 | 8 | -0.05 |
