"""CES edge model v4 — scores every prop on the slate with fixed rules.

    python model.py                       # today's odds/latest.csv
    python model.py --odds odds/2026-10-28.csv --as-of 2026-10-28   # replay a past slate

Inputs (all produced by the GitHub jobs in this repo):
    odds/latest.csv          AU player-prop lines (Odds API)
    odds/game_lines.csv      spreads + totals (optional; D7 and minutes use it)
    data/gamelogs/*.csv      ESPN player game logs (current + previous season)
    data/injuries/latest.csv ESPN injury list (optional; ignored for past slates)

Outputs:
    model/scored/<date>.csv  every prop, Over and Under, with D1-D8, CES, tier, model probability
    model/slate_<date>.md    readable summary for the morning scan

Determinants follow nba_edge_model_v3.py (Edge Model Framework v1.0); thresholds that were
absolute points in v3 are scaled per stat. Probabilities are NOT calibrated yet (step 4).
"""
import argparse
import csv
import math
import statistics as st
from collections import defaultdict
from datetime import date
from pathlib import Path

from nbalib import MARKETS, melb_to_us, norm_name, prev_season, season_of, team_key

VERSION = "v4.0"
WEIGHTS = {"D1": .20, "D2": .20, "D3": .15, "D4": .15, "D5": .10, "D6": .10, "D7": .05, "D8": .05}
MIN_ODDS = 1.55
SHRINK = 0.8          # pull model probabilities toward 50% until calibrated
STAT_SCALE = {"pts": 1.0, "pra": 1.3, "reb": 0.5, "ast": 0.5, "threes": 0.27}
LINE_STEP = {"pts": 1.0, "pra": 1.0, "reb": 0.5, "ast": 0.5, "threes": 0.5}
GTD = {"questionable", "doubtful", "day-to-day", "game-time decision"}


# ─── data loading ────────────────────────────────────────────────────────────

def read_csv(path):
    p = Path(path)
    if not p.exists():
        return []
    with open(p) as f:
        return list(csv.DictReader(f))


def num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class Logs:
    def __init__(self, season, cutoff_us):
        self.season, self.prev = season, prev_season(season)
        rows = [r for s in (self.prev, season) for r in read_csv(f"data/gamelogs/{s}.csv")
                if r["date_us"] < cutoff_us.isoformat()]
        for r in rows:
            for k in ("min", "pts", "reb", "ast", "threes", "pra", "team_pts", "opp_pts"):
                r[k] = num(r[k])
            r["dnp"] = r["dnp"] == "1"
        rows.sort(key=lambda r: (r["date_us"], r["game_id"]))
        self.rows = rows
        self.by_player = defaultdict(list)
        for r in rows:
            self.by_player[r["player_key"]].append(r)
        # team-game totals
        tg = {}
        for r in rows:
            key = (r["game_id"], r["team"])
            g = tg.setdefault(key, {"season": r["season"], "date_us": r["date_us"], "team": r["team"],
                                    "team_name": r["team_name"], "opp": r["opp"],
                                    "pts": r["team_pts"], "opp_pts": r["opp_pts"],
                                    "reb": 0, "ast": 0, "threes": 0, "players": set()})
            g["reb"] += r["reb"]; g["ast"] += r["ast"]; g["threes"] += r["threes"]
            if not r["dnp"]:
                g["players"].add(r["player_key"])
        self.team_games = defaultdict(list)  # team nickname key -> games (sorted)
        self.allowed = defaultdict(lambda: defaultdict(list))  # season -> team -> list of dicts
        for (gid, team), g in sorted(tg.items(), key=lambda kv: kv[1]["date_us"]):
            self.team_games[team_key(g["team_name"])].append(g)
            opp = tg.get((gid, g["opp"]))
            if opp:
                self.allowed[g["season"]][team_key(g["team_name"])].append({
                    "pts": opp["pts"], "reb": opp["reb"], "ast": opp["ast"], "threes": opp["threes"],
                    "pra": opp["pts"] + opp["reb"] + opp["ast"]})
        totals = [g["pts"] + g["opp_pts"] for g in tg.values() if g["season"] == season]
        if len(totals) < 40:
            totals += [g["pts"] + g["opp_pts"] for g in tg.values() if g["season"] == self.prev]
        self.league_total = st.mean(totals) if totals else 228.0
        self.def_rank = self._def_ranks()

    def _def_ranks(self):
        """Per stat: team nickname -> rank 1 (allows least) .. 30 (allows most)."""
        ranks = {}
        teams = set(self.allowed[self.season]) | set(self.allowed[self.prev])
        for stat in STAT_SCALE:
            vals = {}
            for t in teams:
                cur = [g[stat] for g in self.allowed[self.season].get(t, [])]
                prv = [g[stat] for g in self.allowed[self.prev].get(t, [])]
                k = 10 if prv else 0
                if not cur and not prv:
                    continue
                vals[t] = ((sum(cur) + k * (st.mean(prv) if prv else 0)) / (len(cur) + k))
            order = sorted(vals, key=vals.get)
            ranks[stat] = {t: i + 1 for i, t in enumerate(order)}
        return ranks


# ─── market selection ────────────────────────────────────────────────────────

def main_lines(rows):
    """rows for one player+market -> {book: {line, over, under}} using each book's main line."""
    by_book = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        by_book[r["bookmaker"]][num(r["line"])][r["side"].lower()] = num(r["odds"])
    out = {}
    for book, lines in by_book.items():
        both = {ln: p for ln, p in lines.items() if "over" in p and "under" in p}
        if both:
            ln = min(both, key=lambda x: abs(both[x]["over"] - both[x]["under"]))
            out[book] = {"line": ln, "over": both[ln]["over"], "under": both[ln]["under"]}
        else:  # over-only books: keep a single near-even line, skip alternate ladders
            ok = [ln for ln, p in lines.items() if 1.6 <= p.get("over", 0) <= 2.4]
            if len(ok) == 1:
                out[book] = {"line": ok[0], "over": lines[ok[0]]["over"], "under": None}
    return out


def best_option(mains, side, stat):
    if not mains:
        return None
    lines = [m["line"] for m in mains.values()]
    med = st.median(lines)
    if side == "Over":
        line = min(lines)
        offers = {b: m["over"] for b, m in mains.items() if m["line"] == line and m["over"]}
        softer = med - line
    else:
        line = max(lines)
        offers = {b: m["under"] for b, m in mains.items() if m["line"] == line and m["under"]}
        softer = line - med
    if not offers:
        return None
    book = max(offers, key=offers.get)
    med_price = st.median(offers.values())
    return {"line": line, "odds": offers[book], "book": book, "n_books_at_line": len(offers),
            "n_books": len(mains), "median_line": med, "softer": softer,
            "price_edge": offers[book] - med_price}


# ─── probability ─────────────────────────────────────────────────────────────

def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def prob_over(mu, sd, line, stat):
    if mu <= 0:
        return 0.0
    if stat == "threes":  # Poisson
        k = math.floor(line) + 1
        cdf = sum(math.exp(-mu) * mu ** i / math.factorial(i) for i in range(k))
        return 1 - cdf
    x = line + 0.5 if float(line).is_integer() else line
    return 1 - phi((x - mu) / sd)


# ─── determinants (v3 definitions) ───────────────────────────────────────────

def d1(gap, stat):
    s = STAT_SCALE[stat]
    return 2 if gap >= 3 * s else 1 if gap >= 1.5 * s else 0 if gap >= -1.5 * s else -1 if gap >= -3 * s else -2


def d2(l10_avg, season_avg, line, hits10, side):
    better = (l10_avg > season_avg) if side == "Over" else (l10_avg < season_avg)
    beyond = (l10_avg > line) if side == "Over" else (l10_avg < line)
    if better and beyond and hits10 >= 7:
        return 2
    if beyond or hits10 >= 6:
        return 1
    return 0 if hits10 >= 5 else -1 if hits10 >= 3 else -2


def d3(hit_pct):
    return 2 if hit_pct >= 70 else 1 if hit_pct >= 58 else 0 if hit_pct >= 45 else -1 if hit_pct >= 35 else -2


def d4(edge_pts):
    return 2 if edge_pts >= 10 else 1 if edge_pts >= 5 else 0 if edge_pts >= 0 else -1 if edge_pts >= -5 else -2


def d6(rank, side):
    if not rank:
        return 0
    if side == "Under":
        rank = 31 - rank
    return 2 if rank >= 26 else 1 if rank >= 20 else 0 if rank >= 11 else -1 if rank >= 6 else -2


def clamp(x):
    return max(-2, min(2, int(round(x))))


# ─── per-player context ──────────────────────────────────────────────────────

def blend(cur, prev, k):
    if not cur and not prev:
        return 0.0
    k = min(k, len(prev))
    pm = st.mean(prev) if prev else 0
    return (sum(cur) + k * pm) / (len(cur) + k) if (cur or k) else 0.0


def score_player_market(logs, pkey, stat, team, opp, slate_us, inj, game_ctx, market_opts):
    hist = [r for r in logs.by_player.get(pkey, []) if not r["dnp"] and r["min"] > 0]
    cur = [r for r in hist if r["season"] == logs.season]
    prv = [r for r in hist if r["season"] == logs.prev]
    flags = []
    if not hist:
        return None, ["no game logs"]
    last_team = team_key((cur or prv)[-1]["team_name"])
    if last_team not in (team, opp):
        return None, [f"team mismatch ({(cur or prv)[-1]['team_name']})"]
    my_team = last_team
    opp_team = opp if my_team == team else team
    traded = bool(cur and prv and team_key(prv[-1]["team_name"]) != team_key(cur[-1]["team_name"]))
    if traded:
        flags.append("traded/role change: last season down-weighted")
    n = len(cur)
    k = 0 if n >= 20 else (3 if traded else 10)
    xs_c, xs_p = [r[stat] for r in cur], [r[stat] for r in prv]
    ms_c, ms_p = [r["min"] for r in cur], [r["min"] for r in prv]
    season_avg = blend(xs_c, xs_p, k)
    min_avg = blend(ms_c, ms_p, k)
    if n < 5 and not prv:
        flags.append(f"small sample ({n} games, no last-season baseline)")
    elif n < 5:
        flags.append(f"early season: {n} games this season, blended with last season")

    seq = prv + cur
    last10, last5, last20 = seq[-10:], seq[-5:], seq[-20:]
    l10_vals = [r[stat] for r in last10]
    l10_avg = st.mean(l10_vals)

    # minutes projection
    m_proj = 0.5 * st.mean(r["min"] for r in last5) + 0.3 * st.mean(r["min"] for r in last10) + 0.2 * min_avg
    absences = game_ctx["absences"].get(my_team, [])
    absences = [a for a in absences if a != pkey]
    if absences and m_proj >= 20:
        m_proj += min(4.0, 1.5 * len(absences))
        flags.append("key teammates out: " + ", ".join(absences))
    spread = game_ctx["spread"].get(my_team)
    if spread is not None and m_proj >= 28:
        if abs(spread) >= 12:
            m_proj -= 2.5
        elif abs(spread) >= 8:
            m_proj -= 1.0
    rest = game_ctx["rest"].get(my_team)
    if rest == 1:
        m_proj -= 1.0
        flags.append("back-to-back")

    def rate(rows):
        m = sum(r["min"] for r in rows)
        return sum(r[stat] for r in rows) / m if m else 0.0
    rate_season = (rate(cur) * n + rate(prv) * min(k, len(prv))) / (n + min(k, len(prv))) if (n or prv) else 0
    rate_proj = 0.6 * rate_season + 0.4 * rate(last10)
    rate_proj *= 1 + min(0.08, 0.03 * len(absences))
    mu = max(0.0, rate_proj * m_proj)
    vals20 = [r[stat] for r in last20]
    sd_emp = st.pstdev(vals20) if len(vals20) >= 5 else 0
    sd = max(sd_emp, math.sqrt(mu) if mu else 1, 0.15 * mu) if len(vals20) >= 5 else max(1.3 * math.sqrt(mu or 1), 0.25 * mu)

    # hit-rate sample: this season, topped up with last season's most recent games to 20
    sample = cur if n >= 15 else (prv[-(20 - n):] + cur if prv else cur)
    status = inj.get(pkey, "")
    out = []
    for side, opt in market_opts.items():
        if not opt:
            continue
        line, odds = opt["line"], opt["odds"]
        sgn = 1 if side == "Over" else -1
        hits10 = sum((v > line) if side == "Over" else (v < line) for v in l10_vals)
        hits10 = round(hits10 * 10 / len(l10_vals))
        hit_pct = 100 * sum(((r[stat] > line) if side == "Over" else (r[stat] < line)) for r in sample) / len(sample)
        p_over = prob_over(mu, sd, line, stat)
        p = p_over if side == "Over" else 1 - p_over
        if float(line).is_integer():
            p = p * 0.93  # rough push allowance
        p = 0.5 + SHRINK * (p - 0.5)
        implied = 1 / odds
        D = {}
        D["D1"] = d1(sgn * (season_avg - line), stat)
        D["D2"] = d2(l10_avg, season_avg, line, hits10, side)
        D["D3"] = d3(hit_pct)
        D["D4"] = d4(100 * (p - implied))
        s = status.lower()
        if s in GTD:
            D["D5"] = -2
        elif s == "probable":
            D["D5"] = -1
        else:
            D["D5"] = clamp(sgn * min(2, len(absences)))
        D["D6"] = d6(logs.def_rank.get(stat, {}).get(opp_team), side)
        env = 0.0
        total = game_ctx["total"].get(my_team)
        if total is not None:
            env += 1 if total - logs.league_total >= 6 else -1 if total - logs.league_total <= -6 else 0
        env += 0.5 if game_ctx["home"].get(my_team) else 0
        env += 0.5 if (rest or 0) >= 2 else -1 if rest == 1 else 0
        D["D7"] = clamp(sgn * env)
        d8 = 0
        if opt["softer"] >= LINE_STEP[stat]:
            d8 += 1
        if opt["price_edge"] >= 0.07:
            d8 += 1
        D["D8"] = clamp(d8)
        ces = round(sum(D[d] * WEIGHTS[d] for d in WEIGHTS), 2)
        tier = "Diff 4" if ces >= 1.2 else "Diff 3" if ces >= 0.7 else "Watchlist" if ces >= 0.3 else "Pass"
        f = list(flags)
        if opt["softer"] >= LINE_STEP[stat] and opt["n_books_at_line"] == 1:
            f.append("soft at one book only - may be stale")
        if odds < MIN_ODDS:
            tier, _ = "Pass", f.append("odds below 1.55")
        if s == "out":
            tier, _ = "Void", f.append("player OUT")
        elif s in GTD and tier in ("Diff 4", "Diff 3"):
            tier, _ = "Watchlist", f.append(f"GTD ({status}) - Watchlist only")
        if tier in ("Diff 4", "Diff 3") and ("small sample" in " ".join(f) or (traded and n < 3)):
            tier, _ = "Watchlist", f.append("capped: sample too small")
        if side == "Under":
            f.append("under - shadow only")
        out.append({
            "side": side, "line": line, "odds": odds, "book": opt["book"],
            "n_books_at_line": opt["n_books_at_line"], "n_books": opt["n_books"],
            "median_line": opt["median_line"], "implied": round(implied, 3), "model_prob": round(p, 3),
            "ev_pct": round(100 * (p * odds - 1), 1), "proj": round(mu, 1), "proj_min": round(m_proj, 1),
            "sd": round(sd, 1), "season_avg": round(season_avg, 1), "l10_avg": round(l10_avg, 1),
            "l10_hits": f"{hits10}/10", "hit_rate": round(hit_pct), "n_cur": n, "n_prev": len(prv),
            "status": status, **D, "ces": ces, "tier": tier, "flags": "; ".join(f),
        })
    return out, flags


# ─── game context ────────────────────────────────────────────────────────────

def build_game_ctx(games, game_lines, logs, slate_us, injuries, use_injuries):
    ctx = {"spread": {}, "total": {}, "home": {}, "rest": {}, "absences": defaultdict(list)}
    for g in games:
        away, home = [x.strip() for x in g.split(" @ ")]
        ctx["home"][team_key(home)] = True
        ctx["home"][team_key(away)] = False
    spreads, totals = defaultdict(list), defaultdict(list)
    for r in game_lines:
        if r["market"] == "spreads":
            spreads[team_key(r["name"])].append(num(r["point"]))
        elif r["market"] == "totals" and r["name"] == "Over":
            for t in (r["home_team"], r["away_team"]):
                totals[team_key(t)].append(num(r["point"]))
    ctx["spread"] = {t: st.median(v) for t, v in spreads.items() if v}
    ctx["total"] = {t: st.median(v) for t, v in totals.items() if v}
    for t, gl in logs.team_games.items():
        if gl:
            ctx["rest"][t] = (slate_us - date.fromisoformat(gl[-1]["date_us"])).days
    if use_injuries:
        out_by_team = defaultdict(list)
        for r in injuries:
            if r["status"].lower() in ("out", "doubtful"):
                out_by_team[team_key(r["team_name"])].append(r["player_key"])
        for t, keys in out_by_team.items():
            recent = logs.team_games.get(t, [])[-5:]
            for pk in keys:
                hist = [r for r in logs.by_player.get(pk, []) if not r["dnp"]]
                if not hist:
                    continue
                avg_min = st.mean(r["min"] for r in hist[-20:])
                played_recent = sum(pk in g["players"] for g in recent)
                if avg_min >= 24 and played_recent >= min(2, len(recent)):
                    ctx["absences"][t].append(pk)
    return ctx


# ─── main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--odds", default="odds/latest.csv")
    ap.add_argument("--game-lines", default="odds/game_lines.csv")
    ap.add_argument("--as-of", help="Melbourne slate date (default: from the odds file)")
    args = ap.parse_args()

    odds = read_csv(args.odds)
    if not odds:
        raise SystemExit(f"no odds in {args.odds}")
    slate = date.fromisoformat(args.as_of or odds[0]["date_melb"])
    odds = [r for r in odds if r["date_melb"] == slate.isoformat() and r["market"] in MARKETS]
    slate_us = melb_to_us(slate)
    season = season_of(slate_us)
    logs = Logs(season, slate_us)
    live = args.as_of is None or slate >= date.today()
    injuries = read_csv("data/injuries/latest.csv") if live else []
    inj = {r["player_key"]: r["status"] for r in injuries}
    glines = [r for r in read_csv(args.game_lines) if r.get("date_melb") == slate.isoformat()]
    games = sorted({r["game"] for r in odds})
    ctx = build_game_ctx(games, glines, logs, slate_us, injuries, live)

    grouped = defaultdict(list)
    meta = {}
    for r in odds:
        key = (r["game"], norm_name(r["player"]), r["market"])
        grouped[key].append(r)
        meta[key] = (r["player"], r["tipoff_melb"])
    results, skipped = [], defaultdict(list)
    for (game, pkey, market), rows in grouped.items():
        stat = MARKETS[market]
        mains = main_lines(rows)
        opts = {s: best_option(mains, s, stat) for s in ("Over", "Under")}
        away, home = [x.strip() for x in game.split(" @ ")]
        scored, why = score_player_market(logs, pkey, stat, team_key(away), team_key(home),
                                          slate_us, inj, ctx, opts)
        player, tip = meta[(game, pkey, market)]
        if scored is None:
            skipped[why[0]].append(player)
            continue
        for s in scored:
            results.append({"date_melb": slate.isoformat(), "tipoff_melb": tip, "game": game,
                            "player": player, "player_key": pkey, "market": market, "stat": stat,
                            **s, "model_version": VERSION})

    # max 2 bets per game (overs, Diff 3+), no two on the same player
    by_game = defaultdict(list)
    for r in results:
        if r["side"] == "Over" and r["tier"] in ("Diff 4", "Diff 3"):
            by_game[r["game"]].append(r)
    for g, rs in by_game.items():
        used, taken = set(), 0
        for r in sorted(rs, key=lambda x: -x["ces"]):
            if taken < 2 and r["player_key"] not in used:
                used.add(r["player_key"]); taken += 1
            else:
                r["flags"] = (r["flags"] + "; " if r["flags"] else "") + "exceeds 2 bets/game or same player - Watchlist"
                r["tier"] = "Watchlist"

    results.sort(key=lambda r: (-r["ces"], r["player"]))
    out = Path("model/scored")
    out.mkdir(parents=True, exist_ok=True)
    fields = list(results[0].keys()) if results else ["date_melb"]
    with open(out / f"{slate.isoformat()}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(results)
    write_summary(slate, results, skipped, logs, games, ctx)
    tiers = defaultdict(int)
    for r in results:
        tiers[(r["side"], r["tier"])] += 1
    print(f"{slate}: {len(games)} games, {len(results)} scored props, skipped {sum(map(len, skipped.values()))}")
    print(dict(tiers))


def write_summary(slate, results, skipped, logs, games, ctx):
    def line(r):
        return (f"| {r['player']} | {r['stat']} {r['side']} {r['line']:g} | {r['odds']:.2f} {r['book']} | "
                f"{r['ces']:+.2f} | {r['model_prob']:.0%} vs {r['implied']:.0%} | {r['proj']} ({r['proj_min']} min) | "
                f"{r['season_avg']} / {r['l10_avg']} / {r['l10_hits']} / {r['hit_rate']}% | "
                f"{r['D1']} {r['D2']} {r['D3']} {r['D4']} {r['D5']} {r['D6']} {r['D7']} {r['D8']} | {r['flags']} |")
    head = ("| Player | Prop | Price | CES | Model vs implied | Proj | Avg / L10 / L10 hits / hit% | D1-D8 | Flags |\n"
            "|---|---|---|---|---|---|---|---|---|")
    md = [f"# Model {VERSION} slate — {slate}", "",
          f"{len(games)} games, {len(results)} props scored (both sides). Season {logs.season}; "
          f"league avg total {logs.league_total:.1f}. Probabilities are uncalibrated (shrunk {SHRINK}).", ""]
    for title, sel in [("Diff 4 / Diff 3 — Overs", lambda r: r["side"] == "Over" and r["tier"] in ("Diff 4", "Diff 3")),
                       ("Watchlist — Overs (top 15)", lambda r: r["side"] == "Over" and r["tier"] == "Watchlist"),
                       ("Unders CES >= 0.70 (shadow only)", lambda r: r["side"] == "Under" and r["ces"] >= 0.7)]:
        rows = [r for r in results if sel(r)][:15]
        md += [f"## {title}", "", head] + [line(r) for r in rows] + ([""] if rows else ["| none |", ""])
    md += ["## Context", ""]
    for g in games:
        away, home = [team_key(x) for x in g.split(" @ ")]
        md.append(f"- {g}: spread {ctx['spread'].get(home, 'n/a')} (home), total {ctx['total'].get(home, 'n/a')}, "
                  f"rest days {ctx['rest'].get(away, '?')}/{ctx['rest'].get(home, '?')}, "
                  f"key absences: {', '.join(ctx['absences'].get(away, []) + ctx['absences'].get(home, [])) or 'none'}")
    md += ["", "## Skipped", ""] + [f"- {k}: {', '.join(sorted(set(v)))}" for k, v in skipped.items()]
    Path(f"model/slate_{slate.isoformat()}.md").write_text("\n".join(md) + "\n")
    Path("model/slate_latest.md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
