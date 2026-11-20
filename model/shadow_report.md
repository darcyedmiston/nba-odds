# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 16 (2026-11-05 to 2026-11-20)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 6262 | 118 | 51.0 | 1.91 | -3.4 | -6.5 to -0.4 | Not met |
| R1 Under above bias-adjusted AU consensus | 2370 | 118 | 47.9 | 2.01 | -4.1 | -8.2 to +0.2 | Not met |
| R2 R1 and the model agrees | 763 | 116 | 47.6 | 1.99 | -6.0 | -12.5 to +0.2 | Not met |
| R2 capped, 1 per player, 2 per game | 226 | 116 | 49.6 | 2.09 | +2.9 | -10.8 to +15.8 | Not met |
| S1 best AU price above reference price by 2%+ | 615 | 116 | 50.2 | 1.98 | -1.5 | -9.3 to +6.8 | Not met |
| S1 capped, 1 per player, 2 per game | 226 | 116 | 49.6 | 2.01 | -1.9 | -15.2 to +10.8 | Not met |

Under hit rate minus de-vigged AU market: +0.42 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 5007 props across 118 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68886 | | |
| AU minus Over bias | 0.69043 | +0.00157 | -0.00052 to +0.00358 |
| Reference, all | 0.68881 | -0.00006 | -0.00114 to +0.00097 |
| AU and reference, 50/50 | 0.68868 | -0.00018 | -0.00072 to +0.00033 |
| Same blend + 5% model | 0.68871 | -0.00015 | -0.00074 to +0.00040 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 5899 | 0.68832 | 0.68833 |
| Novig, ProphetX, Polymarket | 6105 | 0.68810 | 0.68820 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 58 | 14 | 35 | 9 | -0.01 |
| Diff 3 | 117 | 17 | 83 | 17 | -0.00 |
