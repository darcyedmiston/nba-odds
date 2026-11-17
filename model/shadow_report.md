# Shadow report

Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. Bets use morning prices. The money test needs a lower CI above zero on at least 250 games.

Settled slates: 12 (2026-11-05 to 2026-11-16)

## Frozen rules: flat stakes, ROI

| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |
|---|---|---|---|---|---|---|---|
| R0 every Under at best AU price | 4729 | 89 | 51.6 | 1.91 | -2.5 | -5.9 to +1.0 | Not met |
| R1 Under above bias-adjusted AU consensus | 1773 | 89 | 49.0 | 2.01 | -2.3 | -6.7 to +2.2 | Not met |
| R2 R1 and the model agrees | 542 | 87 | 49.3 | 1.98 | -3.2 | -10.8 to +4.3 | Not met |
| R2 capped, 1 per player, 2 per game | 169 | 87 | 51.5 | 2.08 | +6.8 | -9.1 to +22.2 | Not met |
| S1 best AU price above reference price by 2%+ | 478 | 88 | 50.6 | 1.99 | -0.4 | -9.2 to +8.9 | Not met |
| S1 capped, 1 per player, 2 per game | 174 | 88 | 49.4 | 2.01 | -2.2 | -17.7 to +12.5 | Not met |

Under hit rate minus de-vigged AU market: +0.95 points (2025-26: +3.05 train, +2.27 holdout).

## Forecasts: log-loss on Overs (lower is better)

Same 3706 props across 89 games for every forecast.

| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |
|---|---|---|---|
| AU consensus | 0.68885 | | |
| AU minus Over bias | 0.68980 | +0.00095 | -0.00134 to +0.00323 |
| Reference, all | 0.68876 | -0.00009 | -0.00125 to +0.00102 |
| AU and reference, 50/50 | 0.68865 | -0.00020 | -0.00078 to +0.00035 |
| Same blend + 5% model | 0.68871 | -0.00013 | -0.00076 to +0.00047 |

| Reference group | Props | Log-loss | AU log-loss on same props |
|---|---|---|---|
| FanDuel, DraftKings, BetOnline | 4430 | 0.68778 | 0.68800 |
| Novig, ProphetX, Polymarket | 4589 | 0.68792 | 0.68792 |

## Paper bets: market move, morning median to closing median

Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.

| Tier | Bets | Moved our way | Flat | Moved against | Avg move |
|---|---|---|---|---|---|
| Diff 4 | 55 | 14 | 32 | 9 | -0.01 |
| Diff 3 | 90 | 14 | 65 | 11 | +0.01 |
