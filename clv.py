"""Split closing-line value into line shopping and market movement.

    python clv.py     # writes model/clv_report.md and model/clv_detail.csv

The headline CLV compares our best book's line with the closing median, so a soft
line at one book counts as beating the close even if the market never moved:
    line_shop   = morning median line - our line   (the value of shopping around)
    market_move = closing median line - morning median line
                                                   (did the market move our way?)
Signs are flipped for Unders. Only market_move says the market agreed with the pick.
"""
import csv
import statistics as st
from collections import defaultdict
from pathlib import Path

from model import main_lines, read_csv
from nbalib import norm_name

TIERS = ["Diff 4", "Diff 3", "Watchlist", "Pass"]


def closing_medians(path):
    grouped = defaultdict(list)
    for r in read_csv(path):
        grouped[(r["game"], norm_name(r["player"]), r["market"])].append(r)
    out = {}
    for key, rows in grouped.items():
        mains = main_lines(rows)
        if mains:
            out[key] = st.median(m["line"] for m in mains.values())
    return out


def build_rows():
    rows = []
    for path in sorted(Path("odds/closing").glob("*.csv")):
        day = path.stem
        scored = Path(f"model/scored_morning/{day}.csv")
        scored = scored if scored.exists() else Path(f"model/scored/{day}.csv")
        if not scored.exists():
            continue
        close = closing_medians(path)
        for r in read_csv(scored):
            cm = close.get((r["game"], r["player_key"], r["market"]))
            if cm is None:
                continue
            sign = 1 if r["side"] == "Over" else -1
            line, med = float(r["line"]), float(r["median_line"])
            rows.append({"date_melb": day, "player": r["player"], "market": r["market"],
                         "side": r["side"], "tier": r["tier"], "line": line,
                         "morning_median": med, "close_median": cm,
                         "line_shop": round(sign * (med - line), 2),
                         "market_move": round(sign * (cm - med), 2)})
    return rows


def summary(rows):
    n = len(rows)
    move = [r["market_move"] for r in rows]
    return (f"{n} | {st.mean(r['line_shop'] for r in rows):+.2f} | {st.mean(move):+.2f} | "
            f"{100 * sum(m > 0 for m in move) / n:.1f}% | {100 * sum(m < 0 for m in move) / n:.1f}% | "
            f"{100 * sum(m == 0 for m in move) / n:.1f}%")


def main():
    rows = build_rows()
    if not rows:
        print("no closing lines matched")
        return
    with open("model/clv_detail.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    slates = len({r["date_melb"] for r in rows})
    lines = ["# CLV split: line shopping vs market movement", "",
             f"{len(rows)} props across {slates} slates. A positive market move means the market moved "
             "towards the pick. Samples under ~300 are noise.", "",
             "| Side / tier | n | Avg line shop | Avg market move | Moved our way | Moved against | Flat |",
             "|---|---|---|---|---|---|---|"]
    for side in ("Over", "Under"):
        for tier in TIERS:
            sel = [r for r in rows if r["side"] == side and r["tier"] == tier]
            if sel:
                lines.append(f"| {side} / {tier} | {summary(sel)} |")
    Path("model/clv_report.md").write_text("\n".join(lines) + "\n")
    print(f"clv: {len(rows)} props, {slates} slates")


if __name__ == "__main__":
    main()
