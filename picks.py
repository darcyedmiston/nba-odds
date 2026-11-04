"""The pick log: model/picks_log.csv is the single record of logged picks.

    python picks.py import                   # one-off: build the log from model/import/
    python picks.py log-model [--source S]   # add the slate's Diff 3+ and top 15 Watchlist Overs
    python picks.py settle                   # fill results, P&L and CLV, rewrite the report
    python picks.py update --date D --player P --stat S [--line L] field=value ...
    python picks.py add field=value ...

Rows are never deleted. To replace a pick, set its tier to Superseded and add the new row.
Results come from boxscores/<date>.csv and only fill blank fields, so a hand-entered result
or a correction is never overwritten.
"""
import argparse
import csv
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from model import main_lines
from nbalib import norm_name

LOG = Path("model/picks_log.csv")
IMPORT = Path("model/import/picks_import.psv")
REPORT = Path("model/picks_report.md")
DS = [f"D{i}" for i in range(1, 9)]
COLUMNS = ["date_melb", "tipoff_melb", "game", "player", "player_key", "stat", "side", "line", "odds",
           "book", "tier", "ces", *DS, "model_stake", "rec_stake", "placed", "actual_stake", "override",
           "source", "model_version", "actual", "margin", "result", "pnl_flat10", "close_line",
           "close_odds", "clv_line", "clv_pct", "beat_clv", "market_move", "key_factors",
           "risk_flagged", "post_game_review"]
MARKET = {"pts": "player_points", "reb": "player_rebounds", "ast": "player_assists",
          "threes": "player_threes", "pra": "player_points_rebounds_assists"}
BETS = ("Diff 4", "Diff 3")
EARLY_CAP_END = "2026-11-06"  # runbook: every tier is capped at $10 until about here


def read(path=LOG):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(rows):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, restval="")
        w.writeheader()
        w.writerows(rows)


def stakes(row):
    """Stake columns follow the tier and placed status, per the staking rule."""
    tier, paper = row["tier"], row["placed"] == "Paper"
    model = {"Diff 4": 15, "Diff 3": 10}.get(tier, 0) if paper else 0
    rec = min(model, 10) if row["date_melb"] < EARLY_CAP_END else model
    row.update(model_stake=model, rec_stake=rec, actual_stake=rec if paper else "")
    return row


def cmd_import():
    if LOG.exists():
        sys.exit(f"{LOG} already exists; import only runs once")
    rows = []
    with open(IMPORT, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="|"):
            ds = [("" if d == "_" else d) for d in r["ds"].split()]
            row = dict(zip(DS, ds))
            row.update(date_melb=r["date"], tipoff_melb=r["tip"], game=r["game"], player=r["player"],
                       player_key=norm_name(r["player"]), stat=r["stat"], side="Over", line=r["line"],
                       odds=r["odds"], book=r["book"], tier=r["tier"], ces=r["ces"],
                       placed="Paper" if r["placed"] == "P" else "No",
                       override="Yes" if r["override"] == "Y" else "No", source=r["source"],
                       model_version=r["version"], actual=r["actual"], result=r["result"],
                       key_factors="", risk_flagged="", post_game_review="")
            rows.append(stakes(row))
    write(rows)
    print(f"imported {len(rows)} rows")


def key(r):
    return r["date_melb"], r["player_key"], r["stat"], r["side"]


def cmd_log_model(source):
    scored = sorted(Path("model/scored").glob("*.csv"))
    if not scored:
        print("no scored slate")
        return
    path = scored[-1]
    day = path.stem
    if day < datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%Y-%m-%d"):
        print(f"latest slate {day} has passed, nothing to log")
        return
    rows = read()
    active = {key(r) for r in rows if r["tier"] != "Superseded"}
    bets = defaultdict(int)
    for r in rows:
        if r["date_melb"] == day and r["placed"] == "Paper" and r["tier"] != "Superseded":
            bets[r["game"]] += 1
    cand = [r for r in read(path) if r["side"] == "Over"]
    picks = [r for r in cand if r["tier"] in BETS]
    watch = sorted((r for r in cand if r["tier"] == "Watchlist"), key=lambda r: -float(r["ces"]))[:15]
    added = 0
    for r in picks + watch:
        row = {c: r.get(c, "") for c in ("date_melb", "tipoff_melb", "game", "player", "player_key", "stat",
                                         "side", "line", "odds", "book", "tier", "ces", *DS, "model_version")}
        if key(row) in active:
            continue
        flags = r.get("flags", "")
        if r["tier"] in BETS and bets[r["game"]] >= 2:  # a later refresh can't exceed the cap
            row["tier"] = "Watchlist"
            flags = (flags + "; " if flags else "") + "exceeds 2 bets/game - Watchlist"
        elif r["tier"] in BETS:
            bets[r["game"]] += 1
        row.update(placed="Paper" if row["tier"] in BETS else "No", override="No", source=source,
                   key_factors=(f"Line: {r['book']} {r['line']} @ {r['odds']} (Odds API; {r['n_books_at_line']}/"
                                f"{r['n_books']} books at line, median {r['median_line']}); model {r['model_prob']} "
                                f"vs implied {r['implied']}, EV {r['ev_pct']}%; proj {r['proj']} in {r['proj_min']} "
                                f"min; avg {r['season_avg']} / L10 {r['l10_avg']} ({r['l10_hits']}) / hit {r['hit_rate']}%"),
                   risk_flagged=flags)
        rows.append(stakes(row))
        added += 1
    write(rows)
    print(f"{day}: logged {added} new picks")


def closing_data(day):
    """{(player_key, market): (close median, [rows])} for one slate."""
    path = Path(f"odds/closing/{day}.csv")
    grouped = defaultdict(list)
    for r in read(path):
        grouped[(norm_name(r["player"]), r["market"])].append(r)
    out = {}
    for k, rows in grouped.items():
        mains = main_lines(rows)
        if mains:
            out[k] = (st.median(m["line"] for m in mains.values()), rows)
    return out


def morning_medians(day):
    path = Path(f"model/scored_morning/{day}.csv")
    path = path if path.exists() else Path(f"model/scored/{day}.csv")
    return {(r["player_key"], r["stat"], r["side"]): float(r["median_line"]) for r in read(path)}


def fmt(x):
    return f"{x:g}"


def settle_row(row, box):
    line, odds = float(row["line"]), float(row["odds"])
    if row["actual"] and row["result"] and row["pnl_flat10"]:
        return
    if row["result"] == "Void":
        row["pnl_flat10"] = "0.00"
        return
    if not row["result"]:
        b = box.get(row["player_key"])
        if b is None:
            # A player with no box-score line didn't play, once the slate's games are all final.
            if box and all(x["status"].startswith("Final") for x in box.values()):
                row.update(actual="DNP", result="Void", pnl_flat10="0.00")
            return
        if not b["status"].startswith("Final"):
            return
        if "DNP" in b["status"] or b["minutes"] in ("0", ""):
            row.update(actual="DNP", result="Void", pnl_flat10="0.00")
            return
        row["actual"] = fmt(float(b[row["stat"]]))
    actual = float(row["actual"])
    row["margin"] = f"{actual - line:+g}"
    if not row["result"]:
        if actual == line:
            row["result"] = "Push"
        else:
            won = actual > line if row["side"] == "Over" else actual < line
            row["result"] = "Win" if won else "Loss"
    row["pnl_flat10"] = {"Win": f"{10 * (odds - 1):.2f}", "Loss": "-10.00"}.get(row["result"], "0.00")


def clv_row(row, close, medians):
    got = close.get((row["player_key"], MARKET[row["stat"]]))
    if got is None or row["close_line"]:
        return
    cm, rows = got
    sign = 1 if row["side"] == "Over" else -1
    line, odds = float(row["line"]), float(row["odds"])
    at_line = [r for r in rows if r["side"] == row["side"] and r["line"] and float(r["line"]) == line]
    same = [float(r["odds"]) for r in at_line if r["bookmaker"] == row["book"]]
    co = same[0] if same else max((float(r["odds"]) for r in at_line), default=None)
    clv_line = sign * (cm - line)
    row.update(close_line=fmt(cm), clv_line=f"{clv_line:+g}")
    pct = None
    if co:
        pct = odds / co - 1
        row.update(close_odds=f"{co:.2f}", clv_pct=f"{100 * pct:+.1f}%")
    if clv_line > 0:
        row["beat_clv"] = "Yes"
    elif clv_line < 0:
        row["beat_clv"] = "No"
    elif pct is not None:
        row["beat_clv"] = "Yes" if pct > 0 else "No" if pct < 0 else "Flat"
    med = medians.get((row["player_key"], row["stat"], row["side"]))
    if med is not None:
        row["market_move"] = f"{sign * (cm - med):+g}"


def group_line(rows):
    settled = [r for r in rows if r["result"] in ("Win", "Loss")]
    n = len(settled)
    if not n:
        return "0 | | | |"
    wins = sum(r["result"] == "Win" for r in settled)
    pnl = sum(float(r["pnl_flat10"]) for r in settled)
    return f"{n} | {wins} | {100 * wins / n:.1f} | {pnl:+.2f} | {100 * pnl / (10 * n):+.1f}"


def staked_pnl(rows):
    total = staked = 0.0
    for r in rows:
        if r["placed"] == "Paper" and r["result"] in ("Win", "Loss"):
            stake = float(r["actual_stake"] or 0)
            staked += stake
            total += stake * float(r["pnl_flat10"]) / 10
    return total, staked


def write_report(rows):
    head = "| Group | n | Wins | Hit % | P&L (flat $10) | ROI % |\n|---|---|---|---|---|---|"
    out = ["# Pick log report", "", "Generated from `model/picks_log.csv`. Samples under ~300 are noise.", ""]
    total, staked = staked_pnl(rows)
    roi = f"{100 * total / staked:+.1f}%" if staked else "n/a"
    out += [f"**Paper P&L at logged stakes:** {total:+.2f} on {staked:.0f} staked ({roi}). "
            f"Pending rows: {sum(not r['result'] for r in rows)}.", "", "## By tier (Superseded reported separately)", "", head]
    for tier in ("Diff 4", "Diff 3", "Watchlist", "Pass", "Superseded"):
        out.append(f"| {tier} | {group_line([r for r in rows if r['tier'] == tier])} |")
    out += ["", "## Overrides (shadow result of the row as logged)", "", head]
    for name, flag in (("Overridden", "Yes"), ("Not overridden", "No")):
        out.append(f"| {name} | {group_line([r for r in rows if r['override'] == flag and r['tier'] != 'Superseded'])} |")
    out += ["", "## CLV on paper bets", "",
            "Line CLV includes line shopping. Market move is the morning median to the closing median, "
            "and only that shows the market agreeing.", "",
            "| Tier | With close | Beat CLV | Beat % | Avg market move | Moved our way | Moved against |",
            "|---|---|---|---|---|---|---|"]
    for tier in BETS:
        sel = [r for r in rows if r["tier"] == tier and r["close_line"]]
        moves = [float(r["market_move"]) for r in sel if r["market_move"]]
        beat = sum(r["beat_clv"] == "Yes" for r in sel)
        if sel and moves:
            out.append(f"| {tier} | {len(sel)} | {beat} | {100 * beat / len(sel):.1f} | {st.mean(moves):+.2f} | "
                       f"{sum(m > 0 for m in moves)} | {sum(m < 0 for m in moves)} |")
    REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")


def cmd_settle():
    rows = read()
    cache = {}
    for row in rows:
        day = row["date_melb"]
        if day not in cache:
            box = {norm_name(b["player"]): b for b in read(f"boxscores/{day}.csv")}
            cache[day] = (box, closing_data(day), morning_medians(day))
        box, close, medians = cache[day]
        settle_row(row, box)
        clv_row(row, close, medians)
    write(rows)
    write_report(rows)
    print(f"settled: {sum(bool(r['result']) for r in rows)} of {len(rows)}")


def parse_fields(items):
    out = {}
    for item in items:
        name, _, value = item.partition("=")
        if name not in COLUMNS:
            sys.exit(f"unknown field {name}")
        out[name] = value
    return out


def cmd_update(args):
    rows = read()
    fields = parse_fields(args.fields)
    hits = [r for r in rows if r["date_melb"] == args.date and r["player_key"] == norm_name(args.player)
            and r["stat"] == args.stat and (args.line is None or float(r["line"]) == args.line)
            and r["tier"] != "Superseded"]
    if len(hits) != 1:
        sys.exit(f"expected one active row, found {len(hits)}; add --line if needed")
    hits[0].update(fields)
    if "actual_stake" not in fields:
        stakes(hits[0])
    write(rows)
    print(f"updated {args.player} {args.stat}")


def cmd_add(items):
    rows = read()
    row = parse_fields(items)
    missing = {"date_melb", "player", "stat", "line", "odds", "tier", "placed"} - set(row)
    if missing:
        sys.exit(f"missing fields: {sorted(missing)}")
    row.setdefault("side", "Over")
    row.setdefault("override", "No")
    row["player_key"] = norm_name(row["player"])
    rows.append(stakes(row))
    write(rows)
    print(f"added {row['player']} {row['stat']}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("import")
    lm = sub.add_parser("log-model")
    lm.add_argument("--source", default="scan")
    sub.add_parser("settle")
    up = sub.add_parser("update")
    up.add_argument("--date", required=True)
    up.add_argument("--player", required=True)
    up.add_argument("--stat", required=True, choices=list(MARKET))
    up.add_argument("--line", type=float)
    up.add_argument("fields", nargs="+")
    ad = sub.add_parser("add")
    ad.add_argument("fields", nargs="+")
    a = ap.parse_args()
    if a.cmd == "import":
        cmd_import()
    elif a.cmd == "log-model":
        cmd_log_model(a.source)
    elif a.cmd == "settle":
        cmd_settle()
    elif a.cmd == "update":
        cmd_update(a)
    else:
        cmd_add(a.fields)


if __name__ == "__main__":
    main()
