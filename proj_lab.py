"""Projection lab: test projection ideas on past seasons, judged by mean absolute error.

    python proj_lab.py --season 2025-26

Builds one feature row per rotation player-game (only information from earlier games),
then tunes each idea on the first half of the season and reports the second half
(out-of-sample) against the current v4 projection and a naive average.
Writes model/backtest/<season>_projection_lab.md and model/projection_params.json.
"""
import argparse
import json
import math
import statistics as st
from collections import defaultdict
from pathlib import Path

import model as M
from nbalib import prev_season, team_key

STATS = ["pts", "reb", "ast", "threes", "pra"]


# ─── feature building (single chronological pass) ────────────────────────────

def build(season, rows):
    prev = prev_season(season)
    by_game = defaultdict(list)
    for r in rows:
        by_game[(r["date_us"], r["game_id"])].append(r)
    hist = defaultdict(list)          # player -> played games
    tgames = defaultdict(list)        # team -> games
    game_players = {}                 # (game_id, team) -> set of players who played
    feats = []
    for (d, gid) in sorted(by_game):
        grows = by_game[(d, gid)]
        s = grows[0]["season"]
        teams = {team_key(r["team_name"]) for r in grows}
        played_today = defaultdict(set)
        for r in grows:
            if not r["dnp"] and r["min"] > 0:
                played_today[team_key(r["team_name"])].add(r["player_key"])
        if s == season:
            ctx = {t: team_ctx(t, [x for x in teams if x != t][0], s, prev, d, tgames, hist, played_today[t])
                   for t in teams}
            for r in grows:
                if r["dnp"] or r["min"] <= 0:
                    continue
                H = hist[r["player_key"]]
                if len(H) < 5 or st.mean(h["min"] for h in H[-10:]) < 20:
                    continue
                t = team_key(r["team_name"])
                o = [x for x in teams if x != t][0]
                feats.append(player_feats(r, H, s, prev, t, o, ctx[t], ctx[o], game_players))
        # update state after the game
        for t in teams:
            mine = [r for r in grows if team_key(r["team_name"]) == t]
            theirs = [r for r in grows if team_key(r["team_name"]) != t]
            tot = {k: sum(r[k] for r in mine) for k in STATS}
            alw = {k: sum(r[k] for r in theirs) for k in STATS}
            game_players[(gid, t)] = played_today[t]
            tgames[t].append({"date": d, "season": s, "gid": gid, "players": played_today[t], "tot": tot,
                              "alw": alw, "pts": mine[0]["team_pts"], "opp": mine[0]["opp_pts"],
                              "rot_min": sum(r["min"] for r in mine)})
        for r in grows:
            if not r["dnp"] and r["min"] > 0:
                hist[r["player_key"]].append({k: r[k] for k in ["season", "date_us", "game_id", "min", *STATS]}
                                             | {"team": team_key(r["team_name"])})
    return feats


def season_mean(games, key, s, prev, k=10):
    cur = [g[key] for g in games if g["season"] == s]
    prv = [g[key] for g in games if g["season"] == prev]
    if not cur and not prv:
        return None
    kk = k if prv else 0
    pm = st.mean(prv) if prv else 0
    return (sum(cur) + kk * pm) / (len(cur) + kk)


def team_ctx(t, o, s, prev, d, tgames, hist, played_today):
    G = tgames[t]
    c = {"rest": None, "env": None, "net": None, "alw": {}, "absent": []}
    if G:
        from datetime import date
        c["rest"] = (date.fromisoformat(d) - date.fromisoformat(G[-1]["date"])).days
        c["env"] = season_mean([{"x": g["pts"] + g["opp"], "season": g["season"]} for g in G], "x", s, prev)
        c["net"] = season_mean([{"x": g["pts"] - g["opp"], "season": g["season"]} for g in G], "x", s, prev)
        for k in STATS:
            c["alw"][k] = season_mean([{"x": g["alw"][k], "season": g["season"]} for g in G], "x", s, prev)
        c["tot"] = {k: season_mean([{"x": g["tot"][k], "season": g["season"]} for g in G], "x", s, prev) for k in STATS}
    recent = [g for g in G if g["season"] == s][-5:]
    if recent:
        regulars = set().union(*[g["players"] for g in recent])
        for pk in regulars:
            H = hist.get(pk, [])
            if not H or H[-1]["team"] != t:
                continue
            m20 = st.mean(h["min"] for h in H[-20:])
            if m20 >= 24 and sum(pk in g["players"] for g in recent) >= min(2, len(recent)) and pk not in played_today:
                c["absent"].append({"pk": pk, "min": m20, **{k: st.mean(h[k] for h in H[-20:]) for k in STATS}})
    return c


def player_feats(r, H, s, prev, t, o, ct, co, game_players):
    f = {"date": r["date_us"], "player": r["player_key"], "home": r["home"] == "1", "t": t, "o": o,
         "y_min": r["min"], **{f"y_{k}": r[k] for k in STATS}}
    f["H"] = H[-60:]  # enough history for every variant
    f["season"], f["prev"] = s, prev
    f["traded"] = any(h["team"] != t for h in H[-60:] if h["season"] == s) or (
        H[-1]["team"] != t)
    f["ct"], f["co"] = ct, co
    absent = [a for a in ct["absent"] if a["pk"] != r["player_key"]]
    f["absent"] = absent
    # with / without: this player's games this season on this team, split by whether each absent star played
    ww = {}
    for a in absent:
        w_, wo = [], []
        for h in H:
            if h["season"] != s or h["team"] != t:
                continue
            ps = game_players.get((h["game_id"], t), set())
            (w_ if a["pk"] in ps else wo).append(h)
        ww[a["pk"]] = (w_, wo)
    f["ww"] = ww
    return f


# ─── projection variants ─────────────────────────────────────────────────────

def ewma(vals, half_life):
    if not vals:
        return 0.0
    a = 0.5 ** (1 / half_life)
    w = [a ** (len(vals) - 1 - i) for i in range(len(vals))]
    return sum(v * x for v, x in zip(vals, w)) / sum(w)


def proj_v4(f, k):
    """Reproduces model v4's projection (absences from who sat, no spread)."""
    H, s = f["H"], f["season"]
    cur = [h for h in H if h["season"] == s]
    prv = [h for h in H if h["season"] != s]
    n = len(cur)
    kk = 0 if n >= 20 else (3 if f["traded"] and cur else 10)
    kk = min(kk, len(prv))
    blend = lambda c, p: (sum(c) + kk * (st.mean(p) if p else 0)) / (len(c) + kk) if (c or kk) else 0
    min_avg = blend([h["min"] for h in cur], [h["min"] for h in prv])
    l5, l10 = H[-5:], H[-10:]
    m = 0.5 * st.mean(h["min"] for h in l5) + 0.3 * st.mean(h["min"] for h in l10) + 0.2 * min_avg
    na = len(f["absent"])
    if na and m >= 20:
        m += min(4.0, 1.5 * na)
    if f["ct"]["rest"] == 1:
        m -= 1.0
    rate = lambda rows: (sum(h[k] for h in rows) / sum(h["min"] for h in rows)) if rows and sum(h["min"] for h in rows) else 0
    rs = (rate(cur) * n + rate(prv) * kk) / (n + kk) if (n + kk) else 0
    rp = (0.6 * rs + 0.4 * rate(l10)) * (1 + min(0.08, 0.03 * na))
    return max(0.0, rp * m)


def naive(f, k):
    H, s = f["H"], f["season"]
    cur = [h for h in H if h["season"] == s]
    base = cur if len(cur) >= 5 else H[-20:]
    return 0.6 * st.mean(h[k] for h in base) + 0.4 * st.mean(h[k] for h in H[-10:])


def proj_new(f, k, P):
    """Candidate projection. P holds the tunable parameters."""
    H, s = f["H"], f["season"]
    # 1. minutes and per-minute rate by exponentially weighted history; last season's games and
    #    games for another team are down-weighted
    def wts(h):
        w = 1.0
        if h["season"] != s:
            w *= P["prev_w"]
        if h["team"] != f["t"]:
            w *= P["other_team_w"]
        return w
    a_m = 0.5 ** (1 / P["hl_min"])
    a_r = 0.5 ** (1 / P["hl_rate"])
    N = len(H)
    wm = [a_m ** (N - 1 - i) * wts(h) for i, h in enumerate(H)]
    wr = [a_r ** (N - 1 - i) * wts(h) * h["min"] for i, h in enumerate(H)]
    m = sum(w * h["min"] for w, h in zip(wm, H)) / sum(wm)
    rate = sum(w * h[k] / h["min"] for w, h in zip(wr, H)) / sum(wr)
    # shrink the rate toward last season's rate (stability) when this season's sample is small
    # 2. absences: redistribute missing minutes and usage
    ct = f["ct"]
    if f["absent"]:
        miss_min = sum(a["min"] for a in f["absent"])
        m += P["abs_min"] * miss_min * (m / 240.0) * 5
        team_tot = (ct.get("tot") or {}).get(k) or None
        miss_stat = sum(a[k] for a in f["absent"])
        if team_tot:
            rate *= 1 + P["abs_rate"] * miss_stat / team_tot
        # with/without splits where there's enough sample
        for a in f["absent"]:
            w_, wo = f["ww"].get(a["pk"], ([], []))
            if len(wo) >= 3 and len(w_) >= 3 and P["ww_k"] > 0:
                r_wo = sum(h[k] for h in wo) / sum(h["min"] for h in wo)
                r_w = sum(h[k] for h in w_) / sum(h["min"] for h in w_)
                adj = (r_wo / r_w) if r_w else 1
                wgt = len(wo) / (len(wo) + P["ww_k"])
                rate *= 1 + wgt * (adj - 1)
    # 3. rest, home
    if ct["rest"] == 1:
        m -= P["b2b_min"]
    if f["home"]:
        rate *= 1 + P["home"]
    # 4. blowout proxy from season net ratings (no historical spreads)
    co = f["co"]
    if ct.get("net") is not None and co.get("net") is not None:
        margin = ct["net"] - co["net"] + (2.5 if f["home"] else -2.5)
        if m >= 28 and abs(margin) > P["blow_thr"]:
            m -= P["blow_min"] * (abs(margin) - P["blow_thr"]) / 5
    # 5. opponent: stat allowed vs league, shrunk
    lg = P["_league"].get((s, k))
    if co.get("alw", {}).get(k) and lg:
        rate *= (co["alw"][k] / lg) ** P["opp_beta"]
    # 6. pace / scoring environment
    lgt = P["_league"].get((s, "env"))
    if ct.get("env") and co.get("env") and lgt:
        rate *= (((ct["env"] + co["env"]) / 2) / lgt) ** P["env_gamma"]
    return max(0.0, rate * max(0.0, m))


DEFAULT = {"hl_min": 6.0, "hl_rate": 15.0, "prev_w": 0.6, "other_team_w": 0.4, "abs_min": 0.3,
           "abs_rate": 0.3, "ww_k": 0.0, "b2b_min": 0.8, "home": 0.0, "blow_thr": 10.0, "blow_min": 0.8,
           "opp_beta": 0.5, "env_gamma": 0.5}
GRID = {"hl_min": [3, 5, 8, 12, 20], "hl_rate": [8, 15, 25, 40, 80], "prev_w": [0.3, 0.5, 0.7, 1.0],
        "other_team_w": [0.2, 0.4, 0.7, 1.0], "abs_min": [0, 0.15, 0.3, 0.5], "abs_rate": [0, 0.15, 0.3, 0.5, 0.8],
        "ww_k": [0, 5, 10, 20], "b2b_min": [0, 0.5, 1.0, 2.0], "home": [-0.02, 0, 0.01, 0.02, 0.04],
        "blow_thr": [6, 8, 10, 14], "blow_min": [0, 0.5, 1.0, 2.0], "opp_beta": [0, 0.25, 0.5, 0.75, 1.0],
        "env_gamma": [0, 0.25, 0.5, 1.0]}


def league_avgs(feats):
    out = defaultdict(list)
    for f in feats:
        for k in STATS:
            if f["co"].get("alw", {}).get(k):
                out[(f["season"], k)].append(f["co"]["alw"][k])
        if f["ct"].get("env"):
            out[(f["season"], "env")].append(f["ct"]["env"])
    return {k: st.mean(v) for k, v in out.items()}


def mae(feats, fn, k):
    return st.mean(abs(fn(f, k) - f[f"y_{k}"]) for f in feats)


def mae_min(feats, P):
    # minutes error isolated: run proj_new for a dummy stat 'min' via rate=1
    errs = []
    for f in feats:
        P2 = dict(P)
        errs.append(abs(proj_minutes(f, P2) - f["y_min"]))
    return st.mean(errs)


def proj_minutes(f, P):
    H, s = f["H"], f["season"]
    a_m = 0.5 ** (1 / P["hl_min"])
    N = len(H)
    w = [a_m ** (N - 1 - i) * (P["prev_w"] if h["season"] != s else 1) * (P["other_team_w"] if h["team"] != f["t"] else 1)
         for i, h in enumerate(H)]
    m = sum(x * h["min"] for x, h in zip(w, H)) / sum(w)
    if f["absent"]:
        m += P["abs_min"] * sum(a["min"] for a in f["absent"]) * (m / 240.0) * 5
    if f["ct"]["rest"] == 1:
        m -= P["b2b_min"]
    ct, co = f["ct"], f["co"]
    if ct.get("net") is not None and co.get("net") is not None:
        margin = ct["net"] - co["net"] + (2.5 if f["home"] else -2.5)
        if m >= 28 and abs(margin) > P["blow_thr"]:
            m -= P["blow_min"] * (abs(margin) - P["blow_thr"]) / 5
    return m


def tune(train, lg):
    """Coordinate descent on summed relative MAE across stats."""
    P = dict(DEFAULT, _league=lg)
    base_n = {k: mae(train, naive, k) for k in STATS}

    def score(P):
        return sum(mae(train, lambda f, k: proj_new(f, k, P), k) / base_n[k] for k in STATS)
    best = score(P)
    for _ in range(2):
        for name, vals in GRID.items():
            for v in vals:
                Q = dict(P, **{name: v})
                sc = score(Q)
                if sc < best - 1e-6:
                    best, P = sc, Q
            print(f"  {name} = {P[name]}  (score {best:.4f})")
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", default="2025-26")
    args = ap.parse_args()
    import backtest as B
    rows = B.load_rows(args.season)
    feats = build(args.season, rows)
    lg = league_avgs(feats)
    feats.sort(key=lambda f: f["date"])
    cut = feats[len(feats) // 2]["date"]
    train = [f for f in feats if f["date"] < cut]
    test = [f for f in feats if f["date"] >= cut]
    print(f"{len(feats)} player-games; tune on {len(train)} (< {cut}), test on {len(test)}")
    P = tune(train[::3], lg)
    md = [f"# Projection lab — {args.season}", "",
          f"{len(feats):,} rotation player-games. Parameters tuned on games before {cut} ({len(train):,}); "
          f"results below are on the later half ({len(test):,}), which the tuning never saw.", "",
          "## Mean absolute error, out-of-sample", "",
          "| Stat | Naive avg | Model v4 | New | New vs v4 | New vs naive |", "|---|---|---|---|---|---|"]
    for k in STATS:
        n_, v4, nw = mae(test, naive, k), mae(test, proj_v4, k), mae(test, lambda f, k: proj_new(f, k, P), k)
        md.append(f"| {k} | {n_:.3f} | {v4:.3f} | {nw:.3f} | {100 * (v4 - nw) / v4:+.1f}% | {100 * (n_ - nw) / n_:+.1f}% |")
    m_naive = st.mean(abs(st.mean(h["min"] for h in f["H"][-10:]) - f["y_min"]) for f in test)
    m_new = mae_min(test, P)
    md += ["", f"Minutes MAE: last-10 average {m_naive:.2f}, new {m_new:.2f} ({100 * (m_naive - m_new) / m_naive:+.1f}%).", "",
           "## Which ideas helped (out-of-sample, switching each one off)", "",
           "| Idea | Parameter(s) | Tuned value | Total error change if removed |", "|---|---|---|---|"]
    off = {"Recency weighting (minutes)": {"hl_min": 1000}, "Recency weighting (rate)": {"hl_rate": 1000},
           "Down-weight last season": {"prev_w": 1.0}, "Down-weight games for another team": {"other_team_w": 1.0},
           "Teammates out: extra minutes": {"abs_min": 0}, "Teammates out: extra usage": {"abs_rate": 0},
           "With/without splits": {"ww_k": 0}, "Back-to-back minutes": {"b2b_min": 0}, "Home": {"home": 0},
           "Blowout minutes (net-rating proxy)": {"blow_min": 0}, "Opponent allowed": {"opp_beta": 0},
           "Pace / scoring environment": {"env_gamma": 0}}
    base_tot = sum(mae(test, lambda f, k: proj_new(f, k, P), k) / mae(test, naive, k) for k in STATS)
    for name, q in off.items():
        Q = dict(P, **q)
        tot = sum(mae(test, lambda f, k: proj_new(f, k, Q), k) / mae(test, naive, k) for k in STATS)
        md.append(f"| {name} | {', '.join(q)} | {', '.join(str(P[x]) for x in q)} | {100 * (tot - base_tot) / base_tot:+.2f}% |")
    md += ["", "Positive = removing the idea makes projections worse (so it helps).", ""]
    Path(f"model/backtest/{args.season}_projection_lab.md").write_text("\n".join(md) + "\n")
    Path("model/projection_params.json").write_text(json.dumps({k: v for k, v in P.items() if not k.startswith("_")}, indent=1))
    print("\n".join(md))


if __name__ == "__main__":
    main()
