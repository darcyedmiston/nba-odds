# Projection lab — 2025-26

16,411 rotation player-games. Parameters tuned on games before 2026-01-16 (8,192); results below are on the later half (8,219), which the tuning never saw.

## Mean absolute error, out-of-sample

| Stat | Naive avg | Model v4 | New | New vs v4 | New vs naive |
|---|---|---|---|---|---|
| pts | 5.234 | 5.216 | 5.161 | +1.1% | +1.4% |
| reb | 2.015 | 2.049 | 1.987 | +3.1% | +1.4% |
| ast | 1.575 | 1.582 | 1.559 | +1.5% | +1.0% |
| threes | 1.021 | 1.036 | 1.017 | +1.8% | +0.5% |
| pra | 6.656 | 6.625 | 6.522 | +1.6% | +2.0% |

Minutes MAE: last-10 average 4.71, new 4.66 (+1.1%).

## Which ideas helped (out-of-sample, switching each one off)

| Idea | Parameter(s) | Tuned value | Total error change if removed |
|---|---|---|---|
| Recency weighting (minutes) | hl_min | 8 | +1.34% |
| Recency weighting (rate) | hl_rate | 80 | +0.10% |
| Down-weight last season | prev_w | 0.3 | +0.14% |
| Down-weight games for another team | other_team_w | 0.2 | +0.12% |
| Teammates out: extra minutes | abs_min | 0 | +0.00% |
| Teammates out: extra usage | abs_rate | 0.15 | +0.13% |
| With/without splits | ww_k | 0.0 | +0.00% |
| Back-to-back minutes | b2b_min | 0.8 | +0.04% |
| Home | home | -0.02 | +0.12% |
| Blowout minutes (net-rating proxy) | blow_min | 0.5 | +0.04% |
| Opponent allowed | opp_beta | 0.75 | +0.42% |
| Pace / scoring environment | env_gamma | 0.5 | +0.05% |

Positive = removing the idea makes projections worse (so it helps).

