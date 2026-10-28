"""Backtest model v4 on a past season WITHOUT bookmaker odds.

    python backtest.py --season 2025-26

For every player-game (rotation players: >= 20 min a game over their previous 10),
for each stat, it builds a stand-in "naive market" line from the player's averages
(the .5 line that splits his last 20 games closest to 50/50) at 1.87 both sides, scores
Over and Under with the live model using only games before that date, and settles
against the real result.

What this tests: projection accuracy (minutes and stats vs naive averages), whether
model probabilities are calibrated, and whether CES tiers and each determinant
separate winners from losers. What it can't test: edge over real bookmaker lines,
D8 (no market data), GTD status, and spreads/totals (not stored historically).
Teammate absences use who actually sat (normally known from the injury report).

Outputs: model/backtest/<season>_report.md and model/backtest/<season>_props.csv.gz
"""
import argparse
import csv
import gzip
import math
import statistics as st
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

import model as M
from nbalib import prev_season, team_key

ODDS = 1.87


def load_rows(season):
    rows = []
    for s in (prev_season(season), season):
        for r in M.read_csv(f"data/gamelogs/{s}.csv"):
            for k in ("min", "pts", "reb", "ast", "threes", "pra", "team_pts", "opp_pts"):
                r[k] = M.num(r[k])
            r["dnp"] = r["dnp"] == "1"
            rows.append(r)
    rows.sort(key=lambda r: (r["date_us"], r["game_id"]))
    return rows


def market_line(last20, season):
    """Stand-in for a bookmaker line: the .5 line that splits the player's recent
    games closest to 50/50 (books set props near the median, not the mean, because
    stat distributions are skewed). Ties go to the season split."""
    vals = sorted(last20)
    best = None
    for c in range(int(vals[0]), int(vals[-1]) + 1):
        ln = c + 0.5
        over = sum(v > ln for v in last20) / len(last20)
        over_s = sum(v > ln for v in season) / len(season)
        key = (abs(over - 0.5), abs(over_s - 0.5))
        if best is None or key < best[0]:
            best = (key, ln)
    return best[1] if best else math.floor(st.median(vals)) + 0.5


def opts_for(line):
    base = {"line": line, "odds": ODDS, "book": "naive", "n_books_at_line": 1, "n_books": 1,
            "median_line": line, "softer": 0.0, "price_edge": 0.0}
    return {"Over": dict(base), "Under": dict(base)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", default="2025-26")
    ap.add_argument("--every", type=int, default=1, help="use every Nth date (speed)")
    args = ap.parse_args()
    t0 = time.time()
    rows = load_rows(args.season)
    cur = [r for r in rows if r["season"] == args.season]
    dates = sorted({r["date_us"] for r in cur})[::args.every]
    games_by_date = defaultdict(lambda: defaultdict(list))
    for r in cur:
        games_by_date[r["date_us"]][r["game_id"]].append(r)

    out = []
    for i, d in enumerate(dates):
        d_us = date.fromisoformat(d)
        logs = M.Logs(args.season, d_us, preloaded=rows)
        for gid, grows in games_by_date[d].items():
            home = next(r for r in grows if r["home"] == "1")["team_name"]
            away = next(r for r in grows if r["home"] == "0")["team_name"]
            hk, ak = team_key(home), team_key(away)
            ctx = {"spread": {}, "total": {}, "home": {hk: True, ak: False}, "rest": {},
                   "absences": defaultdict(list)}
            for t in (hk, ak):
                gl = logs.team_games.get(t, [])
                if gl:
                    ctx["rest"][t] = (d_us - date.fromisoformat(gl[-1]["date_us"])).days
                played_today = {r["player_key"] for r in grows if not r["dnp"] and team_key(r["team_name"]) == t}
                recent = [g for g in gl if g["season"] == args.season][-5:]
                if not recent:
                    continue
                regulars = set().union(*[g["players"] for g in recent])
                for pk in regulars:
                    hist = [r for r in logs.by_player.get(pk, []) if not r["dnp"]]
                    if not hist or team_key(hist[-1]["team_name"]) != t:
                        continue
                    if (st.mean(r["min"] for r in hist[-20:]) >= 24
                            and sum(pk in g["players"] for g in recent) >= min(2, len(recent))
                            and pk not in played_today):
                        ctx["absences"][t].append(pk)
            for r in grows:
                if r["dnp"] or r["min"] <= 0:
                    continue
                pk = r["player_key"]
                hist = [h for h in logs.by_player.get(pk, []) if not h["dnp"] and h["min"] > 0]
                if len(hist) < 5 or st.mean(h["min"] for h in hist[-10:]) < 20:
                    continue
                cur_h = [h for h in hist if h["season"] == args.season]
                base_h = cur_h if len(cur_h) >= 5 else hist[-20:]
                last20 = hist[-20:]
                for stat in M.STAT_SCALE:
                    naive = 0.6 * st.mean(h[stat] for h in base_h) + 0.4 * st.mean(h[stat] for h in hist[-10:])
                    line = market_line([h[stat] for h in last20], [h[stat] for h in base_h])
                    scored, _ = M.score_player_market(logs, pk, stat, ak, hk, d_us, {}, ctx, opts_for(line))
                    if not scored:
                        continue
                    actual = r[stat]
                    for s in scored:
                        win = actual > line if s["side"] == "Over" else actual < line
                        out.append({"date_us": d, "player": r["player"], "stat": stat, "side": s["side"],
                                    "line": line, "naive": round(naive, 2), "actual": actual,
                                    "naive_min": round(st.mean(h["min"] for h in hist[-10:]), 1),
                                    "win": int(win), "min": r["min"], "proj": s["proj"],
                                    "proj_min": s["proj_min"], "model_prob": s["model_prob"],
                                    "ces": s["ces"], "tier": s["tier"], "n_cur": s["n_cur"],
                                    **{k: s[k] for k in M.WEIGHTS}})
        if i % 20 == 0:
            print(f"{d}: {len(out)} rows, {time.time() - t0:.0f}s")

    outdir = Path("model/backtest")
    outdir.mkdir(parents=True, exist_ok=True)
    with gzip.open(outdir / f"{args.season}_props.csv.gz", "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    report(args.season, out)
    print(f"done: {len(out)} rows in {time.time() - t0:.0f}s")


def roi(rs):
    n = len(rs)
    w = sum(r["win"] for r in rs)
    pnl = w * (ODDS - 1) - (n - w)
    return n, (100 * w / n if n else 0), (100 * pnl / n if n else 0)


def report(season, out):
    be = 100 / ODDS
    md = [f"# Model v4 backtest — {season} (no bookmaker odds)", "",
          f"{len(out):,} prop-sides from {len({(r['date_us'], r['player']) for r in out}):,} player-games. "
          f"Stand-in line = the .5 line that splits the player's last 20 games closest to 50/50 "
          f"(books set props near the median), at {ODDS} both sides (break-even {be:.1f}%). Real bookmaker lines are sharper than this, so treat ROI "
          "here as an upper bound and focus on accuracy, calibration and ranking.", ""]

    # 1. projection accuracy (one row per player-game-stat: use Over rows)
    overs = [r for r in out if r["side"] == "Over"]
    md += ["## 1. Projection accuracy (mean absolute error)", "",
           "| Stat | n | Model proj | Naive avg (0.6 season + 0.4 L10) | Better? |", "|---|---|---|---|---|"]
    for stat in M.STAT_SCALE:
        rs = [r for r in overs if r["stat"] == stat]
        mae_m = st.mean(abs(r["proj"] - r["actual"]) for r in rs)
        mae_n = st.mean(abs(r["naive"] - r["actual"]) for r in rs)
        md.append(f"| {stat} | {len(rs):,} | {mae_m:.2f} | {mae_n:.2f} | {'yes' if mae_m < mae_n else 'no'} ({100 * (mae_n - mae_m) / mae_n:+.1f}%) |")
    pts = [r for r in overs if r["stat"] == "pts"]
    mae_min = st.mean(abs(r["proj_min"] - r["min"]) for r in pts)
    mae_min_n = st.mean(abs(r["naive_min"] - r["min"]) for r in pts)
    md += ["", f"Minutes: projected vs actual MAE {mae_min:.2f} min; last-10 average {mae_min_n:.2f} min "
           f"(n={len(pts):,}).", "",
           f"Overall: Overs hit {100 * st.mean(r['win'] for r in overs):.1f}% vs the stand-in lines "
           "(a fair line should be close to 50%).", ""]

    # 2. calibration
    md += ["## 2. Calibration — model probability vs actual hit rate", "",
           "| Model prob | n | Actual hit % | Gap |", "|---|---|---|---|"]
    buckets = defaultdict(list)
    for r in out:
        buckets[min(9, int(r["model_prob"] * 10))].append(r)
    for b in sorted(buckets):
        rs = buckets[b]
        hit = 100 * st.mean(r["win"] for r in rs)
        mid = st.mean(100 * r["model_prob"] for r in rs)
        md.append(f"| {b * 10}-{b * 10 + 10}% (avg {mid:.1f}) | {len(rs):,} | {hit:.1f} | {hit - mid:+.1f} |")
    brier = st.mean((r["model_prob"] - r["win"]) ** 2 for r in out)
    md += ["", f"Brier score {brier:.4f} (coin-flip baseline 0.2500; lower is better).", ""]

    # 3. tiers
    md += ["## 3. Tiers (vs stand-in line at 1.87)", "", "| Side / tier | n | Hit % | ROI % |", "|---|---|---|---|"]
    groups = defaultdict(list)
    for r in out:
        groups[(r["side"], r["tier"])].append(r)
    order = ["Diff 4", "Diff 3", "Watchlist", "Pass", "Void"]
    for side in ("Over", "Under"):
        for t in order:
            if (side, t) in groups:
                n, hit, r_ = roi(groups[(side, t)])
                md.append(f"| {side} / {t} | {n:,} | {hit:.1f} | {r_:+.1f} |")
    md += ["", "Overs by stat, Diff 3+:", "", "| Stat | n | Hit % | ROI % |", "|---|---|---|---|"]
    for stat in M.STAT_SCALE:
        rs = [r for r in out if r["side"] == "Over" and r["stat"] == stat and r["tier"] in ("Diff 4", "Diff 3")]
        if rs:
            n, hit, r_ = roi(rs)
            md.append(f"| {stat} | {n:,} | {hit:.1f} | {r_:+.1f} |")
    early = [r for r in out if r["side"] == "Over" and r["tier"] in ("Diff 4", "Diff 3") and r["n_cur"] < 15]
    late = [r for r in out if r["side"] == "Over" and r["tier"] in ("Diff 4", "Diff 3") and r["n_cur"] >= 15]
    for name, rs in (("first 15 games of the season", early), ("after 15 games", late)):
        if rs:
            n, hit, r_ = roi(rs)
            md.append(f"\nOvers Diff 3+, {name}: n={n:,}, hit {hit:.1f}%, ROI {r_:+.1f}%")
    md.append("")

    # 4. determinants
    md += ["## 4. Determinants — hit rate by score (Overs)", "",
           "Does a higher score actually mean a higher hit rate? Spread = hit% at +2 minus hit% at -2.", "",
           "| D | -2 | -1 | 0 | +1 | +2 | Spread |", "|---|---|---|---|---|---|---|"]
    for d in M.WEIGHTS:
        cells, by = [], defaultdict(list)
        for r in overs:
            by[int(r[d])].append(r["win"])
        for v in (-2, -1, 0, 1, 2):
            cells.append(f"{100 * st.mean(by[v]):.1f} ({len(by[v]):,})" if by[v] else "—")
        spread = (100 * (st.mean(by[2]) - st.mean(by[-2]))) if by[2] and by[-2] else float("nan")
        md.append(f"| {d} | " + " | ".join(cells) + f" | {spread:+.1f} |")
    md += ["", "Hit rates in each cell are vs the stand-in line; (n) is the sample.", ""]
    Path(f"model/backtest/{season}_report.md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
