# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 10 (2026-11-05 to 2026-11-14)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 4110 | 76 | 52.0 | 1.91 | -1.8 | -5.6 to +2.1 | Not met |
| R1 Under above bias-adjusted AU consensus | 1525 | 76 | 49.4 | 2.01 | -1.9 | -6.6 to +2.9 | Not met |
| R2 R1 and the model agrees | 473 | 74 | 50.7 | 1.99 | -0.5 | -8.2 to +7.6 | Not met |
| R2 capped, 1 per player, 2 per game | 143 | 74 | 51.7 | 2.09 | +7.6 | -9.2 to +24.0 | Not met |
| S1 best AU price above reference price by 2%+ | 426 | 76 | 51.6 | 1.99 | +1.6 | -8.0 to +11.6 | Not met |
| S1 capped, 1 per player, 2 per game | 151 | 76 | 49.0 | 2.02 | -2.9 | -19.2 to +13.1 | Not met |

Under hit rate minus de-vigged AU market: +1.36 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 3221 props across 76 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68813 | | |
| AU minus Over bias | 0.68827 | +0.00014 | -0.00243 to +0.00268 |
| Reference, all | 0.68777 | -0.00036 | -0.00171 to +0.00088 |
| AU and reference, 50/50 | 0.68779 | -0.00034 | -0.00101 to +0.00028 |
| Same blend + 5% model | 0.68778 | -0.00036 | -0.00109 to +0.00032 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 3857 | 0.68709 | 0.68732 |
| Novig, ProphetX, Polymarket | 3992 | 0.68693 | 0.68735 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 47 | 11 | 29 | 7 | -0.02 |
| Diff 3 | 67 | 9 | 49 | 9 | -0.03 |
