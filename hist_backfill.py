"""Pull closing AU player-prop lines for a spread-out sample of 2025-26 games.

    python hist_backfill.py [--limit N]

Takes evenly spaced games through the season (about 1 in 4), finds each game's Odds API
event on its US date, and saves the snapshot 5 minutes before tip-off. Resumes where it
stopped and never spends past the credit cap. Outputs:
    data/hist_odds/2025-26.csv.gz   one row per price
    data/hist_odds/2025-26_games.csv one row per sampled game: status, books, cost
"""
import argparse
import csv
import gzip
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from nbalib import team_key

API = "https://api.the-odds-api.com/v4/historical/sports/basketball_nba"
KEY = os.environ["ODDS_API_KEY"]
MARKETS = "player_points,player_rebounds,player_assists,player_threes,player_points_rebounds_assists"
SEASON = "2025-26"
CREDIT_CAP = 15000       # approved budget for the whole backfill
MIN_REMAINING = 3000     # never touch what the daily pipeline needs
COST_PER_GAME = 50
PILOT_LOST = 153         # pilot credits whose data wasn't saved (the folder was missing)
OUT = Path(f"data/hist_odds/{SEASON}.csv.gz")
GAMES = Path(f"data/hist_odds/{SEASON}_games.csv")
ROW_FIELDS = ["game_id", "date_us", "tip_utc", "snapshot", "game", "bookmaker", "market", "player",
              "side", "line", "odds", "last_update"]
GAME_FIELDS = ["game_id", "date_us", "game", "event_id", "tip_utc", "snapshot", "status", "books", "rows", "cost"]


class Client:
    remaining = None

    def get(self, path, **params):
        url = f"{API}{path}?{urllib.parse.urlencode(dict(params, apiKey=KEY), safe=',')}"
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    self.remaining = int(float(r.headers.get("x-requests-remaining", 0)))
                    return json.load(r), int(float(r.headers.get("x-requests-last", 0)))
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    raise SystemExit(f"API refused the key: HTTP {e.code}") from None
                if e.code == 404 or e.code == 422:
                    return None, 0
                reason = f"HTTP {e.code}"
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                reason = type(e).__name__
            time.sleep(5 * (attempt + 1))
        print(f"giving up on {path}: {reason}")
        return None, 0


def season_games():
    games = {}
    with open(f"data/gamelogs/{SEASON}.csv") as f:
        for r in csv.DictReader(f):
            g = games.setdefault(r["game_id"], {"game_id": r["game_id"], "date_us": r["date_us"]})
            g["home" if r["home"] == "1" else "away"] = r["team_name"]
    return sorted(games.values(), key=lambda g: (g["date_us"], g["game_id"]))


def sample(games, target):
    step = len(games) / target
    return [games[int(i * step)] for i in range(target)]


def load_done():
    if not GAMES.exists():
        return {}
    with open(GAMES) as f:
        return {r["game_id"]: r for r in csv.DictReader(f)}


def save(new_rows, done):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    is_new = not OUT.exists()
    with gzip.open(OUT, "at", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ROW_FIELDS)
        if is_new:
            w.writeheader()
        w.writerows(new_rows)
    with open(GAMES, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=GAME_FIELDS)
        w.writeheader()
        w.writerows(sorted(done.values(), key=lambda r: r["date_us"]))


def commit(msg):
    subprocess.run(["git", "add", "data/hist_odds"], check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        return
    subprocess.run(["git", "commit", "-q", "-m", msg], check=True)
    for _ in range(3):
        subprocess.run(["git", "pull", "-q", "--rebase"], check=False)
        if subprocess.run(["git", "push", "-q"]).returncode == 0:
            return
        time.sleep(10)
    raise SystemExit("push failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="evenly spaced subset, for a pilot")
    a = ap.parse_args()
    games = season_games()
    days = {g["date_us"] for g in sample(games, 295)}
    target = (CREDIT_CAP - PILOT_LOST - len(days)) // COST_PER_GAME
    chosen = sample(games, target)
    done = load_done()
    spent = PILOT_LOST + sum(int(r["cost"] or 0) for r in done.values())
    todo = [g for g in chosen if g["game_id"] not in done]
    if a.limit:
        todo = [todo[int(i * len(todo) / a.limit)] for i in range(a.limit)]
    print(f"{len(games)} games, sample {len(chosen)} (1 in {len(games) / len(chosen):.2f}), "
          f"{len(todo)} to pull, {spent} credits spent so far")
    client = Client()
    events_by_day = {}
    buffer = []
    for n, g in enumerate(todo, 1):
        if spent + COST_PER_GAME + 1 > CREDIT_CAP:
            print("credit cap reached")
            break
        if client.remaining is not None and client.remaining < MIN_REMAINING:
            print(f"only {client.remaining} credits left, stopping")
            break
        day = g["date_us"]
        cost = 0
        if day not in events_by_day:
            data, c = client.get("/events", date=f"{day}T16:00:00Z")
            cost += c
            events_by_day[day] = (data or {}).get("data", [])
        want = {team_key(g["home"]), team_key(g["away"])}
        ev = next((e for e in events_by_day[day]
                   if {team_key(e["home_team"]), team_key(e["away_team"])} == want), None)
        rec = {"game_id": g["game_id"], "date_us": day, "game": f"{g['away']} @ {g['home']}", "event_id": "",
               "tip_utc": "", "snapshot": "", "status": "no_event", "books": "", "rows": 0, "cost": cost}
        if ev:
            tip = datetime.fromisoformat(ev["commence_time"].replace("Z", "+00:00"))
            snap = (tip - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
            data, c = client.get(f"/events/{ev['id']}/odds", date=snap, regions="au", markets=MARKETS,
                                 oddsFormat="decimal")
            cost += c
            rows = []
            payload = (data or {}).get("data") or {}
            for b in payload.get("bookmakers", []):
                for m in b.get("markets", []):
                    for o in m.get("outcomes", []):
                        rows.append({"game_id": g["game_id"], "date_us": day, "tip_utc": ev["commence_time"],
                                     "snapshot": data.get("timestamp", ""), "game": rec["game"],
                                     "bookmaker": b["key"], "market": m["key"], "player": o.get("description", ""),
                                     "side": o["name"], "line": o.get("point", ""), "odds": o["price"],
                                     "last_update": m.get("last_update", "")})
            buffer += rows
            rec.update(event_id=ev["id"], tip_utc=ev["commence_time"], snapshot=data.get("timestamp", "") if data else "",
                       status="ok" if rows else "no_props",
                       books=" ".join(sorted({r["bookmaker"] for r in rows})), rows=len(rows), cost=cost)
        spent += cost
        done[g["game_id"]] = rec
        print(f"{n}/{len(todo)} {day} {rec['game']}: {rec['status']}, {rec['rows']} prices, cost {cost}, "
              f"spent {spent}, left {client.remaining}", flush=True)
        if n % 25 == 0:
            save(buffer, done)
            buffer = []
            commit(f"Historical odds: {len(done)} games")
        time.sleep(1)
    save(buffer, done)
    commit(f"Historical odds: {len(done)} games")
    ok = [r for r in done.values() if r["status"] == "ok"]
    print(f"done: {len(done)} games, {len(ok)} with props, {spent} credits spent, {client.remaining} left")


if __name__ == "__main__":
    main()
