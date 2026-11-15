# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 11 (2026-11-05 to 2026-11-15)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 4311 | 81 | 51.7 | 1.91 | -2.3 | -5.9 to +1.4 | Not met |
| R1 Under above bias-adjusted AU consensus | 1588 | 81 | 49.2 | 2.01 | -2.2 | -6.7 to +2.5 | Not met |
| R2 R1 and the model agrees | 491 | 79 | 50.1 | 1.99 | -1.7 | -9.7 to +6.0 | Not met |
| R2 capped, 1 per player, 2 per game | 153 | 79 | 51.0 | 2.08 | +5.6 | -11.0 to +22.2 | Not met |
| S1 best AU price above reference price by 2%+ | 453 | 81 | 51.0 | 1.99 | +0.2 | -8.8 to +9.8 | Not met |
| S1 capped, 1 per player, 2 per game | 161 | 81 | 49.7 | 2.01 | -1.8 | -17.4 to +14.2 | Not met |

Under hit rate minus de-vigged AU market: +1.10 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 3388 props across 81 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68798 | | |
| AU minus Over bias | 0.68866 | +0.00067 | -0.00182 to +0.00306 |
| Reference, all | 0.68780 | -0.00018 | -0.00146 to +0.00101 |
| AU and reference, 50/50 | 0.68773 | -0.00025 | -0.00089 to +0.00034 |
| Same blend + 5% model | 0.68775 | -0.00023 | -0.00096 to +0.00043 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 4037 | 0.68696 | 0.68721 |
| Novig, ProphetX, Polymarket | 4184 | 0.68691 | 0.68726 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 50 | 12 | 31 | 7 | +0.00 |
| Diff 3 | 79 | 12 | 56 | 11 | -0.01 |
