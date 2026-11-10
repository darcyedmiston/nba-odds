# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 5 (2026-11-05 to 2026-11-09)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 2156 | 39 | 51.9 | 1.91 | -2.0 | -7.6 to +3.5 | Not met |
| R1 Under above bias-adjusted AU consensus | 798 | 39 | 49.0 | 2.01 | -2.5 | -9.8 to +3.8 | Not met |
| R2 R1 and the model agrees | 222 | 38 | 48.2 | 1.99 | -5.8 | -16.9 to +6.4 | Not met |
| R2 capped, 1 per player, 2 per game | 73 | 38 | 52.1 | 2.09 | +9.3 | -9.4 to +28.6 | Not met |
| S1 best AU price above reference price by 2%+ | 209 | 39 | 53.6 | 2.00 | +6.1 | -7.9 to +19.5 | Not met |
| S1 capped, 1 per player, 2 per game | 78 | 39 | 56.4 | 2.04 | +12.0 | -10.1 to +33.8 | Not met |

Under hit rate minus de-vigged AU market: +1.25 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 1614 props across 39 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68724 | | |
| AU minus Over bias | 0.68727 | +0.00004 | -0.00355 to +0.00372 |
| Reference, all | 0.68693 | -0.00031 | -0.00199 to +0.00151 |
| AU and reference, 50/50 | 0.68694 | -0.00030 | -0.00115 to +0.00060 |
| Same blend + 5% model | 0.68692 | -0.00032 | -0.00133 to +0.00074 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 2011 | 0.68658 | 0.68722 |
| Novig, ProphetX, Polymarket | 2083 | 0.68678 | 0.68685 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 33 | 8 | 21 | 4 | +0.08 |
| Diff 3 | 39 | 5 | 28 | 6 | -0.04 |
