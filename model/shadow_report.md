# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 3 (2026-11-05 to 2026-11-07)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 1386 | 25 | 51.2 | 1.91 | -3.0 | -9.1 to +3.3 | Not met |
| R1 Under above bias-adjusted AU consensus | 509 | 25 | 49.5 | 2.01 | -1.1 | -9.6 to +6.9 | Not met |
| R2 R1 and the model agrees | 130 | 24 | 47.7 | 1.99 | -6.4 | -21.9 to +8.9 | Not met |
| R2 capped, 1 per player, 2 per game | 46 | 24 | 50.0 | 2.06 | +5.3 | -19.5 to +30.7 | Not met |
| S1 best AU price above reference price by 2%+ | 124 | 25 | 58.9 | 2.01 | +16.5 | -1.9 to +34.9 | Not met |
| S1 capped, 1 per player, 2 per game | 50 | 25 | 56.0 | 2.04 | +11.9 | -16.7 to +39.1 | Not met |

Under hit rate minus de-vigged AU market: +0.68 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 1038 props across 25 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68813 | | |
| AU minus Over bias | 0.68808 | -0.00005 | -0.00384 to +0.00408 |
| Reference, all | 0.68742 | -0.00071 | -0.00307 to +0.00173 |
| AU and reference, 50/50 | 0.68763 | -0.00050 | -0.00168 to +0.00070 |
| Same blend + 5% model | 0.68773 | -0.00040 | -0.00158 to +0.00087 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 1279 | 0.68734 | 0.68834 |
| Novig, ProphetX, Polymarket | 1332 | 0.68829 | 0.68802 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 21 | 5 | 13 | 3 | +0.05 |
| Diff 3 | 25 | 2 | 17 | 6 | -0.14 |
