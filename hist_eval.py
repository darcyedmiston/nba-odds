"""Test model v4 against real closing AU lines, 2025-26. Splits by date and fixes the plan up front.

    python hist_eval.py    # writes model/backtest/2025-26_real_lines.md and _props.csv.gz

Train = first 60% of sampled games by date; holdout = last 40%, used once. Each game is scored
only with game logs from before its date. Not available historically: injury status (D5 is 0),
spreads and totals (D7 and the blowout input use rest and home only). proj_lab.py tuned the
projection on the first half of 2025-26, so train has some look-ahead and holdout has none.
"""
import csv
import gzip
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression

from model import Logs, best_option, build_game_ctx, main_lines, score_player_market
from nbalib import MARKETS, norm_name, team_key

BOOKS = {"sportsbet", "pointsbetau", "ladbrokes_au", "neds", "unibet", "tab", "betright"}
SEASON = "2025-26"
TRAIN_SHARE = 0.6
DS = [f"D{i}" for i in range(1, 9)]


def num(r, k):
    return float(r[k])


def load_logs():
    rows = []
    for s in ("2024-25", SEASON):
        with open(f"data/gamelogs/{s}.csv") as f:
            for r in csv.DictReader(f):
                for k in ("min", "pts", "reb", "ast", "threes", "pra", "team_pts", "opp_pts"):
                    r[k] = float(r[k] or 0)
                r["dnp"] = r["dnp"] in ("1", True)
                rows.append(r)
    return rows


def score_all():
    with gzip.open(f"data/hist_odds/{SEASON}.csv.gz", "rt") as f:
        odds = [r for r in csv.DictReader(f) if r["bookmaker"] in BOOKS and r["market"] in MARKETS]
    logs_rows = load_logs()
    actual = {}
    for r in logs_rows:
        if r["season"] == SEASON and not r["dnp"] and r["min"] > 0:
            actual[(r["game_id"], r["player_key"])] = r
    by_day = defaultdict(lambda: defaultdict(list))
    for r in odds:
        by_day[r["date_us"]][(r["game_id"], r["game"], norm_name(r["player"]), r["market"])].append(r)
    out = []
    for day in sorted(by_day):
        slate_us = date.fromisoformat(day)
        logs = Logs(SEASON, slate_us, preloaded=logs_rows)
        games = sorted({k[1] for k in by_day[day]})
        ctx = build_game_ctx(games, [], logs, slate_us, [], False)
        for (gid, game, pkey, market), rows in by_day[day].items():
            stat = MARKETS[market]
            away, home = [x.strip() for x in game.split(" @ ")]
            mains = main_lines(rows)
            if not mains:
                continue
            res = actual.get((gid, pkey))
            val = res[stat] if res else None
            base = dict(date_us=day, game_id=gid, game=game, player_key=pkey, stat=stat, actual=val)
            # A: as the live model would see it (best line per side)
            opts = {s: best_option(mains, s, stat) for s in ("Over", "Under")}
            scored, _ = score_player_market(logs, pkey, stat, team_key(away), team_key(home), slate_us, {}, ctx, opts)
            for s in scored or []:
                out.append({**base, "mode": "live", **{k: s[k] for k in ("side", "line", "odds", "book", "implied",
                            "model_prob", "ev_pct", "ces", "tier", *DS)}})
            # B: every book at the most common line, for the market comparison
            lines = [m["line"] for m in mains.values()]
            mode = max(set(lines), key=lines.count)
            sub = {b: m for b, m in mains.items() if m["line"] == mode and m["under"]}
            if not sub or float(mode).is_integer():
                continue
            devig = [(1 / m["over"]) / (1 / m["over"] + 1 / m["under"]) for m in sub.values()]
            opt = best_option(sub, "Over", stat)
            scored, _ = score_player_market(logs, pkey, stat, team_key(away), team_key(home), slate_us, {}, ctx, {"Over": opt})
            for s in scored or []:
                out.append({**base, "mode": "market", "side": "Over", "line": mode, "odds": s["odds"], "book": s["book"],
                            "implied": s["implied"], "model_prob": s["model_prob"], "ev_pct": s["ev_pct"], "ces": s["ces"],
                            "tier": s["tier"], "market_prob": sum(devig) / len(devig), "n_books": len(sub),
                            **{d: s[d] for d in DS}})
    return pd.DataFrame(out)


def settle(d):
    d = d[d.actual.notna()].copy()
    over = d.actual > d.line
    under = d.actual < d.line
    d["push"] = d.actual == d.line
    d["win"] = np.where(d.side == "Over", over, under).astype(int)
    d["pnl"] = np.where(d.push, 0, np.where(d.win == 1, 10 * (d.odds - 1), -10.0))
    return d


def logit(p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def ll(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


def brier(y, p):
    return float(((p - y) ** 2).mean())


def roi_ci(x, B=2000):
    g = x.groupby("game_id").pnl.agg(["sum", "size"]).values
    rng = np.random.default_rng(1)
    idx = rng.integers(0, len(g), (B, len(g)))
    s = g[idx, 0].sum(1) / (10 * g[idx, 1].sum(1)) * 100
    return np.percentile(s, [2.5, 97.5])


def group(x):
    x = x[~x.push]
    if len(x) == 0:
        return "0 | | | |"
    lo, hi = roi_ci(x)
    return (f"{len(x)} | {x.game_id.nunique()} | {100 * x.win.mean():.1f} | {x.pnl.sum() / (10 * len(x)) * 100:+.1f} | "
            f"{lo:+.1f} to {hi:+.1f}")


def regress(m):
    X = sm.add_constant(pd.DataFrame({"market": logit(m.market_prob.values), "model": logit(m.model_prob.values)}))
    fit = sm.Logit(m.win.values, X).fit(disp=0, cov_type="cluster", cov_kwds={"groups": m.game_id.values})
    return fit


def main():
    d = settle(score_all())
    games = d.drop_duplicates("game_id").sort_values("date_us").game_id.tolist()
    cut = games[int(len(games) * TRAIN_SHARE)]
    cut_date = d[d.game_id == cut].date_us.iloc[0]
    d["split"] = np.where(d.date_us < cut_date, "train", "holdout")
    Path("model/backtest").mkdir(parents=True, exist_ok=True)
    d.to_csv(f"model/backtest/{SEASON}_real_lines_props.csv.gz", index=False)
    live, mkt = d[d["mode"] == "live"], d[d["mode"] == "market"]
    mkt = mkt[~mkt.push].copy()
    train, hold = mkt[mkt.split == "train"].copy(), mkt[mkt.split == "holdout"].copy()
    L = [f"# Model v4 against real closing AU lines, {SEASON}", "",
         f"{len(games)} games with props; train before {cut_date} ({train.game_id.nunique()} games), "
         f"holdout from {cut_date} ({hold.game_id.nunique()} games). Lines are 5 min before tip. "
         "D5 is 0 (no historical injury status). D7 has no totals or spreads.", ""]
    # 1 does the model add to the market?
    L += ["## 1. Does the model add to the market?", "",
          "`logit(win) = a + b*logit(de-vigged market) + c*logit(model)`, Overs at the most common line, errors clustered by game. "
          "c near 0 means no added information.", "",
          "| Set | Props | a | b (market) | c (model) | c 95% CI | c p-value |", "|---|---|---|---|---|---|---|"]
    fits = {}
    for name, x in (("Train", train), ("Holdout", hold)):
        f = regress(x)
        fits[name] = f
        ci = f.conf_int().loc["model"]
        L.append(f"| {name} | {len(x)} | {f.params['const']:+.3f} | {f.params['market']:.3f} | {f.params['model']:+.3f} | "
                 f"{ci[0]:+.3f} to {ci[1]:+.3f} | {f.pvalues['model']:.3f} |")
    # 2 fit on train, score on holdout
    Xtr = np.column_stack([logit(train.market_prob.values), logit(train.model_prob.values)])
    Xho = np.column_stack([logit(hold.market_prob.values), logit(hold.model_prob.values)])
    blend = LogisticRegression(C=1e6).fit(Xtr, train.win)
    Dtr = np.column_stack([logit(train.market_prob.values), train[DS].astype(float).values])
    Dho = np.column_stack([logit(hold.market_prob.values), hold[DS].astype(float).values])
    reg = LogisticRegression(C=0.1, max_iter=2000).fit(Dtr, train.win)
    coef = dict(zip(["market"] + DS, reg.coef_[0]))
    y = hold.win.values
    preds = {"De-vigged market": hold.market_prob.values, "Model alone": hold.model_prob.values,
             "Coin flip": np.full(len(y), .5), "Market + model (fit on train)": blend.predict_proba(Xho)[:, 1],
             "Market + D1-D8 (regularised, fit on train)": reg.predict_proba(Dho)[:, 1]}
    L += ["", "## 2. Holdout accuracy (lower is better)", "", "| Forecast | Log-loss | Brier |", "|---|---|---|"]
    L += [f"| {k} | {ll(y, p):.5f} | {brier(y, p):.5f} |" for k, p in preds.items()]
    L += ["", "Fitted on train only; not applied to the model:", "",
          "| Input | Coefficient |", "|---|---|"] + [f"| {k} | {v:+.3f} |" for k, v in coef.items()]
    # 3 calibration
    L += ["", "## 3. Holdout calibration: model probability", "", "| Bucket | Props | Avg model | Avg market | Hit % |", "|---|---|---|---|---|"]
    b = pd.cut(hold.model_prob, [0, .4, .45, .5, .55, .6, .65, .7, 1])
    for k, x in hold.groupby(b, observed=True):
        L.append(f"| {k} | {len(x)} | {100 * x.model_prob.mean():.1f} | {100 * x.market_prob.mean():.1f} | {100 * x.win.mean():.1f} |")
    # 4 tiers at best price
    L += ["", "## 4. Tier ROI at the best closing price (flat $10)", "",
          "Before the 2-per-game cap. CI is a bootstrap by game.", "",
          "| Set / side / tier | Props | Games | Hit % | ROI % | ROI 95% CI |", "|---|---|---|---|---|---|"]
    for split in ("train", "holdout"):
        for side in ("Over", "Under"):
            for tier in ("Diff 4", "Diff 3", "Watchlist", "Pass"):
                x = live[(live.split == split) & (live.side == side) & (live.tier == tier)]
                L.append(f"| {split} / {side} / {tier} | {group(x)} |")
    Path(f"model/backtest/{SEASON}_real_lines.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
