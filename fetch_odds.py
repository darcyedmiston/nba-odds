"""Pull today's NBA player-prop lines from The Odds API (AU bookmakers)
and save them as a flat CSV for the 6am CES pick scan.

Runs in GitHub Actions. The API key is read from the ODDS_API_KEY
environment variable (a repo secret) and is never written to disk.
"""
import csv
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://api.the-odds-api.com/v4/sports/basketball_nba"
KEY = os.environ["ODDS_API_KEY"]
REGIONS = "au"
MARKETS = ",".join([
    "player_points",
    "player_rebounds",
    "player_assists",
    "player_threes",
    "player_points_rebounds_assists",
])
MELB = timezone(timedelta(hours=11))  # AEDT; switch to +10 in April


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        remaining = r.headers.get("x-requests-remaining")
        used = r.headers.get("x-requests-last")
        return json.load(r), remaining, used


def main():
    now = datetime.now(timezone.utc)
    events, remaining, _ = get(f"{API}/events?apiKey={KEY}")
    # Games tipping off in the next 24 hours = today's Melbourne slate
    slate = [
        e for e in events
        if now <= datetime.fromisoformat(e["commence_time"].replace("Z", "+00:00"))
        <= now + timedelta(hours=24)
    ]
    # Optional filter (pre-tip check): only re-pull games involving these
    # teams, e.g. GAMES="Knicks,Lakers", to save API credits.
    wanted = [t.strip().lower() for t in os.environ.get("GAMES", "").split(",") if t.strip()]
    if wanted:
        slate = [e for e in slate
                 if any(w in e["home_team"].lower() or w in e["away_team"].lower() for w in wanted)]

    rows, credits = [], 0
    for e in slate:
        url = (f"{API}/events/{e['id']}/odds?apiKey={KEY}&regions={REGIONS}"
               f"&markets={MARKETS}&oddsFormat=decimal")
        data, remaining, used = get(url)
        credits += int(used or 0)
        tip = datetime.fromisoformat(e["commence_time"].replace("Z", "+00:00"))
        for book in data.get("bookmakers", []):
            for m in book.get("markets", []):
                for o in m.get("outcomes", []):
                    rows.append({
                        "date_melb": tip.astimezone(MELB).strftime("%Y-%m-%d"),
                        "tipoff_melb": tip.astimezone(MELB).strftime("%H:%M"),
                        "game": f"{e['away_team']} @ {e['home_team']}",
                        "bookmaker": book["key"],
                        "market": m["key"],
                        "player": o.get("description", ""),
                        "side": o["name"],
                        "line": o.get("point", ""),
                        "odds": o["price"],
                        "last_update": m.get("last_update", ""),
                    })

    out = Path("odds")
    out.mkdir(exist_ok=True)
    stamp = datetime.now(MELB).strftime("%Y-%m-%d")
    fields = ["date_melb", "tipoff_melb", "game", "bookmaker", "market",
              "player", "side", "line", "odds", "last_update"]
    # A filtered (pre-tip) pull must not overwrite the full morning file.
    names = ("pretip.csv",) if wanted else (f"{stamp}.csv", "latest.csv")
    for name in names:
        with open(out / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    # Game lines (spread + total) for the model's D7 / minutes projection.
    # The featured-odds endpoint covers every game for 2 credits in total.
    if not wanted and slate:
        ids = {e["id"] for e in slate}
        games, remaining, used = get(f"{API}/odds?apiKey={KEY}&regions={REGIONS}"
                                     f"&markets=spreads,totals&oddsFormat=decimal")
        credits += int(used or 0)
        glines = []
        for g in games:
            if g["id"] not in ids:
                continue
            tip = datetime.fromisoformat(g["commence_time"].replace("Z", "+00:00"))
            for book in g.get("bookmakers", []):
                for m in book.get("markets", []):
                    for o in m.get("outcomes", []):
                        glines.append({
                            "date_melb": tip.astimezone(MELB).strftime("%Y-%m-%d"),
                            "tipoff_melb": tip.astimezone(MELB).strftime("%H:%M"),
                            "game": f"{g['away_team']} @ {g['home_team']}",
                            "home_team": g["home_team"], "away_team": g["away_team"],
                            "bookmaker": book["key"], "market": m["key"],
                            "name": o["name"], "point": o.get("point", ""), "odds": o["price"],
                        })
        with open(out / "game_lines.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["date_melb", "tipoff_melb", "game", "home_team", "away_team",
                                              "bookmaker", "market", "name", "point", "odds"])
            w.writeheader()
            w.writerows(glines)
        print(f"game lines: {len(glines)} prices")

    books = sorted({r["bookmaker"] for r in rows})
    print(f"{len(slate)} games, {len(rows)} prop prices, books: {books}")
    print(f"credits used this run: {credits}, remaining: {remaining}")
    # Credit tracker the scans read to warn Darcy before the quota runs out
    with open(out / "credits.json", "w") as f:
        json.dump({"checked_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "used_this_run": credits, "remaining": remaining,
                   "filtered": bool(wanted)}, f, indent=1)


if __name__ == "__main__":
    sys.exit(main())
