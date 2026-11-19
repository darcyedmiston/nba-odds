# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 14 (2026-11-05 to 2026-11-18)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 5454 | 102 | 51.0 | 1.91 | -3.4 | -6.5 to -0.2 | Not met |
| R1 Under above bias-adjusted AU consensus | 2061 | 102 | 48.3 | 2.01 | -3.5 | -7.7 to +0.8 | Not met |
| R2 R1 and the model agrees | 648 | 100 | 47.7 | 1.99 | -6.0 | -12.6 to +0.7 | Not met |
| R2 capped, 1 per player, 2 per game | 194 | 100 | 50.0 | 2.08 | +3.7 | -10.9 to +18.1 | Not met |
| S1 best AU price above reference price by 2%+ | 544 | 101 | 49.6 | 1.98 | -2.5 | -10.8 to +6.2 | Not met |
| S1 capped, 1 per player, 2 per game | 198 | 101 | 48.0 | 2.01 | -5.2 | -19.6 to +8.7 | Not met |

Under hit rate minus de-vigged AU market: +0.47 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 4324 props across 102 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68885 | | |
| AU minus Over bias | 0.69057 | +0.00172 | -0.00042 to +0.00390 |
| Reference, all | 0.68898 | +0.00013 | -0.00106 to +0.00126 |
| AU and reference, 50/50 | 0.68876 | -0.00009 | -0.00068 to +0.00048 |
| Same blend + 5% model | 0.68880 | -0.00005 | -0.00069 to +0.00056 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 5126 | 0.68785 | 0.68792 |
| Novig, ProphetX, Polymarket | 5308 | 0.68776 | 0.68775 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 57 | 14 | 34 | 9 | -0.01 |
| Diff 3 | 106 | 15 | 77 | 14 | +0.00 |
