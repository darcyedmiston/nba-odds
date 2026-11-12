# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 7 (2026-11-05 to 2026-11-11)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 2882 | 53 | 52.2 | 1.91 | -1.5 | -6.0 to +3.2 | Not met |
| R1 Under above bias-adjusted AU consensus | 1080 | 53 | 49.1 | 2.01 | -2.5 | -8.3 to +3.0 | Not met |
| R2 R1 and the model agrees | 314 | 51 | 50.0 | 1.99 | -2.3 | -12.3 to +8.1 | Not met |
| R2 capped, 1 per player, 2 per game | 99 | 51 | 54.5 | 2.08 | +13.4 | -4.9 to +32.3 | Not met |
| S1 best AU price above reference price by 2%+ | 287 | 53 | 53.3 | 1.99 | +4.8 | -7.6 to +17.1 | Not met |
| S1 capped, 1 per player, 2 per game | 106 | 53 | 52.8 | 2.03 | +4.6 | -15.5 to +24.1 | Not met |

Under hit rate minus de-vigged AU market: +1.55 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 2188 props across 53 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68723 | | |
| AU minus Over bias | 0.68693 | -0.00031 | -0.00321 to +0.00259 |
| Reference, all | 0.68667 | -0.00056 | -0.00209 to +0.00103 |
| AU and reference, 50/50 | 0.68679 | -0.00044 | -0.00120 to +0.00035 |
| Same blend + 5% model | 0.68679 | -0.00044 | -0.00130 to +0.00042 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 2694 | 0.68614 | 0.68669 |
| Novig, ProphetX, Polymarket | 2781 | 0.68576 | 0.68645 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 38 | 10 | 24 | 4 | +0.11 |
| Diff 3 | 43 | 6 | 29 | 8 | -0.08 |
