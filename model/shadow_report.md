# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 21 (2026-11-05 to 2026-11-25)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 8039 | 152 | 50.7 | 1.91 | -4.1 | -6.6 to -1.6 | Not met |
| R1 Under above bias-adjusted AU consensus | 2915 | 152 | 47.4 | 2.02 | -5.1 | -8.9 to -1.3 | Not met |
| R2 R1 and the model agrees | 969 | 149 | 47.9 | 2.00 | -5.1 | -10.6 to +0.8 | Not met |
| R2 capped, 1 per player, 2 per game | 291 | 149 | 48.8 | 2.10 | +1.6 | -9.8 to +14.0 | Not met |
| S1 best AU price above reference price by 2%+ | 832 | 150 | 50.0 | 1.99 | -2.1 | -8.8 to +4.9 | Not met |
| S1 capped, 1 per player, 2 per game | 291 | 150 | 48.8 | 2.03 | -2.9 | -14.4 to +8.5 | Not met |

Under hit rate minus de-vigged AU market: +0.15 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 6502 props across 152 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68827 | | |
| AU minus Over bias | 0.69019 | +0.00192 | +0.00026 to +0.00355 |
| Reference, all | 0.68865 | +0.00038 | -0.00064 to +0.00128 |
| AU and reference, 50/50 | 0.68829 | +0.00002 | -0.00049 to +0.00047 |
| Same blend + 5% model | 0.68825 | -0.00002 | -0.00058 to +0.00047 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 7551 | 0.68793 | 0.68783 |
| Novig, ProphetX, Polymarket | 7839 | 0.68840 | 0.68784 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 67 | 17 | 40 | 10 | +0.01 |
| Diff 3 | 158 | 24 | 112 | 22 | +0.01 |
