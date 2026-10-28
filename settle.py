"""Settle every scored prop against the box scores and keep a running report.

    python settle.py              # settle any model/scored/<date>.csv that has boxscores/<date>.csv

Appends to model/results.csv (one row per scored prop and side, flat $10 shadow P&L)
and rewrites model/report.md (hit rate / ROI by tier, side, market, and a calibration
table of model probability vs actual hit rate).
"""
import csv
from collections import defaultdict
from pathlib import Path

from nbalib import norm_name

RES = Path("model/results.csv")


def read(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def main():
    done = set()
    results = read(RES) if RES.exists() else []
    for r in results:
        done.add(r["date_melb"])
    new = []
    for path in sorted(Path("model/scored").glob("*.csv")):
        d = path.stem
        box_path = Path(f"boxscores/{d}.csv")
        if d in done or not box_path.exists():
            continue
        box = {}
        finals = True
        for b in read(box_path):
            if not b["status"].startswith("Final"):
                finals = False
            box[norm_name(b["player"])] = b
        if not finals:
            print(f"{d}: not all games final yet, skipping")
            continue
        for r in read(path):
            b = box.get(r["player_key"])
            line, odds = float(r["line"]), float(r["odds"])
            if b is None or "DNP" in b["status"] or b["minutes"] in ("0", ""):
                actual, res, pnl = "", "Void", 0.0
            else:
                actual = float(b[r["stat"]])
                if actual == line:
                    res, pnl = "Push", 0.0
                else:
                    won = actual > line if r["side"] == "Over" else actual < line
                    res, pnl = ("Win", round(10 * (odds - 1), 2)) if won else ("Loss", -10.0)
            new.append({**r, "actual": actual, "result": res, "pnl_flat10": pnl})
        print(f"{d}: settled {sum(1 for x in new if x['date_melb'] == d)} props")
    if new:
        results += new
        fields = list(results[0].keys())
        for r in new:
            for k in r:
                if k not in fields:
                    fields.append(k)
        with open(RES, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(results)
    report(results)


def summarise(rows):
    s = [r for r in rows if r["result"] in ("Win", "Loss")]
    n, w = len(s), sum(r["result"] == "Win" for r in s)
    pnl = sum(float(r["pnl_flat10"]) for r in s)
    return n, w, (100 * w / n if n else 0), pnl, (100 * pnl / (10 * n) if n else 0)


def report(results):
    md = ["# Model results (flat $10 shadow on every scored prop)", "",
          f"Settled slates: {len({r['date_melb'] for r in results})}. Samples under ~300 are noise; "
          "treat as early signals only.", ""]

    def table(title, key):
        groups = defaultdict(list)
        for r in results:
            groups[key(r)].append(r)
        md.extend([f"## {title}", "", "| Group | n | Wins | Hit % | P&L | ROI % |", "|---|---|---|---|---|---|"])
        for g in sorted(groups):
            n, w, hit, pnl, roi = summarise(groups[g])
            md.append(f"| {g} | {n} | {w} | {hit:.1f} | {pnl:+.2f} | {roi:+.1f} |")
        md.append("")

    table("By side and tier", lambda r: f"{r['side']} / {r['tier']}")
    table("Overs by market (Diff 3+)", lambda r: r["stat"] if r["side"] == "Over" and r["tier"] in ("Diff 4", "Diff 3") else "other")
    table("Calibration: model probability bucket (both sides)",
          lambda r: f"{int(float(r['model_prob']) * 20) * 5:02d}-{int(float(r['model_prob']) * 20) * 5 + 5}%")
    table("By D4 (model edge) score", lambda r: f"{r['side']} D4={r['D4']}")
    Path("model/report.md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
