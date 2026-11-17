# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 13 (2026-11-05 to 2026-11-17)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 5176 | 97 | 51.2 | 1.91 | -3.1 | -6.4 to +0.1 | Not met |
| R1 Under above bias-adjusted AU consensus | 1950 | 97 | 48.7 | 2.01 | -2.8 | -7.3 to +1.8 | Not met |
| R2 R1 and the model agrees | 595 | 95 | 48.2 | 1.99 | -5.2 | -12.3 to +2.2 | Not met |
| R2 capped, 1 per player, 2 per game | 184 | 95 | 50.0 | 2.07 | +3.4 | -12.0 to +18.4 | Not met |
| S1 best AU price above reference price by 2%+ | 509 | 96 | 49.7 | 1.98 | -2.4 | -11.0 to +6.6 | Not met |
| S1 capped, 1 per player, 2 per game | 188 | 96 | 48.4 | 2.01 | -4.4 | -18.9 to +10.0 | Not met |

Under hit rate minus de-vigged AU market: +0.61 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 4076 props across 97 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68899 | | |
| AU minus Over bias | 0.69050 | +0.00150 | -0.00064 to +0.00380 |
| Reference, all | 0.68908 | +0.00009 | -0.00102 to +0.00115 |
| AU and reference, 50/50 | 0.68889 | -0.00011 | -0.00066 to +0.00042 |
| Same blend + 5% model | 0.68894 | -0.00005 | -0.00066 to +0.00052 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 4861 | 0.68804 | 0.68805 |
| Novig, ProphetX, Polymarket | 5033 | 0.68795 | 0.68789 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 55 | 14 | 32 | 9 | -0.01 |
| Diff 3 | 92 | 14 | 67 | 11 | +0.01 |
