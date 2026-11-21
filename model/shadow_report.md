# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 17 (2026-11-05 to 2026-11-21)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 6763 | 127 | 51.0 | 1.91 | -3.4 | -6.3 to -0.5 | Not met |
| R1 Under above bias-adjusted AU consensus | 2496 | 127 | 47.5 | 2.02 | -5.0 | -8.8 to -1.0 | Not met |
| R2 R1 and the model agrees | 811 | 124 | 46.9 | 1.99 | -7.4 | -13.8 to -1.6 | Not met |
| R2 capped, 1 per player, 2 per game | 242 | 124 | 47.9 | 2.09 | -0.3 | -13.4 to +12.6 | Not met |
| S1 best AU price above reference price by 2%+ | 640 | 125 | 50.3 | 1.98 | -1.4 | -9.6 to +6.6 | Not met |
| S1 capped, 1 per player, 2 per game | 241 | 125 | 49.4 | 2.01 | -2.2 | -15.7 to +11.5 | Not met |

Under hit rate minus de-vigged AU market: +0.49 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 5452 props across 127 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68836 | | |
| AU minus Over bias | 0.68988 | +0.00153 | -0.00043 to +0.00341 |
| Reference, all | 0.68847 | +0.00011 | -0.00099 to +0.00113 |
| AU and reference, 50/50 | 0.68826 | -0.00010 | -0.00064 to +0.00040 |
| Same blend + 5% model | 0.68828 | -0.00008 | -0.00066 to +0.00045 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 6347 | 0.68795 | 0.68783 |
| Novig, ProphetX, Polymarket | 6589 | 0.68792 | 0.68783 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 61 | 15 | 37 | 9 | +0.00 |
| Diff 3 | 126 | 19 | 89 | 18 | +0.00 |
