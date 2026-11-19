# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 15 (2026-11-05 to 2026-11-19)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 6062 | 114 | 51.1 | 1.91 | -3.3 | -6.2 to -0.2 | Not met |
| R1 Under above bias-adjusted AU consensus | 2298 | 114 | 48.0 | 2.01 | -4.0 | -8.0 to +0.1 | Not met |
| R2 R1 and the model agrees | 732 | 112 | 48.1 | 1.99 | -5.1 | -11.1 to +1.1 | Not met |
| R2 capped, 1 per player, 2 per game | 218 | 112 | 50.0 | 2.09 | +3.7 | -9.2 to +16.6 | Not met |
| S1 best AU price above reference price by 2%+ | 587 | 112 | 50.3 | 1.98 | -1.3 | -9.6 to +7.1 | Not met |
| S1 capped, 1 per player, 2 per game | 218 | 112 | 50.0 | 2.01 | -0.9 | -14.7 to +12.5 | Not met |

Under hit rate minus de-vigged AU market: +0.53 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 4826 props across 114 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68887 | | |
| AU minus Over bias | 0.69033 | +0.00146 | -0.00057 to +0.00349 |
| Reference, all | 0.68867 | -0.00020 | -0.00126 to +0.00078 |
| AU and reference, 50/50 | 0.68862 | -0.00025 | -0.00078 to +0.00023 |
| Same blend + 5% model | 0.68865 | -0.00023 | -0.00082 to +0.00032 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 5703 | 0.68815 | 0.68821 |
| Novig, ProphetX, Polymarket | 5905 | 0.68774 | 0.68812 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 58 | 14 | 35 | 9 | -0.01 |
| Diff 3 | 114 | 16 | 82 | 16 | -0.00 |
