"""Shadow report: frozen Under rules and reference-price tests. Reads data, changes no picks.

    python shadow.py              # slates after 3 Nov 2026 -> model/shadow_report.md, shadow_props.csv
    python shadow.py --start 2026-10-29 --end 2026-11-03 --out DIR   # replay

Nothing in the model imports this file or its outputs. The constants below were fixed on
4 Nov 2026 (see claude/NBA_Advanced_Methods_Tests_4Nov2026.md) and must not be tuned on the
results shown here. Every bet is priced from the morning snapshot.
"""
import argparse
import csv
import math
import random
from collections import defaultdict
from pathlib import Path

from model import main_lines, read_csv
from nbalib import MARKETS, norm_name

START = "2026-11-04"
AU_BOOKS = {"sportsbet", "pointsbetau", "ladbrokes_au", "neds", "unibet", "tab", "betright"}
REF_BOOKS = {"fanduel", "draftkings", "betonlineag"}
REF_EXCHANGES = {"novig", "prophetx", "polymarket"}
OVER_BIAS = 0.0305    # Unders beat the de-vigged AU market by this much in the 2025-26 train set
EV_MIN = 0.02
MODEL_WEIGHT = 0.05
MIN_REF_BOOKS = 2
MIN_GAMES_FOR_MONEY = 250


def logit(p):
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def inv(x):
    return 1 / (1 + math.exp(-x))


def devig(over, under):
    return (1 / over) / (1 / over + 1 / under)


def mean(xs):
    return sum(xs) / len(xs)


def group(rows):
    out = defaultdict(list)
    for r in rows:
        out[(r["game"], norm_name(r["player"]), r["market"])].append(r)
    return out


def ref_probs(rows, line):
    """De-vigged Over probability per reference book at exactly this line."""
    prices = defaultdict(dict)
    for r in rows:
        if float(r["line"] or "nan") == line:
            prices[r["bookmaker"]][r["side"].lower()] = float(r["odds"])
    return {b: devig(p["over"], p["under"]) for b, p in prices.items()
            if {"over", "under"} <= set(p) and p["over"] > 1 and p["under"] > 1}


def model_probs(day):
    path = Path(f"model/scored_morning/{day}.csv")
    path = path if path.exists() else Path(f"model/scored/{day}.csv")
    return {(r["game"], r["player_key"], r["market"], r["side"], float(r["line"])): float(r["model_prob"])
            for r in read_csv(path)}


def box_scores(day):
    """{player_key: row}, or None until every game on the slate is final."""
    rows = read_csv(f"boxscores/{day}.csv")
    if not rows or not all(r["status"].startswith("Final") for r in rows):
        return None
    return {norm_name(r["player"]): r for r in rows}


def build_props(day):
    box = box_scores(day)
    if box is None:
        return []
    path = Path(f"odds/morning/{day}.csv")
    path = path if path.exists() else Path(f"odds/{day}.csv")
    au = group(r for r in read_csv(path) if r["date_melb"] == day and r["bookmaker"] in AU_BOOKS)
    ref = group(read_csv(f"odds/reference/{day}.csv"))
    model = model_probs(day)
    out = []
    for key, rows in au.items():
        game, player, market = key
        mains = main_lines(rows)
        if not mains:
            continue
        lines = [m["line"] for m in mains.values()]
        line = max(set(lines), key=lines.count)
        if float(line).is_integer():
            continue
        sub = {b: m for b, m in mains.items() if m["line"] == line}
        b = box.get(player)
        if b is None or "DNP" in b["status"] or b["minutes"] in ("0", ""):
            continue
        actual = float(b[MARKETS[market]])
        if actual == line:
            continue
        book_o = max(sub, key=lambda x: sub[x]["over"])
        book_u = max(sub, key=lambda x: sub[x]["under"])
        probs = ref_probs(ref.get(key, []), line)
        grp = lambda names: [p for k, p in probs.items() if k in names]
        out.append({"date_melb": day, "game": game, "player": player, "market": market, "line": line,
                    "actual": actual, "over_won": int(actual > line),
                    "au_prob": mean([devig(m["over"], m["under"]) for m in sub.values()]),
                    "over_odds": sub[book_o]["over"], "over_book": book_o,
                    "under_odds": sub[book_u]["under"], "under_book": book_u,
                    "model_over": model.get((game, player, market, "Over", line), ""),
                    "model_under": model.get((game, player, market, "Under", line), ""),
                    "ref_prob": mean(list(probs.values())) if len(probs) >= MIN_REF_BOOKS else "",
                    "ref_n": len(probs),
                    "ref_books_prob": mean(grp(REF_BOOKS)) if grp(REF_BOOKS) else "",
                    "ref_exch_prob": mean(grp(REF_EXCHANGES)) if grp(REF_EXCHANGES) else ""})
    return out


def bet(p, side, ev):
    won = p["over_won"] if side == "Over" else 1 - p["over_won"]
    odds = p["over_odds"] if side == "Over" else p["under_odds"]
    return {"game": p["date_melb"] + p["game"], "player": p["player"], "ev": ev, "won": won, "odds": odds,
            "pnl": odds - 1 if won else -1.0}


def capped(bets):
    seen, per_game, out = set(), defaultdict(int), []
    for b in sorted(bets, key=lambda x: -x["ev"]):
        if (b["game"], b["player"]) in seen or per_game[b["game"]] >= 2:
            continue
        seen.add((b["game"], b["player"]))
        per_game[b["game"]] += 1
        out.append(b)
    return out


def rules(props):
    r0, r1, r2, s1 = [], [], [], []
    for p in props:
        pu = 1 - p["au_prob"]
        ev = (pu + OVER_BIAS) * p["under_odds"] - 1
        b = bet(p, "Under", ev)
        r0.append(b)
        if ev > EV_MIN:
            r1.append(b)
            if p["model_under"] != "" and p["model_under"] > pu:
                r2.append(b)
        if p["ref_prob"] != "":
            for side, prob, odds in (("Over", p["ref_prob"], p["over_odds"]),
                                     ("Under", 1 - p["ref_prob"], p["under_odds"])):
                if prob * odds - 1 > EV_MIN:
                    s1.append(bet(p, side, prob * odds - 1))
    return [("R0 every Under at best AU price", r0), ("R1 Under above bias-adjusted AU consensus", r1),
            ("R2 R1 and the model agrees", r2), ("R2 capped, 1 per player, 2 per game", capped(r2)),
            ("S1 best AU price above reference price by 2%+", s1),
            ("S1 capped, 1 per player, 2 per game", capped(s1))]


def by_game(items, value):
    groups = defaultdict(list)
    for i in items:
        groups[i["game"]].append(value(i))
    return list(groups.values())


def boot_ci(groups, stat, n=2000):
    rng = random.Random(1)
    draws = []
    for _ in range(n):
        sample = [groups[rng.randrange(len(groups))] for _ in groups]
        draws.append(stat(sample))
    draws.sort()
    return draws[int(.025 * n)], draws[int(.975 * n)]


def roi_row(name, bets):
    if not bets:
        return f"| {name} | 0 | 0 | | | | | No data |"
    groups = by_game(bets, lambda b: b["pnl"])
    ratio = lambda g: 100 * sum(map(sum, g)) / sum(map(len, g))
    lo, hi = boot_ci(groups, ratio)
    ok = len(groups) >= MIN_GAMES_FOR_MONEY and lo > 0
    return (f"| {name} | {len(bets)} | {len(groups)} | {100 * mean([b['won'] for b in bets]):.1f} | "
            f"{mean([b['odds'] for b in bets]):.2f} | {ratio(groups):+.1f} | {lo:+.1f} to {hi:+.1f} | "
            f"{'Met' if ok else 'Not met'} |")


def forecasts(p):
    au, ref = p["au_prob"], p["ref_prob"]
    blend = .5 * logit(au) + .5 * logit(ref)
    return {"AU consensus": au, "AU minus Over bias": au - OVER_BIAS, "Reference, all": ref,
            "AU and reference, 50/50": inv(blend),
            "Same blend + 5% model": inv((1 - MODEL_WEIGHT) * blend + MODEL_WEIGHT * logit(p["model_over"]))}


def log_loss(y, p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def forecast_table(props):
    common = [p for p in props if p["ref_prob"] != "" and p["model_over"] != ""]
    L = ["## Forecasts: log-loss on Overs (lower is better)", ""]
    if not common:
        return L + ["No props with both reference and model prices settled yet.", ""]
    rows = [{"game": p["date_melb"] + p["game"], "y": p["over_won"], **forecasts(p)} for p in common]
    games = len({r["game"] for r in rows})
    L += [f"Same {len(rows)} props across {games} games for every forecast.", "",
          "| Forecast | Log-loss | Difference from AU consensus | 95% CI by game |", "|---|---|---|---|"]
    base = "AU consensus"
    for name in ("AU consensus", "AU minus Over bias", "Reference, all", "AU and reference, 50/50", "Same blend + 5% model"):
        loss = mean([log_loss(r["y"], r[name]) for r in rows])
        if name == base:
            L.append(f"| {name} | {loss:.5f} | | |")
            continue
        groups = by_game(rows, lambda r: log_loss(r["y"], r[name]) - log_loss(r["y"], r[base]))
        ratio = lambda g: sum(map(sum, g)) / sum(map(len, g))
        lo, hi = boot_ci(groups, ratio)
        L.append(f"| {name} | {loss:.5f} | {ratio(groups):+.5f} | {lo:+.5f} to {hi:+.5f} |")
    L += ["", "| Reference group | Props | Log-loss | AU log-loss on same props |", "|---|---|---|---|"]
    for name, col in (("FanDuel, DraftKings, BetOnline", "ref_books_prob"), ("Novig, ProphetX, Polymarket", "ref_exch_prob")):
        x = [p for p in props if p[col] != ""]
        if x:
            L.append(f"| {name} | {len(x)} | {mean([log_loss(p['over_won'], p[col]) for p in x]):.5f} | "
                     f"{mean([log_loss(p['over_won'], p['au_prob']) for p in x]):.5f} |")
    return L + [""]


def market_move(start, end):
    """Paper bets: did the market's median line move our way from morning to close?"""
    rows = [r for r in read_csv("model/picks_log.csv") if start <= r["date_melb"] <= end
            and r["tier"] in ("Diff 4", "Diff 3") and r.get("market_move") not in ("", None)]
    L = ["## Paper bets: market move, morning median to closing median", "",
         "Beat-CLV counts line shopping, so this is the figure that shows the market agreeing.", "",
         "| Tier | Bets | Moved our way | Flat | Moved against | Avg move |", "|---|---|---|---|---|---|"]
    for tier in ("Diff 4", "Diff 3"):
        m = [float(r["market_move"]) for r in rows if r["tier"] == tier]
        if m:
            L.append(f"| {tier} | {len(m)} | {sum(x > 0 for x in m)} | {sum(x == 0 for x in m)} | "
                     f"{sum(x < 0 for x in m)} | {mean(m):+.2f} |")
    return L + [""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default=START)
    ap.add_argument("--end", default="9999")
    ap.add_argument("--out", default="model")
    a = ap.parse_args()
    days = sorted({p.stem for p in [*Path("odds").glob("20*.csv"), *Path("odds/morning").glob("*.csv")]
                   if a.start <= p.stem <= a.end})
    props = [p for d in days for p in build_props(d)]
    slates = sorted({p["date_melb"] for p in props})
    L = ["# Shadow report", "",
         "Rules were frozen on 4 Nov 2026 and aren't tuned here. No pick, weight or stake depends on this file. "
         f"Bets use morning prices. The money test needs a lower CI above zero on at least {MIN_GAMES_FOR_MONEY} games.", "",
         f"Settled slates: {len(slates)}" + (f" ({slates[0]} to {slates[-1]})" if slates else ""), "",
         "## Frozen rules: flat stakes, ROI", "",
         "| Rule | Bets | Games | Hit % | Avg odds | ROI % | 95% CI by game | Money test |", "|---|---|---|---|---|---|---|---|"]
    L += [roi_row(n, b) for n, b in rules(props)]
    L.append("")
    if props:
        bias = 100 * (mean([1 - p["over_won"] for p in props]) - mean([1 - p["au_prob"] for p in props]))
        L += [f"Under hit rate minus de-vigged AU market: {bias:+.2f} points (2025-26: +3.05 train, +2.27 holdout).", ""]
    L += forecast_table(props) + market_move(a.start, a.end)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "shadow_report.md").write_text("\n".join(L))
    if props:
        with open(out / "shadow_props.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(props[0]))
            w.writeheader()
            w.writerows(props)
    print(f"shadow report: {len(slates)} slates, {len(props)} props")


if __name__ == "__main__":
    main()
