# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 19 (2026-11-05 to 2026-11-23)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 7352 | 139 | 51.1 | 1.91 | -3.2 | -5.8 to -0.5 | Not met |
| R1 Under above bias-adjusted AU consensus | 2685 | 139 | 47.6 | 2.02 | -4.6 | -8.6 to -0.9 | Not met |
| R2 R1 and the model agrees | 892 | 136 | 47.8 | 2.00 | -5.4 | -11.1 to +0.6 | Not met |
| R2 capped, 1 per player, 2 per game | 266 | 136 | 48.5 | 2.09 | +1.1 | -11.8 to +13.5 | Not met |
| S1 best AU price above reference price by 2%+ | 733 | 137 | 50.5 | 1.99 | -1.1 | -8.5 to +6.6 | Not met |
| S1 capped, 1 per player, 2 per game | 265 | 137 | 49.8 | 2.02 | -0.9 | -13.4 to +11.5 | Not met |

Under hit rate minus de-vigged AU market: +0.58 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 5935 props across 139 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68803 | | |
| AU minus Over bias | 0.68948 | +0.00145 | -0.00042 to +0.00319 |
| Reference, all | 0.68820 | +0.00017 | -0.00091 to +0.00113 |
| AU and reference, 50/50 | 0.68795 | -0.00008 | -0.00062 to +0.00040 |
| Same blend + 5% model | 0.68793 | -0.00010 | -0.00068 to +0.00042 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 6905 | 0.68759 | 0.68756 |
| Novig, ProphetX, Polymarket | 7161 | 0.68764 | 0.68758 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 66 | 16 | 40 | 10 | +0.00 |
| Diff 3 | 154 | 24 | 109 | 21 | +0.01 |
